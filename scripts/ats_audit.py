#!/usr/bin/env python3
"""Conservative observable ATS-readability audit (NOT an ATS acceptance score)."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

try:
    from scripts.extract_cv import extract_path
except ImportError:  # standalone python scripts/ats_audit.py
    from extract_cv import extract_path

SECTION_ALIASES = {
    "summary": [r"\b(summary|profile|professional summary)\b", r"الملخص(?: المهني)?"],
    "skills": [r"\b(skills|technical skills)\b", r"المهارات"],
    "experience": [r"\b(experience|employment|work history)\b", r"الخبرة(?: العملية)?"],
    "education": [r"\beducation\b", r"التعليم", r"المؤهلات"],
    "projects": [r"\bprojects\b", r"المشاريع"],
    "certifications": [r"\bcertifications?\b", r"الشهادات"],
}


def audit(path: str | Path) -> dict[str, Any]:
    result = extract_path(path)
    text = result["text"]
    warnings = list(result["warnings"])
    found = sorted(k for k, exprs in SECTION_ALIASES.items()
                   if any(re.search(pattern, text, re.I) for pattern in exprs))
    email_found = bool(re.search(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", text, re.I))
    issues = []
    if not result["extractable"]:
        issues.append("File has no extractable body text; OCR or original editable document required")
    if not email_found and result["extractable"]:
        issues.append("No email was detected in extracted text; verify contact information")
    if len(found) < 2 and result["extractable"]:
        issues.append("Fewer than two standard CV section labels found; review heading names")
    issues.extend(warnings)
    if not result["extractable"]:
        risk = "high_observed"
    elif warnings:
        risk = "medium_observed"
    elif result["format"] == "pdf":
        risk = "unknown_layout_without_visual_review"
    else:
        risk = "low_observed_not_guaranteed"
    return {
        "file": result["filename"],
        "format": result["format"],
        "extractable": result["extractable"],
        "format_risk": risk,
        "sections_detected": found,
        "email_detected": email_found,
        "issues": issues,
        "limits": [
            "Not connected to any ATS vendor",
            "Does not predict acceptance, rejection, interview probability or ranking",
            "Does not semantically assess job-description match",
            "Does not perform full visual layout validation or OCR",
            "PDF extraction and Arabic shaping can vary by parser",
        ],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    data = json.dumps(audit(args.input), ensure_ascii=False, indent=2)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(data + "\n", encoding="utf-8")
        print(args.out)
    else:
        print(data)


if __name__ == "__main__":
    main()
