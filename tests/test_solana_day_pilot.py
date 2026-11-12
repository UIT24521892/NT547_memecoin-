"""Kiểm tra biên ngày và trường hợp dữ liệu thiếu, không gọi mạng."""
import importlib.util
import unittest
from pathlib import Path
from typing import Any

SPEC = importlib.util.spec_from_file_location(
    "solana_day_pilot", Path(__file__).resolve().parents[1] / "scripts/solana_day_pilot.py"
)
pilot = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(pilot)


class FakeReader:
    def __init__(self, responses: list[Any]) -> None:
        self.responses = iter(responses)
        self.calls: list[tuple[str, list[Any]]] = []

    def call(self, method: str, params: list[Any]) -> Any:
        self.calls.append((method, params))
        value = next(self.responses)
        if isinstance(value, Exception):
            raise value
        return value


def item(signature: str, timestamp: int | None, slot: int = 1) -> dict[str, Any]:
    return {"signature": signature, "blockTime": timestamp, "slot": slot, "err": None}


class DayCoverageTests(unittest.TestCase):
    def test_midnight_boundaries_and_pagination(self) -> None:
        start, end = pilot.day_bounds("2026-11-05")
        reader = FakeReader([
            [item("next_midnight", end), item("late", end - 1)],
            [item("first", start), item("previous_day", start - 1)],
        ])
        result = pilot.scan_day(reader, "pool", start, end, 2, 5)
        self.assertEqual({row["signature"] for row in result["signatures"]}, {"late", "first"})
        self.assertTrue(result["window_bracketed"])
        self.assertEqual(reader.calls[1][1][1]["before"], "late")

    def test_page_limit_and_empty_history_do_not_prove_coverage(self) -> None:
        for responses, pages in [([[item("late", 200)]], 1), ([[]], 5)]:
            with self.subTest(responses=responses):
                result = pilot.scan_day(FakeReader(responses), "pool", 100, 200, 2, pages)
                self.assertFalse(result["window_bracketed"])

    def test_null_time_or_missing_upper_boundary_is_incomplete(self) -> None:
        for page in [
            [item("above", 200), item("unknown", None), item("below", 99)],
            [item("inside", 150), item("below", 99)],
        ]:
            with self.subTest(page=page):
                result = pilot.scan_day(FakeReader([page]), "pool", 100, 200, 10, 5)
                self.assertFalse(result["window_bracketed"])

    def test_repeated_cursor_and_rpc_failure_stop_without_full_coverage(self) -> None:
        repeated = item("same", 200)
        for responses, reason in [
            ([[repeated], [repeated]], "cursor_not_advancing"),
            ([RuntimeError("rate limit")], "rpc_error"),
        ]:
            with self.subTest(reason=reason):
                result = pilot.scan_day(FakeReader(responses), "pool", 100, 200, 1, 5)
                self.assertEqual(result["stop_reason"], reason)
                self.assertFalse(result["window_bracketed"])

    def test_failed_transactions_remain_in_inventory(self) -> None:
        failed = {**item("failed", 150), "err": {"InstructionError": [1, "Custom"]}}
        reader = FakeReader([[item("above", 200), failed, item("below", 99)]])
        result = pilot.scan_day(reader, "pool", 100, 200, 10, 5)
        self.assertEqual(result["signatures"], [failed])

    def test_missing_details_and_download_limit_stay_visible(self) -> None:
        rows = pilot.download_details(FakeReader([None]), [item("missing", 100), item("limited", 110)], 1)
        self.assertEqual([row["detail_status"] for row in rows], ["missing", "not_requested"])

    def test_read_v1_and_preserve_execution_errors(self) -> None:
        failed = {"InstructionError": [1, "Custom"]}
        transaction = {"version": 1, "slot": 1, "blockTime": 100,
                       "meta": {"err": failed, "fee": 25000},
                       "transaction": {"message": {"accountKeys": [{"pubkey": "wallet", "signer": True}]}}}
        reader = FakeReader([transaction])
        rows = pilot.download_details(reader, [item("v1", 100)], 5)
        self.assertEqual(reader.calls[0][1][1]["maxSupportedTransactionVersion"], 1)
        self.assertEqual(rows[0]["detail_status"], "downloaded")
        self.assertEqual(rows[0]["transaction_version"], 1)
        self.assertIn("InstructionError", rows[0]["execution_error"])


if __name__ == "__main__":
    unittest.main()
