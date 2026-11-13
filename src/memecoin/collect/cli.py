"""Các lệnh collector có thể chạy lại; không tự chọn mẫu nghiên cứu từ snapshot."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any

import duckdb
from dotenv import load_dotenv

from .common import ROOT, iso_time, load_config, midnight, utc_now, write_csv, write_json
from .evm import EvmReader, collect_factory_logs
from .http import CollectionError, HttpClient
from .ohlcv import FIELDS, GeckoTerminal
from .solana import HeliusReader, migration_candidates
from .swaps import FIELDS as SWAP_FIELDS, decode_logs
from .window import (FIELDS as WINDOW_FIELDS, aggregate, creation_strata, discover_evm_day,
                     discover_solana_day, evm_pool_rows, sample_days, solana_pool_rows)


def client_for(provider: str, rate: float, args: argparse.Namespace) -> HttpClient:
    return HttpClient(ROOT, provider, rate, offline=args.offline, refresh=args.refresh,
                      max_requests=args.max_requests,
                      cache_namespace=args.cache_namespace,
                      secrets=tuple(os.environ.get(k, "") for k in
                                    ("BLOCKSCOUT_API_KEY", "DRPC_API_KEY", "HELIUS_API_KEY")))


def gecko_for(args: argparse.Namespace, config: dict[str, Any]) -> GeckoTerminal:
    settings = config["common"]["ohlcv"]
    return GeckoTerminal(client_for("geckoterminal", settings["max_requests_per_minute"] / 60, args), settings)


def evm_for(args: argparse.Namespace, config: dict[str, Any]) -> EvmReader:
    settings = config[args.chain]["logs"]
    return EvmReader(args.chain, client_for(settings["provider"], settings["max_requests_per_second"], args), config[args.chain])


def helius_for(args: argparse.Namespace, config: dict[str, Any]) -> HeliusReader:
    settings = config["solana"]["rpc"]
    return HeliusReader(client_for("helius", settings["max_requests_per_second"], args), config["solana"])


def save_report(output: Path, report: dict[str, Any], clients: list[HttpClient]) -> None:
    report.update(generated_at=utc_now(), clients={c.provider: c.stats() for c in clients})
    report["config_sha256"] = {name: hashlib.sha256((ROOT / "configs" / name).read_bytes()).hexdigest()
                              for name in ("chains.yaml", "split.yaml", "thresholds.yaml")}
    write_json(output / "report.json", report)
    summary = {k: report[k] for k in ("task", "chain", "pools", "pools_created", "rows", "swaps", "transactions", "complete", "raw_checked") if k in report}
    summary.update(report=str(output / "report.json"), clients=report["clients"])
    print(json.dumps(summary, ensure_ascii=False, indent=2))


def resolve_smoke(args: argparse.Namespace, config: dict[str, Any]) -> int:
    """Chỉ tìm pool ví dụ để kiểm tra đường truyền, không đưa vào bảng samples."""
    gecko = gecko_for(args, config)
    rows, errors = [], []
    with args.tokens.open(encoding="utf-8") as handle:
        tokens = list(csv.DictReader(handle))
    for token in tokens:
        try:
            response = gecko.token_pools(token["chain"], token["token_address"])
            pools = response.data["data"]
            if not pools:
                raise CollectionError("Không có pool tham chiếu.")
            # Thứ hạng nguồn ở HIỆN TẠI chỉ dùng cho smoke test, không chọn mẫu as-of.
            pool = pools[0]
            rows.append({**token, "pool_address": pool["attributes"]["address"],
                         "dex": pool["relationships"]["dex"]["data"]["id"],
                         "pool_created_at": pool["attributes"].get("pool_created_at"),
                         "purpose": "technical_smoke_only_not_research_sample",
                         "source": "geckoterminal_current_snapshot", "raw_ref": response.raw_ref})
        except CollectionError as exc:
            errors.append({"chain": token["chain"], "error": str(exc)})
    write_csv(args.output / "pools.csv", rows,
              ["chain", "token_address", "symbol", "pool_address", "dex", "pool_created_at", "purpose", "source", "raw_ref"])
    save_report(args.output, {"task": "resolve_smoke", "pools": len(rows), "errors": errors,
                              "research_sample": False}, [gecko.client])
    return 2 if errors else 0


def collect_ohlcv(args: argparse.Namespace, config: dict[str, Any]) -> int:
    gecko = gecko_for(args, config)
    with args.pools.open(encoding="utf-8") as handle:
        pools = list(csv.DictReader(handle))
    if not pools:
        raise CollectionError("CSV pool rỗng.")
    rows, reports, errors = [], [], []
    for pool in pools:
        for timeframe in args.timeframes:
            try:
                data, report = gecko.collect(pool["chain"], pool["pool_address"], pool["token_address"],
                                             timeframe, midnight(args.start), midnight(args.end), max_pages=args.max_pages)
                rows.extend(data)
                reports.append(report)
                print(f"{pool['chain']}/{pool.get('symbol', pool['pool_address'])}/{timeframe}: "
                      f"{report['candles']} nến, {report['missing_intervals']} khoảng thiếu", flush=True)
            except (CollectionError, ValueError) as exc:
                errors.append({"chain": pool["chain"], "pool": pool["pool_address"],
                               "timeframe": timeframe, "error": str(exc)})
    # Xuất cả khi một pool lỗi để giữ phần công việc đã làm.
    rows.sort(key=lambda r: (r["chain"], r["pool_address"], r["timeframe"], r["ts"]))
    args.output.mkdir(parents=True, exist_ok=True)
    write_csv(args.output / "ohlcv.csv", rows, FIELDS)
    write_json(args.output / "ohlcv.json", rows)
    if rows:
        # Mỗi lần chạy dựng lại DB/Parquet từ bảng có raw_ref; không sửa data/raw/.
        db = duckdb.connect(str(args.output / "collection.duckdb"))
        try:
            db.execute((ROOT / "docs/schema.sql").read_text(encoding="utf-8"))
            db.execute("DELETE FROM ohlcv")
            db.executemany("INSERT INTO ohlcv VALUES (" + ",".join("?" for _ in FIELDS) + ")",
                           [tuple(row[f] for f in FIELDS) for row in rows])
            db.execute("COPY (SELECT * FROM ohlcv ORDER BY chain,pool_address,timeframe,ts) TO "
                       "? (FORMAT PARQUET)", [str(args.output / "ohlcv.parquet")])
        finally:
            db.close()
    digest = hashlib.sha256((args.output / "ohlcv.csv").read_bytes()).hexdigest()
    save_report(args.output, {"task": "ohlcv", "start": args.start, "end_exclusive": args.end,
        "pools_requested": len(pools), "rows": len(rows), "ohlcv_csv_sha256": digest,
        "errors": errors, "coverage": reports,
        "research_sample": False if any(p.get("purpose", "").startswith("technical_") for p in pools) else "not_validated"},
        [gecko.client])
    return 2 if errors or any(r["error"] or r["stop_reason"] in {"page_limit", "cursor_stalled"} for r in reports) else 0


def discover(args: argparse.Namespace, config: dict[str, Any]) -> int:
    if args.chain == "solana":
        helius = helius_for(args, config)
        account = config["solana"]["token_list"]["migration_account"]
        records, report = helius.history(account, midnight(args.start), midnight(args.end),
                                          page_size=args.page_size, max_pages=args.max_pages)
        candidates = migration_candidates(records, account, config["solana"]["token_list"])
        write_json(args.output / "transactions.json", records)
        write_json(args.output / "migration_candidates.json", candidates)
        pools = solana_pool_rows(candidates)
        write_csv(args.output / "pool_candidates.csv", pools,
                  ["chain", "pool_address", "token_address", "quote_token", "created_at", "created_tx",
                   "instruction", "source", "raw_ref", "collected_at", "eligibility"])
        report.update(task="discover", chain="solana", migrations=len(candidates),
                      pools_resolved=len({r['pool_address'] for c in candidates for r in c['resolved']}),
                      pools_created=len(pools),
                      limitation="Chỉ token tốt nghiệp pump.fun; chưa chọn mẫu A/B/C hoặc pool lớn nhất tại cutoff.")
        save_report(args.output, report, [helius.client])
        return 0 if report["complete"] else 2
    evm = evm_for(args, config)
    if (args.from_block is None) != (args.to_block is None):
        raise ValueError("Phải truyền cả from-block và to-block hoặc không truyền cả hai.")
    left = args.from_block if args.from_block is not None else evm.block_at(midnight(args.start) - 1) + 1
    right = args.to_block if args.to_block is not None else evm.block_at(midnight(args.end) - 1)
    factories = [f for f in config[args.chain]["factories"] if f["name"] in args.factories]
    if set(args.factories) - {f["name"] for f in factories}:
        raise ValueError("Factory chưa có cấu hình; cần xác minh địa chỉ/topic trước.")
    logs, report = collect_factory_logs(evm, left, right, factories, grouped=not args.separate_factories,
                                        max_chunks=args.max_chunks)
    rows = evm_pool_rows(args.chain, logs, factories, config[args.chain]["quote_tokens"])
    write_json(args.output / "factory_logs.json", logs)
    fields = ["chain", "pool_address", "token_address", "quote_token", "dex", "version", "created_at",
              "created_tx", "source", "collected_at", "raw_ref", "eligibility"]
    write_csv(args.output / "pool_candidates.csv", rows, fields)
    save_report(args.output, {"task": "discover", "chain": args.chain, "pools": len(rows), **report,
        "research_sample": False, "limitation": "Log tạo pool chưa chứng minh token là meme, chưa chọn mẫu A/B/C."}, [evm.client])
    return 0 if report["complete"] else 2


def discover_window(args: argparse.Namespace, config: dict[str, Any]) -> int:
    """Quét từng ngày tạo pool trong 3 tầng; chạy lại tiếp từ cache, không sửa raw."""
    split = load_config("split.yaml")
    strata = {k: v for k, v in creation_strata(split).items() if k in args.strata}
    allocation = split["discovery"]["sampled_days"].get(args.chain)
    plan = sample_days(strata, {k: allocation[k] for k in strata} if allocation else None,
                       split["seed"], args.chain)
    today = datetime.now(timezone.utc).date()
    if any(d >= today for days in plan.values() for d in days):
        raise ValueError("Có ngày chưa kết thúc trong kế hoạch quét.")
    write_json(args.output / "plan.json", {"chain": args.chain, "seed": split["seed"],
        "strata": {k: [a.isoformat(), b.isoformat()] for k, (a, b) in strata.items()},
        "sampled": bool(allocation), "days": {k: [d.isoformat() for d in v] for k, v in plan.items()}})
    if args.chain == "solana":
        reader: Any = helius_for(args, config)
    else:
        reader = evm_for(args, config)
        factories = config[args.chain]["factories"]
    planned_days = sorted(d for days in plan.values() for d in days)
    run_days = planned_days
    if args.days:
        wanted = {date.fromisoformat(d) for d in args.days}
        if wanted - set(planned_days):
            raise ValueError("--days có ngày không thuộc kế hoạch quét của chuỗi này.")
        run_days = [d for d in planned_days if d in wanted]  # chạy thử; xác suất chọn vẫn theo kế hoạch đầy đủ
    day_rows, coverage = {}, []
    for day in run_days:
        folder = args.output / "days" / day.isoformat()
        before = reader.client.stats()
        rate_limited = 0
        while True:
            try:
                if args.chain == "solana":
                    rows, report = discover_solana_day(reader, day, config["solana"]["token_list"],
                                                       page_size=args.page_size, max_pages=args.max_pages)
                else:
                    rows, report = discover_evm_day(reader, day, factories, max_chunks=args.max_chunks)
            except CollectionError as exc:
                rows, report = [], {"complete": False, "error": str(exc)}
            errors = " ".join(str(s.get("error") or "") for s in report.get("scans", [])) + str(report.get("error") or "")
            # Gói free báo 429 theo cửa sổ thời gian: nghỉ rồi chạy lại ngày; dải đã thu đọc từ cache.
            if report.get("complete") or "HTTP 429" not in errors or rate_limited >= args.rate_limit_retries:
                break
            rate_limited += 1
            print(f"{args.chain} {day}: 429, nghỉ {args.rate_limit_pause}s rồi chạy tiếp (lần {rate_limited})", flush=True)
            reader.client.sleep(args.rate_limit_pause)
        report["rate_limit_pauses"] = rate_limited
        after = reader.client.stats()
        day_rows[day] = rows
        write_csv(folder / "pool_candidates.csv", rows, WINDOW_FIELDS)
        write_json(folder / "report.json", report)
        coverage.append({"day": day.isoformat(), "complete": bool(report.get("complete")),
            "error": report.get("error"), "pools": len(rows),
            "logs_by_factory": report.get("logs_by_factory"), "migrations": report.get("migrations"),
            "rate_limit_pauses": rate_limited,
            "network_requests": after["network_requests"] - before["network_requests"],
            "cache_hits": after["cache_hits"] - before["cache_hits"]})
        print(f"{args.chain} {day}: {len(rows)} pool, complete={coverage[-1]['complete']}, "
              f"request mới={coverage[-1]['network_requests']}", flush=True)
        write_json(args.output / "coverage.json", coverage)
        if "Hết ngân sách" in errors:
            break  # Chạy lại cùng lệnh để tiếp tục từ cache.
    rows = aggregate({d: r for d, r in day_rows.items()}, plan, strata)
    write_csv(args.output / "pool_candidates.csv", rows, WINDOW_FIELDS)
    planned = len(run_days)
    done = sum(c["complete"] for c in coverage)
    save_report(args.output, {"task": "discover_window", "chain": args.chain, "pools": len(rows),
        "days_planned": planned, "days_complete": done, "complete": done == planned,
        "subset_of_plan": len(run_days) < len(planned_days),
        "by_stratum": {k: sum(r["stratum"] == k for r in rows) for k in plan},
        "research_sample": False,
        "limitation": "Ứng viên chưa xác minh meme, chưa chọn pool lớn nhất tại cutoff, chưa chọn A/B/C."},
        [reader.client])
    return 0 if done == planned else 2


def transactions(args: argparse.Namespace, config: dict[str, Any]) -> int:
    helius = helius_for(args, config)
    records, report = helius.history(args.address, midnight(args.start), midnight(args.end),
                                    page_size=args.page_size, max_pages=args.max_pages)
    write_json(args.output / "transactions.json", records)
    write_csv(args.output / "transactions.csv", ({"signature": r["signature"],
        "block_time": iso_time(r["transaction"]["blockTime"]), "slot": r["transaction"]["slot"],
        "raw_ref": r["raw_ref"], "explorer": "https://solscan.io/tx/" + r["signature"]} for r in records),
        ["signature", "block_time", "slot", "raw_ref", "explorer"])
    report.update(task="transactions", chain="solana")
    save_report(args.output, report, [helius.client])
    return 0 if report["complete"] else 2


def logs_command(args: argparse.Namespace, config: dict[str, Any]) -> int:
    evm = evm_for(args, config)
    if (args.from_block is None) != (args.to_block is None):
        raise ValueError("Phải truyền cả from-block và to-block hoặc không truyền cả hai.")
    left = args.from_block if args.from_block is not None else evm.block_at(midnight(args.start) - 1) + 1
    right = args.to_block if args.to_block is not None else evm.block_at(midnight(args.end) - 1)
    addresses: str | list[str] = args.addresses if len(args.addresses) > 1 else args.addresses[0]
    topics = [args.topics] if args.topics else [args.topic]
    records, report = evm.collect_logs(left, right, addresses, topics, max_chunks=args.max_chunks)
    write_json(args.output / "logs.json", records)
    report.update(task="logs", addresses=args.addresses, topic=args.topic, topics=topics)
    save_report(args.output, report, [evm.client])
    return 0 if report["complete"] else 2


def verify(args: argparse.Namespace, config: dict[str, Any]) -> int:
    metas = list((args.raw or ROOT / "data/raw").rglob("*.meta.json"))
    checked, failures = 0, []
    for path in metas:
        meta = json.loads(path.read_text(encoding="utf-8"))
        if "sha256" not in meta or "raw_ref" not in meta:
            continue  # File pilot cũ có định dạng khác, không tự coi là đã kiểm tra.
        checked += 1
        raw_path = ROOT / meta["raw_ref"]
        if not raw_path.exists() or hashlib.sha256(raw_path.read_bytes()).hexdigest() != meta["sha256"]:
            failures.append(str(path.relative_to(ROOT)))
    if not checked:
        failures.append("Không tìm thấy raw có metadata SHA-256 mới.")
    save_report(args.output, {"task": "verify", "raw_checked": checked, "failures": failures}, [])
    return 2 if failures else 0


def decode_evm(args: argparse.Namespace, config: dict[str, Any]) -> int:
    evm = evm_for(args, config)
    logs = json.loads(args.input.read_text(encoding="utf-8"))
    rows, unresolved = decode_logs(evm, logs, token0=args.token0, meme=args.meme, protocol=args.protocol,
                                   token_decimals=args.token_decimals, quote_decimals=args.quote_decimals)
    write_csv(args.output / "swaps.csv", rows, SWAP_FIELDS)
    write_json(args.output / "swaps.json", rows)
    save_report(args.output, {"task": "decode_evm", "chain": args.chain, "swaps": len(rows),
                              "unresolved": unresolved, "usd_available": False}, [evm.client])
    return 2 if unresolved else 0


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description=__doc__)
    sub = root.add_subparsers(dest="command", required=True)
    for name in ("resolve-smoke", "ohlcv", "discover", "discover-window", "transactions", "logs", "decode-evm", "verify"):
        command = sub.add_parser(name)
        command.add_argument("--output", type=Path, required=True)
        command.add_argument("--offline", action="store_true", help="Chỉ cache, thiếu thì báo lỗi")
        command.add_argument("--refresh", action="store_true", help="Gọi mới, vẫn giữ nguyên mọi raw cũ")
        command.add_argument("--max-requests", type=int, default=10000)
        command.add_argument("--cache-namespace", help="Cache riêng cho benchmark; vẫn chung rate limit provider")
        if name in {"ohlcv", "discover", "transactions", "logs"}:
            command.add_argument("--start", default=str(load_config("split.yaml")["data_start"]))
            command.add_argument("--end", required=True, help="Ngày UTC kết thúc, không bao gồm ngày này")
            command.add_argument("--max-pages", type=int, default=20)
        if name in {"discover", "logs"}:
            command.add_argument("--chain", choices=["ethereum", "base", "solana"] if name == "discover" else ["ethereum", "base"], required=True)
            command.add_argument("--from-block", type=int)
            command.add_argument("--to-block", type=int)
            command.add_argument("--max-chunks", type=int, default=10000)
        if name == "resolve-smoke":
            command.add_argument("--tokens", type=Path, default=ROOT / "validation/collector_smoke_tokens.csv")
        elif name == "ohlcv":
            command.add_argument("--pools", type=Path, required=True)
            command.add_argument("--timeframes", nargs="+", choices=["day", "hour"], default=["day"])
        elif name == "discover":
            command.add_argument("--factories", nargs="+", default=["uniswap_v2"])
            command.add_argument("--separate-factories", action="store_true", help="Quét riêng để đối chiếu với Base gộp mặc định")
            command.add_argument("--page-size", type=int, default=100)
        elif name == "transactions":
            command.add_argument("--address", required=True)
            command.add_argument("--page-size", type=int, default=100)
        elif name == "logs":
            command.add_argument("--addresses", nargs="+", required=True)
            topic_group = command.add_mutually_exclusive_group()
            topic_group.add_argument("--topic", help="Bỏ trống để lấy mọi loại log của địa chỉ")
            topic_group.add_argument("--topics", nargs="+", help="Nhiều lựa chọn OR tại topic0")
        elif name == "decode-evm":
            command.add_argument("--chain", choices=["ethereum", "base"], required=True)
            command.add_argument("--input", type=Path, required=True)
            command.add_argument("--token0", required=True)
            command.add_argument("--meme", required=True)
            command.add_argument("--protocol", choices=["v2", "v3"], required=True)
            command.add_argument("--token-decimals", type=int)
            command.add_argument("--quote-decimals", type=int)
        elif name == "discover-window":
            command.add_argument("--chain", choices=["ethereum", "base", "solana"], required=True)
            command.add_argument("--strata", nargs="+", default=["train", "validation", "test"],
                                 choices=["train", "validation", "test"])
            command.add_argument("--max-chunks", type=int, default=10000)
            command.add_argument("--max-pages", type=int, default=50)
            command.add_argument("--page-size", type=int, default=100)
            command.add_argument("--days", nargs="+", help="Chỉ chạy các ngày này (chạy thử), phải thuộc kế hoạch")
            command.add_argument("--rate-limit-pause", type=float, default=60, help="Giây nghỉ khi nhà cung cấp trả 429")
            command.add_argument("--rate-limit-retries", type=int, default=10)
        elif name == "verify":
            command.add_argument("--raw", type=Path)
    return root


def main() -> int:
    args = parser().parse_args()
    if not args.offline:
        load_dotenv(ROOT / ".env", override=False)
    handlers = {"resolve-smoke": resolve_smoke, "ohlcv": collect_ohlcv, "discover": discover,
                "discover-window": discover_window,
                "transactions": transactions, "logs": logs_command, "decode-evm": decode_evm, "verify": verify}
    try:
        if hasattr(args, "start"):
            if midnight(args.start) >= midnight(args.end):
                raise ValueError("start phải trước end.")
            if args.command != "ohlcv" and midnight(args.end) > int(datetime.now(timezone.utc).timestamp()):
                raise ValueError("Không thu lịch sử giao dịch cho ngày tương lai.")
        return handlers[args.command](args, load_config("chains.yaml"))
    except (CollectionError, ValueError, KeyError) as exc:
        message = str(exc)
        for key in ("BLOCKSCOUT_API_KEY", "DRPC_API_KEY", "HELIUS_API_KEY"):
            if os.environ.get(key):
                message = message.replace(os.environ[key], "<redacted>")
        write_json(args.output / "error.json", {"error": message, "generated_at": utc_now()})
        print(f"Lỗi: {message}")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
