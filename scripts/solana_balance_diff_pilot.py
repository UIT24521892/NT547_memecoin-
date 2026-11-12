"""Thử nghiệm: đọc swap Solana bằng cách so số dư trước/sau (không phụ thuộc sàn).

Cách làm (PLAN Mục 6, "Cách đọc swap Solana"):
1. Gộp thay đổi số dư token (post - pre) theo chủ ví (owner) cho mint meme và mint quote.
2. Phía pool = chủ ví giữ nhiều token meme nhất trong giao dịch (kho của pool).
   Thay đổi của nó cho lượng meme/quote thực sự qua pool.
3. Pool mất meme => người dùng MUA; pool nhận meme => người dùng BÁN.
4. Trader = chủ ví khác có thay đổi meme ròng ngược dấu và bằng đúng lượng qua pool,
   ưu tiên ví có ký. Không tìm được thì để trống và ghi `unclear`, không đoán.

Chỉ đọc file đã lưu trong data/raw/, không gọi mạng. Đây là bài thử, chưa phải collector.
Lượng token dùng số nguyên (chuỗi raw) để không mất chính xác.
"""
from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from decimal import Decimal
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
WSOL = "So11111111111111111111111111111111111111112"
HEGE = "ULwSJmmpxmnRfpu6BjnK6rprKXqD5jXUmPpS1FxHXFy"


def account_keys(tx: dict[str, Any]) -> list[str]:
    """Danh sách địa chỉ theo đúng thứ tự accountIndex (gồm cả địa chỉ nạp từ lookup table)."""
    keys = tx["transaction"]["message"]["accountKeys"]
    out = [k["pubkey"] if isinstance(k, dict) else k for k in keys]
    loaded = tx["meta"].get("loadedAddresses") or {}
    return out + list(loaded.get("writable", [])) + list(loaded.get("readonly", []))


def signers(tx: dict[str, Any]) -> list[str]:
    """Các ví ký giao dịch (chỉ có khi encoding jsonParsed)."""
    keys = tx["transaction"]["message"]["accountKeys"]
    return [k["pubkey"] for k in keys if isinstance(k, dict) and k.get("signer")]


def token_deltas(tx: dict[str, Any], mint: str) -> tuple[dict[str, int], dict[str, int], int]:
    """Trả (thay đổi ròng theo owner, số dư trước theo owner, decimals) cho một mint.

    Tài khoản token mở rồi đóng ngay trong giao dịch không xuất hiện ở pre/post,
    nên không làm sai tổng: phần đó chỉ là trung gian.
    """
    meta = tx["meta"]
    before: dict[int, tuple[str, int]] = {}
    after: dict[int, tuple[str, int]] = {}
    decimals = 0
    for rows, target in ((meta.get("preTokenBalances") or [], before), (meta.get("postTokenBalances") or [], after)):
        for row in rows:
            if row["mint"] != mint:
                continue
            decimals = int(row["uiTokenAmount"]["decimals"])
            target[row["accountIndex"]] = (row.get("owner") or "", int(row["uiTokenAmount"]["amount"]))
    delta: dict[str, int] = defaultdict(int)
    held_before: dict[str, int] = defaultdict(int)
    for idx in set(before) | set(after):
        owner = (after.get(idx) or before.get(idx))[0]
        pre = before.get(idx, ("", 0))[1]
        post = after.get(idx, ("", 0))[1]
        delta[owner] += post - pre
        held_before[owner] += pre
    return dict(delta), dict(held_before), decimals


def ui(raw: int, decimals: int) -> str:
    """Đổi số nguyên raw sang chuỗi thập phân, không qua float."""
    return format(Decimal(raw).scaleb(-decimals).normalize(), "f") if raw else "0"


