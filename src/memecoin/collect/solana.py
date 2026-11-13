"""Lịch sử Solana qua Helius: lọc ngày, phân trang, nhận diện migration."""
from __future__ import annotations

import os
from typing import Any

from .http import CollectionError, HttpClient, Response


class HeliusReader:
    def __init__(self, client: HttpClient, config: dict[str, Any]) -> None:
        self.client, self.config = client, config
        key = os.environ.get(config["rpc"]["key_env"], "")
        if not key and not client.offline:
            raise CollectionError(f"Thiếu {config['rpc']['key_env']} trong .env.")
        key = key or "<redacted>"
        self.url = config["rpc"]["base_url"] + "?api-key=" + key

    def history(self, address: str, start: int, end: int, *, page_size: int = 100,
                max_pages: int = 100, max_transactions: int | None = None) -> tuple[list[dict[str, Any]], dict[str, Any]]:
        if start >= end or not 1 <= page_size <= 1000 or max_pages < 1:
            raise ValueError("Cửa sổ hoặc phân trang không hợp lệ.")
        cap = max_transactions or self.config["max_transactions_per_token"]
        records: dict[str, dict[str, Any]] = {}
        cursor = None
        seen: set[str] = set()
        complete, error, reason = False, None, "page_limit"
        pages = 0
        while pages < max_pages and len(records) < cap:
            options: dict[str, Any] = {"transactionDetails": "full", "sortOrder": "asc",
                "limit": min(page_size, cap - len(records)), "encoding": "jsonParsed",
                "maxSupportedTransactionVersion": self.config["max_supported_transaction_version"],
                "filters": {"blockTime": {"gte": start, "lt": end}, "status": "succeeded"}}
            if cursor:
                options["paginationToken"] = cursor
            try:
                response = self.client.rpc(self.url, "getTransactionsForAddress", [address, options])
            except CollectionError as exc:
                error, reason = str(exc), "request_error"
                break
            pages += 1
            result = response.data["result"]
            data = result["data"]
            for tx in data:
                if not start <= tx["blockTime"] < end or tx["meta"]["err"] is not None:
                    raise CollectionError("Helius trả giao dịch sai cửa sổ/trạng thái.")
                signature = tx["transaction"]["signatures"][0]
                records[signature] = {"signature": signature, "transaction": tx,
                    "source": "helius", "collected_at": response.collected_at, "raw_ref": response.raw_ref}
            cursor = result.get("paginationToken")
            if not cursor:
                complete, reason = True, "provider_exhausted"
                break
            if cursor in seen or not data:
                reason = "cursor_stalled"
                break
            seen.add(cursor)
        if len(records) >= cap and not complete:
            reason = "transaction_cap"
        return list(records.values()), {"address": address, "start": start, "end_exclusive": end,
            "pages": pages, "transactions": len(records), "complete": complete,
            "swaps_partial": not complete, "stop_reason": reason, "error": error,
            "pagination_token": cursor, "note": "Giao dịch tham chiếu account chưa chắc là swap."}


def base58_decode(value: str) -> bytes:
    """Giải mã bytes instruction, giữ byte 0 đầu chuỗi; không đổi hoa/thường."""
    alphabet = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"
    number = 0
    for character in value:
        number = number * 58 + alphabet.index(character)
    prefix = len(value) - len(value.lstrip("1"))
    return b"\0" * prefix + number.to_bytes((number.bit_length() + 7) // 8, "big")


def migration_candidates(records: list[dict[str, Any]], account: str,
                         settings: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    """Chỉ lấy tx có log Migrate + account đã cấu hình; mint từ initializeMint.

    Không suy rằng mọi tx thành công của ví migration đều là token mới.
    Nếu có layout IDL, đọc đúng program/discriminator/accounts, không nhầm LP mint.
    """
    result = []
    for record in records:
        tx = record["transaction"]
        keys = tx["transaction"]["message"]["accountKeys"]
        keys = [k["pubkey"] if isinstance(k, dict) else k for k in keys]
        if account not in keys or not any("Instruction: Migrate" in line for line in tx["meta"].get("logMessages", [])):
            continue
        instructions = list(tx["transaction"]["message"]["instructions"])
        for inner in tx["meta"].get("innerInstructions") or []:
            instructions.extend(inner["instructions"])
        mints = sorted({i["parsed"]["info"]["mint"] for i in instructions
                       if isinstance(i.get("parsed"), dict)
                       and i["parsed"].get("type") in {"initializeMint", "initializeMint2"}})
        balance_mints = sorted({b["mint"] for b in tx["meta"].get("postTokenBalances", [])})
        resolved = []
        if settings:
            for instruction in instructions:
                if instruction.get("programId") != settings["program_id"] or not instruction.get("data"):
                    continue
                encoded = base58_decode(instruction["data"])
                for layout in settings["migration_layouts"]:
                    if encoded[:8] != bytes(layout["discriminator"]):
                        continue
                    accounts = instruction["accounts"]
                    if max(layout[k] for k in ("mint_index", "quote_index", "pool_index")) >= len(accounts):
                        continue
                    resolved.append({"token_address": accounts[layout["mint_index"]],
                        "quote_token": accounts[layout["quote_index"]], "pool_address": accounts[layout["pool_index"]],
                        "instruction": layout["name"]})
        unique = {r["pool_address"]: r for r in resolved}
        # Migrate lặp lại có thể thành công mà không tạo pool. Xác nhận CPI CreatePool.
        creation_confirmed = False
        if settings and len(unique) == 1:
            candidate = next(iter(unique.values()))
            for instruction in instructions:
                if instruction.get("programId") != settings["amm_program_id"] or not instruction.get("data"):
                    continue
                if base58_decode(instruction["data"])[:8] != bytes(settings["create_pool_discriminator"]):
                    continue
                accounts = instruction.get("accounts", [])
                if all(candidate[k] in accounts for k in ("pool_address", "token_address", "quote_token")):
                    creation_confirmed = True
        result.append({"chain": "solana", "signature": record["signature"], "block_time": tx["blockTime"],
            "initialized_mints": mints, "balance_mints": balance_mints,
            "status": "resolved_from_idl" if len(unique) == 1 else "needs_pool_and_meme_mint_resolution",
            "resolved": list(unique.values()), "pool_creation_confirmed": creation_confirmed, "source": "helius",
            "collected_at": record["collected_at"], "raw_ref": record["raw_ref"]})
    return result
