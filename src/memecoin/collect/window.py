"""Liệt kê pool ứng viên theo ngày tạo trên cả cửa sổ (task 2).

Vì sao cần: muốn chọn mẫu không thiên lệch (survivorship bias) thì phải có
tổng thể pool mới tạo, kể cả pool đã chết. Ngày tạo được giới hạn trong 3 tầng
(train/validation/test) suy từ `configs/split.yaml`; Base chọn ngẫu nhiên ngày
vì dRPC free chỉ cho 100 block/lần. Mỗi ngày chạy lại được nhờ cache HttpClient.
"""
from __future__ import annotations

import random
from collections import Counter
from datetime import date, timedelta
from typing import Any

from .common import iso_time, midnight
from .evm import EvmReader, as_int, collect_factory_logs, decode_pool_log
from .http import CollectionError
from .solana import HeliusReader, migration_candidates

FIELDS = ["chain", "pool_address", "token_address", "quote_token", "dex", "version", "hooks", "instruction",
          "created_at", "creation_day", "stratum", "day_sampled_fraction", "token_pool_count",
          "created_tx", "source", "collected_at", "raw_ref", "eligibility"]


def _as_date(value: str | date) -> date:
    return value if isinstance(value, date) else date.fromisoformat(str(value))


def creation_strata(split: dict[str, Any]) -> dict[str, tuple[date, date]]:
    """Khoảng ngày tạo pool [đầu, cuối] (gồm hai đầu) để cutoff có thể rơi vào từng tập."""
    history = int(split["min_history_days"])
    buffer = int(split["discovery"]["late_activation_buffer_days"])
    data_start = _as_date(split["data_start"])
    strata = {}
    for name, bounds in split["sets"].items():
        first = max(data_start, _as_date(bounds["cutoff_start"]) - timedelta(days=history + buffer))
        last = _as_date(bounds["cutoff_end"]) - timedelta(days=history)
        if first > last:
            raise ValueError(f"Tầng {name} rỗng.")
        strata[name] = (first, last)
    ordered = sorted(strata.values())
    if any(a[1] >= b[0] for a, b in zip(ordered, ordered[1:])):
        raise ValueError("Các tầng ngày tạo không được chồng nhau.")
    return strata


def days_between(first: date, last: date) -> list[date]:
    return [first + timedelta(days=i) for i in range((last - first).days + 1)]


def sample_days(strata: dict[str, tuple[date, date]], allocation: dict[str, int] | None,
                seed: int, chain: str) -> dict[str, list[date]]:
    """Không có allocation: lấy mọi ngày. Có: chọn ngẫu nhiên, tái lập theo seed + chuỗi + tầng."""
    chosen = {}
    for name, (first, last) in strata.items():
        days = days_between(first, last)
        if allocation is None:
            chosen[name] = days
            continue
        count = int(allocation[name])
        if not 0 < count <= len(days):
            raise ValueError(f"Số ngày chọn cho {name} phải trong 1..{len(days)}.")
        chosen[name] = sorted(random.Random(f"{seed}:{chain}:{name}").sample(days, count))
    return chosen


