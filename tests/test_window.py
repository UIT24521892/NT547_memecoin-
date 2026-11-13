"""Task 2: tầng ngày tạo, chọn ngày, tìm block, giải mã V4, gộp ứng viên, cutoff/nhóm A."""
from __future__ import annotations

from datetime import date, timedelta
from types import SimpleNamespace
from typing import Any

import pytest

from memecoin.collect.common import load_config
from memecoin.collect.evm import decode_pool_log, event_topic
from memecoin.collect.http import Response
from memecoin.collect.window import aggregate, creation_strata, days_between, find_block, sample_days
from memecoin.model.sampling import assign_cutoff

SPLIT = load_config("split.yaml")
CHAINS = load_config("chains.yaml")


def test_strata_match_split_and_avoid_gaps() -> None:
    strata = creation_strata(SPLIT)
    assert strata == {"train": (date(2026, 5, 26), date(2026, 7, 6)),
                      "validation": (date(2026, 7, 30), date(2026, 8, 23)),
                      "test": (date(2026, 9, 16), date(2026, 10, 16))}
    # Pool tạo ngày cuối mỗi tầng, đủ 7 ngày liên tục, có cutoff đúng ngày cuối của tập.
    for name, (_, last) in strata.items():
        assert last + timedelta(days=SPLIT["min_history_days"]) == date.fromisoformat(str(SPLIT["sets"][name]["cutoff_end"]))


def test_sample_days_reproducible_and_allocated() -> None:
    strata = creation_strata(SPLIT)
    alloc = SPLIT["discovery"]["sampled_days"]["base"]
    one, two = (sample_days(strata, alloc, SPLIT["seed"], "base") for _ in range(2))
    assert one == two
    for name, days in one.items():
        assert len(days) == alloc[name] == len(set(days))
        assert all(strata[name][0] <= d <= strata[name][1] for d in days)
    assert sample_days(strata, alloc, SPLIT["seed"] + 1, "base") != one
    full = sample_days(strata, None, SPLIT["seed"], "ethereum")
    assert sum(map(len, full.values())) == 98
    with pytest.raises(ValueError):
        sample_days(strata, {"train": 999, "validation": 1, "test": 1}, 1, "base")


def _fake_base_reader(genesis_ts: int, block_time: int, latest: int, calls: list) -> Any:
    def call(method: str, params: list) -> Response:
        calls.append(method)
        if method == "eth_blockNumber":
            return Response({"result": hex(latest)}, "raw", "now")
        number = int(params[0], 16)
        return Response({"result": {"timestamp": hex(genesis_ts + number * block_time)}}, "raw", "now")
    return SimpleNamespace(chain="base", config={"block_time_seconds": block_time}, call=call)


@pytest.mark.parametrize("target_offset", [0, 1, 2, 3, 12_345_679])
def test_find_block_base_is_last_block_at_or_before(target_offset: int) -> None:
    calls: list = []
    reader = _fake_base_reader(1_000_000, 2, 50_000_000, calls)
    target = 1_000_000 + target_offset
    block = find_block(reader, target)
    assert 1_000_000 + block * 2 <= target < 1_000_000 + (block + 1) * 2
    assert len(calls) <= 8  # nội suy, không tìm nhị phân ~26 lần


def _v4_log(currency0: str, currency1: str, hooks: str = "0" * 40) -> dict[str, Any]:
    factory = next(f for f in CHAINS["base"]["factories"] if f["name"] == "uniswap_v4")
    pad = lambda a: "0x" + "0" * 24 + a[2:]
    words = ["0" * 64, "0" * 64, "0" * 24 + hooks, "0" * 64, "0" * 64]
    return {"address": factory["address"], "topics": [event_topic(factory["event_signature"]), "0x" + "ab" * 32,
            pad(currency0), pad(currency1)], "data": "0x" + "".join(words), "transactionHash": "0xtx",
            "source": "drpc", "collected_at": "now", "raw_ref": "raw"}


