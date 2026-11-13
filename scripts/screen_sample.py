"""Sàng lọc tuần tự để chọn nhóm A/B (quy tắc sinh viên duyệt 2026-11-12).

Làm gì:
1. Xáo ngẫu nhiên ứng viên của một chuỗi (seed cố định), mỗi token chỉ xét một pool.
2. EVM: bỏ token cũ (contract tạo > N ngày trước pool) TRƯỚC khi tốn lượt OHLCV.
3. Thu nến ngày GeckoTerminal từ ngày tạo pool, gán cutoff, xếp nhóm A (chỉ dùng nến <= cutoff).
4. Đủ điều kiện = có cutoff trong một tập VÀ còn hoạt động tại cutoff (volume TB 7 ngày lịch
   tới cutoff >= ngưỡng trong split.yaml; sinh viên chọn 2026-11-13).
   B = token đủ điều kiện đầu tiên theo thứ tự ngẫu nhiên, tới khi đủ quota từng tập.
   A = token đạt tiêu chí A (không nằm trong B) tới khi đủ quota, hoặc hết trần sàng lọc.
5. Lọc trước (chuỗi trong `prefilter_swap_days_chains`, 2026-11-13): đếm ngày có log Swap qua
   Blockscout; pool chắc chắn < 7 ngày giao dịch thì bỏ qua GeckoTerminal. Pool bị loại vẫn
   tính vào trần sàng lọc, nên tập được chọn giống hệt khi không lọc trước, chỉ nhanh hơn.

Vì sao B vẫn là mẫu ngẫu nhiên: thứ tự đã xáo trước, nên "đủ điều kiện đầu tiên" là bốc
ngẫu nhiên trong tập token đủ điều kiện. B có thể chứa token đạt tiêu chí A (cột meets_a).
Nến thu ở đây cũng là OHLCV ngày đợt 1, dùng cho cổng 18/11.

Chạy:   .venv/bin/python scripts/screen_sample.py --chain solana
Chạy lại cùng lệnh sẽ đọc cache và tiếp tục (cache không tính vào giới hạn tốc độ).
"""
from __future__ import annotations

import argparse
import csv
import os
import random
import sys
from datetime import date, datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from memecoin.collect.activity import count_swap_days  # noqa: E402
from memecoin.collect.common import load_config, midnight, utc_now, write_csv, write_json  # noqa: E402
from memecoin.collect.evm import EvmReader  # noqa: E402
from memecoin.collect.http import CollectionError, HttpClient  # noqa: E402
from memecoin.collect.ohlcv import FIELDS as OHLCV_FIELDS, GeckoTerminal  # noqa: E402
from memecoin.collect.window import token_is_new  # noqa: E402
from memecoin.model.sampling import allocate, assign_cutoff  # noqa: E402

SCREEN_FIELDS = ["order", "chain", "pool_address", "token_address", "dex", "version", "stratum", "creation_day",
                 "token_new", "token_age_evidence", "ohlcv_requested", "indexed", "error", "candles",
                 "cutoff", "split", "first_close", "cutoff_close", "price_ratio", "group_a",
                 "active_volume_usd", "active", "prefilter", "prefilter_swap_days", "prefilter_reason",
                 "selected_group"]
SETS = ("train", "validation", "test")


