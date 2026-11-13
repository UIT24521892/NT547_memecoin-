"""Kiểm tra lỗi làm sai dữ liệu: cache, phân trang, biên UTC, trần log/tx."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from memecoin.collect.common import midnight
from memecoin.collect.evm import EvmReader, decode_pool_log
from memecoin.collect.http import CollectionError, HttpClient, Response
from memecoin.collect.ohlcv import GeckoTerminal, normalized_address
from memecoin.collect.solana import HeliusReader, migration_candidates
from memecoin.collect.swaps import V2_SWAP, V3_SWAP, decode_amounts


class FakeReply:
    def __init__(self, data: Any, status: int = 200, headers: dict | None = None) -> None:
        self.data, self.status_code, self.headers = data, status, headers or {}
        self.content = json.dumps(data).encode()

    def json(self) -> Any:
        return self.data


class Session:
    def __init__(self, replies: list[FakeReply]) -> None:
        self.replies, self.calls = replies, []

    def request(self, *args: Any, **kwargs: Any) -> FakeReply:
        self.calls.append((args, kwargs))
        return self.replies.pop(0)


def test_cache_replay_hash_refresh_and_secret_redaction(tmp_path: Path) -> None:
    session = Session([FakeReply({"result": [1]}), FakeReply({"result": [2]})])
    client = HttpClient(tmp_path, "test", 10, session=session, secrets=("secret-value",), sleep=lambda _: None)
    first = client.request("GET", "https://example.test/secret-value", params={"apikey": "secret-value", "a": 1})
    assert client.request("GET", "https://example.test/secret-value", params={"apikey": "secret-value", "a": 1}) == first
    assert client.network_requests == client.cache_hits == 1
    original = (tmp_path / first.raw_ref).read_bytes()
    client.refresh = True
    second = client.request("GET", "https://example.test/secret-value", params={"apikey": "secret-value", "a": 1})
    assert second.raw_ref != first.raw_ref and second.data == {"result": [2]}
    assert (tmp_path / first.raw_ref).read_bytes() == original
    assert not any("secret-value" in p.read_text() for p in tmp_path.rglob("*.json"))
    client.offline = True
    assert client.request("GET", "https://example.test/secret-value", params={"apikey": "secret-value", "a": 1}) == second
    (tmp_path / second.raw_ref).write_text("broken")
    with pytest.raises(CollectionError, match="SHA-256"):
        client.request("GET", "https://example.test/secret-value", params={"apikey": "secret-value", "a": 1})


def test_offline_miss_does_not_use_network(tmp_path: Path) -> None:
    session = Session([])
    client = HttpClient(tmp_path, "test", 10, offline=True, session=session)
    with pytest.raises(CollectionError, match="Thiếu cache"):
        client.request("GET", "https://example.test/data")
    assert not session.calls


def test_retry_rate_limit_obeys_retry_after_and_does_not_cache_error(tmp_path: Path) -> None:
    sleep = []
    session = Session([FakeReply({"error": "limited"}, 429, {"Retry-After": "12"}), FakeReply({"data": []})])
    client = HttpClient(tmp_path, "test", 10, session=session, sleep=sleep.append)
    assert client.request("GET", "https://example.test/data").data == {"data": []}
    assert client.network_requests == 2 and 12 in sleep
    assert len(list((tmp_path / "data/raw").rglob("*.body"))) == 2


def test_only_read_rpc_and_request_budget(tmp_path: Path) -> None:
    session = Session([FakeReply({"result": 1})])
    client = HttpClient(tmp_path, "test", 10, session=session, max_requests=1)
    with pytest.raises(ValueError, match="chỉ đọc"):
        client.rpc("https://example.test", "eth_sendRawTransaction", ["bad"])
    client.request("GET", "https://example.test/1")
    with pytest.raises(CollectionError, match="ngân sách"):
        client.request("GET", "https://example.test/2")
    assert len(session.calls) == 1


def test_api_error_not_cached_but_idl_error_definitions_are_data(tmp_path: Path) -> None:
    session = Session([FakeReply({"status": "0", "result": "limit reached"}),
                       FakeReply({"errors": [{"code": 1}], "instructions": []})])
    client = HttpClient(tmp_path, "test", 10, session=session, sleep=lambda _: None)
    with pytest.raises(CollectionError, match="status=0"):
        client.request("GET", "https://example.test/data")
    assert client.request("GET", "https://example.test/data").data["instructions"] == []
    assert client.network_requests == 2


def test_rpc_rate_limit_and_http_timeout_retry(tmp_path: Path) -> None:
    session = Session([FakeReply({}, 408), FakeReply({"error": {"code": -32005}}), FakeReply({"result": []})])
    client = HttpClient(tmp_path, "test", 10, session=session, sleep=lambda _: None)
    assert client.rpc("https://example.test", "eth_getLogs", []).data == {"result": []}
    assert client.network_requests == 3


class Pages:
    def __init__(self, replies: list[dict]) -> None:
        self.replies, self.requests = replies, []
        self.offline = True

    def request(self, method: str, url: str, **kwargs: Any) -> Response:
        self.requests.append(kwargs)
        return Response(self.replies.pop(0), "data/raw/test.body", "2026-11-12T00:00:00+00:00")

    def rpc(self, url: str, method: str, params: list) -> Response:
        self.requests.append(params)
        return Response(self.replies.pop(0), "data/raw/test.body", "2026-11-12T00:00:00+00:00")


def candles(stamps: list[int]) -> dict:
    return {"data": {"attributes": {"ohlcv_list": [[t, 1, 2, 0.5, 1.1, 0] for t in stamps]}}}


def gecko(client: Pages) -> GeckoTerminal:
    return GeckoTerminal(client, {"base_url": "https://example.test", "lookback_days_free": 180,
                                  "max_candles_per_request": 2})


def test_ohlcv_pagination_closed_candles_missing_is_not_zero() -> None:
    start = midnight("2026-11-01")
    pages = Pages([candles([start + 3 * 86400, start + 2 * 86400]), candles([start])])
    rows, report = gecko(pages).collect("solana", "AbC", "MintCase", "day", start, start + 5 * 86400,
                                        now=start + 4 * 86400 + 10)
    assert len(rows) == 3 and report["missing_intervals"] == 1
    assert report["future_tail_pending"] and not report["coverage_complete"]
    assert rows[0]["volume_usd"] == 0
    assert all(r["pool_address"] == "AbC" for r in rows)
    assert pages.requests[1]["params"]["before_timestamp"] == start + 2 * 86400 - 1
    assert pages.requests[0]["params"]["token"] == "MintCase"
    assert normalized_address("base", "0xAbC") == "0xabc"


def test_ohlcv_duplicate_pages_conflicting_data_is_error() -> None:
    start = midnight("2026-11-01")
    one, two = candles([start + 86400, start + 2 * 86400]), candles([start + 86400, start])
    two["data"]["attributes"]["ohlcv_list"][0][4] = 1.2
    with pytest.raises(CollectionError, match="khác nhau"):
        gecko(Pages([one, two])).collect("base", "0xp", "0xt", "day", start, start + 3 * 86400,
                                        now=start + 4 * 86400)


def test_ohlcv_hour_pagination_reaches_start() -> None:
    start = midnight("2026-11-01")
    pages = Pages([candles([start + 7200, start + 3600]), candles([start])])
    rows, report = gecko(pages).collect("base", "0xp", "0xt", "hour", start, start + 10800, now=start + 86400)
    assert len(rows) == 3 and report["coverage_complete"]


def test_ohlcv_underfilled_page_does_not_prove_end_of_history() -> None:
    start = midnight("2026-11-01")
    pages = Pages([candles([start + 7200]), candles([start + 3600]), candles([start])])
    rows, report = gecko(pages).collect("base", "0xp", "0xt", "hour", start, start + 10800, now=start + 86400)
    assert len(rows) == 3 and report["coverage_complete"] and len(pages.requests) == 3


def test_ohlcv_lookback_boundary_and_page_limit_are_not_complete() -> None:
    start = midnight("2026-11-01")
    pages = Pages([])
    pages.offline = False
    rows, report = gecko(pages).collect("base", "0xp", "0xt", "day", start, start + 86400,
                                           now=start + 200 * 86400)
    assert not rows and report["stop_reason"] == "free_lookback_boundary"
    pages = Pages([candles([start + 86400, start + 2 * 86400])])
    _, report = gecko(pages).collect("base", "0xp", "0xt", "day", start, start + 3 * 86400,
                                     now=start + 4 * 86400, max_pages=1)
    assert report["stop_reason"] == "page_limit" and not report["coverage_complete"]


def test_evm_splits_at_truncation_and_preserves_pending(monkeypatch: pytest.MonkeyPatch) -> None:
    reader = object.__new__(EvmReader)
    reader.chain = "ethereum"
    reader.logs = {"max_rows_per_request": 2, "provider": "blockscout"}
    queried = []
    def get_logs(left: int, right: int, address: str, topics: list) -> tuple[list, Response]:
        queried.append((left, right))
        result = [{"blockNumber": left, "logIndex": 0, "transactionHash": str(left),
                   "address": "0xpool", "topics": ["topic"]}]
        if left != right:
            result *= 2
        return result, Response({}, "raw", "2026-11-12")
    monkeypatch.setattr(reader, "get_logs", get_logs)
    rows, report = reader.collect_logs(10, 11, "0xpool", ["topic"])
    assert queried == [(10, 11), (10, 10), (11, 11)]
    assert len(rows) == 2 and report["complete"]
    _, limited = reader.collect_logs(10, 11, "0xpool", ["topic"], max_chunks=1)
    assert not limited["complete"] and limited["next_block"] == 10


def test_evm_pool_decoding_uses_protocol_layout_and_quote() -> None:
    address = lambda c: "0x" + c * 40
    word = lambda c: "0" * 24 + c * 40
    log = {"topics": ["topic", "0x" + word("1"), "0x" + word("2")],
           "data": "0x" + "0" * 64 + word("3"), "transactionHash": "tx", "timeStamp": "0x1",
           "source": "test", "collected_at": "now", "raw_ref": "raw"}
    row = decode_pool_log("base", {"name": "uniswap_v3", "event_topic0": "topic"}, log, {"WETH": address("1")})
    assert row["pool_address"] == address("3") and row["token_address"] == address("2")
    assert decode_pool_log("base", {"name": "uniswap_v3", "event_topic0": "topic"}, log, {}) is None


def test_blockscout_timestamp_result_object() -> None:
    reader = object.__new__(EvmReader)
    reader.chain, reader.url, reader.key = "ethereum", "https://example.test", ""
    reader.client = Pages([{"status": "1", "result": {"blockNumber": "25283318"}}])
    assert reader.block_at(midnight("2026-06-10") - 1) == 25283318


def tx(signature: str, stamp: int) -> dict:
    return {"blockTime": stamp, "slot": 123, "transaction": {"signatures": [signature],
        "message": {"accountKeys": [], "instructions": []}}, "meta": {"err": None}}


def test_solana_cap_and_cursor_stall_are_partial() -> None:
    stamp = midnight("2026-11-01")
    client = Pages([{"result": {"data": [tx("a", stamp)], "paginationToken": "p"}}])
    reader = HeliusReader(client, {"rpc": {"key_env": "FAKE_KEY", "base_url": "https://example.test"},
                                   "max_supported_transaction_version": 1, "max_transactions_per_token": 1})
    _, report = reader.history("pool", stamp, stamp + 86400)
    assert report["swaps_partial"] and report["stop_reason"] == "transaction_cap"
    client = Pages([{"result": {"data": [tx("a", stamp)], "paginationToken": "p"}},
                    {"result": {"data": [tx("a", stamp)], "paginationToken": "p"}}])
    reader.client, reader.config["max_transactions_per_token"] = client, 10
    records, report = reader.history("pool", stamp, stamp + 86400)
    assert len(records) == 1 and report["stop_reason"] == "cursor_stalled"


def test_migration_not_all_successful_transactions_are_new_tokens() -> None:
    transaction = tx("sig", 1)
    record = {"transaction": transaction, "signature": "sig", "collected_at": "now", "raw_ref": "raw"}
    assert not migration_candidates([record], "migration_account")
    transaction["transaction"]["message"]["accountKeys"] = [{"pubkey": "migration_account"}]
    transaction["meta"]["logMessages"] = ["Program log: Instruction: Migrate"]
    row = migration_candidates([record], "migration_account")[0]
    assert row["status"] == "needs_pool_and_meme_mint_resolution"
    assert not row["initialized_mints"]


def test_v2_buy_sell_and_v3_signed_amounts_preserve_integer_precision() -> None:
    def log(topic: str, values: list[int]) -> dict:
        return {"topics": [topic], "data": "0x" + "".join(f"{v % (2 ** 256):064x}" for v in values)}
    amount = 123456789123456789123456789
    buy = decode_amounts(log(V2_SWAP, [0, 5, amount, 0]), "0xmeme", "0xmeme", "v2")
    sell = decode_amounts(log(V2_SWAP, [amount, 0, 0, 5]), "0xmeme", "0xmeme", "v2")
    assert buy == {"side": "buy", "amount_token_raw": str(amount), "amount_quote_raw": "5"}
    assert sell["side"] == "sell"
    assert decode_amounts(log(V3_SWAP, [5, -amount, 100, 100, 0]), "0xquote", "0xmeme", "v3") == buy
    with pytest.raises(CollectionError, match="Flash swap"):
        decode_amounts(log(V2_SWAP, [amount, 0, 1, 5]), "0xmeme", "0xmeme", "v2")


def test_migration_creation_requires_real_create_pool_instruction() -> None:
    # Byte 0 được mã hóa base58 thành 1: không cần thư viện bên ngoài trong test.
    transaction = tx("sig", 1)
    transaction["transaction"]["message"].update(accountKeys=[{"pubkey": "migration_account"}],
        instructions=[{"programId": "pump", "data": "1", "accounts": ["mint", "quote", "pool"]}])
    transaction["meta"]["logMessages"] = ["Program log: Instruction: Migrate"]
    settings = {"program_id": "pump", "amm_program_id": "amm", "create_pool_discriminator": [0],
                "migration_layouts": [{"name": "migrate", "discriminator": [0],
                                       "mint_index": 0, "quote_index": 1, "pool_index": 2}]}
    record = {"transaction": transaction, "signature": "sig", "collected_at": "now", "raw_ref": "raw"}
    assert not migration_candidates([record], "migration_account", settings)[0]["pool_creation_confirmed"]
    transaction["meta"]["innerInstructions"] = [{"index": 0, "instructions": [
        {"programId": "amm", "data": "1", "accounts": ["pool", "mint", "quote"]}]}]
    assert migration_candidates([record], "migration_account", settings)[0]["pool_creation_confirmed"]


def test_two_clients_share_provider_rate_limit(tmp_path: Path) -> None:
    clock = [100.0]
    pauses = []
    def sleep(seconds: float) -> None:
        pauses.append(seconds)
        clock[0] += seconds
    one = HttpClient(tmp_path, "test", 2, session=Session([FakeReply({})]), clock=lambda: clock[0], sleep=sleep)
    two = HttpClient(tmp_path, "test", 2, session=Session([FakeReply({})]), clock=lambda: clock[0], sleep=sleep)
    one.request("GET", "https://example.test/1")
    two.request("GET", "https://example.test/2")
    assert pauses == [0.5]


def test_evm_cached_prefix_does_not_prevent_resume(monkeypatch: pytest.MonkeyPatch) -> None:
    from types import SimpleNamespace
    reader = object.__new__(EvmReader)
    reader.chain, reader.logs = "base", {"provider": "drpc", "max_block_range": 100}
    reader.client = SimpleNamespace(network_requests=0)
    cached = set()
    def get_logs(left: int, right: int, address: str, topics: list) -> tuple[list, Response]:
        if left not in cached:
            reader.client.network_requests += 1
            cached.add(left)
        return [], Response({}, "raw", "now")
    monkeypatch.setattr(reader, "get_logs", get_logs)
    _, first = reader.collect_logs(0, 199, "address", [], max_chunks=1)
    assert not first["complete"]
    _, second = reader.collect_logs(0, 199, "address", [], max_chunks=1)
    assert second["complete"] and second["new_chunks"] == 1


def test_cache_pointer_read_during_rewrite_sees_complete_version(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Ca review Codex 12/11: đọc pointer trong lúc tiến trình khác ghi đè không được JSONDecodeError."""
    import os
    import threading
    from memecoin.collect import common

    url = "https://example.test/data"
    HttpClient(tmp_path, "test", 10, session=Session([FakeReply({"result": [1]})]), sleep=lambda _: None).request("GET", url)

    pointer_dir = tmp_path / "data/interim/http_cache/test"
    entered, release = threading.Event(), threading.Event()
    real_fsync = os.fsync

    def slow_fsync(fd: int) -> None:
        # Chặn đúng lúc pointer mới đã ghi vào file tạm nhưng chưa thay file thật.
        real_fsync(fd)
        if any(p.suffix == ".tmp" for p in pointer_dir.iterdir()):
            entered.set()
            release.wait(5)

    monkeypatch.setattr(common.os, "fsync", slow_fsync)
    writer = HttpClient(tmp_path, "test", 10, refresh=True, session=Session([FakeReply({"result": [2]})]), sleep=lambda _: None)
    thread = threading.Thread(target=writer.request, args=("GET", url))
    thread.start()
    try:
        assert entered.wait(5)
        reader = HttpClient(tmp_path, "test", 10, offline=True)
        assert reader.request("GET", url).data == {"result": [1]}  # bản cũ, đầy đủ
    finally:
        release.set()
        thread.join(5)
    assert HttpClient(tmp_path, "test", 10, offline=True).request("GET", url).data == {"result": [2]}
    assert not [p for p in pointer_dir.iterdir() if p.suffix == ".tmp"]


def test_failed_write_keeps_old_file_and_no_temp(tmp_path: Path) -> None:
    from memecoin.collect.common import write_csv

    path = tmp_path / "out.csv"
    write_csv(path, [{"a": 1}], ["a"])
    old = path.read_bytes()

    def broken_rows():
        yield {"a": 2}
        raise RuntimeError("đứt giữa chừng")

    with pytest.raises(RuntimeError):
        write_csv(path, broken_rows(), ["a"])
    assert path.read_bytes() == old
    assert [p.name for p in tmp_path.iterdir()] == ["out.csv"]


def test_atomic_write_keeps_normal_file_permissions(tmp_path: Path) -> None:
    from memecoin.collect.common import write_json

    path = tmp_path / "sub" / "x.json"
    write_json(path, {"k": "giá trị"})
    assert json.loads(path.read_text(encoding="utf-8")) == {"k": "giá trị"}
    assert path.stat().st_mode & 0o777 == 0o644
