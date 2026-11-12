"""Kiểm tra giải mã swap và bảo vệ trước việc nhận nhầm phí/router thành trader."""
from __future__ import annotations

import copy
import importlib.util
import struct
import unittest
from pathlib import Path
from typing import Any

SPEC = importlib.util.spec_from_file_location(
    "solana_decode_pilot", Path(__file__).resolve().parents[1] / "scripts/solana_decode_pilot.py"
)
decode = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(decode)


def encoded_instruction(opcode: int, first: int, second: int) -> str:
    number = int.from_bytes(struct.pack("<BQQ", opcode, first, second), "big")
    text = ""
    while number:
        number, remainder = divmod(number, 58)
        text = decode.BASE58[remainder] + text
    return text


def transfer(source: str, destination: str, amount: int, height: int = 3) -> dict[str, Any]:
    return {"programId": decode.TOKEN_PROGRAM, "stackHeight": height,
            "parsed": {"type": "transfer", "info": {
                "source": source, "destination": destination, "amount": str(amount), "authority": "authority"}}}


def fixture(side: str = "sell", routed: bool = False) -> dict[str, Any]:
    """100 HEGE đổi 0,5 WSOL; fee payer khác chủ HEGE, phí nằm ngoài Raydium CPI."""
    token_amount, quote_amount = 100 * 10**9, 500_000_000
    keys = ["sponsor", "wallet", "user_hege", "user_wsol", "vault_hege", "vault_wsol", "router_hege", "router_wsol"]
    pre = {"user_hege": 200 * 10**9, "user_wsol": 10 * 10**9,
           "vault_hege": 1000 * 10**9, "vault_wsol": 100 * 10**9,
           "router_hege": 0, "router_wsol": 0}
    post = dict(pre)
    direction = -1 if side == "sell" else 1
    post["user_hege"] += direction * token_amount
    post["vault_hege"] -= direction * token_amount
    post["user_wsol"] -= direction * quote_amount
    post["vault_wsol"] += direction * quote_amount

    def balances(values: dict[str, int]) -> list[dict[str, Any]]:
        result = []
        for account, amount in values.items():
            result.append({"accountIndex": keys.index(account),
                           "owner": "amm_authority" if account.startswith("vault") else (
                               "router_authority" if account.startswith("router") else "wallet"),
                           "mint": decode.HEGE if account.endswith("hege") else decode.WSOL,
                           "uiTokenAmount": {"amount": str(amount), "decimals": 9}})
        return result

    token_account = "router_hege" if routed else "user_hege"
    quote_account = "router_wsol" if routed else "user_wsol"
    source, destination = (token_account, quote_account) if side == "sell" else (quote_account, token_account)
    amount_in, amount_out = (token_amount, quote_amount) if side == "sell" else (quote_amount, token_amount)
    instruction = {"programId": decode.RAYDIUM, "stackHeight": 2,
                   "data": encoded_instruction(16, amount_in, amount_out - 1),
                   "accounts": [decode.TOKEN_PROGRAM, decode.POOL, "amm_authority", "vault_hege", "vault_wsol",
                                source, destination, "router_authority" if routed else "wallet"]}
    children = []
    if routed and side == "sell":
        children.append(transfer("user_hege", "router_hege", token_amount, 2))
    children += [instruction,
                 transfer(source, "vault_hege" if side == "sell" else "vault_wsol", amount_in),
                 transfer("vault_wsol" if side == "sell" else "vault_hege", destination, amount_out)]
    if routed and side == "buy":
        children.append(transfer("router_hege", "user_hege", token_amount, 2))
    # Không được cộng 0,01 WSOL của lệnh anh em vào lượng swap 0,5 WSOL.
    children.append(transfer("user_wsol", "fee_account", 10_000_000, 2))
    return {"slot": 1, "blockTime": 1793871470, "version": 1,
            "transaction": {"signatures": ["test_signature"], "message": {
                "accountKeys": [{"pubkey": key, "signer": key in {"sponsor", "wallet"}} for key in keys],
                "instructions": [{"programId": "router_program", "accounts": [], "data": "1"}]}},
            "meta": {"err": None, "fee": 25000, "preTokenBalances": balances(pre),
                     "postTokenBalances": balances(post), "innerInstructions": [{"index": 0, "instructions": children}]}}


