#!/usr/bin/env python3
"""Extract document text and a few observable layout signals. Does not OCR scans."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

MAX_FILE_BYTES = 10 * 1024 * 1024
MAX_TEXT_CHARS = 250_000
MAX_PDF_PAGES = 50


def extract_bytes(content: bytes, filename: str) -> dict[str, Any]:
    if len(content) > MAX_FILE_BYTES:
        raise ValueError("File is over 10MB limit")
    extension = Path(filename).suffix.lower()
    if extension not in (".pdf", ".docx"):
        raise ValueError("Only .pdf and .docx are supported")
    if extension == ".pdf":
        if not content.startswith(b"%PDF-"):
            raise ValueError("Invalid PDF file signature")
        import fitz
        doc = fitz.open(stream=content, filetype="pdf")
        try:
            if doc.page_count > MAX_PDF_PAGES:
                raise ValueError("PDF is longer than 50 pages")
            all_text = []
            pages_without_text = 0
            for page in doc:
                page_text = page.get_text(sort=False)  # preserve RTL PDF word order
                all_text.append(page_text)
                if len(page_text.strip()) < 30:
                    pages_without_text += 1
            full = "\n\n".join(all_text)[:MAX_TEXT_CHARS]
            flags = []
            if pages_without_text:
                flags.append(f"{pages_without_text} page(s) have little extractable text; OCR may be needed")
            return {"filename": Path(filename).name, "format": "pdf", "pages": doc.page_count,
                    "text": full, "extractable": bool(full.strip()), "needs_ocr": not bool(full.strip()),
                    "warnings": flags,
                    "checks_performed": ["PDF text extraction"],
                    "checks_not_performed": ["ATS vendor evaluation", "complete reading-order verification", "visual layout audit"]}
        finally:
            doc.close()

    if not content.startswith(b"PK"):
        raise ValueError("Invalid DOCX file signature")
    import io
    from docx import Document
    try:
        doc = Document(io.BytesIO(content))
    except Exception as exc:
        raise ValueError(f"Unable to open DOCX: {exc}") from exc
    lines = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
    # Read tables too, but flag them: what looks readable in Word can parse poorly in ATS.
    for table in doc.tables:
        for row in table.rows:
            lines.append(" | ".join(cell.text.strip() for cell in row.cells))
    header_text = " ".join(p.text for section in doc.sections for p in section.header.paragraphs).strip()
    footer_text = " ".join(p.text for section in doc.sections for p in section.footer.paragraphs).strip()
    flags = []
    if doc.tables:
        flags.append(f"{len(doc.tables)} table(s) detected: evaluate reading order")
    if header_text:
        flags.append("Header text exists; verify it is not essential contact information")
    if footer_text:
        flags.append("Footer text exists; verify it is not essential information")
    text = "\n".join(lines)[:MAX_TEXT_CHARS]
    if not text:
        flags.append("No body or table text was extracted")
    return {"filename": Path(filename).name, "format": "docx", "pages": None,
            "text": text, "extractable": bool(text.strip()), "needs_ocr": False,
            "warnings": flags,
            "checks_performed": ["DOCX paragraph/table extraction", "basic table/header/footer checks"],
            "checks_not_performed": ["ATS vendor evaluation", "complete reading-order verification", "visual layout audit"]}


def extract_path(path: str | Path) -> dict[str, Any]:
    p = Path(path)
    return extract_bytes(p.read_bytes(), p.name)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--out", type=Path, help="Write JSON to file; otherwise stdout")
    args = parser.parse_args()
    result = json.dumps(extract_path(args.input), ensure_ascii=False, indent=2)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(result + "\n", encoding="utf-8")
        print(args.out)
    else:
        print(result)


if __name__ == "__main__":
    main()
