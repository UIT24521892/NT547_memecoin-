"""Thu nến ngày/giờ theo pool; giữ nến thật, không tự điền ngày thiếu."""
from __future__ import annotations

import math
from datetime import datetime, timezone
from typing import Any

from .common import iso_time
from .http import CollectionError, HttpClient, Response

NETWORKS = {"ethereum": "eth", "base": "base", "solana": "solana"}
FIELDS = ["chain", "pool_address", "ts", "timeframe", "open", "high", "low", "close",
          "volume_usd", "currency", "source", "collected_at", "raw_ref"]


def normalized_address(chain: str, address: str) -> str:
    return address if chain == "solana" else address.lower()


class GeckoTerminal:
    def __init__(self, client: HttpClient, config: dict[str, Any]) -> None:
        self.client, self.config = client, config
        self.url = config["base_url"]

    def pool(self, chain: str, pool: str) -> Response:
        return self.client.request("GET", f"{self.url}/networks/{NETWORKS[chain]}/pools/{pool}")

    def token_pools(self, chain: str, token: str, page: int = 1) -> Response:
        """Snapshot hiện tại chỉ hỗ trợ tìm ví dụ kỹ thuật, không chọn pool tại cutoff."""
        return self.client.request("GET", f"{self.url}/networks/{NETWORKS[chain]}/tokens/{token}/pools",
                                   params={"page": page})

    def collect(self, chain: str, pool: str, token: str, timeframe: str,
                start: int, end: int, *, max_pages: int = 20,
                now: int | None = None) -> tuple[list[dict[str, Any]], dict[str, Any]]:
        """Khoảng [start,end), chỉ nến đã đóng. `end` cố định giúp replay đúng cache."""
        if timeframe not in {"day", "hour"} or start >= end or max_pages < 1:
            raise ValueError("Cửa sổ, timeframe hoặc max_pages không hợp lệ.")
        step = 86400 if timeframe == "day" else 3600
        if start % step or end % step:
            raise ValueError("Biên cửa sổ phải trùng biên nến UTC.")
        now = int(datetime.now(timezone.utc).timestamp()) if now is None else now
        closed_end = min(end, now // step * step)
        if start >= closed_end:
            raise ValueError("Chưa có nến đóng trong cửa sổ yêu cầu.")
        pool = normalized_address(chain, pool)
        token = normalized_address(chain, token)
        cursor = closed_end - 1
        rows: dict[int, dict[str, Any]] = {}
        page_refs: list[str] = []
        reason = "page_limit"
        error = None
        for _ in range(max_pages):
            # Không gửi cursor quá giới hạn free; vẫn báo phần đầu chưa thu được.
            if not self.client.offline and cursor < now - self.config["lookback_days_free"] * 86400:
                reason = "free_lookback_boundary"
                break
            try:
                response = self.client.request(
                    "GET", f"{self.url}/networks/{NETWORKS[chain]}/pools/{pool}/ohlcv/{timeframe}",
                    params={"aggregate": 1, "before_timestamp": cursor,
                            "limit": self.config["max_candles_per_request"], "currency": "usd",
                            "token": token, "include_empty_intervals": "false"})
            except CollectionError as exc:
                reason, error = "request_error", str(exc)
                break
            page_refs.append(response.raw_ref)
            candles = response.data["data"]["attributes"]["ohlcv_list"]
            if not candles:
                reason = "provider_exhausted"
                break
            timestamps: list[int] = []
            for candle in candles:
                if len(candle) != 6:
                    raise CollectionError("Nến phải có đúng timestamp + OHLCV.")
                stamp = int(candle[0])
                values = [None if v is None else float(v) for v in candle[1:]]
                if stamp % step or any(v is not None and (not math.isfinite(v) or v < 0) for v in values):
                    raise CollectionError("Nến có timestamp hoặc giá trị không hợp lệ.")
                opening, high, low, close, volume = values
                if None not in (opening, high, low, close) and not (low <= min(opening, close) <= max(opening, close) <= high):
                    raise CollectionError("Nến vi phạm low <= open/close <= high.")
                timestamps.append(stamp)
                if start <= stamp < closed_end:
                    row = dict(zip(FIELDS, [chain, pool, iso_time(stamp), timeframe, *values,
                                           "usd", "geckoterminal", response.collected_at, response.raw_ref]))
                    if stamp in rows and any(rows[stamp][field] != row[field] for field in FIELDS[4:9]):
                        raise CollectionError("Hai trang trả OHLCV khác nhau cho cùng nến.")
                    rows[stamp] = row
            oldest = min(timestamps)
            if oldest <= start:
                reason = "reached_start"
                break
            if oldest >= cursor:
                reason = "cursor_stalled"
                break
            # Trang ít hơn limit vẫn có thể chỉ phủ một cửa sổ nội bộ của nguồn.
            # Phải đi tiếp đến start hoặc trang rỗng, không kết luận hết lịch sử sớm.
            cursor = oldest - 1
        ordered = [rows[t] for t in sorted(rows)]
        missing = [iso_time(t) for t in range(start, closed_end, step) if t not in rows]
        report = {"chain": chain, "pool_address": pool, "token_address": token, "timeframe": timeframe,
                  "requested_start": iso_time(start), "requested_end_exclusive": iso_time(end),
                  "closed_end_exclusive": iso_time(closed_end), "future_tail_pending": end > closed_end,
                  "candles": len(rows), "expected_intervals": (closed_end - start) // step,
                  "first_ts": ordered[0]["ts"] if ordered else None,
                  "last_ts": ordered[-1]["ts"] if ordered else None,
                  "missing_intervals": len(missing), "missing_examples": missing[:20],
                  "coverage_complete": not missing and error is None,
                  "stop_reason": reason, "error": error, "raw_refs": page_refs,
                  "note": "Thiếu nến có thể do không có swap hoặc nguồn thiếu dữ liệu; không tự gán volume=0."}
        return ordered, report