def secrets() -> tuple[str, ...]:
    return tuple(os.environ.get(k, "") for k in ("BLOCKSCOUT_API_KEY", "DRPC_API_KEY", "HELIUS_API_KEY"))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--chain", choices=["ethereum", "base", "solana"], required=True)
    parser.add_argument("--end", default="2026-11-12", help="Ngày UTC kết thúc nến (không gồm), cố định để replay")
    parser.add_argument("--budget", type=int, help="Ghi đè trần số pool thu OHLCV (mặc định từ split.yaml)")
    parser.add_argument("--offline", action="store_true")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--no-prefilter", action="store_true", help="Tắt lọc trước bằng log Swap (để đối chiếu)")
    args = parser.parse_args()
    output = args.output or ROOT / f"data/interim/task2/screening/{args.chain}"
    split, chains = load_config("split.yaml"), load_config("chains.yaml")
    settings = split["sampling"]
    budget = args.budget or int(settings.get("screening_budget_pools_by_chain", {}).get(
        args.chain, settings["screening_budget_pools"]))
    quota = allocate(int(settings["per_group_per_chain"]), split)
    if not args.offline:
        from dotenv import load_dotenv
        load_dotenv(ROOT / ".env", override=False)

    gecko_cfg = chains["common"]["ohlcv"]
    gecko = GeckoTerminal(HttpClient(ROOT, "geckoterminal", gecko_cfg["max_requests_per_minute"] / 60,
                                     offline=args.offline, max_requests=100000, secrets=secrets()), gecko_cfg)
    reader = None
    if args.chain != "solana":
        logs = chains[args.chain]["logs"]
        reader = EvmReader(args.chain, HttpClient(ROOT, logs["provider"], logs["max_requests_per_second"],
                           offline=args.offline, max_requests=100000, secrets=secrets()), chains[args.chain])

    source = ROOT / f"data/interim/task2/candidates/{args.chain}/pool_candidates.csv"
    candidates = list(csv.DictReader(source.open(encoding="utf-8")))
    random.Random(f"{split['seed']}:screen:{args.chain}").shuffle(candidates)
    start_ts, end_ts = None, midnight(args.end)
    now = min(end_ts, int(datetime.now(timezone.utc).timestamp()))
    use_prefilter = args.chain in settings.get("prefilter_swap_days_chains", []) and not args.no_prefilter
    # Ngày cutoff muộn nhất của mọi tập: swap sau ngày này không giúp token có cutoff trong tập nào.
    last_cutoff = max(date.fromisoformat(str(b["cutoff_end"])) for b in split["sets"].values())
    prefilter_counts = {"pass": 0, "reject": 0, "unknown": 0}

    selected = {"B": {s: [] for s in SETS}, "A": {s: [] for s in SETS}}
    screened, candles_out, seen_tokens = [], [], set()
    ohlcv_pools = 0
    stop_reason = "candidates_exhausted"

    def full(group: str) -> bool:
        return all(len(selected[group][s]) >= quota[s] for s in SETS)

    def flush() -> None:
        write_csv(output / "screened.csv", screened, SCREEN_FIELDS)
        write_csv(output / "ohlcv_day.csv", candles_out, OHLCV_FIELDS)
        write_csv(output / "selected.csv", [r for r in screened if r["selected_group"]], SCREEN_FIELDS)
        write_json(output / "progress.json", {"chain": args.chain, "updated_at": utc_now(), "quota_per_group": quota,
            "budget_pools": budget, "ohlcv_pools": ohlcv_pools, "rows_screened": len(screened),
            "selected": {g: {s: len(v) for s, v in sets.items()} for g, sets in selected.items()},
            "stop_reason": stop_reason, "gecko": gecko.client.stats(),
            "prefilter": {"enabled": use_prefilter, **prefilter_counts},
            "evm": reader.client.stats() if reader else None, "candidates_total": len(candidates),
            "research_sample": "selection_pending_student_review"})

    def report_progress() -> None:
        if ohlcv_pools % 25 == 0:
            flush()
            sel = {g: sum(len(v) for v in s.values()) for g, s in selected.items()}
            extra = f", lọc trước {prefilter_counts}" if use_prefilter else ""
            print(f"{args.chain}: đã xét {ohlcv_pools}/{budget} pool (trần), dòng {len(screened)}, "
                  f"B={sel['B']}, A={sel['A']}{extra}", flush=True)

    # Ethereum: hỏi tuổi token theo lô (đúng thứ tự xáo) để tiết kiệm credit; không đổi kết quả từng token.
    batch_size = int(chains[args.chain]["logs"].get("creation_batch_size", 1)) if reader is not None else 1
    token_order = list(dict.fromkeys(p["token_address"] for p in candidates)) if batch_size > 1 else []
    token_index = {t: i for i, t in enumerate(token_order)}
    prefetched: set[str] = set()

    for order, pool in enumerate(candidates):
        if full("A") and full("B"):
            stop_reason = "quotas_filled"
            break
        if ohlcv_pools >= budget:
            stop_reason = "budget_exhausted"
            break
        token = pool["token_address"]
        if token in seen_tokens:
            continue  # một token chỉ xét một pool (pool gặp trước theo thứ tự ngẫu nhiên)
        seen_tokens.add(token)
        creation = date.fromisoformat(pool["creation_day"])
        row = {"order": order, **{k: pool.get(k, "") for k in ("chain", "pool_address", "token_address", "dex",
               "version", "stratum", "creation_day")}, "selected_group": ""}
        if reader is not None:
            try:
                if batch_size > 1 and token not in prefetched:
                    batch = token_order[token_index[token]: token_index[token] + batch_size]
                    reader.prefetch_contract_creations(batch)
                    prefetched.update(batch)
                is_new, evidence = token_is_new(reader, token, creation, int(settings["new_token_max_age_days"]))
            except CollectionError as exc:
                # Lỗi nguồn (hết credit, mất mạng) thì DỪNG, không bỏ qua token: bỏ qua sẽ làm đổi mẫu
                # theo cách không tái tạo được. Lỗi không được cache, nên chạy lại là tiếp tục đúng chỗ.
                stop_reason = f"evm_error: {str(exc)[:200]}"
                break
            row.update(token_new=is_new, token_age_evidence=evidence.get("created_at") or evidence.get("checked_at")
                       or evidence.get("reason") or evidence.get("error"))
            if is_new is not True:
                row["ohlcv_requested"] = False
                screened.append(row)
                continue
        else:
            row["token_new"] = "pumpfun_mint"
        ohlcv_pools += 1  # trần tính cả pool bị lọc trước loại, để kết quả không đổi so với khi không lọc
        if use_prefilter:
            check = count_swap_days(reader, pool, chains[args.chain], creation, last_cutoff,
                                    int(split["min_history_days"]))
            prefilter_counts[check.status] += 1
            row.update(prefilter=check.status, prefilter_swap_days=check.swap_days, prefilter_reason=check.reason)
            if check.passed is False:
                row.update(ohlcv_requested=False, split="no_cutoff")
                screened.append(row)
                report_progress()
                continue
        row["ohlcv_requested"] = True
        try:
            candles, report = gecko.collect(args.chain, pool["pool_address"], token, "day",
                                            midnight(creation), end_ts, max_pages=2, now=now)
            row.update(indexed=report["error"] is None, error=report["error"], candles=len(candles))
        except CollectionError as exc:
            candles = []
            row.update(indexed=False, error=str(exc)[:200], candles=0)
        candles_out.extend(candles)
        result = assign_cutoff(candles, creation, split)
        row.update(cutoff=result.cutoff, split=result.split, first_close=result.first_close,
                   cutoff_close=result.cutoff_close, price_ratio=result.price_ratio, group_a=result.group_a,
                   active_volume_usd=result.active_volume_usd, active=result.active)
        # Chỉ token còn hoạt động tại cutoff mới đủ điều kiện (phương án (a), 2026-11-13).
        if result.split in SETS and result.active:
            if len(selected["B"][result.split]) < quota[result.split]:
                row["selected_group"] = "B"
            elif result.group_a and len(selected["A"][result.split]) < quota[result.split]:
                row["selected_group"] = "A"
            if row["selected_group"]:
                selected[row["selected_group"]][result.split].append(token)
        screened.append(row)
        report_progress()
    flush()
    print(f"{args.chain}: xong ({stop_reason}). Xem {output / 'progress.json'}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