def test_v4_initialize_decodes_pool_id_quote_and_hooks() -> None:
    factory = next(f for f in CHAINS["base"]["factories"] if f["name"] == "uniswap_v4")
    weth, meme = CHAINS["base"]["quote_tokens"]["WETH"], "0x" + "12" * 20
    row = decode_pool_log("base", factory, _v4_log(weth, meme, "cc" * 20), CHAINS["base"]["quote_tokens"])
    assert row["pool_address"] == "0x" + "ab" * 32 and row["version"] == "v4"
    assert row["token_address"] == meme and row["quote_token"] == weth and row["hooks"] == "0x" + "cc" * 20
    native = decode_pool_log("base", factory, _v4_log("0x" + "0" * 40, meme), CHAINS["base"]["quote_tokens"])
    assert native["quote_token"] == "0x" + "0" * 40
    # Không có đồng quote (hoặc cả hai đều là quote) thì không phải ứng viên.
    assert decode_pool_log("base", factory, _v4_log(meme, "0x" + "34" * 20), CHAINS["base"]["quote_tokens"]) is None
    assert decode_pool_log("base", factory, _v4_log("0x" + "0" * 40, weth), CHAINS["base"]["quote_tokens"]) is None


def test_aggregate_dedupes_and_marks_stratum_fraction_and_multi_pool_tokens() -> None:
    strata = {"train": (date(2026, 6, 1), date(2026, 6, 10))}
    plan = {"train": [date(2026, 6, 2), date(2026, 6, 5)]}
    row = lambda pool, token: {"chain": "solana", "pool_address": pool, "token_address": token}
    merged = aggregate({date(2026, 6, 5): [row("P1", "T1")], date(2026, 6, 2): [row("P1", "T1"), row("P2", "T1")]},
                       plan, strata)
    assert [r["pool_address"] for r in merged] == ["P1", "P2"]
    assert merged[0]["creation_day"] == "2026-06-02"  # giữ lần sớm nhất
    assert all(r["stratum"] == "train" and r["day_sampled_fraction"] == 0.2 for r in merged)
    assert all(r["token_pool_count"] == 2 for r in merged)


def _candles(closes: list[float], created: date, volume: float = 100.0) -> list[dict[str, Any]]:
    return [{"ts": (created + timedelta(days=i)).isoformat() + "T00:00:00+00:00", "close": c, "volume_usd": volume}
            for i, c in enumerate(closes)]


def test_cutoff_group_a_positive_and_negative() -> None:
    created = date(2026, 6, 1)
    # Ngày tạo (nến 0) không tính; ngày đầy đủ đầu tiên close=1; ngày thứ 7 close=2.5 -> A.
    positive = assign_cutoff(_candles([9, 1, 1, 1, 1, 1, 1, 2.5], created), created, SPLIT)
    assert positive.cutoff == date(2026, 6, 8) and positive.group_a and positive.split == "outside"
    negative = assign_cutoff(_candles([9, 1, 1, 1, 1, 1, 1, 1.9], created), created, SPLIT)
    assert negative.group_a is False
    late = date(2026, 6, 5)
    in_train = assign_cutoff(_candles([1] * 8, late), late, SPLIT)
    assert in_train.cutoff == date(2026, 6, 12) and in_train.split == "train"
    none = assign_cutoff(_candles([1, 1, 1], created), created, SPLIT)
    assert none.cutoff is None and none.split == "no_cutoff"
    zero_volume = assign_cutoff(_candles([1] * 10, created, volume=0), created, SPLIT)
    assert zero_volume.cutoff is None


def test_cutoff_and_group_ignore_candles_after_cutoff() -> None:
    """Chống rò rỉ: thêm nến sau cutoff (tăng vọt hay sụp) không đổi kết quả."""
    created = date(2026, 6, 5)
    base = _candles([1, 1, 1, 1, 1, 1, 1, 3], created)
    reference = assign_cutoff(base, created, SPLIT)
    for tail in ([0.0001] * 30, [1000] * 30):
        extra = _candles([1] * 8 + tail, created)[8:]
        assert assign_cutoff(base + extra, created, SPLIT) == reference


def test_allocate_by_cutoff_days() -> None:
    from memecoin.model.sampling import allocate
    assert allocate(40, SPLIT) == {"train": 18, "validation": 9, "test": 13}
    assert sum(allocate(7, SPLIT).values()) == 7


