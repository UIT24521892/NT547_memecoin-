"""Gán cutoff và xếp nhóm A cho một token từ nến ngày (PLAN Mục 4.1, 5.3).

Chống rò rỉ tương lai: kết quả chỉ phụ thuộc nến có ngày <= cutoff. Nến sau
cutoff (kể cả nến sụp giá) không được làm đổi cutoff hay nhóm.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from typing import Any, Iterable


@dataclass(frozen=True)
class CutoffResult:
    cutoff: date | None            # ngày giao dịch đầy đủ thứ `min_history_days`
    first_full_day: date | None
    first_close: float | None
    cutoff_close: float | None
    price_ratio: float | None      # cutoff_close / first_close
    group_a: bool | None           # None khi chưa có cutoff
    split: str                     # train/validation/test/gap/outside/no_cutoff
    full_days_seen: int            # số ngày đầy đủ tính tới cutoff (không nhìn sau cutoff)
    active_volume_usd: float | None = None  # volume TB các ngày lịch kết thúc ở cutoff
    active: bool | None = None              # còn hoạt động tại cutoff; None khi chưa có cutoff


def _day(value: Any) -> date:
    return date.fromisoformat(str(value)[:10])


def full_trading_days(candles: Iterable[dict[str, Any]], created: date,
                      min_volume_usd: float = 0) -> list[tuple[date, float]]:
    """Ngày UTC sau ngày tạo pool, có close và volume_usd > ngưỡng; sắp theo ngày."""
    days = {}
    for candle in candles:
        day = _day(candle["ts"])
        close, volume = candle.get("close"), candle.get("volume_usd")
        if day <= created or close in (None, "") or volume in (None, ""):
            continue
        if float(volume) > min_volume_usd and float(close) > 0:
            days[day] = float(close)
    return sorted(days.items())


def active_volume(candles: Iterable[dict[str, Any]], cutoff: date, window_days: int) -> float:
    """Volume USD trung bình trong `window_days` ngày lịch [cutoff - window + 1, cutoff].

    Ngày không có nến tính volume 0 (không có giao dịch). Nến sau cutoff bị bỏ qua để
    không rò rỉ tương lai.
    """
    first = cutoff - timedelta(days=window_days - 1)
    volumes: dict[date, float] = {}
    for candle in candles:
        day, volume = _day(candle["ts"]), candle.get("volume_usd")
        if first <= day <= cutoff and volume not in (None, ""):
            volumes[day] = float(volume)
    return sum(volumes.values()) / window_days


def split_of(cutoff: date, split: dict[str, Any]) -> str:
    for name, bounds in split["sets"].items():
        if _day(bounds["cutoff_start"]) <= cutoff <= _day(bounds["cutoff_end"]):
            return name
    for first, last in split["gaps"]:
        if _day(first) <= cutoff <= _day(last):
            return "gap"
    return "outside"


def assign_cutoff(candles: Iterable[dict[str, Any]], created: date, split: dict[str, Any]) -> CutoffResult:
    settings = split["sampling"]
    candles = list(candles)  # dùng hai lần: ngày đầy đủ và volume hoạt động
    days = full_trading_days(candles, created, float(settings["full_day_min_volume_usd"]))
    need = int(split["min_history_days"])
    if len(days) < need:
        first = days[0] if days else (None, None)
        return CutoffResult(None, first[0], first[1], None, None, None, "no_cutoff", len(days))
    (first_day, first_close), (cutoff, cutoff_close) = days[0], days[need - 1]
    ratio = cutoff_close / first_close
    volume = active_volume(candles, cutoff, int(settings["active_window_days"]))
    # Chỉ báo số ngày tới cutoff; đếm cả ngày sau cutoff là rò rỉ tương lai.
    return CutoffResult(cutoff, first_day, first_close, cutoff_close, ratio,
                        ratio >= float(settings["group_a_min_price_ratio"]), split_of(cutoff, split), need,
                        volume, volume >= float(settings["active_min_mean_volume_usd"]))


def allocate(total: int, split: dict[str, Any]) -> dict[str, int]:
    """Chia `total` cho các tập theo số ngày cutoff (gồm hai đầu), phần dư lớn nhất."""
    days = {name: (_day(b["cutoff_end"]) - _day(b["cutoff_start"])).days + 1 for name, b in split["sets"].items()}
    exact = {name: total * d / sum(days.values()) for name, d in days.items()}
    quota = {name: int(v) for name, v in exact.items()}
    for name in sorted(exact, key=lambda n: exact[n] - quota[n], reverse=True)[: total - sum(quota.values())]:
        quota[name] += 1
    return quota