class SwapTests(unittest.TestCase):
    def test_buy_sell_and_sponsor_are_not_confused(self) -> None:
        for side in ["buy", "sell"]:
            for routed in [False, True]:
                with self.subTest(side=side, routed=routed):
                    result = decode.decode_transaction(fixture(side, routed))
                    row = result["swaps"][0]
                    self.assertEqual(row["decode_status"], "decoded")
                    self.assertEqual(row["side"], side)
                    self.assertEqual(row["trader"], "wallet")
                    self.assertEqual(row["amount_token"], "100.000000000")
                    self.assertEqual(row["amount_quote"], "0.500000000")
                    self.assertEqual(row["transaction_fee_sol"], "0.000025000")
                    self.assertEqual(sum(flow["scope"] == "swap_leg" for flow in result["flows"]), 2)

    def test_closed_transient_accounts_use_initialization_metadata(self) -> None:
        transaction = fixture("sell", True)
        for field in ["preTokenBalances", "postTokenBalances"]:
            transaction["meta"][field] = [b for b in transaction["meta"][field] if b["accountIndex"] not in {6, 7}]
        children = transaction["meta"]["innerInstructions"][0]["instructions"]
        for account, mint in [("router_hege", decode.HEGE), ("router_wsol", decode.WSOL)]:
            children.insert(0, {"programId": decode.TOKEN_PROGRAM, "stackHeight": 2,
                                "parsed": {"type": "initializeAccount3", "info": {
                                    "account": account, "mint": mint, "owner": "router_authority"}}})
        self.assertEqual(decode.decode_transaction(transaction)["swaps"][0]["trader"], "wallet")

    def test_branching_path_is_not_forced_into_one_trader(self) -> None:
        transaction = fixture("sell", True)
        children = transaction["meta"]["innerInstructions"][0]["instructions"]
        children.insert(0, transfer("other_account", "router_hege", 1, 2))
        row = decode.decode_transaction(transaction)["swaps"][0]
        self.assertEqual(row["decode_status"], "decoded")
        self.assertEqual(row["trader_status"], "unclear")
        self.assertEqual(row["trader"], "")

    def test_non_signing_owner_is_left_unclear(self) -> None:
        transaction = fixture()
        transaction["transaction"]["message"]["accountKeys"][1]["signer"] = False
        row = decode.decode_transaction(transaction)["swaps"][0]
        self.assertEqual(row["trader_status"], "unclear")

    def test_failed_execution_never_produces_a_swap(self) -> None:
        transaction = fixture()
        transaction["meta"]["err"] = {"InstructionError": [0, "Custom"]}
        result = decode.decode_transaction(transaction)
        self.assertEqual(result["swaps"][0]["decode_status"], "failed_execution")
        self.assertNotIn("side", result["swaps"][0])

    def test_unsupported_opcode_and_missing_stack_are_visible(self) -> None:
        for mutation in ["opcode", "height"]:
            with self.subTest(mutation=mutation):
                transaction = fixture()
                children = transaction["meta"]["innerInstructions"][0]["instructions"]
                if mutation == "opcode":
                    children[0]["data"] = encoded_instruction(3, 100 * 10**9, 0)
                else:
                    children[1]["stackHeight"] = None
                self.assertEqual(decode.decode_transaction(transaction)["swaps"][0]["decode_status"], "unclear")

    def test_transfer_amount_must_match_instruction(self) -> None:
        transaction = fixture()
        transaction["meta"]["innerInstructions"][0]["instructions"][1]["parsed"]["info"]["amount"] = "1"
        self.assertEqual(decode.decode_transaction(transaction)["swaps"][0]["decode_status"], "unclear")

    def test_exact_output_variant_uses_actual_input(self) -> None:
        transaction = fixture()
        transaction["meta"]["innerInstructions"][0]["instructions"][0]["data"] = encoded_instruction(
            17, 101 * 10**9, 500_000_000)
        row = decode.decode_transaction(transaction)["swaps"][0]
        self.assertEqual(row["decode_status"], "decoded")
        self.assertEqual(row["amount_token"], "100.000000000")

    def test_two_swaps_in_one_transaction_remain_two_rows(self) -> None:
        transaction = fixture()
        children = transaction["meta"]["innerInstructions"][0]["instructions"]
        children.extend(copy.deepcopy(children[:3]))
        result = decode.decode_transaction(transaction)
        self.assertEqual(len(result["swaps"]), 2)
        self.assertEqual(len({row["swap_id"] for row in result["swaps"]}), 2)
        self.assertTrue(all(row["decode_status"] == "decoded" for row in result["swaps"]))

    def test_balance_change_alone_does_not_imply_swap(self) -> None:
        transaction = fixture()
        transaction["meta"]["innerInstructions"][0]["instructions"].pop(0)
        self.assertEqual(decode.decode_transaction(transaction)["swaps"][0]["decode_status"], "no_supported_swap")

    def test_integer_units_keep_all_digits(self) -> None:
        self.assertEqual(decode.units(18446744073709551615, 9), "18446744073.709551615")


if __name__ == "__main__":
    unittest.main()
