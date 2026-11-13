"""Giải mã swap EVM V2/V3 từ log; USD để trống khi chưa có nguồn quy đổi."""
from __future__ import annotations

from decimal import Decimal
from typing import Any

from .common import iso_time
from .evm import EvmReader, as_int, event_topic
from .http import CollectionError

V2_SWAP = event_topic("Swap(address,uint256,uint256,uint256,uint256,address)")
V3_SWAP = event_topic("Swap(address,address,int256,int256,uint160,uint128,int24)")
FIELDS = ["chain", "pool_address", "tx_hash", "event_index", "block_number", "block_time",
          "trader", "trader_method", "side", "amount_token_raw", "amount_quote_raw", "amount_token_ui",
          "amount_quote_ui", "amount_usd", "usd_method", "execution_ok", "source", "collected_at", "raw_ref"]


def decode_amounts(log: dict[str, Any], token0: str, meme: str, protocol: str) -> dict[str, Any]:
    """Dấu theo pool: pool mất meme => buy. Router không phải trader mặc định."""
    topic = V2_SWAP if protocol == "v2" else V3_SWAP
    if log["topics"][0].lower() != topic or log.get("removed"):
        raise CollectionError("Log không khớp loại swap hoặc đã bị removed.")
    data = log["data"][2:]
    if len(data) % 64:
        raise CollectionError("Swap data không đủ word 32 byte.")
    values = [int(data[i:i + 64], 16) for i in range(0, len(data), 64)]
    if protocol == "v2":
        if len(values) != 4:
            raise CollectionError("Swap V2 phải có 4 lượng uint256.")
        if (values[0] and values[2]) or (values[1] and values[3]):
            raise CollectionError("Flash swap nhiều chân chưa hỗ trợ; không lấy net amount thay gross volume.")
        delta0, delta1 = values[0] - values[2], values[1] - values[3]
    else:
        if len(values) != 5:
            raise CollectionError("Swap V3 phải có 5 trường data theo ABI chuẩn.")
        delta0, delta1 = (n - 2 ** 256 if n >= 2 ** 255 else n for n in values[:2])
    token_delta, quote_delta = (delta0, delta1) if token0.lower() == meme.lower() else (delta1, delta0)
    if token_delta == 0 or quote_delta == 0 or (token_delta > 0) == (quote_delta > 0):
        raise CollectionError("Swap không có hai chân ngược dấu.")
    return {"side": "buy" if token_delta < 0 else "sell",
            "amount_token_raw": str(abs(token_delta)), "amount_quote_raw": str(abs(quote_delta))}


def decode_logs(reader: EvmReader, logs: list[dict[str, Any]], *, token0: str, meme: str,
                protocol: str, token_decimals: int | None = None, quote_decimals: int | None = None
                ) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    swaps, unresolved = [], []
    transactions: dict[str, Any] = {}
    timestamps: dict[int, int] = {}
    for log in logs:
        try:
            amount = decode_amounts(log, token0, meme, protocol)
            tx_hash, block = log["transactionHash"], as_int(log["blockNumber"])
            if tx_hash not in transactions:
                response = reader.call("eth_getTransactionByHash", [tx_hash])
                transactions[tx_hash] = response.data["result"]
            tx = transactions[tx_hash]
            if not tx or tx["hash"].lower() != tx_hash.lower() or as_int(tx["blockNumber"]) != block:
                raise CollectionError("Giao dịch không khớp log/block.")
            if log.get("timeStamp"):
                stamp = as_int(log["timeStamp"])
            else:
                if block not in timestamps:
                    result = reader.call("eth_getBlockByNumber", [hex(block), False]).data["result"]
                    timestamps[block] = as_int(result["timestamp"])
                stamp = timestamps[block]
            row = {"chain": reader.chain, "pool_address": log["address"].lower(), "tx_hash": tx_hash,
                   "event_index": as_int(log["logIndex"]), "block_number": block, "block_time": iso_time(stamp),
                   "trader": tx["from"].lower(), "trader_method": "evm_tx_from", **amount,
                   "amount_token_ui": None, "amount_quote_ui": None, "amount_usd": None, "usd_method": None,
                   "execution_ok": True, "source": log["source"], "collected_at": log["collected_at"],
                   "raw_ref": log["raw_ref"]}
            for side, decimals in (("token", token_decimals), ("quote", quote_decimals)):
                if decimals is not None:
                    row[f"amount_{side}_ui"] = str(Decimal(row[f"amount_{side}_raw"]).scaleb(-decimals))
            swaps.append(row)
        except CollectionError as exc:
            unresolved.append({"tx_hash": log["transactionHash"], "log_index": log["logIndex"], "error": str(exc)})
    return swaps, unresolved
