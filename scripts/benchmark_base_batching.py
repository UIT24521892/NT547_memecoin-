"""Đo và kiểm thử gộp truy vấn Base trên 1.000 block lịch sử.

Lần thu mới: .venv/bin/python scripts/benchmark_base_batching.py --online
Kiểm thử lại bằng cache, không key: .venv/bin/python scripts/benchmark_base_batching.py
Mỗi lần online có thư mục/cache riêng; vẫn dùng rate limit dRPC trong configs.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import os
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from memecoin.collect.common import load_config, write_json
from memecoin.collect.evm import as_int
from memecoin.collect.http import CollectionError
from memecoin.collect.swaps import V2_SWAP, V3_SWAP

START_BLOCK, END_BLOCK = 47130126, 47131125
FACTORIES = ["uniswap_v2", "uniswap_v3", "aerodrome"]
# Pool chỉ để kiểm tra kỹ thuật, không vào mẫu nghiên cứu/as-of.
POOLS = ["0x4e829f8a5213c42535ab84aa40bd4adcce9cba02", "0x6298bf80e26bf2228e9e8e9bcdd0d4c80be369cb"]


def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def canonical_logs(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """So nội dung on-chain; metadata ngày thu/raw_ref của hai lần gọi được giữ riêng."""
    fields = ["address", "blockHash", "data", "topics", "transactionHash"]
    result = []
    for row in rows:
        item = {k: [v.lower() for v in row[k]] if isinstance(row[k], list) else row[k].lower() for k in fields}
        item.update({k: as_int(row[k]) for k in ("blockNumber", "transactionIndex", "logIndex")})
        item["removed"] = bool(row.get("removed", False))
        result.append(item)
    return sorted(result, key=lambda r: (r["blockNumber"], r["logIndex"]))


def canonical_pools(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8") as handle:
        rows = [{k: v for k, v in row.items() if k not in {"raw_ref", "collected_at"}} for row in csv.DictReader(handle)]
    return sorted(rows, key=lambda r: (r["chain"], r["pool_address"]))


def execute_case(case: dict[str, Any], output: Path, *, offline: bool) -> dict[str, Any]:
    """Mỗi tình huống là tiến trình mới: resume chỉ dựa vào file đã lưu."""
    command = [sys.executable, "scripts/collect.py", *case["options"], "--output", str(output),
               "--cache-namespace", case["cache_namespace"], "--max-requests", "200"]
    if offline:
        command.append("--offline")
    environment = dict(os.environ)
    if offline:
        for key in ("DRPC_API_KEY", "BLOCKSCOUT_API_KEY", "HELIUS_API_KEY"):
            environment.pop(key, None)
    started = time.monotonic()
    result = subprocess.run(command, cwd=ROOT, env=environment, capture_output=True, text=True, timeout=300)
    expected = 0 if offline else case["exit_code"]
    if result.returncode != expected:
        raise CollectionError(f"{case['name']}: exit={result.returncode}, cần {expected}. " + result.stdout[-1000:] + result.stderr[-1000:])
    report = read_json(output / "report.json")
    stats = report["clients"]["drpc"]
    if offline and stats["network_requests"]:
        raise CollectionError(f"{case['name']}: offline đã gọi mạng.")
    report["process_elapsed_seconds"] = round(time.monotonic() - started, 6)
    print(f"{case['name']}: {stats['network_requests']} request mạng, {stats['cache_hits']} cache hit, "
          f"{report['process_elapsed_seconds']:.2f}s", flush=True)
    return report


def cases_for(namespace: str) -> list[dict[str, Any]]:
    common = ["--chain", "base", "--start", "2026-06-10", "--end", "2026-06-11",
              "--from-block", str(START_BLOCK), "--to-block", str(END_BLOCK)]
    discover = ["discover", *common, "--factories", *FACTORIES]
    definitions = [
        ("factories_separate", [*discover, "--separate-factories"], namespace, 0),
        ("factories_grouped", discover, namespace, 0),
        ("resume_paused", [*discover, "--max-chunks", "3"], namespace + "_resume", 2),
        ("resume_completed", discover, namespace + "_resume", 0),
        ("pool_separate_0", ["logs", *common, "--addresses", POOLS[0], "--topics", V2_SWAP, V3_SWAP], namespace, 0),
        ("pool_separate_1", ["logs", *common, "--addresses", POOLS[1], "--topics", V2_SWAP, V3_SWAP], namespace, 0),
        ("pools_grouped", ["logs", *common, "--addresses", *POOLS, "--topics", V2_SWAP, V3_SWAP], namespace, 0),
    ]
    return [{"name": name, "options": options, "cache_namespace": ns, "exit_code": code} for name, options, ns, code in definitions]


def verify_raw(namespaces: set[str]) -> dict[str, Any]:
    checked, failures = 0, []
    for meta_path in (ROOT / "data/raw").glob("*/drpc/*.meta.json"):
        meta = read_json(meta_path)
        if meta.get("cache_namespace") not in namespaces:
            continue
        checked += 1
        raw_path = ROOT / meta["raw_ref"]
        if not raw_path.exists() or hashlib.sha256(raw_path.read_bytes()).hexdigest() != meta["sha256"]:
            failures.append(meta["raw_ref"])
    return {"checked": checked, "failures": failures}


def compare_cases(folder: Path, reports: dict[str, Any], chunks: int, width: int) -> dict[str, Any]:
    factory_logs = {name: read_json(folder / name / "factory_logs.json") for name in
                    ("factories_separate", "factories_grouped", "resume_paused", "resume_completed")}
    apart = canonical_logs(factory_logs["factories_separate"])
    together = canonical_logs(factory_logs["factories_grouped"])
    pool_apart = sum((read_json(folder / f"pool_separate_{i}/logs.json") for i in range(len(POOLS))), [])
    pool_together = read_json(folder / "pools_grouped/logs.json")
    paused, resumed = reports["resume_paused"], reports["resume_completed"]
    checks = {
        "factory_logs_equal": apart == together,
        "pool_candidates_equal": canonical_pools(folder / "factories_separate/pool_candidates.csv") == canonical_pools(folder / "factories_grouped/pool_candidates.csv"),
        "pool_logs_equal": canonical_logs(pool_apart) == canonical_logs(pool_together),
        "resume_logs_equal": canonical_logs(factory_logs["resume_completed"]) == together,
        "resume_stopped_after_three_ranges": not paused["complete"] and paused["scans"][0]["chunks"] == 3 and paused["scans"][0]["error"] is None,
        "resume_next_block_correct": paused["scans"][0]["next_block"] == START_BLOCK + 3 * width,
        "resume_reads_cached_prefix": resumed["complete"] and resumed["clients"]["drpc"]["cache_hits"] == 3
                                      and resumed["scans"][0]["new_chunks"] == chunks - 3,
        "all_factories_have_logs": all(f["logs"] > 0 for f in reports["factories_grouped"]["factories"]),
        "both_pools_have_logs": all(read_json(folder / f"pool_separate_{i}/logs.json") for i in range(len(POOLS))),
    }
    statistics = []
    for name, separate_names, grouped_name, count in (
        ("factories", ["factories_separate"], "factories_grouped", len(FACTORIES)),
        ("pools", [f"pool_separate_{i}" for i in range(len(POOLS))], "pools_grouped", len(POOLS))):
        separate_requests = sum(reports[n]["clients"]["drpc"]["network_requests"] for n in separate_names)
        grouped_requests = reports[grouped_name]["clients"]["drpc"]["network_requests"]
        seconds_separate = sum(reports[n]["process_elapsed_seconds"] for n in separate_names)
        seconds_grouped = reports[grouped_name]["process_elapsed_seconds"]
        statistics.append({"case": name, "addresses": count, "block_ranges": chunks,
            "logical_requests_separate": chunks * count, "logical_requests_grouped": chunks,
            "http_requests_separate": separate_requests, "http_requests_grouped": grouped_requests,
            "http_reduction_pct": round((1 - grouped_requests / separate_requests) * 100, 2) if separate_requests else None,
            "seconds_separate": round(seconds_separate, 3), "seconds_grouped": round(seconds_grouped, 3),
            "time_reduction_pct": round((1 - seconds_grouped / seconds_separate) * 100, 2),
            "note": "Số HTTP gồm retry; thời gian gồm khởi động tiến trình, rate limit và backoff. Chưa đo CU."})
    return {"checks": checks, "factory_log_count": len(together), "pool_log_count": len(pool_together),
            "pool_candidates": len(canonical_pools(folder / "factories_grouped/pool_candidates.csv")),
            "statistics": statistics}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--online", action="store_true", help="Tạo một lần benchmark mới và gọi API chỉ đọc")
    parser.add_argument("--output", type=Path, default=ROOT / "data/interim/base_batch_check")
    parser.add_argument("--run", type=Path, help="Thư mục run cụ thể để replay offline")
    args = parser.parse_args()
    args.output = args.output.resolve()
    if args.online and args.run:
        parser.error("--run chỉ dùng khi replay offline.")
    if args.online:
        run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S_%fZ")
        folder = args.output / ("run_" + run_id)
        folder.mkdir(parents=True, exist_ok=False)
        namespace = "base_task1_" + run_id
        config = load_config("chains.yaml")
        manifest = {"run_id": run_id, "namespace": namespace, "start_block": START_BLOCK, "end_block": END_BLOCK,
            "max_block_range": config["base"]["logs"]["max_block_range"], "cases": cases_for(namespace),
            "config_sha256": hashlib.sha256((ROOT / "configs/chains.yaml").read_bytes()).hexdigest(),
            "research_sample": False}
        write_json(folder / "manifest.json", manifest)
        reports = {}
        for case in manifest["cases"]:
            reports[case["name"]] = execute_case(case, folder / case["name"], offline=False)
            write_json(folder / "measurements.json", reports)
        chunks = math.ceil((END_BLOCK - START_BLOCK + 1) / manifest["max_block_range"])
        comparison = compare_cases(folder, reports, chunks, manifest["max_block_range"])
        comparison["raw_integrity"] = verify_raw({namespace, namespace + "_resume"})
        comparison.update(run_dir=str(folder), run_id=run_id, measured_at_utc=datetime.now(timezone.utc).isoformat())
        write_json(folder / "comparison.json", comparison)
        write_json(args.output / "comparison.json", comparison)
        write_json(args.output / "latest.json", {"run_dir": str(folder)})
    else:
        folder = args.run.resolve() if args.run else Path(read_json(args.output / "latest.json")["run_dir"])
        manifest, comparison = read_json(folder / "manifest.json"), read_json(folder / "comparison.json")
        failures = []
        for case in manifest["cases"]:
            if case["name"] == "resume_paused":
                continue  # Cache đã đủ sau resume; giữ báo cáo dừng ban đầu làm bằng chứng.
            replay_dir = folder / "offline_replay" / case["name"]
            execute_case(case, replay_dir, offline=True)
            for filename in ("factory_logs.json", "pool_candidates.csv", "logs.json"):
                original, replay = folder / case["name"] / filename, replay_dir / filename
                if original.exists() and (not replay.exists() or original.read_bytes() != replay.read_bytes()):
                    failures.append(f"{case['name']}/{filename}")
        integrity = verify_raw({manifest["namespace"], manifest["namespace"] + "_resume"})
        write_json(folder / "offline_replay/results.json", {"cases": 6, "network_requests": 0,
                   "byte_comparison_failures": failures, "raw_integrity": integrity})
        if failures or integrity["failures"]:
            raise CollectionError(f"Replay sai nội dung/raw: {failures}, {integrity['failures']}")
    print(json.dumps(comparison, ensure_ascii=False, indent=2))
    if not all(comparison["checks"].values()) or comparison["raw_integrity"]["failures"]:
        return 2
    print(f"PASS. Kết quả: {folder / 'comparison.json'}")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (CollectionError, FileNotFoundError, subprocess.TimeoutExpired) as error:
        print(f"Chưa hoàn tất benchmark: {error}")
        raise SystemExit(2)
