# ATS and readable-resume audit

The optional `scripts/ats_audit.py` automates a narrow observable subset of these checks. It does not assess vendor-specific ATS behavior or guarantee successful Arabic PDF parsing.

## What can and cannot be measured

There is no universal ATS score or guaranteed recruiter selection. Most commercial ATS platforms operate differently; keyword matching, parsing, recruiter filters, and employer configuration vary. Never claim a deterministic pass/fail result from generic heuristics.

Use three independent dimensions:

1. **Extractability:** Can text, sections and key fields be extracted in a sensible order from the *actual* file? Verified by a parser if available. Mark untested if no file access.
2. **Layout risk:** Is key information in images, text boxes, columns, headers or footers? Are dates and headings recognizable? Risk is low / medium / high with evidence. PDF visual appearance alone is insufficient to assess extraction.
3. **Job alignment:** Only when a vacancy is supplied. Track required/preferred requirements and whether evidence exists in the CV. This is *content alignment*, not an ATS vendor score.

## Review checklist

- File: DOCX or a text-based PDF. Scanned PDFs: require OCR and manual proofreading.
- Single logical reading order. Avoid text boxes and multi-column flow in ATS master.
- Information is selectable text. Name, email and phone live in body, not only header/footer.
- Standard section titles: Summary, Experience, Education, Skills, Projects, Certifications. For Arabic CVs: الملخص المهني، الخبرة العملية، التعليم، المهارات، المشاريع، الشهادات.
- Consistent roles, employers, dates and reverse chronology where relevant.
- Plain simple bullets; no icons replacing headings or skills.
- Use standard fonts with Arabic glyph coverage and consistent spacing.
- Avoid profile photo and graphs as essential data. No skills-as-progress-bars.
- Dates consistently formatted. Distinguish graduation date from ongoing enrollment.
- Avoid stuffing keywords. Mention skills only when supported by evidence.
- Match output to application instructions: some employers require DOCX, PDF, or specific template.

## Job evidence map

For each **required** criterion and **preferred** criterion, return:

`requirement | priority | resume evidence | supported / partial / missing / unknown | suggested edit`

- "missing keyword" means the skill is evidenced but the term is absent.
- "missing evidence" means the candidate's skill cannot be verified from provided facts.
- Use semantic judgment: exact words are not always necessary, but they can help discoverability.

Optional transparent indicator: **verified requirement coverage** = supported required items / total explicit required items. Report denominator, count, limitations, and never label it "ATS acceptance probability". For zero extractable requirements, write `غير قابل للتقييم`.

## Example report outline (Arabic interface)

- **قابلية قراءة الملف:** قابل للاستخراج / يحتاج مراجعة / غير قابل للاستخراج / غير مفحوص.
- **مخاطر التنسيق:** منخفضة / متوسطة / مرتفعة, with 1–3 concrete reasons.
- **المتطلبات المثبتة:** 5 من 8 متطلبات أساسية, *only where a posting exists*.
- **أهم التعديلات:** prioritised issues with factual corrections.
- **الناتج:** complete revised CV in correct language.
