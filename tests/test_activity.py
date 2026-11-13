"""Lọc trước pool EVM bằng số ngày có log Swap (dữ liệu giả, chỉ dùng trong test)."""
from __future__ import annotations

from datetime import date, datetime, timedelta, timezone
from typing import Any

from memecoin.collect.activity import V4_SWAP, count_swap_days, swap_filter
from memecoin.collect.common import load_config, midnight
from memecoin.collect.evm import event_topic
from memecoin.collect.http import CollectionError
from memecoin.collect.swaps import V2_SWAP

CHAINS = load_config("chains.yaml")
CREATED = date(2026, 6, 1)
LAST = date(2026, 10, 23)
POOL_V2 = {"version": "v2", "pool_address": "0x" + "ab" * 20}
POOL_V4 = {"version": "v4", "pool_address": "0x" + "cd" * 32}


class FakeReader:
    """Block = giây Unix (đơn giản hoá); trả log theo dải block, có trần dòng như Blockscout."""

    def __init__(self, days: list[date], address: str, topics: list[str], max_rows: int = 1000,
                 per_day: int = 1, fail: bool = False) -> None:
        self.logs = {"max_rows_per_request": max_rows}
        self.calls = 0
        self.fail = fail
        self.items = []
        for day in days:
            for i in range(per_day):
                stamp = midnight(day) + 3600 + i
                self.items.append({"address": address, "topics": topics, "blockNumber": hex(stamp),
                                   "timeStamp": hex(stamp), "transactionHash": f"0x{stamp:x}", "logIndex": "0x0"})

    def block_at(self, timestamp: int) -> int:
        return timestamp

    def get_logs(self, start: int, end: int, address: Any, topics: list[Any]) -> tuple[list[dict], None]:
        self.calls += 1
        if self.fail:
            raise CollectionError("giả lập lỗi mạng")
        found = [x for x in self.items if start <= int(x["blockNumber"], 16) <= end]
        return found[: self.logs["max_rows_per_request"]], None


def _days(n: int, first: date = date(2026, 6, 2), step: int = 1) -> list[date]:
    return [first + timedelta(days=i * step) for i in range(n)]


def _reader(days: list[date], pool: dict = POOL_V2, **kw: Any) -> FakeReader:
    address, topics = swap_filter(pool, CHAINS["ethereum"])
    return FakeReader(days, address, [t for t in topics], **kw)


def test_v4_swap_topic_matches_official_signature() -> None:
    # Chữ ký event Swap trong IPoolManager (v4-core, đọc 2026-11-13).
    assert V4_SWAP == event_topic("Swap(bytes32,address,int128,int128,uint160,uint128,int24,uint24)")
    address, topics = swap_filter(POOL_V4, CHAINS["ethereum"])
    assert address == "0x000000000004444c5dc75cb358380d2e3de08a90"
    assert topics == [V4_SWAP, POOL_V4["pool_address"]]
    assert swap_filter(POOL_V2, CHAINS["ethereum"]) == (POOL_V2["pool_address"], [V2_SWAP])


def test_passes_with_seven_swap_days() -> None:
    result = count_swap_days(_reader(_days(7)), POOL_V2, CHAINS["ethereum"], CREATED, LAST, 7)
    assert (result.passed, result.swap_days, result.reason) == (True, 7, "enough_days")


def test_rejects_with_six_swap_days_even_if_many_swaps() -> None:
    # Ca âm: nhiều swap nhưng chỉ trong 6 ngày khác nhau.
    result = count_swap_days(_reader(_days(6), per_day=50), POOL_V2, CHAINS["ethereum"], CREATED, LAST, 7)
    assert (result.passed, result.swap_days, result.reason) == (False, 6, "too_few_days")


def test_ignores_creation_day_and_days_after_last_cutoff() -> None:
    # Ngày tạo không tính (giống quy tắc "ngày giao dịch đầy đủ"); sau cutoff muộn nhất không tính.
    days = [CREATED] + _days(5) + [LAST + timedelta(days=1), LAST + timedelta(days=2)]
    reader = _reader(days)
    # Block giả = giây Unix nên dải truy vấn đã loại ngày ngoài khoảng; kiểm tra thêm bằng cách nới dải.
    reader.block_at = lambda ts: ts - 86400 * 3 if ts < midnight(LAST) else ts + 86400 * 3  # type: ignore[assignment]
    result = count_swap_days(reader, POOL_V2, CHAINS["ethereum"], CREATED, LAST, 7)
    assert (result.passed, result.swap_days) == (False, 5)


