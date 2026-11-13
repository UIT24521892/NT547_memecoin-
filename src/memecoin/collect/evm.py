"""Đọc log lịch sử EVM và giải mã log tạo pool (không ký/gửi giao dịch)."""
from __future__ import annotations

import os
import time
from typing import Any

from eth_hash.auto import keccak

from .common import iso_time
from .http import CollectionError, HttpClient, Response


def as_int(value: str | int) -> int:
    return int(value, 16) if isinstance(value, str) and value.startswith("0x") else int(value)


def event_topic(signature: str) -> str:
    """Ethereum dùng Keccak-256, khác SHA3-256 trong hashlib."""
    return "0x" + keccak(signature.encode()).hex()


def factory_topic(factory: dict[str, Any]) -> str:
    return factory.get("event_topic0") or event_topic(factory["event_signature"])


def log_matches_filter(log: dict[str, Any], address: str | list[str], topics: list[Any]) -> bool:
    """OR trong một vị trí topic, AND giữa các vị trí; địa chỉ không phân biệt hoa/thường."""
    addresses = [address] if isinstance(address, str) else address
    if log.get("address", "").lower() not in {a.lower() for a in addresses}:
        return False
    actual = log.get("topics", [])
    for index, condition in enumerate(topics):
        if condition is None:
            continue
        accepted = [condition] if isinstance(condition, str) else condition
        if index >= len(actual) or actual[index].lower() not in {t.lower() for t in accepted}:
            return False
    return True


