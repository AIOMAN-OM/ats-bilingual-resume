---
name: ats-bilingual-resume
description: Audit, rewrite, translate, and generate ATS-ready resumes in Arabic and English from user-entered data or an uploaded CV. Use for ATS compatibility checks, CV conversion, job-tailored keyword alignment, and editable Word plus PDF outputs in classic, photo-color, or accent-color styles.
---

# ATS Bilingual Resume

Turn supplied career information or an uploaded resume into accurate, editable Arabic and English resumes. Never invent employment, education, dates, achievements, metrics, credentials, or contact details.

## Route the request

- If the user uploads a CV, extract all readable text and structure first. Use the document workflow for DOCX and the PDF workflow for PDF; use OCR only when the file is image-based.
- If the user enters data, normalize it with [the input schema](references/input-schema.md).
- If a target job description is provided, compare its terminology with the evidence in the CV. Add a keyword only when the user's experience supports it.
- If required facts are missing, ask only the smallest set of questions needed. Mark optional unknowns as omitted, never as placeholders in final files.
- If a photo style is requested but no photo is available, generate the non-photo styles and request the photo for that one remaining style.

## Audit before rewriting

Read [ATS audit rubric](references/ats-audit.md) and produce:

1. Overall compatibility score out of 100 and rating.
2. Evidence-based findings by category.
3. Missing or ambiguous information requiring user confirmation.
4. A concise before-and-after improvement summary.

Treat ATS compatibility as an informed assessment, not a guarantee. Do not claim a resume will pass every employer system.

## Rewrite and bilingual quality

Read [language and content rules](references/language-and-content.md). Preserve meaning while improving clarity, specificity, action verbs, and measurable impact. Keep chronology and official names accurate. Use natural Modern Standard Arabic and professional international English, not literal word-for-word translation.

For Arabic, use correct RTL paragraphs, Arabic punctuation where natural, and consistent Arabic terminology. Keep proper nouns, product names, certifications, URLs, and technical acronyms in their official form when translation would reduce accuracy. For English, use one consistent regional convention and date style throughout.

## Generate deliverables

Read [output matrix and styles](references/output-matrix.md). Unless the user narrows the request, create all of these for each of the three styles:

- Arabic-only DOCX and PDF.
- English-only DOCX and PDF.
- Combined bilingual DOCX and PDF, with complete English followed by complete Arabic; do not use side-by-side columns.

That is 18 resume files. Also create `ats-audit-report.md` and `delivery-manifest.json`, then package the outputs in one ZIP while keeping individual files accessible when possible.

Use `scripts/generate_resume.py` after preparing a validated UTF-8 JSON record. Run `scripts/validate_resume_data.py` first. The generator creates editable DOCX files and converts them to PDF when LibreOffice is available.

## Document constraints

- Keep the classic version single-column, without photo, icons, charts, skill bars, text boxes, header/footer contact details, or essential information in tables.
- Keep the accent-color version single-column and without photo. Color may support headings only; meaning must not depend on color.
- The photo-color version may use a small professional user-supplied photo and restrained color. Label it as visually oriented and less universally ATS-safe.
- Use conventional headings, selectable text, ordinary bullets, and reverse-chronological experience unless the user's field requires another order.
- Do not include sensitive personal attributes unless the user explicitly asks and they are appropriate for the destination market.
- Do not force an arbitrary one-page limit. Prefer readable 1-2 pages, expanding when seniority or evidence requires it.
- Default to Letter portrait unless the user or target market requests A4.

## Verification gate

Before delivery:

1. Validate the input JSON and confirm no unresolved placeholder tokens remain.
2. Open each DOCX structurally and confirm headings, text, language direction, and image presence or absence match the selected style.
3. Render every DOCX to PNG and inspect every page for clipped text, missing Arabic glyphs, overlaps, broken bullets, and bad page breaks.
4. Confirm every requested PDF exists, is non-empty, has the same page count as its DOCX render, and contains selectable text.
5. Confirm the manifest lists every delivered file and its language, style, format, and ATS suitability.
6. Revise and rerender until the latest inspection passes.

## Delivery explanation

State clearly that the classic version is the primary submission copy, the accent version is an ATS-aware visual alternative, and the photo-color version is best for direct sharing where photos are accepted. Mention any factual gaps that were omitted.
