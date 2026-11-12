"""Bước 3: đọc swap Raydium của HEGE từ JSON đã lưu, không gọi mạng.

Chỉ hỗ trợ Raydium AMM SwapBaseInV2/SwapBaseOutV2 (opcode 16/17).
Mỗi dòng ứng với một lệnh swap của pool, không phải toàn bộ tuyến đổi token.
Chạy: python3 scripts/solana_decode_pilot.py --day 2026-11-05
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
HEGE = "ULwSJmmpxmnRfpu6BjnK6rprKXqD5jXUmPpS1FxHXFy"
WSOL = "So11111111111111111111111111111111111111112"
POOL = "CJcu7ciRHBHu4BDnpLgAUm1A6iSp9RuhJMG36rjjrxnd"
RAYDIUM = "675kPX9MHTjS2zt1qfr1NYHuzeLXfQM9H24wFSUt1Mp8"
TOKEN_PROGRAM = "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"
SYSTEM_PROGRAM = "11111111111111111111111111111111"
BASE58 = "123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz"


class Unclear(ValueError):
    """Dữ liệu/chỉ dẫn chưa đủ rõ: xuất trạng thái thay vì đoán."""


def units(raw: int, decimals: int) -> str:
    """Đặt dấu thập phân bằng số nguyên, không mất chính xác do float."""
    if decimals < 0:
        raise Unclear("decimals âm")
    sign = "-" if raw < 0 else ""
    digits = str(abs(raw)).zfill(decimals + 1)
    return sign + (digits if not decimals else digits[:-decimals] + "." + digits[-decimals:])


def base58_bytes(value: str) -> bytes:
    number = 0
    for character in value:
        if character not in BASE58:
            raise Unclear("Instruction data không phải base58 hợp lệ")
        number = number * 58 + BASE58.index(character)
    leading = len(value) - len(value.lstrip("1"))
    return b"\0" * leading + number.to_bytes((number.bit_length() + 7) // 8, "big")


def execution_events(transaction: dict[str, Any]) -> list[dict[str, Any]]:
    """Xen inner instructions ngay sau lệnh cha để giữ thứ tự thực thi."""
    groups = {group["index"]: group["instructions"] for group in transaction["meta"].get("innerInstructions", [])}
    events: list[dict[str, Any]] = []
    for outer, instruction in enumerate(transaction["transaction"]["message"]["instructions"]):
        events.append({"instruction": instruction, "outer": outer, "height": 1, "path": f"outer:{outer}"})
        for inner, child in enumerate(groups.get(outer, [])):
            events.append({"instruction": child, "outer": outer, "height": child.get("stackHeight"),
                           "path": f"outer:{outer}/inner:{inner}"})
    for position, event in enumerate(events):
        event["position"] = position
    return events


def token_metadata(
    transaction: dict[str, Any], events: list[dict[str, Any]],
) -> tuple[dict[str, dict[str, str]], dict[str, int], dict[str, int]]:
    """Ghép mint/owner từ số dư và lệnh khởi tạo, kể cả account tạo rồi đóng."""
    keys = transaction["transaction"]["message"]["accountKeys"]
    accounts: dict[str, dict[str, str]] = {}
    decimals: dict[str, int] = {}
    owner_net: dict[str, int] = defaultdict(int)

    def merge(address: str, values: dict[str, str]) -> None:
        target = accounts.setdefault(address, {})
        for field, value in values.items():
            if value:
                if field in target and target[field] != value:
                    raise Unclear(f"Metadata {field} thay đổi cho token account {address}")
                target[field] = value

    for field, sign in [("preTokenBalances", -1), ("postTokenBalances", 1)]:
        if field not in transaction["meta"]:
            raise Unclear(f"Thiếu {field}")
        for balance in transaction["meta"][field]:
            key = keys[balance["accountIndex"]]
            address = key["pubkey"] if isinstance(key, dict) else key
            mint = balance["mint"]
            amount = balance["uiTokenAmount"]
            merge(address, {"mint": mint, "owner": balance.get("owner", "")})
            if mint in decimals and decimals[mint] != amount["decimals"]:
                raise Unclear("Số decimals không nhất quán")
            decimals[mint] = amount["decimals"]
            if mint == HEGE and balance.get("owner"):
                owner_net[balance["owner"]] += sign * int(amount["amount"])
    for event in events:
        instruction = event["instruction"]
        parsed = instruction.get("parsed", {})
        if instruction.get("programId") == TOKEN_PROGRAM:
            info = parsed.get("info", {})
            if parsed.get("type") in {"initializeAccount", "initializeAccount2", "initializeAccount3"}:
                merge(info["account"], {"mint": info["mint"], "owner": info["owner"]})
            if parsed.get("type") == "setAuthority":
                raise Unclear("Có thay đổi authority trong giao dịch; pilot chưa hỗ trợ")
    return accounts, decimals, dict(owner_net)


def transfer_flows(
    events: list[dict[str, Any]], accounts: dict[str, dict[str, str]], decimals: dict[str, int],
) -> list[dict[str, Any]]:
    """Ghi các chuyển SPL token và SOL riêng; không tự gọi chuyển ngoài swap là phí."""
    flows: list[dict[str, Any]] = []
    for event in events:
        instruction = event["instruction"]
        parsed = instruction.get("parsed", {})
        kind, info = parsed.get("type"), parsed.get("info", {})
        program = instruction.get("programId")
        if program == TOKEN_PROGRAM and kind in {"transfer", "transferChecked"}:
            source, destination = info["source"], info["destination"]
            source_meta, destination_meta = accounts.get(source, {}), accounts.get(destination, {})
            mints = {mint for mint in [source_meta.get("mint"), destination_meta.get("mint"), info.get("mint")] if mint}
            if len(mints) != 1:
                raise Unclear("Chưa xác định duy nhất mint của một SPL transfer")
            mint = mints.pop()
            raw = int(info["amount"] if kind == "transfer" else info["tokenAmount"]["amount"])
            if kind == "transferChecked":
                checked_decimals = info["tokenAmount"]["decimals"]
                if mint in decimals and decimals[mint] != checked_decimals:
                    raise Unclear("decimals của transferChecked không khớp số dư")
                decimals[mint] = checked_decimals
            flows.append({"position": event["position"], "path": event["path"], "kind": "spl_transfer",
                          "mint": mint, "raw": raw, "source": source, "destination": destination,
                          "source_owner": source_meta.get("owner", ""), "destination_owner": destination_meta.get("owner", "")})
        elif program == SYSTEM_PROGRAM and kind == "transfer":
            flows.append({"position": event["position"], "path": event["path"], "kind": "native_sol_transfer",
                          "mint": "native_SOL", "raw": int(info["lamports"]),
                          "source": info["source"], "destination": info["destination"],
                          "source_owner": "", "destination_owner": ""})
    return flows


def trace_token_owner(
    token_flow: dict[str, Any], side: str, flows: list[dict[str, Any]],
    accounts: dict[str, dict[str, str]], owner_net: dict[str, int], signers: set[str],
) -> tuple[str, list[str], str]:
    """Lần HEGE qua đường đơn, rồi kiểm tra chủ ví có net change và chữ ký khớp."""
    address = token_flow["source" if side == "sell" else "destination"]
    position = token_flow["position"]
    wanted_net = token_flow["raw"] * (-1 if side == "sell" else 1)
    path = [token_flow["path"]]
    visited: set[str] = set()
    for _ in range(8):
        if address in visited:
            return "", path, "Đường token tạo vòng; chưa xác định chủ ví"
        visited.add(address)
        owner = accounts.get(address, {}).get("owner", "")
        if owner and owner in signers and owner_net.get(owner) == wanted_net:
            return owner, path, "Chủ tài khoản HEGE trên đường chuyển có net change khớp và ký giao dịch"
        candidates = [flow for flow in flows if flow["mint"] == HEGE and (
            (side == "sell" and flow["destination"] == address and flow["position"] < position)
            or (side == "buy" and flow["source"] == address and flow["position"] > position)
        )]
        if len(candidates) != 1 or candidates[0]["raw"] != token_flow["raw"]:
            return "", path, "Đường token rẽ nhánh, khác lượng hoặc chủ ví chưa đủ bằng chứng"
        flow = candidates[0]
        address = flow["source" if side == "sell" else "destination"]
        position = flow["position"]
        path.append(flow["path"])
    return "", path, "Đạt giới hạn 8 bước lần token"


def swap_children(events: list[dict[str, Any]], position: int) -> list[dict[str, Any]]:
    """Chỉ lấy lệnh con thuộc đúng lời gọi Raydium, không lấy lệnh anh em của router."""
    parent = events[position]
    if parent["height"] is None:
        raise Unclear("Thiếu stackHeight của Raydium invocation")
    children: list[dict[str, Any]] = []
    for child in events[position + 1:]:
        if child["outer"] != parent["outer"]:
            break
        if child["height"] is None:
            raise Unclear("Thiếu stackHeight trong các lệnh con")
        if child["height"] <= parent["height"]:
            break
        children.append(child)
    return children


def decode_swap(
    event: dict[str, Any], events: list[dict[str, Any]], flows: list[dict[str, Any]],
    accounts: dict[str, dict[str, str]], decimals: dict[str, int], owner_net: dict[str, int],
    signers: set[str],
) -> tuple[dict[str, Any], dict[str, Any]]:
    instruction = event["instruction"]
    data = base58_bytes(instruction.get("data", ""))
    ac = instruction.get("accounts", [])
    if len(data) != 17 or data[0] not in {16, 17} or len(ac) != 8 or ac[0] != TOKEN_PROGRAM:
        raise Unclear("Chưa hỗ trợ opcode/layout Raydium này; pilot chỉ đọc 16/17, 8 accounts")
    vaults = ac[3:5]
    if {accounts.get(vault, {}).get("mint") for vault in vaults} != {HEGE, WSOL}:
        raise Unclear("Hai vault chưa xác định đúng cặp HEGE/WSOL")
    if any(accounts.get(vault, {}).get("owner") != ac[2] for vault in vaults):
        raise Unclear("Chủ vault không khớp AMM authority")
    positions = {child["position"] for child in swap_children(events, event["position"])}
    scoped = [flow for flow in flows if flow["position"] in positions]
    # SPL token CPI chưa được node parse cũng có thể chứa chuyển tiền: không bỏ qua.
    for child in events:
        ins = child["instruction"]
        if child["position"] in positions and ins.get("programId") == TOKEN_PROGRAM:
            if ins.get("parsed", {}).get("type") not in {"transfer", "transferChecked"}:
                raise Unclear("Có lệnh token con chưa hỗ trợ trong swap")
    if len(scoped) != 2 or any(flow["kind"] != "spl_transfer" for flow in scoped):
        raise Unclear("Không có đúng hai SPL transfer trong lời gọi swap")
    incoming = [flow for flow in scoped if flow["source"] == ac[5] and flow["destination"] in vaults]
    outgoing = [flow for flow in scoped if flow["source"] in vaults and flow["destination"] == ac[6]]
    if len(incoming) != 1 or len(outgoing) != 1:
        raise Unclear("Không ghép được hai chân vào/ra của pool")
    paid, received = incoming[0], outgoing[0]
    if paid["destination"] == received["source"] or {paid["mint"], received["mint"]} != {HEGE, WSOL}:
        raise Unclear("Hai chân swap không đổi hai tài sản khác nhau")
    first, second = int.from_bytes(data[1:9], "little"), int.from_bytes(data[9:17], "little")
    valid_amounts = (paid["raw"] == first and received["raw"] >= second) if data[0] == 16 else (
        paid["raw"] <= first and received["raw"] == second)
    if not valid_amounts or min(paid["raw"], received["raw"]) <= 0:
        raise Unclear("Lượng chuyển không khớp amount/bound của instruction")
    if HEGE not in decimals or WSOL not in decimals:
        raise Unclear("Thiếu decimals để đổi đơn vị")
    side = "sell" if paid["mint"] == HEGE else "buy"
    token_flow, quote_flow = (paid, received) if side == "sell" else (received, paid)
    trader, trace, basis = trace_token_owner(token_flow, side, flows, accounts, owner_net, signers)
    row = {"side": side, "amount_token": units(token_flow["raw"], decimals[HEGE]),
           "amount_quote": units(quote_flow["raw"], decimals[WSOL]), "quote_symbol": "WSOL",
           "trader": trader, "trader_status": "identified" if trader else "unclear",
           "trader_basis": basis, "pool_input_owner": paid["source_owner"],
           "pool_output_owner": received["destination_owner"], "opcode": data[0], "decode_status": "decoded"}
    proof = {"invocation_path": event["path"], "input_transfer": paid, "output_transfer": received,
             "token_owner_trace_paths": trace, "trader_net_token_raw": owner_net.get(trader) if trader else None}
    return row, proof


def decode_transaction(transaction: dict[str, Any], pool: str = POOL) -> dict[str, Any]:
    """Trả các swap riêng, luồng chuyển và bằng chứng; mọi ca chưa rõ vẫn có dòng."""
    signature = transaction["transaction"]["signatures"][0]
    keys = transaction["transaction"]["message"]["accountKeys"]
    signers = {key["pubkey"] for key in keys if isinstance(key, dict) and key.get("signer")}
    meta = transaction.get("meta")
    base = {"signature": signature, "time_utc": datetime.fromtimestamp(transaction["blockTime"], timezone.utc).isoformat(),
            "pool_address": pool, "token_address": HEGE, "transaction_signers": "|".join(sorted(signers)),
            "transaction_fee_sol": units(meta["fee"], 9) if meta else "",
            "explorer_url": f"https://solscan.io/tx/{signature}", "manual_status": "pending"}
    if not meta or meta.get("err") is not None:
        return {"swaps": [{**base, "decode_status": "missing_meta" if not meta else "failed_execution"}], "flows": [], "evidence": []}
    try:
        events = execution_events(transaction)
        accounts, decimals, owner_net = token_metadata(transaction, events)
        flows = transfer_flows(events, accounts, decimals)
    except (Unclear, KeyError, IndexError, TypeError, ValueError) as exc:
        return {"swaps": [{**base, "decode_status": "unclear", "note": str(exc)}], "flows": [], "evidence": []}
    rows, evidence = [], []
    for event in events:
        instruction = event["instruction"]
        if instruction.get("programId") != RAYDIUM or pool not in instruction.get("accounts", []):
            continue
        row = {**base, "swap_id": f"{signature}:{event['path']}", "instruction_path": event["path"]}
        try:
            if instruction["accounts"][1] != pool:
                raise Unclear("Địa chỉ pool không ở vị trí AMM account")
            decoded, proof = decode_swap(event, events, flows, accounts, decimals, owner_net, signers)
            row.update(decoded)
            evidence.append({"swap_id": row["swap_id"], **proof})
            for flow in flows:
                if flow["path"] in {proof["input_transfer"]["path"], proof["output_transfer"]["path"]}:
                    flow["swap_id"] = row["swap_id"]
        except (Unclear, KeyError, IndexError, TypeError, ValueError) as exc:
            row.update(decode_status="unclear", note=str(exc))
        rows.append(row)
    if not rows:
        rows.append({**base, "decode_status": "no_supported_swap", "note": "Không thấy lời gọi Raydium hỗ trợ cho pool chọn"})
    for flow in flows:
        flow["signature"] = signature
        flow["scope"] = "swap_leg" if flow.get("swap_id") else "outside_decoded_swap"
        places = 9 if flow["mint"] == "native_SOL" else decimals.get(flow["mint"])
        flow["amount"] = units(flow["raw"], places) if places is not None else ""
    return {"swaps": rows, "flows": flows, "evidence": evidence}


def write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def choose_run(day: str) -> Path:
    """Chọn lần thu gần nhất có manifest báo lấy được cửa sổ và chi tiết."""
    folder = ROOT / "data/raw/solana_day_pilot" / day
    for run in sorted(folder.glob("run_*"), reverse=True):
        manifests = sorted(run.glob("manifest_*.json"), reverse=True)
        if manifests and json.loads(manifests[0].read_text()).get("provider_window_retrieved"):
            return run
    raise ValueError("Chưa có lần thu thành công; chạy solana_day_pilot.py trước hoặc chỉ định --run-dir.")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--day", default="2026-11-05")
    parser.add_argument("--run-dir", type=Path, help="Thư mục raw của một lần thu; mặc định chọn lần thành công mới nhất")
    args = parser.parse_args()
    try:
        run = (args.run_dir or choose_run(args.day)).resolve()
        config = json.loads((run / "config.json").read_text())
        if config["day_utc"] != args.day or config["pool"] != POOL:
            parser.error("Pilot chỉ hỗ trợ pool HEGE/SOL này; ngày phải khớp config của lần thu.")
        output = ROOT / "data/interim/solana_day_pilot" / args.day / run.name
        # Kiểm kê đầu vào giúp không quên giao dịch tải thiếu hoặc không có cache.
        with (output / "transactions.csv").open() as stream:
            inventory = list(csv.DictReader(stream))
    except (OSError, ValueError, KeyError) as exc:
        parser.error(str(exc))
    cache: dict[str, Path] = {}
    for request_file in sorted((run / "rpc").glob("*.request.json")):
        request = json.loads(request_file.read_text())["request"]
        if request["method"] == "getTransaction":
            response_file = request_file.with_name(request_file.name.replace(".request.json", ".json"))
            if response_file.exists():
                cache[request["params"][0]] = response_file
    swaps, flows, evidence = [], [], []
    for item in inventory:
        source = cache.get(item["signature"])
        if source is None:
            swaps.append({"signature": item["signature"], "time_utc": item["time_utc"],
                          "decode_status": "missing_raw", "manual_status": "pending"})
            continue
        content = source.read_bytes()
        transaction = json.loads(content)["result"]
        if not transaction or transaction["transaction"]["signatures"][0] != item["signature"]:
            swaps.append({"signature": item["signature"], "decode_status": "raw_signature_mismatch", "manual_status": "pending"})
            continue
        result = decode_transaction(transaction)
        for row in result["swaps"]:
            row["source_json"] = str(source.relative_to(ROOT)) if source.is_relative_to(ROOT) else str(source)
            row["source_sha256"] = hashlib.sha256(content).hexdigest()
        swaps.extend(result["swaps"])
        flows.extend(result["flows"])
        evidence.extend(result["evidence"])
    fields = ["time_utc", "signature", "swap_id", "side", "trader", "trader_status", "amount_token",
              "amount_quote", "quote_symbol", "decode_status", "pool_input_owner", "pool_output_owner",
              "transaction_signers", "transaction_fee_sol", "opcode", "instruction_path", "trader_basis",
              "pool_address", "token_address", "explorer_url", "manual_status", "note", "source_json", "source_sha256"]
    write_csv(output / "swaps.csv", swaps, fields)
    write_csv(output / "token_flows.csv", flows, ["signature", "path", "position", "kind", "mint", "amount",
              "raw", "source", "destination", "source_owner", "destination_owner", "scope", "swap_id"])
    (output / "swap_evidence.json").write_text(json.dumps(evidence, ensure_ascii=False, indent=2) + "\n")
    decoded = [row for row in swaps if row.get("decode_status") == "decoded"]
    summary = {"raw_dir": str(run), "input_transactions": len(inventory), "output_rows": len(swaps),
               "decoded_pool_swaps": len(decoded), "buy_count": sum(row["side"] == "buy" for row in decoded),
               "sell_count": sum(row["side"] == "sell" for row in decoded),
               "trader_identified": sum(row["trader_status"] == "identified" for row in decoded),
               "status_counts": dict(Counter(row["decode_status"] for row in swaps)),
               "network_requests": 0, "manual_validation": "pending",
               "scope": "Chỉ hai chân swap Raydium opcode 16/17; trader là chủ HEGE trên đường token, chưa xác minh người hưởng lợi hay danh tính."}
    (output / "swap_decode_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    print(f"Bảng mua/bán: {output / 'swaps.csv'}")
    return 0 if len(decoded) == len(swaps) and len(swaps) > 0 else 2


if __name__ == "__main__":
    raise SystemExit(main())
