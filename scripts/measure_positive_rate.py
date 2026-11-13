"""Đo thử tỷ lệ ca dương cho cổng 18/11 (PLAN Mục 5.2, Mục 7). Chạy offline, không gọi API.

Làm gì:
1. Đọc nến ngày và danh sách token đã sàng lọc của một chuỗi (đầu ra của scripts/screen_sample.py).
2. CHỈ giữ token có cutoff thuộc train hoặc validation (trước T2). Gặp tập test thì dừng ngay.
3. Với mỗi token, chỉ dùng nến trong (cutoff, cutoff + H] để tính:
   - mức giảm sâu nhất của giá đóng cửa so với giá tại cutoff (target "sụp giá" ở 70/80/90%);
   - rug pull theo configs/thresholds.yaml (thiếu nến KHÔNG coi là volume 0, như config);
   - số ngày có nến và số ngày "im lặng" ở cuối cửa sổ (không có nến nào = không có giao dịch
     được GeckoTerminal ghi nhận). Đây là phần định nghĩa hiện tại bỏ sót.
4. Báo tỷ lệ trên hai tập: (a) token đã chọn vào A/B (đúng định nghĩa cổng),
   (b) mọi token đủ điều kiện đã sàng lọc (để ước lượng ổn định hơn, chỉ tham khảo).

Chạy:   .venv/bin/python scripts/measure_positive_rate.py --chain solana
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from memecoin.collect.common import load_config, utc_now  # noqa: E402

ALLOWED_SPLITS = ("train", "validation")   # cổng chỉ được đo trên cutoff trước T2
SILENT_DAYS = (7, 14)                      # đề xuất để báo cáo, chưa phải định nghĩa target


def rug_pull_day(window: pd.DataFrame, cfg: dict) -> str | None:
    """Ngày rug pull đầu tiên theo rule paper/artifact, hoặc None.

    Ngày sập: lợi nhuận ngày (close/close hôm trước - 1) <= return_pct_lt.
    Các ngày sau trong cửa sổ (window_days - 1 ngày) phải CÓ nến và volume < tỷ lệ * volume ngày sập.
    """
    rows = window.reset_index(drop=True)
    later_days = int(cfg["window_days"]) - 1
    for i in range(1, len(rows)):
        prev, cur = rows.loc[i - 1], rows.loc[i]
        if (cur.ts - prev.ts).days != 1:
            continue  # không có nến hôm trước thì không tính được lợi nhuận ngày
        ret_pct = (cur.close / prev.close - 1) * 100
        if ret_pct > cfg["return_pct_lt"]:
            continue
        expected = [cur.ts + pd.Timedelta(days=k) for k in range(1, later_days + 1)]
        after = rows[rows.ts.isin(expected)]
        if len(after) < later_days and not cfg["missing_candle_is_zero_volume"]:
            continue
        limit = cfg["later_volume_max_ratio"] * cur.volume_usd
        if (after.volume_usd < limit).all():
            return cur.ts.date().isoformat()
    return None


def label_token(tok: pd.Series, candles: pd.DataFrame, horizon: int, rug_cfg: dict) -> dict:
    """Tính các đại lượng nhãn cho một token, chỉ từ nến trong (cutoff, cutoff + H]."""
    cutoff = pd.Timestamp(tok.cutoff, tz="UTC")
    end = cutoff + pd.Timedelta(days=horizon)
    window = candles[(candles.ts > cutoff) & (candles.ts <= end)].sort_values("ts")
    # Lợi nhuận ngày đầu cửa sổ cần nến tại cutoff; nến này <= cutoff nên không rò rỉ nhãn.
    at_cutoff = candles[candles.ts == cutoff]
    rug_input = pd.concat([at_cutoff, window])
    last = window.ts.max() if len(window) else None
    return {
        "chain": tok.chain, "pool_address": tok.pool_address, "token_address": tok.token_address,
        "group": tok.get("selected_group"), "split": tok.split, "cutoff": tok.cutoff,
        "cutoff_close": tok.cutoff_close, "window_end": end.date().isoformat(),
        "candles_in_window": len(window),
        "min_close_drop": (window.close.min() / tok.cutoff_close - 1) if len(window) else None,
        "last_candle": last.date().isoformat() if last is not None else None,
        "silent_tail_days": (end - last).days if last is not None else horizon,
        "last_close_vs_cutoff": (window.close.iloc[-1] / tok.cutoff_close - 1) if len(window) else None,
        "rug_pull_day": rug_pull_day(rug_input, rug_cfg),
    }


def summarize(df: pd.DataFrame, drops: list[float], horizon: int) -> dict:
    """Đếm ca dương theo từng định nghĩa; mẫu số = số token trong df."""
    n = len(df)
    out: dict = {"n": n}
    rug = df.rug_pull_day.notna()
    for d in drops:
        crash = df.min_close_drop.le(-d)
        out[f"crash_{int(d * 100)}"] = int(crash.sum())
        out[f"crash_{int(d * 100)}_or_rug"] = int((crash | rug).sum())
        for k in SILENT_DAYS:
            silent = df.silent_tail_days.ge(k)
            out[f"crash_{int(d * 100)}_or_rug_or_silent{k}"] = int((crash | rug | silent).sum())
    out["rug_pull"] = int(rug.sum())
    for k in SILENT_DAYS:
        out[f"silent_tail_ge_{k}"] = int(df.silent_tail_days.ge(k).sum())
    out["no_candle_in_window"] = int((df.candles_in_window == 0).sum())
    out["full_window_candles"] = int((df.candles_in_window == horizon).sum())
    out["candles_in_window_median"] = float(df.candles_in_window.median()) if n else None
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--chain", choices=["ethereum", "base", "solana"], required=True)
    parser.add_argument("--screening", type=Path, help="Thư mục đầu ra của screen_sample.py")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    src = args.screening or ROOT / f"data/interim/task2/screening/{args.chain}"
    out_dir = args.output or ROOT / f"data/interim/task2/gate_1811/{args.chain}"

    split_cfg, thr = load_config("split.yaml"), load_config("thresholds.yaml")
    horizon = int(split_cfg["horizon_days"])
    drops = [thr["target"]["severe_crash_min_drop"], *thr["target"]["sensitivity"]]

    screened = pd.read_csv(src / "screened.csv")
    selected = pd.read_csv(src / "selected.csv")
    candles = pd.read_csv(src / "ohlcv_day.csv")
    candles["ts"] = pd.to_datetime(candles.ts, utc=True)

    eligible = screened[screened.split.isin(ALLOWED_SPLITS)].copy()
    chosen = selected[selected.split.isin(ALLOWED_SPLITS)].copy()
    if set(eligible.split) - set(ALLOWED_SPLITS) or set(chosen.split) - set(ALLOWED_SPLITS):
        raise SystemExit("Có cutoff ngoài train/validation; dừng để không chạm tập test.")
    # Nhãn muộn nhất phải nằm trước ngày thu dữ liệu, nếu không cửa sổ chưa quan sát đủ.
    collected = pd.to_datetime(candles.collected_at, utc=True).min()
    latest_end = pd.to_datetime(eligible.cutoff, utc=True).max() + pd.Timedelta(days=horizon)
    if latest_end >= collected:
        raise SystemExit(f"Cửa sổ nhãn {latest_end} chưa kết thúc trước ngày thu {collected}.")

    by_pool = {p: g for p, g in candles.groupby("pool_address")}
    empty = candles.iloc[0:0]
    labels = pd.DataFrame([label_token(t, by_pool.get(t.pool_address, empty), horizon, thr["rug_pull"])
                           for _, t in eligible.iterrows()])
    labels["selected_group"] = labels.pool_address.map(dict(zip(chosen.pool_address, chosen.selected_group)))

    sel = labels[labels.selected_group.notna()]
    report = {
        "chain": args.chain, "generated_at": utc_now(), "horizon_days": horizon,
        "splits_used": list(ALLOWED_SPLITS), "data_collected_from": str(collected),
        "note": "Chỉ cutoff trước T2. Thiếu nến không coi là volume 0 khi tính rug pull (thresholds.yaml).",
        "selected_A_plus_B": summarize(sel, drops, horizon),
        "selected_by_group": {g: summarize(d, drops, horizon) for g, d in sel.groupby("selected_group")},
        "selected_by_split": {s: summarize(d, drops, horizon) for s, d in sel.groupby("split")},
        "all_eligible_screened": summarize(labels, drops, horizon),
    }
    out_dir.mkdir(parents=True, exist_ok=True)
    labels.to_csv(out_dir / "labels_pre_t2.csv", index=False)
    (out_dir / "summary.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