class EvmReader:
    def __init__(self, chain: str, client: HttpClient, config: dict[str, Any]) -> None:
        self.chain, self.client, self.config = chain, client, config
        self.logs = config["logs"]
        key = os.environ.get(self.logs["key_env"], "")
        if not key and not client.offline:
            raise CollectionError(f"Thiếu {self.logs['key_env']} trong .env.")
        key = key or "<redacted>"  # Cho phép replay offline khi không mang theo .env.
        self.key = key
        self.url = self.logs["base_url"]
        if chain == "base":
            self.url += "/" + key

    def call(self, method: str, params: list[Any]) -> Response:
        if self.chain == "base":
            return self.client.rpc(self.url, method, params)
        if method == "eth_getTransactionByHash":
            response = self.client.request("GET", self.url, params={"module": "transaction", "action": "gettxinfo",
                "txhash": params[0], "apikey": self.key})
            if response.data.get("status") != "1":
                raise CollectionError(f"Blockscout không trả txinfo; raw={response.raw_ref}")
            return Response({"result": response.data["result"]}, response.raw_ref, response.collected_at)
        if method not in {"eth_getTransactionByHash", "eth_getBlockByNumber", "eth_blockNumber", "eth_call"}:
            raise ValueError("Phương thức Ethereum chưa được hỗ trợ.")
        query: dict[str, Any] = {"module": "proxy", "action": method, "apikey": self.key}
        if method == "eth_getTransactionByHash":
            query["txhash"] = params[0]
        elif method == "eth_getBlockByNumber":
            query.update(tag=params[0], boolean="false")
        elif method == "eth_call":
            query.update(to=params[0]["to"], data=params[0]["data"], tag=params[1])
        return self.client.request("GET", self.url, params=query)

    def block_at(self, timestamp: int) -> int:
        """Block cuối có thời gian <= timestamp; dùng cho biên trái/phải cửa sổ."""
        if self.chain == "ethereum":
            response = self.client.request("GET", self.url,
                params={"module": "block", "action": "getblocknobytime", "timestamp": timestamp,
                        "closest": "before", "apikey": self.key})
            if response.data.get("status") != "1":
                raise CollectionError("Blockscout không trả block theo timestamp.")
            result = response.data["result"]
            return as_int(result["blockNumber"] if isinstance(result, dict) else result)
        high = as_int(self.call("eth_blockNumber", []).data["result"])
        low = 0
        while low < high:
            mid = (low + high + 1) // 2
            block = self.call("eth_getBlockByNumber", [hex(mid), False]).data["result"]
            if not block:
                raise CollectionError("RPC không trả block lịch sử.")
            if as_int(block["timestamp"]) <= timestamp:
                low = mid
            else:
                high = mid - 1
        return low

    def contract_creation_time(self, address: str) -> tuple[int | None, dict[str, Any]]:
        """Thời điểm tạo contract (Unix). Ethereum: Blockscout getcontractcreation (kèm creator)."""
        if self.chain != "ethereum":
            raise ValueError("Chỉ Ethereum có getcontractcreation miễn phí; Base dùng code_exists_at.")
        fetched = getattr(self, "_creations", {})
        if address.lower() not in fetched:
            fetched = self.prefetch_contract_creations([address])
        return fetched[address.lower()]

    def prefetch_contract_creations(self, addresses: list[str]) -> dict[str, tuple[int | None, dict[str, Any]]]:
        """Hỏi thời điểm tạo của nhiều contract trong MỘT lần gọi (tiết kiệm credit Blockscout).

        Thử thật 2026-11-13: 5 và 10 địa chỉ/lần đều trả đủ. Kết quả giữ trong bộ nhớ để
        `contract_creation_time` dùng lại; địa chỉ không có bản ghi nhận (None, ...).
        """
        if self.chain != "ethereum":
            raise ValueError("Chỉ Ethereum có getcontractcreation miễn phí; Base dùng code_exists_at.")
        wanted = [a.lower() for a in addresses]
        response = self.client.request("GET", self.url, params={"module": "contract",
            "action": "getcontractcreation", "contractaddresses": ",".join(wanted), "apikey": self.key})
        found = {str(r.get("contractAddress", "")).lower(): r for r in response.data.get("result") or []}
        store = self.__dict__.setdefault("_creations", {})
        for address in wanted:
            row = found.get(address)
            if not row or not row.get("timestamp"):
                store[address] = (None, {"raw_ref": response.raw_ref})
            else:
                store[address] = (int(row["timestamp"]), {"creator": str(row.get("contractCreator", "")).lower(),
                                                          "creation_tx": row.get("txHash"), "raw_ref": response.raw_ref})
        return store

    def code_exists_at(self, address: str, block: int) -> tuple[bool, str]:
        """Contract đã có mã tại block lịch sử chưa (eth_getCode, chỉ đọc)."""
        response = self.call("eth_getCode", [address, hex(block)])
        code = response.data.get("result")
        if not isinstance(code, str):
            raise CollectionError(f"RPC không trả mã contract; raw={response.raw_ref}")
        return code not in ("0x", "0x0", ""), response.raw_ref

    def get_logs(self, start: int, end: int, address: str | list[str], topics: list[Any]) -> tuple[list[dict[str, Any]], Response]:
        if self.chain == "base":
            response = self.call("eth_getLogs", [{"fromBlock": hex(start), "toBlock": hex(end),
                                                 "address": address, "topics": topics}])
            result = response.data["result"]
        else:
            if isinstance(address, list):
                if len(address) != 1:
                    raise ValueError("Blockscout: lấy log từng địa chỉ.")
                address = address[0]
            query: dict[str, Any] = {"module": "logs", "action": "getLogs", "fromBlock": start,
                                     "toBlock": end, "address": address, "apikey": self.key}
            for i, topic in enumerate(topics):
                if topic is not None:
                    if not isinstance(topic, str):
                        raise ValueError("Blockscout: mỗi vị trí chỉ hỗ trợ một topic.")
                    query[f"topic{i}"] = topic
            # Blockscout bắt buộc toán tử giữa mỗi cặp topic (thiếu thì trả status=0, đo 2026-11-13).
            present = [i for i, topic in enumerate(topics) if topic is not None]
            for a, i in enumerate(present):
                for j in present[a + 1:]:
                    query[f"topic{i}_{j}_opr"] = "and"
            response = self.client.request("GET", self.url, params=query)
            result = response.data.get("result")
            if not isinstance(result, list):
                raise CollectionError(f"Blockscout không trả danh sách log; raw={response.raw_ref}")
        if not isinstance(result, list):
            raise CollectionError("RPC không trả danh sách log.")
        return result, response

    def collect_logs(self, start: int, end: int, address: str | list[str], topics: list[Any],
                     *, max_chunks: int = 10000) -> tuple[list[dict[str, Any]], dict[str, Any]]:
        """Dải block bao gồm hai đầu. Chia tiếp khi Blockscout chạm trần 1.000 dòng."""
        if start > end or max_chunks < 1:
            raise ValueError("Dải block hoặc max_chunks không hợp lệ.")
        width = self.logs.get("max_block_range", end - start + 1)
        pending = [(a, min(a + width - 1, end)) for a in range(start, end + 1, width)]
        records: dict[tuple[str, int], dict[str, Any]] = {}
        consumed, new_chunks = 0, 0
        error = None
        while pending and new_chunks < max_chunks:
            left, right = pending[0]
            client = getattr(self, "client", None)
            requests_before = getattr(client, "network_requests", None)
            try:
                logs, response = self.get_logs(left, right, address, topics)
            except CollectionError as exc:
                error = str(exc)
                break
            consumed += 1
            # Dải đọc từ cache không ăn ngân sách mới, nên chạy lại sẽ tiến xa hơn.
            if requests_before is None or client.network_requests > requests_before:
                new_chunks += 1
            if self.chain == "ethereum" and len(logs) >= self.logs["max_rows_per_request"]:
                if left == right:
                    error = "Một block chạm trần log; chưa chứng minh đầy đủ, cần nguồn dự phòng."
                    break
                middle = (left + right) // 2
                pending[:1] = [(left, middle), (middle + 1, right)]
                continue
            for log in logs:
                if not left <= as_int(log["blockNumber"]) <= right or log.get("removed"):
                    raise CollectionError("Log nằm ngoài dải block hoặc đã removed.")
                if not log_matches_filter(log, address, topics):
                    raise CollectionError("Nguồn trả log sai địa chỉ hoặc topic so với bộ lọc.")
                row = dict(log, source=self.logs["provider"], raw_ref=response.raw_ref,
                           collected_at=response.collected_at)
                records[(log["transactionHash"], as_int(log["logIndex"]))] = row
            pending.pop(0)
        return sorted(records.values(), key=lambda r: (as_int(r["blockNumber"]), as_int(r["logIndex"]))), {
            "chain": self.chain, "from_block": start, "to_block": end, "chunks": consumed, "new_chunks": new_chunks,
            "complete": not pending and error is None, "remaining_chunks": len(pending),
            "next_block": pending[0][0] if pending else None, "error": error,
            "logs": len(records), "resume": "Chạy lại cùng tham số: các dải thành công đọc từ cache."}


