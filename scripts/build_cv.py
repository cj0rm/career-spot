#!/usr/bin/env python3
"""Create ATS-readable DOCX and optional PDF from factual Career Spot CV JSON.

No AI rewriting occurs here. Feed only candidate-approved facts.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor

HEADINGS = {
    "en": {"skills": "SKILLS", "experience": "EXPERIENCE", "education": "EDUCATION",
           "projects": "PROJECTS", "certifications": "CERTIFICATIONS", "languages": "LANGUAGES"},
    "ar": {"skills": "المهارات", "experience": "الخبرة العملية", "education": "التعليم",
           "projects": "المشاريع", "certifications": "الشهادات", "languages": "اللغات"},
}


def _text(value: Any) -> str:
    return str(value).strip() if value is not None else ""


def _bidi(paragraph, rtl: bool) -> None:
    if not rtl:
        return
    # With w:bidi set, LibreOffice treats LEFT as the physical right edge;
    # the logical RTL reading direction remains encoded in w:bidi.
    paragraph.alignment = WD_ALIGN_PARAGRAPH.LEFT
    ppr = paragraph._p.get_or_add_pPr()
    if ppr.find(qn("w:bidi")) is None:
        bidi = OxmlElement("w:bidi")
        bidi.set(qn("w:val"), "1")
        ppr.append(bidi)


def _rtl_run(run, rtl: bool) -> None:
    if not rtl:
        return
    rpr = run._r.get_or_add_rPr()
    if rpr.find(qn("w:rtl")) is None:
        el = OxmlElement("w:rtl")
        el.set(qn("w:val"), "1")
        rpr.append(el)


def _para(doc, text: str, *, bold: bool = False, size: float = 10,
          space_before: float = 0, space_after: float = 4, rtl: bool = False,
          bullet: bool = False, color: RGBColor | None = None):
    text = _text(text)
    if not text:
        return None
    p = doc.add_paragraph(style="Normal")
    p.paragraph_format.space_before = Pt(space_before)
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.line_spacing = 1.12
    p.paragraph_format.keep_together = True
    if bullet:
        p.paragraph_format.left_indent = Inches(0.19 if not rtl else 0)
        p.paragraph_format.right_indent = Inches(0.19 if rtl else 0)
        p.paragraph_format.first_line_indent = Inches(-0.12 if not rtl else 0)
        if rtl:
            p.add_run("•  ")
        else:
            p.add_run("•  ")
    _bidi(p, rtl)
    run = p.add_run(text)
    run.bold = bold
    run.font.name = "Arial"
    run.font.size = Pt(size)
    if color:
        run.font.color.rgb = color
    _rtl_run(run, rtl)
    return p


def _section(doc, title: str, rtl: bool):
    p = _para(doc, title, bold=True, size=11, space_before=10, space_after=4,
              rtl=rtl, color=RGBColor(22, 32, 20))
    if p:
        p.paragraph_format.keep_with_next = True
        pPr = p._p.get_or_add_pPr()
        borders = OxmlElement('w:pBdr')
        bottom = OxmlElement('w:bottom')
        bottom.set(qn('w:val'), 'single')
        bottom.set(qn('w:sz'), '5')
        bottom.set(qn('w:color'), 'D5DCD4')
        borders.append(bottom)
        pPr.append(borders)


def _join(*parts: str, sep: str = " | ") -> str:
    return sep.join(_text(x) for x in parts if _text(x))


def _date_range(start: Any, end: Any) -> str:
    return _join(start, end, sep=" – ")


def render_docx(data: dict[str, Any], outpath: str | Path) -> Path:
    if not isinstance(data, dict):
        raise ValueError("Resume data must be a JSON object")
    profile = data.get("profile") or {}
    if not isinstance(profile, dict) or not _text(profile.get("full_name")):
        raise ValueError("profile.full_name is required")
    lang = _text(data.get("language", "en")).lower()
    if lang not in HEADINGS:
        raise ValueError("language must be 'en' or 'ar'")
    rtl = lang == "ar"
    labels = HEADINGS[lang]

    doc = Document()
    sec = doc.sections[0]
    sec.top_margin = Inches(.66)
    sec.bottom_margin = Inches(.64)
    sec.left_margin = Inches(.72)
    sec.right_margin = Inches(.72)
    normal = doc.styles["Normal"]
    normal.font.name = "Arial"
    normal.font.size = Pt(10)
    normal.paragraph_format.space_after = Pt(4)
    doc.core_properties.title = f"Curriculum Vitae - {_text(profile['full_name'])}"
    doc.core_properties.author = "SpotEase Career Spot"

    _para(doc, profile["full_name"], size=17.5, bold=True, space_after=4, rtl=rtl,
          color=RGBColor(22, 32, 20))
    _para(doc, profile.get("headline", ""), size=10.8, bold=True, rtl=rtl)
    _para(doc, _join(profile.get("email"), profile.get("phone"), profile.get("location")),
          size=9.5, rtl=rtl)
    _para(doc, _join(profile.get("linkedin"), profile.get("portfolio")), size=9, rtl=rtl)
    _para(doc, profile.get("summary", ""), size=10, space_before=8, space_after=6, rtl=rtl)

    skills = data.get("skills") or []
    if skills:
        _section(doc, labels["skills"], rtl)
        for s in skills:
            if isinstance(s, dict):
                _para(doc, _join(s.get("category"), ", ".join(_text(x) for x in s.get("items", []) if _text(x)), sep=": "), rtl=rtl, space_after=2)
            elif isinstance(s, str):
                _para(doc, s, rtl=rtl, space_after=2)

    experiences = data.get("experience") or []
    if experiences:
        _section(doc, labels["experience"], rtl)
        for role in experiences:
            title_line = _join(role.get("title"), role.get("organization"))
            _para(doc, title_line, bold=True, space_before=5, space_after=1, rtl=rtl)
            _para(doc, _join(role.get("location"), _date_range(role.get("start"), role.get("end"))),
                  size=9, space_after=3, rtl=rtl)
            for bullet in role.get("bullets") or []:
                _para(doc, bullet, bullet=True, space_after=3, rtl=rtl)

    schools = data.get("education") or []
    if schools:
        _section(doc, labels["education"], rtl)
        for item in schools:
            _para(doc, _join(item.get("degree"), item.get("institution")), bold=True, space_before=4, space_after=1, rtl=rtl)
            _para(doc, _join(item.get("location"), _date_range(item.get("start"), item.get("end"))),
                  size=9, space_after=2, rtl=rtl)
            for detail in item.get("details") or []:
                _para(doc, detail, bullet=True, space_after=2, rtl=rtl)

    projects = data.get("projects") or []
    if projects:
        _section(doc, labels["projects"], rtl)
        for item in projects:
            _para(doc, _join(item.get("title"), item.get("context"), item.get("date")),
                  bold=True, space_before=4, space_after=2, rtl=rtl)
            for bullet in item.get("bullets") or []:
                _para(doc, bullet, bullet=True, space_after=2, rtl=rtl)

    certs = data.get("certifications") or []
    if certs:
        _section(doc, labels["certifications"], rtl)
        for item in certs:
            _para(doc, _join(item.get("name"), item.get("issuer"), item.get("date")), rtl=rtl, space_after=2)

    languages = data.get("languages") or []
    if languages:
        _section(doc, labels["languages"], rtl)
        for item in languages:
            _para(doc, _join(item.get("name"), item.get("level"), sep=": "), rtl=rtl, space_after=2)

    for section in data.get("additional_sections") or []:
        heading = _text(section.get("title"))
        if not heading:
            continue
        _section(doc, heading, rtl)
        for item in section.get("entries") or []:
            _para(doc, item, bullet=True, space_after=2, rtl=rtl)

    out = Path(outpath)
    out.parent.mkdir(parents=True, exist_ok=True)
    doc.save(out)
    return out


def convert_pdf(docx_path: str | Path, outdir: str | Path) -> Path:
    cmd = shutil.which("libreoffice") or shutil.which("soffice")
    if not cmd:
        raise RuntimeError("PDF export requires LibreOffice/soffice installed on the server")
    path = Path(docx_path)
    output_dir = Path(outdir)
    output_dir.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="career-spot-lo-") as profile_dir:
        run = subprocess.run([cmd, f"-env:UserInstallation={Path(profile_dir).as_uri()}",
                              "--headless", "--convert-to", "pdf", "--outdir",
                              str(output_dir), str(path)], check=False,
                              capture_output=True, text=True, timeout=45)
    output = output_dir / f"{path.stem}.pdf"
    if run.returncode or not output.exists() or output.stat().st_size < 200:
        raise RuntimeError(f"PDF conversion failed: {run.stderr.strip() or run.stdout.strip()}")
    return output


def _filename(name: str) -> str:
    ascii_name = re.sub(r"[^\w-]+", "_", name, flags=re.UNICODE).strip("_")
    return (ascii_name or "candidate")[:60] + "_CareerSpot_CV"


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="Career Spot JSON file")
    parser.add_argument("--outdir", type=Path, default=Path("exports"))
    parser.add_argument("--pdf", action="store_true", help="Also export PDF (requires LibreOffice)")
    args = parser.parse_args()
    data = json.loads(args.input.read_text(encoding="utf-8"))
    out = render_docx(data, args.outdir / (_filename(data.get("profile", {}).get("full_name", "candidate")) + ".docx"))
    print(f"DOCX: {out}")
    if args.pdf:
        print(f"PDF: {convert_pdf(out, args.outdir)}")


if __name__ == "__main__":
    main()
