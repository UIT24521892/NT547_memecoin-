"""Gộp truy vấn phải giữ đúng tập log, bộ lọc topic và rate limit chung."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from memecoin.collect.evm import EvmReader, collect_factory_logs, log_matches_filter
from memecoin.collect.http import CollectionError, HttpClient


class RpcReply:
    status_code, headers = 200, {}

    def __init__(self, rows: list[dict[str, Any]]) -> None:
        self.data = {"jsonrpc": "2.0", "id": 1, "result": rows}
        self.content = json.dumps(self.data).encode()

    def json(self) -> dict[str, Any]:
        return self.data


class RpcSession:
    """Nguồn giả có ba factory để kiểm tra request gửi đi và tập log nhận về."""
    def __init__(self, rows: list[dict[str, Any]], *, ignore_filter: bool = False) -> None:
        self.rows, self.ignore_filter, self.calls = rows, ignore_filter, []

    def request(self, *args: Any, **kwargs: Any) -> RpcReply:
        query = kwargs["json"]["params"][0]
        self.calls.append(query)
        if self.ignore_filter:
            return RpcReply(self.rows)
        addresses = query["address"] if isinstance(query["address"], list) else [query["address"]]
        return RpcReply([r for r in self.rows if r["address"].lower() in {a.lower() for a in addresses}
                         and int(query["fromBlock"], 16) <= int(r["blockNumber"], 16) <= int(query["toBlock"], 16)])


FACTORIES = [{"name": name, "address": "0x" + c * 40, "event_topic0": "0x" + c * 64}
             for name, c in (("v2", "a"), ("v3", "b"), ("aero", "c"))]


def fixture_logs() -> list[dict[str, Any]]:
    return [{"address": f["address"], "topics": [f["event_topic0"]], "blockNumber": "0xa",
             "logIndex": hex(i), "transactionHash": "0x" + str(i) * 64, "data": "0x", "removed": False}
            for i, f in enumerate(FACTORIES)]


def reader(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, session: RpcSession, **kwargs: Any) -> EvmReader:
    monkeypatch.setenv("TEST_DRPC_KEY", "unit-test-key")
    settings = {"base_url": "https://example.test/base", "key_env": "TEST_DRPC_KEY", "provider": "drpc",
                "max_block_range": 100, "multi_address": True}
    client = HttpClient(tmp_path, "drpc", 2, session=session, secrets=("unit-test-key",), sleep=lambda _: None, **kwargs)
    return EvmReader("base", client, {"logs": settings})


def test_grouped_factory_scan_preserves_all_logs_with_one_request(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    grouped_session, separate_session = RpcSession(fixture_logs()), RpcSession(fixture_logs())
    grouped_reader = reader(tmp_path, monkeypatch, grouped_session, cache_namespace="grouped")
    separate_reader = reader(tmp_path, monkeypatch, separate_session, cache_namespace="separate")
    together, grouped = collect_factory_logs(grouped_reader, 10, 10, FACTORIES)
    apart, separate = collect_factory_logs(separate_reader, 10, 10, FACTORIES, grouped=False)
    strip = lambda rows: [{k: v for k, v in r.items() if k not in {"raw_ref", "collected_at"}} for r in rows]
    assert strip(together) == strip(apart)
    assert grouped["complete"] and separate["complete"]
    assert len(grouped_session.calls) == 1 and len(separate_session.calls) == 3
    assert grouped_session.calls[0]["address"] == sorted(f["address"] for f in FACTORIES)
    assert grouped_session.calls[0]["topics"] == [sorted(f["event_topic0"] for f in FACTORIES)]
    assert [f["logs"] for f in grouped["factories"]] == [1, 1, 1]


def test_rpc_or_topics_do_not_justify_wrong_factory_event_pair(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    rows = fixture_logs()
    rows[0]["topics"] = [FACTORIES[1]["event_topic0"]]
    source = reader(tmp_path, monkeypatch, RpcSession(rows))
    with pytest.raises(CollectionError, match="sai cặp factory/event"):
        collect_factory_logs(source, 10, 10, FACTORIES)


@pytest.mark.parametrize("change", ["address", "topic", "block", "removed"])
def test_unrelated_or_removed_log_cannot_enter_grouped_data(tmp_path: Path, monkeypatch: pytest.MonkeyPatch, change: str) -> None:
    rows = fixture_logs()
    if change == "address":
        rows[0]["address"] = "0x" + "d" * 40
    elif change == "topic":
        rows[0]["topics"] = ["0x" + "d" * 64]
    elif change == "block":
        rows[0]["blockNumber"] = "0xb"
    else:
        rows[0]["removed"] = True
    source = reader(tmp_path, monkeypatch, RpcSession(rows, ignore_filter=True))
    with pytest.raises(CollectionError):
        collect_factory_logs(source, 10, 10, FACTORIES)


def test_topic_or_is_within_position_not_between_positions() -> None:
    log = {"address": "0xAbC", "topics": ["0xAA", "0xBB", "0xCC"]}
    assert log_matches_filter(log, ["0xabc", "0xdef"], [["0x00", "0xaa"], None, "0xcc"])
    assert not log_matches_filter(log, "0xabc", [["0xaa", "0xbb"], "0xcc"])
    assert not log_matches_filter(log, "0xabc", ["0xaa", None, None, "0xdd"])


def test_cache_namespaces_keep_global_rate_and_default_cache(tmp_path: Path) -> None:
    one = HttpClient(tmp_path, "drpc", 2, cache_namespace="benchmark")
    two = HttpClient(tmp_path, "drpc", 2)
    assert one.rate_file == two.rate_file
    assert one.cache_dir != two.cache_dir and one.cache_dir.parent == two.cache_dir
    with pytest.raises(ValueError, match="Tên cache"):
        HttpClient(tmp_path, "drpc", 2, cache_namespace="../other")


def test_disabled_multi_address_retains_separate_mode(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    source = reader(tmp_path, monkeypatch, RpcSession(fixture_logs()))
    source.logs["multi_address"] = False
    records, report = collect_factory_logs(source, 10, 10, FACTORIES)
    assert len(records) == 3 and report["mode"] == "separate"
    assert source.client.network_requests == 3