def collect_factory_logs(reader: EvmReader, start: int, end: int, factories: list[dict[str, Any]],
                         *, grouped: bool = True, max_chunks: int = 10000
                         ) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Gộp Base thành một lượt quét; Ethereum hoặc baseline vẫn quét từng factory.

    RPC áp dụng tích các bộ address/topic. Sau khi nhận, phải kiểm tra cả cặp
    (factory address, đúng event topic) trước khi giải mã, tránh gán nhầm ABI.
    """
    if not factories:
        raise ValueError("Phải chọn ít nhất một factory.")
    for factory in factories:
        if not factory.get("address") or not (factory.get("event_topic0") or factory.get("event_signature")):
            raise CollectionError(f"Factory {factory['name']} chưa có địa chỉ/topic đã xác minh.")
    addresses = [f["address"].lower() for f in factories]
    if len(set(addresses)) != len(addresses):
        raise ValueError("Danh sách factory bị trùng địa chỉ.")
    use_group = grouped and reader.chain == "base" and reader.logs.get("multi_address", False) and len(factories) > 1
    groups = [factories] if use_group else [[f] for f in factories]
    records, scans = [], []
    for group in groups:
        if len(group) > 1:
            query_address: str | list[str] = sorted(f["address"].lower() for f in group)
            query_topics: list[Any] = [sorted({factory_topic(f).lower() for f in group})]
        else:
            # Giữ nguyên request cũ để replay cache của đợt collector đầu tiên.
            query_address, query_topics = group[0]["address"], [factory_topic(group[0])]
        started = time.monotonic()
        previous = reader.client.stats()
        data, report = reader.collect_logs(start, end, query_address, query_topics, max_chunks=max_chunks)
        valid_pairs = {(f["address"].lower(), factory_topic(f).lower()) for f in group}
        for log in data:
            if (log["address"].lower(), log["topics"][0].lower()) not in valid_pairs:
                raise CollectionError("Log khớp bộ lọc gộp nhưng sai cặp factory/event; không giải mã bằng ABI khác.")
        scans.append(dict(report, factories=[f["name"] for f in group],
                          elapsed_seconds=round(time.monotonic() - started, 6),
                          network_requests=reader.client.network_requests - previous["network_requests"],
                          cache_hits=reader.client.cache_hits - previous["cache_hits"]))
        records.extend(data)
    # Giữ thứ tự factory như trước, sau đó thứ tự block/log, để CSV ổn định.
    order = {f["address"].lower(): i for i, f in enumerate(factories)}
    records.sort(key=lambda r: (order[r["address"].lower()], as_int(r["blockNumber"]), as_int(r["logIndex"])))
    summaries = []
    for factory in factories:
        scan = next(s for s in scans if factory["name"] in s["factories"])
        summaries.append({"factory": factory["name"], "logs": sum(r["address"].lower() == factory["address"].lower() for r in records),
                          "complete": scan["complete"], "error": scan["error"], "scan_index": scans.index(scan)})
    return records, {"mode": "grouped" if use_group else "separate", "complete": all(s["complete"] for s in scans),
                     "factories": summaries, "scans": scans}


def decode_pool_log(chain: str, factory: dict[str, Any], log: dict[str, Any],
                    quote_tokens: dict[str, str]) -> dict[str, Any] | None:
    """PoolCreated V3 có pool ở word 1; V2 ở word 0. Không suy mint từ tên token."""
    topics = log["topics"]
    if topics[0].lower() != factory_topic(factory).lower():
        raise CollectionError("topic0 không khớp factory.")
    if factory["name"] == "uniswap_v4":
        return _decode_v4_initialize(chain, factory, log, quote_tokens)
    token0, token1 = ("0x" + topics[i][-40:].lower() for i in (1, 2))
    quotes = {v.lower() for v in quote_tokens.values()}
    if (token0 in quotes) == (token1 in quotes):
        return None
    words = [log["data"][2:][i:i + 64] for i in range(0, len(log["data"]) - 2, 64)]
    pool_word = 1 if factory["name"] == "uniswap_v3" else 0
    if len(words) <= pool_word or len(words[pool_word]) != 64:
        raise CollectionError("Log tạo pool thiếu trường address.")
    version = "v3" if factory["name"] == "uniswap_v3" else "v2"
    if factory["name"] == "aerodrome" and as_int(topics[3]):
        version = "stable"  # Pool stable Aerodrome không tuân x*y=k.
    return {"chain": chain, "pool_address": "0x" + words[pool_word][-40:].lower(),
            "token_address": token1 if token0 in quotes else token0,
            "quote_token": token0 if token0 in quotes else token1,
            "dex": factory["name"], "version": version,
            "created_at": iso_time(as_int(log["timeStamp"])) if log.get("timeStamp") else None,
            "created_tx": log["transactionHash"], "source": log["source"],
            "collected_at": log["collected_at"], "raw_ref": log["raw_ref"],
            "eligibility": "candidate_only_meme_status_unverified"}


def _decode_v4_initialize(chain: str, factory: dict[str, Any], log: dict[str, Any],
                          quote_tokens: dict[str, str]) -> dict[str, Any] | None:
    """Initialize của PoolManager V4: topics = [sig, PoolId, currency0, currency1].

    `pool_address` giữ nguyên PoolId 32 byte (GeckoTerminal tra được bằng id này).
    Data: fee, tickSpacing, hooks, sqrtPriceX96, tick. Hook có thể đổi cách tính giá,
    nên cột `hooks` được giữ để báo cáo và lọc sau; không tự coi pool có hook là x*y=k.
    """
    topics = log["topics"]
    if len(topics) != 4 or len(topics[1]) != 66:
        raise CollectionError("Initialize V4 phải có PoolId và hai currency indexed.")
    token0, token1 = ("0x" + topics[i][-40:].lower() for i in (2, 3))
    quotes = {v.lower() for v in quote_tokens.values()}
    if (token0 in quotes) == (token1 in quotes):
        return None
    words = [log["data"][2:][i:i + 64] for i in range(0, len(log["data"]) - 2, 64)]
    if len(words) != 5 or any(len(w) != 64 for w in words):
        raise CollectionError("Initialize V4 phải có đúng 5 trường data.")
    return {"chain": chain, "pool_address": topics[1].lower(),
            "token_address": token1 if token0 in quotes else token0,
            "quote_token": token0 if token0 in quotes else token1,
            "dex": factory["name"], "version": "v4", "hooks": "0x" + words[2][-40:].lower(),
            "created_at": iso_time(as_int(log["timeStamp"])) if log.get("timeStamp") else None,
            "created_tx": log["transactionHash"], "source": log["source"],
            "collected_at": log["collected_at"], "raw_ref": log["raw_ref"],
            "eligibility": "candidate_only_meme_status_unverified"}