class _AgeReader:
    def __init__(self, chain: str, created: int | None = None, code_from_block: int | None = None) -> None:
        self.chain, self.created, self.code_from = chain, created, code_from_block
        self.config = {"block_time_seconds": 2}
    def contract_creation_time(self, token: str):
        return self.created, {"raw_ref": "raw"}
    def call(self, method: str, params: list) -> Response:
        if method == "eth_blockNumber":
            return Response({"result": hex(60_000_000)}, "raw", "now")
        return Response({"result": {"timestamp": hex(1_700_000_000 + int(params[0], 16) * 2)}}, "raw", "now")
    def code_exists_at(self, token: str, block: int):
        return self.code_from is not None and block >= self.code_from, "raw"


def test_token_is_new_positive_negative_and_unknown() -> None:
    from memecoin.collect.common import midnight
    from memecoin.collect.window import token_is_new
    day = date(2026, 6, 10)
    start = midnight(day)
    assert token_is_new(_AgeReader("ethereum", created=start - 3 * 86400), "t", day, 7)[0] is True
    assert token_is_new(_AgeReader("ethereum", created=start - 30 * 86400), "t", day, 7)[0] is False
    assert token_is_new(_AgeReader("ethereum", created=None), "t", day, 7)[0] is None
    # Base: mã contract đã có ở block 7 ngày trước -> token cũ; chưa có -> mới.
    block_7d = (start - 7 * 86400 - 1 - 1_700_000_000) // 2
    assert token_is_new(_AgeReader("base", code_from_block=block_7d - 100), "t", day, 7)[0] is False
    assert token_is_new(_AgeReader("base", code_from_block=block_7d + 100), "t", day, 7)[0] is True


def test_active_at_cutoff_positive_negative_and_missing_days() -> None:
    """Lọc 'còn hoạt động tại cutoff' (phương án (a), 2026-11-13)."""
    created = date(2026, 6, 1)
    threshold = float(SPLIT["sampling"]["active_min_mean_volume_usd"])
    alive = assign_cutoff(_candles([1] * 8, created, volume=threshold * 2), created, SPLIT)
    assert alive.active is True and alive.active_volume_usd == threshold * 2
    # Ngày đầu sôi động rồi chết: volume TB 7 ngày tới cutoff dưới ngưỡng.
    dead = _candles([1] * 8, created, volume=1.0)
    dead[1]["volume_usd"] = threshold * 3  # ngày đầy đủ đầu tiên, nằm trong cửa sổ 7 ngày
    result = assign_cutoff(dead, created, SPLIT)
    assert result.active is False
    assert result.active_volume_usd == (threshold * 3 + 6 * 1.0) / 7
    # Ngày không có nến tính volume 0: bỏ 3 nến trong cửa sổ thì trung bình giảm.
    gaps = [c for i, c in enumerate(_candles([1] * 12, created, volume=700.0)) if i not in (6, 7, 8)]
    with_gaps = assign_cutoff(gaps, created, SPLIT)
    assert with_gaps.cutoff == date(2026, 6, 11)
    assert with_gaps.active_volume_usd == 700.0 * 4 / 7 and with_gaps.active is False
    none = assign_cutoff(_candles([1, 1, 1], created), created, SPLIT)
    assert none.active is None


def test_active_at_cutoff_ignores_candles_after_cutoff() -> None:
    """Chống rò rỉ: volume sau cutoff (vọt hay về 0) không đổi cờ hoạt động."""
    created = date(2026, 6, 5)
    base = _candles([1] * 8, created, volume=500.0)
    reference = assign_cutoff(base, created, SPLIT)
    for volume in (0.0, 1e9):
        tail = [{"ts": (created + timedelta(days=8 + i)).isoformat() + "T00:00:00+00:00",
                 "close": 1.0, "volume_usd": volume} for i in range(30)]
        later = assign_cutoff(base + tail, created, SPLIT)
        assert (later.active, later.active_volume_usd) == (reference.active, reference.active_volume_usd)
