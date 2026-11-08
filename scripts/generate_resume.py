#!/usr/bin/env python3
"""Generate Arabic, English, and combined ATS resume DOCX/PDF files."""

import argparse
import json
import re
import shutil
import subprocess
from pathlib import Path

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_CELL_VERTICAL_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor

STYLES = ("classic", "photo-color", "accent-color")
LANGUAGES = ("ar", "en", "bilingual")
HEADINGS = {
    "en": {"summary": "Professional Summary", "skills": "Core Skills", "experience": "Professional Experience", "education": "Education", "certifications": "Certifications", "projects": "Selected Projects", "awards": "Awards", "languages": "Languages"},
    "ar": {"summary": "الملخص المهني", "skills": "المهارات الأساسية", "experience": "الخبرات المهنية", "education": "المؤهلات العلمية", "certifications": "الشهادات المهنية", "projects": "المشروعات المختارة", "awards": "الجوائز", "languages": "اللغات"},
}


def rgb(hex_value):
    value = hex_value.lstrip("#")
    return RGBColor(int(value[:2], 16), int(value[2:4], 16), int(value[4:], 16))


def local(value, lang):
    return str(value.get(lang, "") if isinstance(value, dict) else value or "").strip()


def set_rtl(paragraph, enabled):
    paragraph.alignment = WD_ALIGN_PARAGRAPH.RIGHT if enabled else WD_ALIGN_PARAGRAPH.LEFT
    if enabled:
        ppr = paragraph._p.get_or_add_pPr()
        if ppr.find(qn("w:bidi")) is None:
            node = OxmlElement("w:bidi")
            node.set(qn("w:val"), "1")
            ppr.append(node)


def format_run(run, size=10.5, bold=False, ink=RGBColor(0, 0, 0), rtl=False):
    run.font.name = "DejaVu Sans"
    rpr = run._element.get_or_add_rPr()
    for key in ("w:ascii", "w:hAnsi", "w:cs"):
        rpr.rFonts.set(qn(key), "DejaVu Sans")
    run.font.size = Pt(size)
    run.font.bold = bold
    run.font.color.rgb = ink
    if rtl:
        node = OxmlElement("w:rtl")
        node.set(qn("w:val"), "1")
        rpr.append(node)


def add_paragraph(doc, text="", lang="en", size=10.5, bold=False, ink=RGBColor(0, 0, 0), before=0, after=3, keep=False):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(before)
    p.paragraph_format.space_after = Pt(after)
    p.paragraph_format.line_spacing = 1.08
    p.paragraph_format.keep_with_next = keep
    run = p.add_run(text)
    format_run(run, size, bold, ink, lang == "ar")
    set_rtl(p, lang == "ar")
    return p


def add_heading(doc, text, lang, accent):
    add_paragraph(doc, text, lang, 11.5, True, accent, 8, 3, True)


def add_bullet(doc, text, lang):
    p = add_paragraph(doc, "", lang, after=2)
    p.style = doc.styles["List Bullet"]
    format_run(p.add_run(text), rtl=lang == "ar")
    set_rtl(p, lang == "ar")


def date_range(item, lang):
    start, end = str(item.get("start", "")).strip(), str(item.get("end", "")).strip()
    if end.lower() == "present":
        end = "حتى الآن" if lang == "ar" else "Present"
    return " - ".join(x for x in (start, end) if x)


def contact_line(person, lang):
    values = [local(person.get("location"), lang)]
    values += [str(person.get(k, "")).strip() for k in ("phone", "email", "linkedin", "portfolio")]
    return " | ".join(x for x in values if x)


