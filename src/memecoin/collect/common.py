"""Hàm nhỏ dùng chung: cấu hình, thời gian UTC và bảng CSV."""
from __future__ import annotations

import csv
import json
import os
import tempfile
from contextlib import contextmanager
from datetime import date, datetime, time, timezone
from pathlib import Path
from typing import IO, Any, Iterable, Iterator

import yaml

ROOT = Path(__file__).resolve().parents[3]


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_config(name: str) -> dict[str, Any]:
    return yaml.safe_load((ROOT / "configs" / name).read_text(encoding="utf-8"))


def midnight(day: str | date) -> int:
    parsed = date.fromisoformat(day) if isinstance(day, str) else day
    return int(datetime.combine(parsed, time.min, timezone.utc).timestamp())


def iso_time(timestamp: int) -> str:
    return datetime.fromtimestamp(timestamp, timezone.utc).isoformat()


@contextmanager
def _atomic_open(path: Path, **open_kwargs: Any) -> Iterator[IO[str]]:
    """Ghi vào file tạm cùng thư mục rồi `os.replace` sang tên thật.

    Tiến trình khác đọc cùng lúc chỉ thấy bản cũ hoặc bản mới hoàn chỉnh,
    không bao giờ thấy file ghi dở. Lỗi giữa chừng thì xoá file tạm, giữ bản cũ.
    Đuôi `.tmp` để các lệnh glob `*.json`/`*.meta.json` không nhặt nhầm.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(dir=path.parent, prefix=f".{path.name}.", suffix=".tmp")
    tmp = Path(tmp_name)
    try:
        with os.fdopen(fd, "w", **open_kwargs) as handle:
            yield handle
            handle.flush()
            os.fsync(handle.fileno())
        # mkstemp tạo quyền 600; trả về 644 như file ghi thường (umask 022).
        os.chmod(tmp, 0o644)
        os.replace(tmp, path)
    except BaseException:
        tmp.unlink(missing_ok=True)
        raise


def write_json(path: Path, value: Any) -> None:
    """Ghi JSON nguyên tử: đầu ra dựng lại được và pointer cache của HttpClient.

    Raw phản hồi do HttpClient ghi riêng, không đi qua hàm này.
    """
    text = json.dumps(value, ensure_ascii=False, indent=2, default=str) + "\n"
    with _atomic_open(path, encoding="utf-8") as handle:
        handle.write(text)


def write_csv(path: Path, rows: Iterable[dict[str, Any]], fields: list[str]) -> None:
    """Ghi CSV nguyên tử, cùng cách với `write_json`."""
    with _atomic_open(path, newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
