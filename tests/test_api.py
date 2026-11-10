"""Authentication and export roundtrip for the optional document service."""
import json
import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from api.server import app


class ApiTests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.cv = json.loads((ROOT / "examples/sample_cv_en.json").read_text(encoding="utf-8"))

    def test_api_rejects_without_config(self):
        with patch.dict(os.environ, {}, clear=True):
            resp = self.client.post("/api/cv/export", json={"cv": self.cv, "format": "docx"})
        self.assertEqual(resp.status_code, 503)

    def test_api_rejects_bad_secret(self):
        with patch.dict(os.environ, {"SPOTEASE_API_TOKEN": "expected"}):
            resp = self.client.post("/api/cv/export", headers={"X-SPOTEASE-TOKEN": "wrong"},
                                    json={"cv": self.cv, "format": "docx"})
        self.assertEqual(resp.status_code, 401)

    def test_export_extract_roundtrip(self):
        with patch.dict(os.environ, {"SPOTEASE_API_TOKEN": "expected"}):
            exported = self.client.post("/api/cv/export", headers={"X-SPOTEASE-TOKEN": "expected"},
                                        json={"cv": self.cv, "format": "docx"})
            self.assertEqual(exported.status_code, 200)
            imported = self.client.post("/api/cv/extract", headers={"X-SPOTEASE-TOKEN": "expected"},
                                        files={"file": ("resume.docx", exported.content,
                                                        "application/vnd.openxmlformats-officedocument.wordprocessingml.document")})
        self.assertEqual(imported.status_code, 200)
        self.assertIn("Sample Candidate", imported.json()["text"])


if __name__ == "__main__":
    unittest.main()
