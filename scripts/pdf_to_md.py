"""Chuyển PDF trong docs/references/papers/ sang Markdown để Codex / Claude Code đọc.

Vì sao: đọc PDF bằng công cụ đọc ảnh/trang tốn token và hay lỗi. Markdown thì
tìm kiếm (grep) được và đọc nhanh hơn.

Dùng pymupdf4llm làm bộ chuyển chính (xử lý paper 2 cột tốt). Nếu lỗi thì
dùng markitdown (Microsoft) làm dự phòng.

Chạy:  .venv/bin/python scripts/pdf_to_md.py            # chuyển tất cả PDF
       .venv/bin/python scripts/pdf_to_md.py path/x.pdf  # chuyển 1 file
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PDF_DIR = ROOT / "docs" / "references" / "papers"
MD_DIR = ROOT / "docs" / "references" / "markdown"


def convert_pymupdf(pdf: Path) -> str:
    import pymupdf4llm

    return pymupdf4llm.to_markdown(str(pdf))


def convert_markitdown(pdf: Path) -> str:
    from markitdown import MarkItDown

    return MarkItDown().convert(str(pdf)).text_content


def convert_one(pdf: Path) -> Path:
    """Chuyển một PDF, trả về đường dẫn file .md đã ghi."""
    try:
        text, engine = convert_pymupdf(pdf), "pymupdf4llm"
    except Exception as exc:  # noqa: BLE001 - chủ ý bắt rộng để rơi về dự phòng
        print(f"  pymupdf4llm lỗi ({exc}); dùng markitdown")
        text, engine = convert_markitdown(pdf), "markitdown"
    MD_DIR.mkdir(parents=True, exist_ok=True)
    out = MD_DIR / f"{pdf.stem}.md"
    header = f"<!-- Chuyển từ {pdf.name} bằng {engine}. Số liệu quan trọng hãy đối chiếu PDF gốc. -->\n\n"
    out.write_text(header + text, encoding="utf-8")
    print(f"{pdf.name} -> {out.relative_to(ROOT)} [{engine}, {len(text) // 1024} KB]")
    return out


def main(args: list[str]) -> None:
    pdfs = [Path(a) for a in args] if args else sorted(PDF_DIR.glob("*.pdf"))
    for pdf in pdfs:
        convert_one(pdf)


if __name__ == "__main__":
    main(sys.argv[1:])
