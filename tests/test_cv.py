"""Unit tests for real file generation/extraction, no external AI access."""
import json
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from scripts.ats_audit import audit
from scripts.build_cv import render_docx
from scripts.extract_cv import extract_bytes, extract_path


class CareerSpotTests(unittest.TestCase):
    def test_english_docx_roundtrip(self):
        self._roundtrip("en")

    def test_arabic_docx_roundtrip(self):
        self._roundtrip("ar")

    def _roundtrip(self, lang):
        data = json.loads((ROOT / "examples" / f"sample_cv_{lang}.json").read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory() as outdir:
            path = render_docx(data, Path(outdir) / "resume.docx")
            result = extract_path(path)
            self.assertTrue(result["extractable"])
            self.assertIn(data["profile"]["full_name"], result["text"])
            self.assertEqual(result["warnings"], [])
            with zipfile.ZipFile(path) as archive:
                xml = archive.read("word/document.xml").decode("utf-8")
                self.assertNotIn("<w:tbl>", xml)
                if lang == "ar":
                    self.assertIn("w:bidi", xml)

    def test_simple_ats_audit(self):
        data = json.loads((ROOT / "examples/sample_cv_en.json").read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory() as outdir:
            path = render_docx(data, Path(outdir) / "resume.docx")
            report = audit(path)
            self.assertTrue(report["extractable"])
            self.assertIn("skills", report["sections_detected"])
            self.assertIn("education", report["sections_detected"])
            self.assertNotIn("ats_score", report)

    def test_no_name_rejected(self):
        with tempfile.TemporaryDirectory() as outdir:
            with self.assertRaises(ValueError):
                render_docx({"language": "en", "profile": {}}, Path(outdir) / "cv.docx")

    def test_wrong_extension_rejected(self):
        with self.assertRaises(ValueError):
            extract_bytes(b"irrelevant", "malicious.txt")

    def test_spoofed_pdf_rejected(self):
        with self.assertRaises(ValueError):
            extract_bytes(b"This is not really a PDF", "fake.pdf")

    def test_10mb_cap(self):
        with self.assertRaises(ValueError):
            extract_bytes(b"A" * (10 * 1024 * 1024 + 1), "large.docx")


if __name__ == "__main__":
    unittest.main()