def decode_balance_diff(tx: dict[str, Any], token_mint: str, quote_mint: str = WSOL) -> dict[str, Any]:
    """Suy ra một dòng swap từ chênh lệch số dư. Không ném lỗi: trường hợp khó ghi vào `status`."""
    result: dict[str, Any] = {"status": "ok", "side": None, "trader": None, "trader_status": "unclear",
                              "amount_token_raw": None, "amount_quote_raw": None, "pool_owner": None}
    if tx["meta"].get("err") is not None:
        result["status"] = "execution_failed"
        return result
    meme_delta, meme_held, meme_dec = token_deltas(tx, token_mint)
    quote_delta, _, quote_dec = token_deltas(tx, quote_mint)
    if not meme_held:
        result["status"] = "no_token_balance"
        return result

    pool_owner = max(meme_held, key=lambda o: meme_held[o])
    pool_meme = meme_delta.get(pool_owner, 0)
    pool_quote = quote_delta.get(pool_owner, 0)
    result["pool_owner"] = pool_owner
    if pool_meme == 0:
        result["status"] = "pool_meme_unchanged"
        return result
    if pool_quote == 0 or (pool_meme > 0) == (pool_quote > 0):
        # Pool nhận cả hai hoặc mất cả hai: thêm/rút thanh khoản hoặc giao dịch phức tạp, không phải swap đơn.
        result["status"] = "not_simple_swap"
        return result

    result["side"] = "buy" if pool_meme < 0 else "sell"
    amount = abs(pool_meme)
    result["amount_token_raw"] = str(amount)
    result["amount_quote_raw"] = str(abs(pool_quote))
    result["amount_token"] = ui(amount, meme_dec)
    result["amount_quote"] = ui(abs(pool_quote), quote_dec)

    # Trader: ví khác có thay đổi meme ròng = -pool_meme (đúng chiều, đúng lượng).
    exact = [o for o, d in meme_delta.items() if o != pool_owner and d == -pool_meme]
    signed = set(signers(tx))
    exact_signed = [o for o in exact if o in signed]
    if len(exact_signed) == 1:
        result["trader"], result["trader_status"] = exact_signed[0], "exact_signer"
    elif len(exact) == 1:
        result["trader"], result["trader_status"] = exact[0], "exact_not_signer"
    elif len(exact) > 1:
        result["trader_status"] = "multiple_candidates"
    else:
        result["trader_status"] = "no_exact_match"   # vd: meme đi tiếp sang pool/ví khác trong cùng giao dịch
    return result


def load_tx(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    return data.get("result", data)


def compare_with_raydium(run_dir: Path, interim_dir: Path) -> list[dict[str, Any]]:
    """So kết quả với swaps.csv của bộ đọc Raydium (đã có) trên cùng giao dịch."""
    reference = {r["signature"]: r for r in csv.DictReader((interim_dir / "swaps.csv").open(encoding="utf-8"))}
    by_sig: dict[str, Path] = {}
    for p in (run_dir / "rpc").glob("*.json"):
        if p.name.endswith((".request.json", ".meta.json")):
            continue
        tx = load_tx(p)
        if isinstance(tx, dict) and "transaction" in tx:
            by_sig[tx["transaction"]["signatures"][0]] = p
    rows = []
    for sig, ref in reference.items():
        got = decode_balance_diff(load_tx(by_sig[sig]), HEGE)
        rows.append({
            "signature": sig,
            "status": got["status"],
            "side_match": got["side"] == ref["side"],
            "token_match": got.get("amount_token") is not None and Decimal(got["amount_token"]) == Decimal(ref["amount_token"]),
            "quote_match": got.get("amount_quote") is not None and Decimal(got["amount_quote"]) == Decimal(ref["amount_quote"]),
            "trader_match": got["trader"] == ref["trader"],
            "trader_status": got["trader_status"],
            "side": got["side"], "amount_token": got.get("amount_token"), "amount_quote": got.get("amount_quote"),
            "trader": got["trader"], "ref_trader": ref["trader"],
        })
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--run", default="run_20261106T155457_437217Z")
    parser.add_argument("--day", default="2026-11-05")
    args = parser.parse_args()
    run_dir = ROOT / "data/raw/solana_day_pilot" / args.day / args.run
    interim_dir = ROOT / "data/interim/solana_day_pilot" / args.day / args.run
    rows = compare_with_raydium(run_dir, interim_dir)
    out = interim_dir / "balance_diff_vs_raydium.csv"
    with out.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    keys = ("side_match", "token_match", "quote_match", "trader_match")
    print(f"{len(rows)} giao dịch; " + ", ".join(f"{k}: {sum(r[k] for r in rows)}/{len(rows)}" for k in keys))
    for r in rows:
        if not all(r[k] for k in keys):
            print(f"  lệch {r['signature'][:10]}…: status={r['status']} trader_status={r['trader_status']} "
                  f"trader={str(r['trader'])[:8]} ref={r['ref_trader'][:8]}")
    print(f"Ghi: {out.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
