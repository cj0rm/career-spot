"""Optional server-side document API for SpotEase; AI rewriting is external.

Start: uvicorn api.server:app --host 127.0.0.1 --port 8000
Requests require the private SPOTEASE_API_TOKEN header sent from the trusted backend.
Do NOT call directly from an unauthenticated frontend/browser.
"""
from __future__ import annotations

import io
import os
import secrets
import tempfile
from pathlib import Path
from typing import Literal

from fastapi import Depends, FastAPI, File, Header, HTTPException, UploadFile
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from scripts.build_cv import convert_pdf, render_docx
from scripts.extract_cv import MAX_FILE_BYTES, extract_bytes

app = FastAPI(title="Career Spot Document Service", version="1.0.0", docs_url=None, redoc_url=None)


def require_token(x_spotease_token: str | None = Header(default=None)) -> None:
    correct = os.getenv("SPOTEASE_API_TOKEN")
    if not correct:
        raise HTTPException(status_code=503, detail="Document API token not configured")
    if not x_spotease_token or not secrets.compare_digest(x_spotease_token, correct):
        raise HTTPException(status_code=401, detail="Unauthorized")


@app.get("/health")
def health():
    return {"status": "ok", "service": "career-spot-documents"}


@app.post("/api/cv/extract", dependencies=[Depends(require_token)])
async def extract(file: UploadFile = File(...)):
    data = await file.read(MAX_FILE_BYTES + 1)
    try:
        return extract_bytes(data, file.filename or "unknown")
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except Exception as exc:
        # Do not expose document content or internal stack details to callers.
        raise HTTPException(status_code=422, detail="File could not be parsed") from exc


class ExportRequest(BaseModel):
    cv: dict
    format: Literal["docx", "pdf"] = "docx"


@app.post("/api/cv/export", dependencies=[Depends(require_token)])
def export(request: ExportRequest):
    try:
        with tempfile.TemporaryDirectory(prefix="spotease-cv-") as root:
            path = render_docx(request.cv, Path(root) / "career-spot-cv.docx")
            if request.format == "pdf":
                path = convert_pdf(path, root)
            file_bytes = path.read_bytes()
    except (ValueError, TypeError) as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    mime = ("application/pdf" if request.format == "pdf"
            else "application/vnd.openxmlformats-officedocument.wordprocessingml.document")
    return StreamingResponse(io.BytesIO(file_bytes), media_type=mime, headers={
        "Content-Disposition": f'attachment; filename="career-spot-cv.{request.format}"',
        "Cache-Control": "no-store",
        "X-Content-Type-Options": "nosniff",
    })
