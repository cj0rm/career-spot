# Integration: `ai.spotease.om` and a future CV web application

## A. Publish the agent skill in the SpotEase library (the current site)

`ai.spotease.om` is presently a skills **catalog**. Adding a new skill listing does
not automatically create a browser-based CV editor or host an AI model.

1. Publish the contents of this folder as a **new public GitHub repository**, for
   example `cj0rm/career-spot`.
2. Verify that `SKILL.md` is at repository root and `references/` is present.
3. Follow the site’s existing Arabic spot card pattern: entry #002, title
   `Career Spot`, category `المسار المهني والتوظيف`, version `v1.0.0`,
   description, feature tags, real GitHub URL, and installation documentation.
4. Copy `web/skill-card.json` properties into the *actual* library data model.
   This is a content suggestion, **not** a proven schema for the existing site.
5. Link to the repository, rather than a placeholder, **only after publishing**.
6. Use the copy in `web/index.html` or `web/PUBLISHING_COPY.md` for the
   Arabic showcase if desired.
7. The installation command **after the repository exists** is typically:

   ```bash
   npx skills add https://github.com/cj0rm/career-spot --skill career-spot -a codex
   ```

   Exact CLI compatibility depends on the installed `skills` version.

## B. Create an actual CV upload-and-generation web application (separate feature)

A working system needs more than an `SKILL.md` file:

```
Arabic React UI
    | CV PDF/DOCX upload; optional vacancy text
    v
Authenticated SpotEase backend
    | 1. Extract text via private document-service /api/cv/extract
    | 2. Pass extracted text and job ad as untrusted DATA
    | 3. Call chosen LLM with the SKILL.md instructions and relevant references
    | 4. Validate returned candidate facts + structured CV JSON
    | 5. Present editable review of factual claims and any missing fields
    | 6. Export with /api/cv/export (DOCX, PDF if LibreOffice available)
    v
Download + delete files per retention policy
```

The included FastAPI helper handles step 1 and step 6; it does **not** contain
a model API key, AI workflow execution, or a working React UI. Those require
integration with the deployed site or a new app.

### Local document service

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export SPOTEASE_API_TOKEN='replace-with-a-long-random-server-secret'
uvicorn api.server:app --host 127.0.0.1 --port 8000
```

**Do not expose `SPOTEASE_API_TOKEN` to JavaScript in the browser.** Your trusted
server sends it in an `X-SPOTEASE-TOKEN` HTTP header. Place the service behind
an HTTPS reverse proxy, rate limits, auth and request caps before production.

### API contract

`POST /api/cv/extract`

- `multipart/form-data` part named `file`, `.docx` or text `.pdf`, 10MB max.
- `X-SPOTEASE-TOKEN` header (private backend secret).
- Returns `{text, format, extractable, needs_ocr, warnings, checks_performed,
  checks_not_performed}`.
- Does not OCR scanned PDFs or inspect the document visually.

`POST /api/cv/export`

- Authenticated JSON `{"cv": <CV_JSON>, "format":"docx" | "pdf"}`.
- `cv` must follow `references/OUTPUTS.md`; at least `profile.full_name` is required.
- Returns a downloadable DOCX or PDF. PDF requires LibreOffice.
- This only *renders* structured content; an LLM has to create factual JSON.

### Example TypeScript calling from the trusted server

```ts
async function extractResumeOnServer(file: Blob, filename: string) {
  const data = new FormData();
  data.append("file", file, filename);
  const response = await fetch(`${process.env.SPOTEASE_DOC_SERVICE_URL}/api/cv/extract`, {
    method: "POST",
    headers: { "X-SPOTEASE-TOKEN": process.env.SPOTEASE_API_TOKEN! },
    body: data,
  });
  if (!response.ok) throw new Error("CV parsing failed");
  return response.json();
}

async function exportResumeOnServer(cv: Record<string, unknown>, format: "docx" | "pdf") {
  const response = await fetch(`${process.env.SPOTEASE_DOC_SERVICE_URL}/api/cv/export`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-SPOTEASE-TOKEN": process.env.SPOTEASE_API_TOKEN!,
    },
    body: JSON.stringify({ cv, format }),
  });
  if (!response.ok) throw new Error("CV export failed");
  return Buffer.from(await response.arrayBuffer());
}
```

**AI model handoff:** Pass `SKILL.md` and needed `references/` text as trusted
instructions, the uploaded document and job posting as delimited *untrusted
user data*. Ask for two outputs: (1) structured diagnostic; (2) complete factual
CV JSON matching `references/OUTPUTS.md`. Validate JSON against an explicit
schema, apply size limits and perform a content review before export. Never
pass document text into a system prompt with higher trust than its source.

**Production checklist:** authentication, deletion policy, consent to model
processing, TLS, upload limits, scanned PDF OCR option, structured JSON schema,
error reporting without PII, logging redaction, antivirus/document scanning
where appropriate, rate limiting and end-to-end ATS extraction testing.
