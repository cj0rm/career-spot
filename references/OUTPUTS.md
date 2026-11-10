# Output contracts

## Default response: review and rewrite

1. **التشخيص المختصر**: file readability, format risk, 3–5 specific issues.
2. **ما الذي تغيّر؟**: 3–5 substantive improvements, no generic hype.
3. **السيرة الذاتية المحسّنة**: full final content in CV's target language.
4. **ملفات جاهزة**: actual working DOCX/PDF links only if created and tested.
5. **معلومات تحتاج مراجعتك**: short list of material unknowns outside the document.

## New CV

If most essentials are missing, ask a short structured set of questions; don't force an artificial ATS rating with no posting. If enough facts exist, generate immediately. CV output must be complete, ready to copy, and consistent.

## Job match

Output required vs preferred evidence map and risks, then full tailored CV. A ratio only when countable. Explain match coverage is not a real ATS prediction.

## JSON document model v1

These keys form the interchange contract for `scripts/build_cv.py`. All list fields optional; omitted strings are empty. Only supplied facts are populated. No placeholder claims.

```json
{
  "language": "en",
  "profile": {
    "full_name": "Candidate Name",
    "headline": "Target position",
    "email": "candidate@example.org",
    "phone": "+968 ...",
    "location": "Muscat, Oman",
    "linkedin": "",
    "portfolio": "",
    "summary": "Factual professional summary."
  },
  "skills": [{"category": "Technical Skills", "items": ["Skill 1", "Skill 2"]}],
  "experience": [{
    "title": "Intern", "organization": "Example Organization",
    "location": "Muscat", "start": "2025-06", "end": "2025-08",
    "bullets": ["Assisted with documented tasks and reporting."]
  }],
  "education": [{"degree": "Diploma", "institution": "Example University", "location": "", "start": "2023", "end": "2025", "details": ["Relevant course project"]}],
  "projects": [{"title": "Project title", "context": "", "date": "", "bullets": ["What was done"]}],
  "certifications": [{"name": "Course or certificate", "issuer": "Issuer", "date": ""}],
  "languages": [{"name": "Arabic", "level": "Native"}],
  "additional_sections": [{"title": "Volunteering", "entries": ["Factual item"]}]
}
```

Use `language: "ar"` for Arabic. The script uses RTL body paragraphs and Arabic section labels. An optional PDF is generated via LibreOffice and then checked for extractability. The script does not validate professional claims and does not run the AI itself.
