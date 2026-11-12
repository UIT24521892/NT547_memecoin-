"""Thử thu giao dịch tham chiếu một pool Solana trong một ngày UTC.

Chỉ đọc RPC công khai, lưu phản hồi gốc và bảng kiểm kê để học/đối chiếu.
Chưa giải mã swap: một giao dịch tham chiếu pool có thể có nhiều thao tác.
Chạy: python3 scripts/solana_day_pilot.py --day 2026-11-05
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import subprocess
import time
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Protocol

ROOT = Path(__file__).resolve().parent.parent
RPC_URL = "https://api.mainnet-beta.solana.com"
HEGE_POOL = "CJcu7ciRHBHu4BDnpLgAUm1A6iSp9RuhJMG36rjjrxnd"


class Reader(Protocol):
    def call(self, method: str, params: list[Any]) -> Any: ...


def utc_now() -> str:
    """Ghi thời gian có múi giờ để tránh nhầm UTC với giờ Việt Nam."""
    return datetime.now(timezone.utc).isoformat()


def write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def day_bounds(day: str) -> tuple[int, int]:
    """Ngày UTC là khoảng [00:00 ngày chọn, 00:00 ngày kế tiếp)."""
    start = datetime.combine(date.fromisoformat(day), datetime.min.time(), timezone.utc)
    return int(start.timestamp()), int((start + timedelta(days=1)).timestamp())


class PublicRpc:
    """RPC chỉ đọc: cache theo yêu cầu, nghỉ giữa request, retry có giới hạn."""

    def __init__(self, folder: Path, delay: float = 3, offline: bool = False) -> None:
        self.folder = folder
        self.folder.mkdir(parents=True, exist_ok=True)
        self.delay = delay
        self.offline = offline
        self.network_requests = 0
        self.cache_hits = 0
        self.last_request = 0.0

    def call(self, method: str, params: list[Any]) -> Any:
        if method not in {"getSignaturesForAddress", "getTransaction"}:
            raise ValueError("Bài thử chỉ cho phép hai phương thức đọc lịch sử.")
        body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params})
        key = hashlib.sha256(body.encode()).hexdigest()
        cache_file = self.folder / f"{key}.json"
        if cache_file.exists():
            self.cache_hits += 1
            return json.loads(cache_file.read_text(encoding="utf-8"))["result"]
        if self.offline:
            raise RuntimeError(f"Chưa có cache cho {method}; chế độ offline không gọi mạng.")

        # Không ghi đè request/phản hồi cũ; các lần retry có file riêng.
        request_file = self.folder / f"{key}.request.json"
        if not request_file.exists():
            write_json(request_file, {"url": RPC_URL, "request": json.loads(body), "created_at_utc": utc_now()})
        for attempt in range(4):
            time.sleep(max(0, self.delay - (time.monotonic() - self.last_request)))
            self.network_requests += 1
            self.last_request = time.monotonic()
            # Dùng curl có sẵn trên máy, truyền body qua stdin; không dùng shell.
            result = subprocess.run(
                ["curl", "--silent", "--show-error", "--max-time", "30", RPC_URL,
                 "-H", "Content-Type: application/json", "--data-binary", "@-",
                 "--write-out", "\n%{http_code}"],
                input=body.encode(), capture_output=True, check=False,
            )
            response_body, _, status_bytes = result.stdout.rpartition(b"\n")
            status = int(status_bytes) if status_bytes.isdigit() else 0
            raw_file = self.folder / f"{key}.attempt-{time.time_ns()}.body"
            raw_file.write_bytes(response_body)
            write_json(raw_file.with_suffix(".meta.json"), {
                "received_at_utc": utc_now(), "http_status": status,
                "curl_exit": result.returncode, "stderr": result.stderr.decode(errors="replace"),
            })
            try:
                payload = json.loads(response_body)
            except (ValueError, UnicodeDecodeError):
                payload = {}
            if result.returncode == 0 and status == 200 and "result" in payload and "error" not in payload:
                # Bản cache giữ đúng bytes phản hồi; không làm tròn hoặc sửa JSON.
                if payload["result"] is not None:
                    with cache_file.open("xb") as stream:
                        stream.write(response_body)
                return payload["result"]
            rpc_error = payload.get("error") if isinstance(payload, dict) else None
            can_retry = result.returncode != 0 or status == 429 or status >= 500 or (
                isinstance(rpc_error, dict) and rpc_error.get("code") == -32005
            )
            if not can_retry or attempt == 3:
                raise RuntimeError(f"{method}: HTTP {status}, curl={result.returncode}, RPC={rpc_error}")
            wait_seconds = min(60, (30 if status == 429 else 5) * 2**attempt)
            print(f"  Tạm nghỉ {wait_seconds}s rồi thử lại ({method}, HTTP {status}).", flush=True)
            time.sleep(wait_seconds)
        raise RuntimeError("Không nhận được phản hồi RPC.")


def scan_day(
    reader: Reader, pool: str, start: int, end: int, page_size: int, max_pages: int,
) -> dict[str, Any]:
    """Lùi theo cursor, giữ cả giao dịch lỗi; chưa phân loại giao dịch là swap."""
    selected: dict[str, dict[str, Any]] = {}
    all_seen: set[str] = set()
    before: str | None = None
    state: dict[str, Any] = {
        "pages": 0, "signatures_scanned": 0, "unknown_timestamps": 0,
        "upper_boundary_observed": False, "lower_boundary_crossed": False,
        "stop_reason": "max_pages", "scan_error": None,
    }
    for _ in range(max_pages):
        options: dict[str, Any] = {"limit": page_size, "commitment": "finalized"}
        if before:
            options["before"] = before
        try:
            page = reader.call("getSignaturesForAddress", [pool, options])
            if not isinstance(page, list):
                raise RuntimeError("RPC trả danh sách không hợp lệ.")
        except RuntimeError as exc:
            state.update(stop_reason="rpc_error", scan_error=str(exc))
            break
        state["pages"] += 1
        if not page:
            # Hết kết quả của node chưa chứng minh lịch sử chưa từng bị cắt.
            state["stop_reason"] = "empty_page_without_lower_boundary"
            break
        new_items = [item for item in page if item["signature"] not in all_seen]
        if not new_items:
            state["stop_reason"] = "cursor_not_advancing"
            break
        for item in new_items:
            signature = item["signature"]
            all_seen.add(signature)
            timestamp = item.get("blockTime")
            if timestamp is None:
                state["unknown_timestamps"] += 1
                continue
            state["upper_boundary_observed"] |= timestamp >= end
            state["lower_boundary_crossed"] |= timestamp < start
            if start <= timestamp < end:
                selected[signature] = item
        state["signatures_scanned"] = len(all_seen)
        print(f"Trang {state['pages']}: đã xem {len(all_seen)} mã, thuộc ngày chọn: {len(selected)}.", flush=True)
        if state["lower_boundary_crossed"]:
            state["stop_reason"] = "crossed_day_start"
            break
        before = page[-1]["signature"]
    state["window_bracketed"] = bool(
        state["upper_boundary_observed"] and state["lower_boundary_crossed"]
        and not state["unknown_timestamps"] and not state["scan_error"]
    )
    state["signatures"] = sorted(selected.values(), key=lambda item: (item["slot"], item["signature"]))
    return state


def download_details(
    reader: Reader, signatures: list[dict[str, Any]], max_transactions: int,
) -> list[dict[str, Any]]:
    """Bảng kiểm kê hiển thị cả phần thiếu/lỗi; không tự suy ra nhãn mua bán."""
    rows: list[dict[str, Any]] = []
    consecutive_errors = 0
    for index, item in enumerate(signatures):
        signature = item["signature"]
        row = {
            "signature": signature, "slot": item["slot"],
            "time_utc": datetime.fromtimestamp(item["blockTime"], timezone.utc).isoformat(),
            "execution_error": json.dumps(item.get("err")),
            "detail_status": "not_requested", "signers": "", "fee_sol": "",
            "explorer_url": f"https://solscan.io/tx/{signature}", "note": "",
        }
        if index >= max_transactions or consecutive_errors >= 3:
            row["note"] = "Đạt giới hạn số giao dịch hoặc 3 lỗi liên tiếp."
        else:
            try:
                transaction = reader.call("getTransaction", [signature, {
                    "encoding": "jsonParsed", "maxSupportedTransactionVersion": 1,
                    "commitment": "finalized",
                }])
                if transaction is None:
                    row["detail_status"] = "missing"
                elif not transaction.get("meta"):
                    row["detail_status"] = "missing_meta"
                elif transaction.get("blockTime") != item["blockTime"] or transaction.get("slot") != item["slot"]:
                    row["detail_status"] = "time_or_slot_mismatch"
                else:
                    meta = transaction["meta"]
                    row["detail_status"] = "downloaded"
                    row["transaction_version"] = transaction.get("version", "")
                    row["execution_error"] = json.dumps(meta.get("err"))
                    row["signers"] = "|".join(
                        key["pubkey"] for key in transaction["transaction"]["message"]["accountKeys"]
                        if key.get("signer")
                    )
                    row["fee_sol"] = f"{meta['fee'] / 10**9:.9f}"
                consecutive_errors = 0
            except RuntimeError as exc:
                row.update(detail_status="rpc_error", note=str(exc))
                consecutive_errors += 1
            print(f"Chi tiết {index + 1}/{len(signatures)}: {row['detail_status']}", flush=True)
        rows.append(row)
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--day", required=True, help="Ngày UTC, ví dụ 2026-11-05")
    parser.add_argument("--pool", default=HEGE_POOL)
    parser.add_argument("--page-size", type=int, default=10)
    parser.add_argument("--max-pages", type=int, default=20)
    parser.add_argument("--max-transactions", type=int, default=100)
    parser.add_argument("--delay", type=float, default=3)
    parser.add_argument("--run-dir", type=Path, help="Dùng lại thư mục raw của một lần chạy để đọc cache")
    parser.add_argument("--offline", action="store_true", help="Chỉ đọc cache, không gọi mạng")
    args = parser.parse_args()
    try:
        start, end = day_bounds(args.day)
    except ValueError:
        parser.error("Ngày phải có dạng YYYY-MM-DD.")
    if end > datetime.now(timezone.utc).timestamp():
        parser.error("Chọn ngày UTC đã kết thúc để kiểm tra đủ cửa sổ.")
    if not (1 <= args.page_size <= 1000 and args.max_pages > 0 and args.max_transactions > 0 and args.delay >= 2):
        parser.error("page-size: 1–1000; số trang/giao dịch > 0; delay >= 2 giây.")
    if args.offline and args.run_dir is None:
        parser.error("Chế độ offline cần --run-dir của lần chạy đã có dữ liệu.")
    stamp = datetime.now(timezone.utc).strftime("run_%Y%m%dT%H%M%S_%fZ")
    run_dir = args.run_dir or ROOT / "data/raw/solana_day_pilot" / args.day / stamp
    run_dir = run_dir.resolve()
    run_dir.mkdir(parents=True, exist_ok=True)
    config = {"day_utc": args.day, "pool": args.pool, "page_size": args.page_size,
              "max_pages": args.max_pages, "max_transactions": args.max_transactions,
              "max_supported_transaction_version": 1, "rpc_url": RPC_URL}
    config_file = run_dir / "config.json"
    if config_file.exists():
        if json.loads(config_file.read_text()) != config:
            parser.error("Tham số khác lần chạy cũ; tạo thư mục mới để không trộn dữ liệu.")
    else:
        write_json(config_file, {**config})
    output_dir = ROOT / "data/interim/solana_day_pilot" / args.day / run_dir.name
    output_dir.mkdir(parents=True, exist_ok=True)
    reader = PublicRpc(run_dir / "rpc", args.delay, args.offline)
    started = time.monotonic()
    started_utc = utc_now()
    scan = scan_day(reader, args.pool, start, end, args.page_size, args.max_pages)
    signatures = scan.pop("signatures")
    write_json(output_dir / "signatures.json", signatures)
    rows = download_details(reader, signatures, args.max_transactions)
    fields = ["signature", "slot", "time_utc", "execution_error", "detail_status", "transaction_version", "signers", "fee_sol", "explorer_url", "note"]
    with (output_dir / "transactions.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    downloaded = sum(row["detail_status"] == "downloaded" for row in rows)
    summary = {
        **config, **scan, "run_started_at_utc": started_utc, "finished_at_utc": utc_now(),
        "window_start_utc": datetime.fromtimestamp(start, timezone.utc).isoformat(),
        "window_end_exclusive_utc": datetime.fromtimestamp(end, timezone.utc).isoformat(),
        "transactions_in_day": len(rows), "details_downloaded": downloaded,
        "failed_execution_count": sum(row["execution_error"] != "null" for row in rows),
        "details_all_downloaded": downloaded == len(rows),
        "provider_window_retrieved": scan["window_bracketed"] and downloaded == len(rows),
        "network_requests_this_run": reader.network_requests, "cache_hits_this_run": reader.cache_hits,
        "elapsed_seconds": round(time.monotonic() - started, 2), "raw_dir": str(run_dir),
        "scope_note": "Giao dịch tham chiếu pool theo RPC; chưa giải mã swap. Hai biên và đủ chi tiết không chứng minh node không bỏ sót dữ liệu.",
    }
    # Mỗi lần chạy có manifest riêng, kể cả lần chạy lại offline.
    write_json(run_dir / f"manifest_{time.time_ns()}.json", summary)
    write_json(output_dir / "summary.json", summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    print(f"Bảng kiểm kê: {output_dir / 'transactions.csv'}")
    return 0 if summary["provider_window_retrieved"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
