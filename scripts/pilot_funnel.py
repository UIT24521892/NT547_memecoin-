"""Pilot phễu chọn mẫu (task 2, bước 2): đo tỷ lệ ứng viên dùng được.

Mỗi chuỗi lấy ngẫu nhiên N ứng viên của MỘT ngày train, thu nến ngày GeckoTerminal,
rồi đo: có dữ liệu không, có đủ 7 ngày giao dịch (có cutoff) không, cutoff rơi vào
tập nào, có đạt tiêu chí nhóm A không. Chỉ dùng ngày train, không đụng tập test.
Kết quả chỉ để ước tính số lần gọi OHLCV cần cho bước chọn mẫu, không phải mẫu nghiên cứu.

Chạy:  .venv/bin/python scripts/pilot_funnel.py            (gọi API, có cache)
       .venv/bin/python scripts/pilot_funnel.py --offline  (chỉ đọc cache)
"""
from __future__ import annotations

import argparse
import csv
import random
import sys
from datetime import date, datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from memecoin.collect.common import load_config, midnight, utc_now, write_csv, write_json  # noqa: E402
from memecoin.collect.http import CollectionError, HttpClient  # noqa: E402
from memecoin.collect.ohlcv import GeckoTerminal  # noqa: E402
from memecoin.model.sampling import assign_cutoff  # noqa: E402

# Ngày train đã quét đầy đủ ở bước chạy thử (data/interim/task2/trial/<chuỗi>).
PILOT_DAYS = {"ethereum": "2026-06-10", "solana": "2026-06-10", "base": "2026-06-03"}
FIELDS = ["chain", "pool_address", "token_address", "dex", "version", "creation_day", "indexed", "error",
          "candles", "cutoff", "split", "first_close", "cutoff_close", "price_ratio", "group_a"]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--per-chain", type=int, default=30)
    parser.add_argument("--offline", action="store_true")
    parser.add_argument("--end", default="2026-11-12", help="Ngày UTC kết thúc (không gồm), cố định để replay")
    parser.add_argument("--output", type=Path, default=ROOT / "data/interim/task2/pilot_funnel")
    args = parser.parse_args()
    split = load_config("split.yaml")
    settings = load_config("chains.yaml")["common"]["ohlcv"]
    if not args.offline:
        from dotenv import load_dotenv
        load_dotenv(ROOT / ".env", override=False)
    gecko = GeckoTerminal(HttpClient(ROOT, "geckoterminal", settings["max_requests_per_minute"] / 60,
                                     offline=args.offline), settings)
    start, end = midnight(str(split["data_start"])), midnight(args.end)
    now = min(end, int(datetime.now(timezone.utc).timestamp()))
    rows = []
    for chain, day in PILOT_DAYS.items():
        source = ROOT / f"data/interim/task2/trial/{chain}/pool_candidates.csv"
        candidates = [r for r in csv.DictReader(source.open(encoding="utf-8")) if r["creation_day"] == day]
        picked = random.Random(f"{split['seed']}:pilot:{chain}").sample(candidates, min(args.per_chain, len(candidates)))
        for pool in picked:
            row = {k: pool[k] for k in ("chain", "pool_address", "token_address", "dex", "version", "creation_day")}
            try:
                candles, report = gecko.collect(chain, pool["pool_address"], pool["token_address"], "day",
                                                start, end, max_pages=2, now=now)
                row.update(indexed=report["error"] is None, error=report["error"], candles=len(candles))
            except CollectionError as exc:
                candles = []
                row.update(indexed=False, error=str(exc)[:200], candles=0)
            result = assign_cutoff(candles, date.fromisoformat(day), split)
            row.update(cutoff=result.cutoff, split=result.split, first_close=result.first_close,
                       cutoff_close=result.cutoff_close, price_ratio=result.price_ratio, group_a=result.group_a)
            rows.append(row)
            print(chain, pool["pool_address"][:14], row["indexed"], row["candles"], row["split"], row["group_a"], flush=True)
    write_csv(args.output / "pilot.csv", rows, FIELDS)
    summary = {}
    for chain in PILOT_DAYS:
        part = [r for r in rows if r["chain"] == chain]
        in_set = [r for r in part if r["split"] in {"train", "validation", "test"}]
        group_a = [r for r in in_set if r["group_a"]]
        eligible = len(in_set) / len(part) if part else 0
        share_a = len(group_a) / len(in_set) if in_set else 0
        summary[chain] = {"day": PILOT_DAYS[chain], "sampled": len(part),
            "indexed": sum(bool(r["indexed"]) for r in part),
            "with_cutoff": sum(r["cutoff"] is not None for r in part),
            "cutoff_in_a_set": len(in_set), "group_a": len(group_a),
            "split_counts": {s: sum(r["split"] == s for r in part) for s in
                             ("train", "validation", "test", "gap", "outside", "no_cutoff")},
            # Ước tính thô từ một ngày, cỡ mẫu nhỏ: chỉ để lên kế hoạch số lần gọi.
            "ohlcv_calls_for_40_B": round(40 / eligible) if eligible else None,
            "ohlcv_calls_for_40_A": round(40 / (eligible * share_a)) if eligible and share_a else None}
    write_json(args.output / "summary.json", {"generated_at": utc_now(), "end_exclusive": args.end,
        "research_sample": False, "note": "Một ngày train mỗi chuỗi, N nhỏ; tỷ lệ có thể khác theo ngày.",
        "chains": summary, "gecko": gecko.client.stats()})
    print(summary)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