def add_identity(doc, data, lang, style, accent, photo):
    person = data["person"]
    name, headline = local(person["name"], lang), local(person["headline"], lang)
    if style == "photo-color" and photo:
        table = doc.add_table(rows=1, cols=2)
        table.autofit = False
        text_cell, image_cell = (table.cell(0, 0), table.cell(0, 1)) if lang == "en" else (table.cell(0, 1), table.cell(0, 0))
        text_cell.width, image_cell.width = Inches(5.8), Inches(0.8)
        text_cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
        p = text_cell.paragraphs[0]
        format_run(p.add_run(name), 20, True, accent, lang == "ar")
        set_rtl(p, lang == "ar")
        p2 = text_cell.add_paragraph()
        format_run(p2.add_run(headline), 11, True, RGBColor(55, 65, 81), lang == "ar")
        set_rtl(p2, lang == "ar")
        image_cell.paragraphs[0].add_run().add_picture(str(photo), width=Inches(0.75))
    else:
        add_paragraph(doc, name, lang, 20, True, accent, after=1)
        add_paragraph(doc, headline, lang, 11, True, RGBColor(55, 65, 81), after=2)
    add_paragraph(doc, contact_line(person, lang), lang, 9.3, after=6)


def add_resume(doc, data, lang, style, accent, photo=None):
    add_identity(doc, data, lang, style, accent, photo)
    labels = HEADINGS[lang]
    summary = local(data.get("summary"), lang)
    if summary:
        add_heading(doc, labels["summary"], lang, accent)
        add_paragraph(doc, summary, lang)
    skills = [local(x, lang) for x in data.get("skills", []) if local(x, lang)]
    if skills:
        add_heading(doc, labels["skills"], lang, accent)
        add_paragraph(doc, ("، " if lang == "ar" else " | ").join(skills), lang)
    if data.get("experience"):
        add_heading(doc, labels["experience"], lang, accent)
        for item in data["experience"]:
            title = " | ".join(x for x in (local(item.get("role"), lang), local(item.get("organization"), lang)) if x)
            add_paragraph(doc, title, lang, bold=True, after=0, keep=True)
            meta = " | ".join(x for x in (date_range(item, lang), local(item.get("location"), lang)) if x)
            if meta:
                add_paragraph(doc, meta, lang, 9.2, ink=RGBColor(75, 85, 99), after=2, keep=True)
            for bullet in item.get("bullets", []):
                text = local(bullet, lang)
                if text:
                    add_bullet(doc, text, lang)
    if data.get("education"):
        add_heading(doc, labels["education"], lang, accent)
        for item in data["education"]:
            title = " | ".join(x for x in (local(item.get("degree"), lang), local(item.get("institution"), lang)) if x)
            add_paragraph(doc, title, lang, bold=True, after=0, keep=True)
            meta = " | ".join(x for x in (str(item.get("year", "")).strip(), local(item.get("location"), lang)) if x)
            if meta:
                add_paragraph(doc, meta, lang, 9.2, ink=RGBColor(75, 85, 99), after=1)
            details = local(item.get("details"), lang)
            if details:
                add_paragraph(doc, details, lang)
    sections = (
        ("certifications", lambda x: " | ".join(v for v in (local(x.get("name"), lang), local(x.get("issuer"), lang), str(x.get("year", "")).strip()) if v)),
        ("projects", lambda x: " | ".join(v for v in (local(x.get("name"), lang), local(x.get("details"), lang)) if v)),
        ("awards", lambda x: " | ".join(v for v in (local(x.get("name"), lang), local(x.get("issuer"), lang), str(x.get("year", "")).strip()) if v)),
        ("languages", lambda x: " | ".join(v for v in (local(x.get("language"), lang), local(x.get("level"), lang)) if v)),
    )
    for key, formatter in sections:
        items = [formatter(x) for x in data.get(key, [])]
        if any(items):
            add_heading(doc, labels[key], lang, accent)
            for text in items:
                if text:
                    add_bullet(doc, text, lang)
    for section in data.get("optional_sections", []):
        title = local(section.get("title"), lang)
        items = [local(x, lang) for x in section.get("items", [])]
        if title and any(items):
            add_heading(doc, title, lang, accent)
            for text in items:
                if text:
                    add_bullet(doc, text, lang)


