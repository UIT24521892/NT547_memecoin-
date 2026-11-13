"""Lọc trước pool EVM bằng số ngày có log Swap, trước khi tốn lượt GeckoTerminal.

Vì sao cần: GeckoTerminal free chỉ ~10 lần/phút (đo 2026-11-13), trong khi 82–95% pool EVM
mới không bao giờ có đủ 7 ngày giao dịch nên không có cutoff. Blockscout có hạn mức riêng
(5 lần/giây), nên đếm ngày có swap ở đó rẻ hơn nhiều.

Vì sao không làm lệch mẫu: cùng một quy tắc cho mọi pool, theo đúng thứ tự ngẫu nhiên đã xáo.
Bộ lọc chỉ loại pool CHẮC CHẮN không có cutoff trong một tập: nếu log cho thấy ít hơn 7 ngày
có swap trong (ngày tạo, ngày cutoff muộn nhất], thì GeckoTerminal (nến dựng từ chính các swap
đó) cũng không thể có 7 ngày giao dịch đầy đủ. Khi không chắc (lỗi, thiếu timestamp, quá số
lần gọi) thì trả None để vẫn hỏi GeckoTerminal, không bao giờ loại nhầm.

Uniswap V4: PoolManager luôn phát event Swap trong `_swap`, kể cả pool có hooks
(v4-core PoolManager.sol, đọc 2026-11-13).
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from typing import Any

from .common import midnight
from .evm import EvmReader, as_int, event_topic, log_matches_filter
from .http import CollectionError
from .swaps import V2_SWAP, V3_SWAP

# IPoolManager: Swap(PoolId indexed id, address indexed sender, int128 amount0, int128 amount1,
#                    uint160 sqrtPriceX96, uint128 liquidity, int24 tick, uint24 fee)
V4_SWAP = event_topic("Swap(bytes32,address,int128,int128,uint160,uint128,int24,uint24)")


@dataclass(frozen=True)
class PrefilterResult:
    passed: bool | None      # True: có thể có cutoff; False: chắc chắn không; None: chưa chắc
    swap_days: int           # số ngày UTC có swap đã thấy (cận dưới nếu dừng sớm)
    calls: int               # số lần gọi getLogs (kể cả đọc từ cache)
    reason: str              # enough_days / too_few_days / lý do chưa chắc

    @property
    def status(self) -> str:
        return {True: "pass", False: "reject", None: "unknown"}[self.passed]


def swap_filter(pool: dict[str, Any], chain_config: dict[str, Any]) -> tuple[str, list[Any]]:
    """Địa chỉ + topic để lấy log Swap của đúng một pool."""
    version = pool["version"]
    if version == "v2":
        return pool["pool_address"].lower(), [V2_SWAP]
    if version == "v3":
        return pool["pool_address"].lower(), [V3_SWAP]
    if version == "v4":
        # V4 không có contract riêng cho pool: lọc PoolManager theo PoolId ở topic1.
        manager = next(f["address"] for f in chain_config["factories"] if f["name"] == "uniswap_v4")
        return manager.lower(), [V4_SWAP, pool["pool_address"].lower()]
    raise ValueError(f"Chưa hỗ trợ lọc trước cho phiên bản pool {version!r}.")


def _log_day(log: dict[str, Any]) -> date | None:
    stamp = log.get("timeStamp") or log.get("blockTimestamp")
    if stamp in (None, ""):
        return None
    return datetime.fromtimestamp(as_int(stamp), timezone.utc).date()


def count_swap_days(reader: EvmReader, pool: dict[str, Any], chain_config: dict[str, Any],
                    created: date, last_day: date, need: int, *, max_calls: int = 50) -> PrefilterResult:
    """Đếm ngày UTC có swap trong (created, last_day]; dừng ngay khi đủ `need` ngày.

    Duyệt dải block từ trái sang phải. Trang chạm trần dòng thì vẫn đếm các log đã trả (đều là
    swap thật), rồi chia đôi dải để đọc đủ; vì vậy kết luận "reject" chỉ đưa ra khi đã đọc hết.
    """
    if last_day <= created:
        return PrefilterResult(False, 0, 0, "too_few_days")
    address, topics = swap_filter(pool, chain_config)
    max_rows = int(reader.logs.get("max_rows_per_request", 10 ** 9))
    try:
        start = reader.block_at(midnight(created + timedelta(days=1)))
        end = reader.block_at(midnight(last_day + timedelta(days=1)) - 1)
    except CollectionError as exc:
        return PrefilterResult(None, 0, 0, f"block_lookup_error: {str(exc)[:120]}")
    days: set[date] = set()
    pending, calls = [(start, end)], 0
    while pending:
        if calls >= max_calls:
            return PrefilterResult(None, len(days), calls, "max_calls")
        left, right = pending[0]
        try:
            logs, _ = reader.get_logs(left, right, address, topics)
        except CollectionError as exc:
            return PrefilterResult(None, len(days), calls, f"logs_error: {str(exc)[:120]}")
        calls += 1
        for log in logs:
            if log.get("removed") or not log_matches_filter(log, address, topics):
                return PrefilterResult(None, len(days), calls, "unexpected_log")
            day = _log_day(log)
            if day is None:
                return PrefilterResult(None, len(days), calls, "missing_timestamp")
            if created < day <= last_day:
                days.add(day)
        if len(days) >= need:
            return PrefilterResult(True, len(days), calls, "enough_days")
        if len(logs) >= max_rows:
            if left == right:
                return PrefilterResult(None, len(days), calls, "block_hits_row_cap")
            middle = (left + right) // 2
            pending[:1] = [(left, middle), (middle + 1, right)]
            continue
        pending.pop(0)
    return PrefilterResult(False, len(days), calls, "too_few_days")