def test_full_page_splits_until_complete_before_rejecting() -> None:
    # 6 ngày, mỗi ngày 30 swap, trần 10 dòng/lần: phải chia dải và đọc hết mới được loại.
    reader = _reader(_days(6, step=10), per_day=30, max_rows=10)
    result = count_swap_days(reader, POOL_V2, CHAINS["ethereum"], CREATED, LAST, 7, max_calls=500)
    assert (result.passed, result.swap_days) == (False, 6)
    assert reader.calls > 1


def test_full_page_counts_early_and_stops() -> None:
    # Trang đầy vẫn là swap thật: đủ 7 ngày ngay trang đầu thì dừng, không chia tiếp.
    reader = _reader(_days(20), max_rows=10)
    result = count_swap_days(reader, POOL_V2, CHAINS["ethereum"], CREATED, LAST, 7)
    assert (result.passed, reader.calls) == (True, 1)


def test_uncertain_cases_never_reject() -> None:
    # Lỗi mạng, thiếu timestamp hoặc vượt số lần gọi: trả None để vẫn hỏi GeckoTerminal.
    failed = count_swap_days(_reader(_days(3), fail=True), POOL_V2, CHAINS["ethereum"], CREATED, LAST, 7)
    assert failed.passed is None
    reader = _reader(_days(3))
    for item in reader.items:
        del item["timeStamp"]
    assert count_swap_days(reader, POOL_V2, CHAINS["ethereum"], CREATED, LAST, 7).passed is None
    capped = count_swap_days(_reader(_days(6, step=10), per_day=30, max_rows=10), POOL_V2, CHAINS["ethereum"],
                             CREATED, LAST, 7, max_calls=2)
    assert (capped.passed, capped.reason) == (None, "max_calls")


def test_log_day_uses_utc() -> None:
    # 23:30 UTC ngày 2/6 vẫn là ngày 2/6 dù giờ Việt Nam đã sang 3/6.
    stamp = int(datetime(2026, 6, 2, 23, 30, tzinfo=timezone.utc).timestamp())
    reader = _reader([])
    address, topics = swap_filter(POOL_V2, CHAINS["ethereum"])
    reader.items = [{"address": address, "topics": topics, "blockNumber": hex(stamp), "timeStamp": hex(stamp),
                     "transactionHash": "0x1", "logIndex": "0x0"}]
    result = count_swap_days(reader, POOL_V2, CHAINS["ethereum"], date(2026, 6, 2), LAST, 1)
    assert (result.passed, result.swap_days) == (False, 0)  # đúng ngày tạo nên không tính


def test_batched_contract_creation_matches_single_lookup() -> None:
    # Hỏi tuổi theo lô phải cho cùng kết quả từng địa chỉ; địa chỉ thiếu bản ghi nhận None.
    from memecoin.collect.evm import EvmReader
    from memecoin.collect.http import Response

    a, b, c = ("0x" + x * 40 for x in "abc")

    class FakeClient:
        calls = 0

        def request(self, method: str, url: str, params: dict) -> Response:
            FakeClient.calls += 1
            asked = params["contractaddresses"].split(",")
            rows = [{"contractAddress": x.upper().replace("0X", "0x"), "timestamp": str(1000 + i),
                     "contractCreator": "0xDEAD", "txHash": "0x1"} for i, x in enumerate(asked) if x != c]
            return Response({"result": rows}, "raw/fake", "2026-11-13T00:00:00+00:00")

    reader = EvmReader.__new__(EvmReader)
    reader.chain, reader.client, reader.url, reader.key = "ethereum", FakeClient(), "http://fake", ""
    reader.prefetch_contract_creations([a, b, c])
    assert reader.contract_creation_time(a)[0] == 1000
    assert reader.contract_creation_time(b.upper().replace("0X", "0x"))[0] == 1001
    assert reader.contract_creation_time(c)[0] is None
    assert FakeClient.calls == 1  # ba địa chỉ, một lần gọi