def find_block(reader: EvmReader, timestamp: int) -> int:
    """Block cuối có timestamp <= timestamp.

    Ethereum dùng Blockscout getblocknobytime (1 lần gọi). Base đoán vị trí theo
    thời gian block rồi kiểm tra block đó và block kế tiếp, thường 2–4 lần gọi,
    thay vì tìm nhị phân khoảng 26 lần.
    """
    if reader.chain != "base":
        return reader.block_at(timestamp)
    block_time = int(reader.config["block_time_seconds"])

    def stamp(number: int) -> int:
        block = reader.call("eth_getBlockByNumber", [hex(number), False]).data["result"]
        if not block:
            raise CollectionError("RPC không trả block lịch sử.")
        return as_int(block["timestamp"])

    latest = as_int(reader.call("eth_blockNumber", []).data["result"])
    if timestamp >= stamp(latest):
        raise ValueError("Thời điểm chưa có trong block đã biết.")
    guess = latest - (stamp(latest) - timestamp) // block_time
    for _ in range(40):
        current = stamp(guess)
        if current > timestamp:
            guess -= max(1, (current - timestamp) // block_time)
            continue
        following = stamp(guess + 1)
        if following > timestamp:
            return guess
        guess += 1 + (timestamp - following) // block_time
    raise CollectionError("Không tìm được block theo thời gian sau 40 bước.")


def evm_pool_rows(chain: str, logs: list[dict[str, Any]], factories: list[dict[str, Any]],
                  quote_tokens: dict[str, str]) -> list[dict[str, Any]]:
    by_address = {f["address"].lower(): f for f in factories}
    rows = []
    for log in logs:
        row = decode_pool_log(chain, by_address[log["address"].lower()], log, quote_tokens)
        if row:
            rows.append(row)
    return rows


def solana_pool_rows(candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Chỉ migration giải mã được theo IDL và có CPI CreatePool; Migrate lặp lại bị gộp."""
    # dex = PumpSwap AMM (program `amm_program_id` trong chains.yaml), nơi pump.fun migrate sang.
    pools = [{"chain": "solana", "dex": "pumpswap", **c["resolved"][0], "created_at": iso_time(c["block_time"]),
              "created_tx": c["signature"], "source": c["source"], "raw_ref": c["raw_ref"],
              "collected_at": c["collected_at"], "eligibility": "candidate_only_cutoff_and_sampling_pending"}
             for c in candidates if c["status"] == "resolved_from_idl" and c["pool_creation_confirmed"]]
    return list({p["pool_address"]: p for p in pools}.values())


def discover_evm_day(reader: EvmReader, day: date, factories: list[dict[str, Any]],
                     *, max_chunks: int = 10000) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    start = midnight(day)
    left = find_block(reader, start - 1) + 1
    right = find_block(reader, start + 86400 - 1)
    logs, report = collect_factory_logs(reader, left, right, factories, max_chunks=max_chunks)
    rows = evm_pool_rows(reader.chain, logs, factories, reader.config["quote_tokens"])
    counts = Counter(log["address"].lower() for log in logs)
    report.update(from_block=left, to_block=right,
                  logs_by_factory={f["name"]: counts[f["address"].lower()] for f in factories})
    return rows, report


def discover_solana_day(reader: HeliusReader, day: date, settings: dict[str, Any],
                        *, page_size: int = 100, max_pages: int = 50) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    start = midnight(day)
    account = settings["migration_account"]
    records, report = reader.history(account, start, start + 86400, page_size=page_size, max_pages=max_pages)
    candidates = migration_candidates(records, account, settings)
    rows = solana_pool_rows(candidates)
    report.update(migrations=len(candidates), pools_created=len(rows))
    return rows, report


def aggregate(day_rows: dict[date, list[dict[str, Any]]], plan: dict[str, list[date]],
              strata: dict[str, tuple[date, date]]) -> list[dict[str, Any]]:
    """Gộp các ngày: khử trùng theo pool (giữ lần tạo sớm nhất), gắn tầng và xác suất chọn ngày."""
    stratum_of = {d: name for name, days in plan.items() for d in days}
    fraction = {name: len(plan[name]) / len(days_between(*strata[name])) for name in plan}
    merged: dict[tuple[str, str], dict[str, Any]] = {}
    for day in sorted(day_rows):
        for row in day_rows[day]:
            key = (row["chain"], row["pool_address"])
            if key in merged:
                continue
            name = stratum_of[day]
            merged[key] = dict(row, creation_day=day.isoformat(), stratum=name,
                               day_sampled_fraction=round(fraction[name], 6))
    per_token = Counter((r["chain"], r["token_address"]) for r in merged.values())
    for row in merged.values():
        row["token_pool_count"] = per_token[(row["chain"], row["token_address"])]
    return sorted(merged.values(), key=lambda r: (r["creation_day"], r.get("created_at") or "", r["pool_address"]))


def token_is_new(reader: EvmReader, token: str, creation_day: date, max_age_days: int) -> tuple[bool | None, dict[str, Any]]:
    """Token có được tạo không sớm hơn `max_age_days` trước ngày tạo pool không.

    Chỉ dùng thông tin có tại lúc tạo pool (không rò rỉ). Trả None khi nguồn không có
    bản ghi; người gọi phải coi None là "chưa xác minh", không mặc định là mới.
    """
    threshold = midnight(creation_day) - max_age_days * 86400
    if reader.chain == "ethereum":
        created, evidence = reader.contract_creation_time(token)
        if created is None:
            return None, dict(evidence, reason="no_creation_record")
        return created >= threshold, dict(evidence, created_at=iso_time(created), method="getcontractcreation")
    block = find_block(reader, threshold - 1)
    existed, raw_ref = reader.code_exists_at(token, block)
    return not existed, {"raw_ref": raw_ref, "checked_block": block, "method": "eth_getCode",
                         "checked_at": iso_time(threshold - 1)}
