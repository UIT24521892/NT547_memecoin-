"""Kiểm thử lại đợt collector 12/11 hoàn toàn offline, không cần API key.

Chạy từ thư mục repo: .venv/bin/python scripts/check_collection.py
Các đầu ra replay để riêng; không sửa bộ dữ liệu online hay phản hồi raw.
"""
from __future__ import annotations

import csv
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

import duckdb

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "data/interim/collector_check"


def main() -> int:
    if not (BASE / "ohlcv_online/report.json").exists():
        print("Chưa có dữ liệu kiểm thử trên máy. Chạy bước online trong docs/COLLECTOR_RUNBOOK.md trước.")
        return 2
    cases = [
        ("smoke", ["resolve-smoke"]),
        ("ohlcv_online", ["ohlcv", "--pools", str(BASE / "smoke/pools.csv"), "--start", "2026-05-26",
                          "--end", "2026-11-12", "--timeframes", "day", "hour", "--max-pages", "12"]),
        ("ethereum_discovery", ["discover", "--chain", "ethereum", "--start", "2026-06-10", "--end", "2026-06-11",
                                "--factories", "uniswap_v2", "uniswap_v3"]),
        ("base_discovery", ["discover", "--chain", "base", "--start", "2026-06-10", "--end", "2026-06-11",
                            "--from-block", "47130126", "--to-block", "47131125",
                            "--factories", "uniswap_v2", "uniswap_v3", "--max-chunks", "10", "--separate-factories"]),
        ("aerodrome_discovery", ["discover", "--chain", "base", "--start", "2026-06-10", "--end", "2026-06-11",
                                 "--from-block", "47130126", "--to-block", "47135125", "--factories", "aerodrome",
                                 "--max-chunks", "50"]),
        ("solana_discovery", ["discover", "--chain", "solana", "--start", "2026-06-10", "--end", "2026-06-11",
                              "--page-size", "100", "--max-pages", "15"]),
        ("solana_transactions", ["transactions", "--address", "CJcu7ciRHBHu4BDnpLgAUm1A6iSp9RuhJMG36rjjrxnd",
                                 "--start", "2026-11-05", "--end", "2026-11-06", "--page-size", "100"]),
        ("ethereum_swaps", ["decode-evm", "--chain", "ethereum", "--input", str(BASE / "ethereum_swap_logs/logs.json"),
                            "--token0", "0x6982508145454ce325ddbe47a25d4ec3d2311933", "--meme",
                            "0x6982508145454ce325ddbe47a25d4ec3d2311933", "--protocol", "v2",
                            "--token-decimals", "18", "--quote-decimals", "18"]),
        ("base_swaps", ["decode-evm", "--chain", "base", "--input", str(BASE / "base_swap_logs/logs.json"),
                        "--token0", "0x4200000000000000000000000000000000000006", "--meme",
                        "0x532f27101965dd16442e59d40670faf5ebb142e4", "--protocol", "v3",
                        "--token-decimals", "18", "--quote-decimals", "18"]),
        ("verify", ["verify"]),
    ]
    failures = []
    for name, options in cases:
        previous_failures = len(failures)
        output = BASE / "offline_replay" / name
        # Cố ý bỏ key khỏi môi trường: offline vẫn phải tìm đúng request đã che key.
        result = subprocess.run([sys.executable, "scripts/collect.py", *options, "--offline", "--output", str(output)],
                                cwd=ROOT, capture_output=True, text=True,
                                env={k: v for k, v in os.environ.items()
                                     if k not in {"BLOCKSCOUT_API_KEY", "HELIUS_API_KEY", "DRPC_API_KEY"}})
        if result.returncode:
            failures.append({"case": name, "error": result.stdout[-1200:] + result.stderr[-1200:]})
            print(f"FAIL {name}")
            continue
        report = json.loads((output / "report.json").read_text())
        if any(c["network_requests"] for c in report["clients"].values()):
            failures.append({"case": name, "error": "Offline đã gọi mạng."})
        # Dữ liệu tái dựng phải giống byte; timestamp sinh report có thể khác.
        original = BASE / name
        for filename in ("pools.csv", "pool_candidates.csv", "ohlcv.csv", "swaps.csv", "transactions.csv"):
            left, right = original / filename, output / filename
            if left.exists() and (not right.exists() or left.read_bytes() != right.read_bytes()):
                failures.append({"case": name, "error": f"Replay thiếu/khác {filename}."})
        print(f"{'PASS' if len(failures) == previous_failures else 'FAIL'} {name}: 0 request mạng")
    folder = BASE / "ohlcv_online"
    db = duckdb.connect(str(folder / "collection.duckdb"), read_only=True)
    try:
        count_db = db.execute("SELECT count(*) FROM ohlcv").fetchone()[0]
        parquet = str(folder / "ohlcv.parquet")
        count_parquet = db.execute("SELECT count(*) FROM read_parquet(?)", [parquet]).fetchone()[0]
        csv_rows = list(csv.DictReader((folder / "ohlcv.csv").open(encoding="utf-8")))
        differences = db.execute("SELECT count(*) FROM ((SELECT * FROM ohlcv EXCEPT SELECT * FROM read_parquet(?)) "
                                 "UNION ALL (SELECT * FROM read_parquet(?) EXCEPT SELECT * FROM ohlcv))", [parquet, parquet]).fetchone()[0]
        if count_db != count_parquet or count_db != len(csv_rows) or differences:
            failures.append({"case": "storage", "error": "CSV/Parquet/DuckDB không khớp."})
        print(f"CSV/Parquet/DuckDB: {count_db}/{count_parquet}/{len(csv_rows)} dòng; {differences} khác biệt DB–Parquet")
    finally:
        db.close()
    # So chữ ký cũ để xác nhận Helius và bài thử RPC public lấy cùng 8 tx.
    transactions = json.loads((BASE / "solana_transactions/transactions.json").read_text())
    new_signatures = {r["signature"] for r in transactions}
    old_dir = ROOT / "data/raw/solana_day_pilot/2026-11-05/run_20261106T155457_437217Z/rpc"
    old_signatures = set()
    for path in old_dir.glob("*.json"):
        data = json.loads(path.read_text())
        tx = data.get("result")
        if isinstance(tx, dict) and "transaction" in tx:
            old_signatures.add(tx["transaction"]["signatures"][0])
    if not old_signatures or new_signatures != old_signatures:
        failures.append({"case": "solana_crosscheck", "error": "Signature không khớp pilot public RPC."})
    print(f"Solana so với RPC public pilot: {len(new_signatures & old_signatures)}/{len(old_signatures)} signature")
    summary = {"cases": len(cases), "failures": failures, "rows": count_db,
               "ohlcv_csv_sha256": hashlib.sha256((folder / "ohlcv.csv").read_bytes()).hexdigest()}
    (BASE / "offline_replay/check_results.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n")
    if failures:
        print(json.dumps(failures, ensure_ascii=False, indent=2))
        return 2
    print("PASS: replay giống dữ liệu online; mọi lời gọi mạng = 0.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
