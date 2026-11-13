"""Đối chiếu bộ lọc trước (log Swap) với kết quả GeckoTerminal đã sàng lọc.

Yêu cầu bắt buộc: 0 pool bị lọc trước loại mà GeckoTerminal lại có cutoff TRONG MỘT TẬP (loại nhầm).
Cutoff rơi vào khoảng đệm/ngoài cửa sổ vốn không đủ điều kiện, nên loại không làm đổi mẫu.
Chỉ dùng các dòng đã gọi GeckoTerminal trong `screened.csv`; gọi Blockscout có cache + rate limit.

Chạy:   .venv/bin/python scripts/validate_prefilter.py --chain ethereum
"""
from __future__ import annotations

import argparse
import collections
import csv
import os
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from memecoin.collect.activity import count_swap_days  # noqa: E402
from memecoin.collect.common import load_config, utc_now, write_csv, write_json  # noqa: E402
from memecoin.collect.evm import EvmReader  # noqa: E402
from memecoin.collect.http import HttpClient  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--chain", choices=["ethereum"], default="ethereum")
    parser.add_argument("--screened", type=Path, help="Mặc định: bản sao screened.csv trong thư mục đầu ra")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    from dotenv import load_dotenv
    load_dotenv(ROOT / ".env", override=False)
    output = args.output or ROOT / f"data/interim/task2/prefilter_validation/{args.chain}"
    source = args.screened or ROOT / f"data/interim/task2/screening/{args.chain}/screened.csv"
    split, chains = load_config("split.yaml"), load_config("chains.yaml")
    last = max(date.fromisoformat(str(b["cutoff_end"])) for b in split["sets"].values())
    need = int(split["min_history_days"])
    logs = chains[args.chain]["logs"]
    secrets = tuple(os.environ.get(k, "") for k in ("BLOCKSCOUT_API_KEY", "DRPC_API_KEY", "HELIUS_API_KEY"))
    reader = EvmReader(args.chain, HttpClient(ROOT, logs["provider"], logs["max_requests_per_second"],
                       max_requests=100000, secrets=secrets), chains[args.chain])
    rows = [r for r in csv.DictReader(source.open(encoding="utf-8"))
            if r["ohlcv_requested"] == "True" and r["indexed"] == "True"]
    out, table = [], collections.Counter()
    for row in rows:
        check = count_swap_days(reader, row, chains[args.chain], date.fromisoformat(row["creation_day"]), last, need)
        has_cutoff = row["split"] in split["sets"]  # cutoff trong train/validation/test
        table[(check.status, has_cutoff)] += 1
        out.append({"pool_address": row["pool_address"], "version": row["version"],
                    "creation_day": row["creation_day"], "gecko_candles": row["candles"],
                    "gecko_cutoff": row["cutoff"], "gecko_split": row["split"],
                    "prefilter": check.status, "swap_days": check.swap_days, "reason": check.reason,
                    "calls": check.calls, "false_reject": check.passed is False and has_cutoff})
    false_rejects = sum(r["false_reject"] for r in out)
    write_csv(output / "comparison.csv", out, list(out[0]) if out else ["pool_address"])
    summary = {"chain": args.chain, "checked_at": utc_now(), "source": str(source),
               "pools": len(out), "false_rejects": false_rejects,
               "table": {f"{s}|gecko_cutoff_in_set={c}": n for (s, c), n in sorted(table.items())},
               "blockscout": reader.client.stats()}
    write_json(output / "summary.json", summary)
    print(summary)
    return 1 if false_rejects else 0


if __name__ == "__main__":
    raise SystemExit(main())
