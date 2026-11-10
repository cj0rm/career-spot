# Codex handoff: publish Career Spot on ai.spotease.om

Copy this brief into Codex **while the SpotEase AI website repository is open**.

---

You are working on the existing SpotEase AI Arabic Skills Library codebase.
Integrate the adjacent `career-spot/` project as the **second skill**, while
preserving the design system, current Arabic Spot listing, responsive behavior,
SEO, accessibility, and existing routes. Follow the actual website architecture;
do not assume it is Next.js, React, or any specific data schema until inspected.

1. Inspect the existing library's source of truth for skills, any category filters,
   library counts, featured cards and individual skill routes. Add `career-spot`
   without hardcoding inconsistent counts. Proposed skill content lives in
   `career-spot/web/skill-card.json` and `career-spot/web/PUBLISHING_COPY.md`.
2. Feature the Arabic title **Career Spot | المسار المهني**, the headline
   **من السيرة الأولى إلى طلب التوظيف** and the six capabilities: CV analysis,
   factual rewriting, new CV generation, ATS layout review, job matching, and
   supporting application materials. Mention that the unified system internally
   supports 22 career workflows.
3. Publish links to the real GitHub repository and actual installation guide
   using the published `cj0rm/career-spot` repository URL.
4. Explain clearly that this is an AI agent **skill**. The current site is a
   skills library, not a functioning upload/AI document generator. Do not create
   decorative nonworking file-upload buttons or claim a live ATS integration.
5. Expose a real installation command based on the published repo's URL, matching
   the current Arabic Spot install UX and preserving an easy copy action.
6. Add metadata and an Arabic `lang="ar"` / RTL-friendly layout where appropriate.
   Keep technical terms ATS, CV, DOCX, PDF properly rendered.
7. Show a clear limitation: no guarantee of ATS acceptance, hiring, or correctness
   of unsupported employment history. User must verify claims.
8. Run the website's existing type checking, linting, tests and production build.
   Report affected files, routes and whether the new repository link is live.

**Optional future phase:** If the user separately approves building an actual
CV generator, use `career-spot/docs/INTEGRATION.md`. Wire authenticated PDF/DOCX
upload, extraction, model-based rewriting/JSON validation, review, and document
export on a protected server. Do not expose the document API secret in client
code, do not invent candidate data, and do not store CV files indefinitely.

---
