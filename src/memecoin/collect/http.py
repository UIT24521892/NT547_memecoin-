"""Client chỉ đọc: raw bất biến, cache theo request, rate limit và retry.

Key chỉ đi trong kết nối HTTPS. URL/tham số trong metadata và thông báo lỗi
được che key; file raw chỉ chứa đúng body phản hồi, không ghi thêm bản sao.
"""
from __future__ import annotations

import hashlib
import fcntl
import json
import re
import time
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

import requests

from .common import utc_now, write_json

READ_METHODS = {
    "eth_getLogs", "eth_getBlockByNumber", "eth_blockNumber", "eth_getTransactionByHash",
    "eth_getTransactionReceipt", "eth_call", "getTransactionsForAddress", "getTransaction",
    "getSignaturesForAddress", "getAccountInfo", "web3_sha3", "eth_getCode",
}


class CollectionError(RuntimeError):
    """Lỗi đã bỏ thông tin nhạy cảm, có thể ghi vào báo cáo."""


@dataclass(frozen=True)
class Response:
    data: Any
    raw_ref: str
    collected_at: str


class HttpClient:
    def __init__(self, root: Path, provider: str, requests_per_second: float,
                 *, offline: bool = False, refresh: bool = False,
                 max_requests: int = 10000, secrets: tuple[str, ...] = (),
                 cache_namespace: str | None = None,
                 session: Any = None, sleep: Any = time.sleep, clock: Any = time.monotonic) -> None:
        if requests_per_second <= 0 or max_requests < 1:
            raise ValueError("Tốc độ và ngân sách request phải dương.")
        self.root, self.provider = root, provider
        self.delay = 1 / requests_per_second
        self.offline, self.refresh, self.max_requests = offline, refresh, max_requests
        self.secrets = tuple(s for s in secrets if s)
        self.session = session or requests.Session()
        self.sleep, self.clock = sleep, clock
        self.last_call: float | None = None
        self.network_requests = 0
        self.cache_hits = 0
        if cache_namespace is not None and not re.fullmatch(r"[A-Za-z0-9_-]+", cache_namespace):
            raise ValueError("Tên cache chỉ gồm chữ, số, dấu gạch ngang hoặc gạch dưới.")
        self.cache_namespace = cache_namespace
        self.cache_dir = root / "data/interim/http_cache" / provider
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        # Cache benchmark tách riêng nhưng mọi namespace vẫn chung giới hạn provider.
        self.rate_file = self.cache_dir / ".rate.lock"
        if cache_namespace:
            self.cache_dir /= cache_namespace
            self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _pace(self) -> None:
        """Khóa theo provider để hai tiến trình cũng chia sẻ cùng rate limit."""
        with self.rate_file.open("a+") as handle:
            fcntl.flock(handle, fcntl.LOCK_EX)
            handle.seek(0)
            text = handle.read().strip()
            previous = float(text) if text else None
            current = self.clock()
            if previous is not None and current >= previous:
                self.sleep(max(0, self.delay - (current - previous)))
            handle.seek(0)
            handle.truncate()
            handle.write(str(self.clock()))
            handle.flush()
            fcntl.flock(handle, fcntl.LOCK_UN)

    def redact(self, value: str) -> str:
        for secret in self.secrets:
            value = value.replace(secret, "<redacted>")
        return value

    def _safe_url(self, url: str) -> str:
        parsed = urlsplit(self.redact(url))
        query = [(k, "<redacted>" if k.lower() in {"apikey", "api-key", "api_key", "key"} else v)
                 for k, v in parse_qsl(parsed.query)]
        return urlunsplit((parsed.scheme, parsed.netloc, parsed.path, urlencode(query), ""))

    def request(self, method: str, url: str, *, params: dict[str, Any] | None = None,
                body: dict[str, Any] | None = None) -> Response:
        if method not in {"GET", "POST"}:
            raise ValueError("Chỉ GET hoặc POST JSON-RPC chỉ đọc.")
        if method == "POST" and (not body or body.get("method") not in READ_METHODS):
            raise ValueError("Phương thức RPC không thuộc danh sách chỉ đọc.")
        safe_params = {k: "<redacted>" if k.lower() in {"apikey", "api-key", "api_key", "key"}
                       else v for k, v in (params or {}).items()}
        request = {"method": method, "url": self._safe_url(url), "params": safe_params, "body": body}
        canonical = json.dumps(request, sort_keys=True, separators=(",", ":"))
        key = hashlib.sha256(canonical.encode()).hexdigest()
        pointer = self.cache_dir / f"{key}.json"
        if pointer.exists() and (self.offline or not self.refresh):
            meta = json.loads(pointer.read_text(encoding="utf-8"))
            raw_path = self.root / meta["raw_ref"]
            raw = raw_path.read_bytes()
            if hashlib.sha256(raw).hexdigest() != meta["sha256"]:
                raise CollectionError(f"Cache sai SHA-256: {meta['raw_ref']}")
            self.cache_hits += 1
            return Response(json.loads(raw), meta["raw_ref"], meta["collected_at"])
        if self.offline:
            raise CollectionError(f"Thiếu cache {self.provider}/{key}; offline không gọi mạng.")

        for attempt in range(4):
            if self.network_requests >= self.max_requests:
                raise CollectionError(f"Hết ngân sách {self.max_requests} request cho {self.provider}; có thể chạy tiếp bằng cache.")
            self._pace()
            self.network_requests += 1
            try:
                reply = self.session.request(method, url, params=params, json=body,
                                             timeout=(10, 60), headers={"User-Agent": "nt547-student-research"})
            except requests.RequestException:
                if attempt == 3:
                    raise CollectionError(f"{self.provider}: lỗi kết nối sau 4 lần thử.") from None
                self.sleep(2 ** (attempt + 1))
                continue
            collected_at = utc_now()
            raw = reply.content
            # Một dịch vụ phản chiếu key trong lỗi thì không lưu key ra đĩa.
            if any(secret.encode() in raw for secret in self.secrets):
                raise CollectionError(f"{self.provider}: phản hồi chứa key, đã bỏ qua việc ghi file.")
            folder = self.root / "data/raw" / collected_at[:10] / self.provider
            folder.mkdir(parents=True, exist_ok=True)
            raw_path = folder / f"{key}_{uuid.uuid4().hex}.body"
            with raw_path.open("xb") as handle:
                handle.write(raw)
            raw_ref = str(raw_path.relative_to(self.root))
            meta = {"request": request, "collected_at": collected_at,
                    "status_code": reply.status_code, "raw_ref": raw_ref,
                    "sha256": hashlib.sha256(raw).hexdigest()}
            if self.cache_namespace:
                meta["cache_namespace"] = self.cache_namespace
            write_json(raw_path.with_suffix(".meta.json"), meta)
            if reply.status_code in {408, 429} or reply.status_code >= 500:
                if attempt == 3:
                    raise CollectionError(f"{self.provider}: HTTP {reply.status_code} sau 4 lần thử; raw={raw_ref}")
                retry_after = reply.headers.get("Retry-After", "0")
                try:
                    pause = max(float(retry_after), 2 ** (attempt + 1))
                except ValueError:
                    pause = 2 ** (attempt + 1)
                self.sleep(pause)
                continue
            if reply.status_code != 200:
                raise CollectionError(f"{self.provider}: HTTP {reply.status_code}; raw={raw_ref}")
            try:
                data = reply.json()
            except ValueError:
                raise CollectionError(f"{self.provider}: phản hồi không phải JSON; raw={raw_ref}") from None
            if isinstance(data, dict) and data.get("error"):
                code = data["error"].get("code") if isinstance(data["error"], dict) else "unknown"
                if code in {-32005, -32029, -32429} and attempt < 3:
                    self.sleep(2 ** (attempt + 1))
                    continue
                raise CollectionError(f"{self.provider}: RPC error {code}; raw={raw_ref}")
            if isinstance(data, dict) and data.get("errors") and not any(k in data for k in ("data", "result", "instructions")):
                raise CollectionError(f"{self.provider}: API trả errors; raw={raw_ref}")
            if isinstance(data, dict) and str(data.get("status")) == "0" and data.get("result") != []:
                raise CollectionError(f"{self.provider}: API status=0; raw={raw_ref}")
            # Chỉ cache phản hồi thành công. Raw từng lần gọi vẫn bất biến.
            write_json(pointer, meta)
            return Response(data, raw_ref, collected_at)
        raise CollectionError("Không có phản hồi thành công.")

    def rpc(self, url: str, method: str, params: list[Any]) -> Response:
        return self.request("POST", url, body={"jsonrpc": "2.0", "id": 1, "method": method, "params": params})

    def stats(self) -> dict[str, int]:
        return {"network_requests": self.network_requests, "cache_hits": self.cache_hits}
