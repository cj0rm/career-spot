#!/usr/bin/env python3
"""Check Career Spot package structure and example document generation."""
from __future__ import annotations

import json
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FILES = [
    "SKILL.md", "README.md", "LICENSE", "THIRD_PARTY_NOTICES.md",
    "agents/openai.yaml", "references/MODES.md", "references/ATS.md",
    "references/WRITING.md", "references/ARABIC.md", "references/OUTPUTS.md",
    "references/PRIVACY.md", "docs/INTEGRATION.md", "docs/CODEX_HANDOFF.md", "api/server.py",
    "examples/sample_cv_en.json", "examples/sample_cv_ar.json",
    "scripts/build_cv.py", "scripts/extract_cv.py", "scripts/ats_audit.py", "web/PUBLISHING_COPY.md",
    "web/skill-card.json", "web/index.html",
]


def main() -> None:
    from build_cv import render_docx
    from extract_cv import extract_path
    missing = [p for p in FILES if not (ROOT / p).is_file()]
    if missing:
        raise SystemExit("Missing files: " + ", ".join(missing))
    skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
    if not skill.startswith("---\n") or "name: career-spot" not in skill:
        raise SystemExit("Invalid skill frontmatter")
    with tempfile.TemporaryDirectory(prefix="career-spot-check-") as temp:
        for lang in ("en", "ar"):
            path = ROOT / "examples" / f"sample_cv_{lang}.json"
            cv = json.loads(path.read_text(encoding="utf-8"))
            dest = Path(temp) / f"sample_{lang}.docx"
            render_docx(cv, dest)
            extracted = extract_path(dest)
            if not extracted["extractable"]:
                raise SystemExit(f"No extractable text from {lang} example")
            if cv["profile"]["full_name"] not in extracted["text"]:
                raise SystemExit(f"Name not preserved in {lang} example")
    print("Career Spot structure and bilingual DOCX smoke tests: OK")


if __name__ == "__main__":
    main()
