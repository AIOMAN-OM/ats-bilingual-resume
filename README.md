# ats-bilingual-resume

مهارة (Skill) لتدقيق السير الذاتية وإعادة كتابتها وترجمتها وإنشائها بالعربية والإنجليزية بشكل متوافق مع أنظمة تتبع المتقدمين (ATS): تقييم من 100، وإعادة صياغة دون اختلاق معلومات، وملفات Word وPDF بثلاثة أنماط (كلاسيكي، بلون مميز، بصورة).

An agent skill that audits, rewrites, translates and generates ATS-ready resumes in Arabic and English, with a scored audit, evidence-based rewriting (no invented facts) and editable DOCX + PDF outputs in classic, accent-color and photo-color styles.

## Structure
- `SKILL.md` — main instructions
- `references/` — ATS audit rubric, input schema, language rules, output matrix
- `scripts/validate_resume_data.py` — validates the bilingual JSON record
- `scripts/generate_resume.py` — builds DOCX files and converts them to PDF (needs `python-docx`; LibreOffice for PDF)
- `agents/openai.yaml`, `assets/icon.svg`

## Install
Copy the `ats-bilingual-resume` folder into your skills directory (e.g. `~/.claude/skills/`), or download the repo as ZIP and upload it as a skill.

By [AIOMAN](https://github.com/AIOMAN-OM)

## License

MIT — see [LICENSE](LICENSE).