def configure(doc, page_size):
    section = doc.sections[0]
    if page_size == "a4":
        section.page_width, section.page_height = Inches(8.27), Inches(11.69)
    else:
        section.page_width, section.page_height = Inches(8.5), Inches(11)
    section.top_margin = section.bottom_margin = Inches(0.55)
    section.left_margin = section.right_margin = Inches(0.65)
    doc.styles["Normal"].font.name = "DejaVu Sans"
    doc.styles["Normal"].font.size = Pt(10.5)


def build_docx(data, style, language, output, photo, accent_hex):
    doc = Document()
    configure(doc, str(data.get("settings", {}).get("page_size", "letter")).lower())
    accent = RGBColor(0, 0, 0) if style == "classic" else rgb(accent_hex if style == "accent-color" else "1F4E78")
    selected_photo = photo if style == "photo-color" else None
    if language == "bilingual":
        add_resume(doc, data, "en", style, accent, selected_photo)
        doc.add_section(WD_SECTION.NEW_PAGE)
        add_resume(doc, data, "ar", style, accent, selected_photo)
    else:
        add_resume(doc, data, language, style, accent, selected_photo)
    doc.core_properties.title = local(data["person"]["name"], "en") + " Resume"
    doc.core_properties.subject = "ATS-ready bilingual resume"
    doc.save(output)


def to_pdf(docx_path, output_dir):
    office = shutil.which("soffice") or shutil.which("libreoffice")
    if not office:
        return None
    result = subprocess.run([office, "--headless", "--convert-to", "pdf", "--outdir", str(output_dir), str(docx_path)], capture_output=True, text=True)
    pdf = output_dir / f"{docx_path.stem}.pdf"
    if result.returncode or not pdf.exists():
        raise RuntimeError(f"PDF conversion failed for {docx_path.name}: {result.stderr.strip()}")
    return pdf


def page_count(pdf_path):
    tool = shutil.which("pdfinfo")
    if not tool:
        return None
    result = subprocess.run([tool, str(pdf_path)], capture_output=True, text=True)
    match = re.search(r"^Pages:\s+(\d+)", result.stdout, re.MULTILINE)
    return int(match.group(1)) if match else None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--styles", nargs="+", choices=STYLES, default=list(STYLES))
    parser.add_argument("--languages", nargs="+", choices=LANGUAGES, default=list(LANGUAGES))
    parser.add_argument("--photo", type=Path)
    parser.add_argument("--accent", default="0F766E")
    parser.add_argument("--skip-pdf", action="store_true")
    args = parser.parse_args()
    data = json.loads(args.input.read_text(encoding="utf-8"))
    args.output_dir.mkdir(parents=True, exist_ok=True)
    if "photo-color" in args.styles and not args.photo:
        raise SystemExit("--photo is required when photo-color is requested")
    accent = args.accent.lstrip("#")
    if not re.fullmatch(r"[0-9A-Fa-f]{6}", accent):
        raise SystemExit("--accent must be a six-digit hex color")
    manifest = []
    for style in args.styles:
        for lang in args.languages:
            stem = f"resume_{style.replace('-', '_')}_{lang}"
            docx = args.output_dir / f"{stem}.docx"
            build_docx(data, style, lang, docx, args.photo, accent)
            suitability = "primary" if style == "classic" else ("acceptable alternative" if style == "accent-color" else "visual sharing")
            base = {"language": lang, "style": style, "photo_included": bool(args.photo and style == "photo-color"), "ats_suitability": suitability}
            docx_record = {"filename": docx.name, "format": "docx", **base}
            manifest.append(docx_record)
            if not args.skip_pdf:
                pdf = to_pdf(docx, args.output_dir)
                if pdf:
                    pages = page_count(pdf)
                    if pages is not None:
                        docx_record["page_count"] = pages
                    pdf_record = {"filename": pdf.name, "format": "pdf", **base}
                    if pages is not None:
                        pdf_record["page_count"] = pages
                    manifest.append(pdf_record)
    (args.output_dir / "delivery-manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"created": len(manifest), "output_dir": str(args.output_dir)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
