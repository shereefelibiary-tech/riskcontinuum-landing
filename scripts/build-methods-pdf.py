#!/usr/bin/env python3
"""Build the downloadable methods appendix from the public HTML source.

Dependencies: beautifulsoup4, reportlab. Run from any directory. The full
contents of technical details are included, even when collapsed on the web.
"""
from __future__ import annotations

from html import escape
from pathlib import Path
import re

from bs4 import BeautifulSoup, NavigableString, Tag
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import HRFlowable, KeepTogether, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

ROOT = Path(__file__).resolve().parents[1]
FONT_DIR = Path("/usr/share/fonts/truetype/dejavu")
for name, filename in (("Methods", "DejaVuSans.ttf"), ("Methods-Bold", "DejaVuSans-Bold.ttf"), ("Methods-Italic", "DejaVuSans-Oblique.ttf")):
    font_file = FONT_DIR / filename
    if not font_file.is_file():
        font_file = FONT_DIR / "DejaVuSans.ttf"
    pdfmetrics.registerFont(TTFont(name, str(font_file)))
pdfmetrics.registerFontFamily("Methods", normal="Methods", bold="Methods-Bold", italic="Methods-Italic", boldItalic="Methods-Bold")

INK = colors.HexColor("#24191D")
GARNET = colors.HexColor("#861327")
MUTED = colors.HexColor("#6F6064")
LINE = colors.HexColor("#E8DFE1")
WIDTH = 504
styles = getSampleStyleSheet()
for style in styles.byName.values():
    style.fontName = "Methods"
    style.textColor = INK
styles.add(ParagraphStyle(name="MethodsBody", fontName="Methods", fontSize=9.3, leading=14.5, spaceAfter=9, splitLongWords=True))
styles.add(ParagraphStyle(name="MethodsSmall", parent=styles["MethodsBody"], fontSize=8, leading=12, textColor=MUTED))
styles.add(ParagraphStyle(name="MethodsTitle", fontName="Methods", fontSize=30, leading=37, spaceAfter=22, textColor=INK))
styles.add(ParagraphStyle(name="MethodsH2", fontName="Methods", fontSize=21, leading=27, spaceAfter=16, keepWithNext=True))
styles.add(ParagraphStyle(name="MethodsH3", fontName="Methods-Bold", fontSize=12.5, leading=17, spaceBefore=16, spaceAfter=9, keepWithNext=True))
styles.add(ParagraphStyle(name="MethodsH4", fontName="Methods-Bold", fontSize=10.5, leading=15, spaceBefore=12, spaceAfter=7, keepWithNext=True))
styles.add(ParagraphStyle(name="MethodsTable", parent=styles["MethodsBody"], fontSize=7.7, leading=11.5, spaceAfter=0))
styles.add(ParagraphStyle(name="MethodsTableHeader", parent=styles["MethodsTable"], fontName="Methods-Bold", textColor=GARNET))
styles.add(ParagraphStyle(name="MethodsCaption", parent=styles["MethodsSmall"], spaceAfter=6, keepWithNext=True))


def clean(value: str) -> str:
    return value.replace("\u2013", "-").replace("\u2014", "-").replace("\u2212", "-").replace("\u2011", "-").replace("\u00a0", " ")


def inline(node: Tag | NavigableString) -> str:
    if isinstance(node, NavigableString):
        return escape(clean(str(node)))
    body = "".join(inline(child) for child in node.children)
    if node.name in {"b", "strong"}:
        return f"<b>{body}</b>"
    if node.name in {"i", "em"}:
        return f"<i>{body}</i>"
    if node.name == "br":
        return "<br/>"
    if node.name == "code":
        return f'<font name="Methods" size="7.3">{body}</font>'
    if node.name == "a":
        href = node.get("href", "")
        if href.startswith(("https://", "mailto:")):
            return f'<link href="{escape(href, quote=True)}" color="#861327">{body}</link>'
    if node.name == "span" and "reference-note" in node.get("class", []):
        return "<br/>" + body
    return body


def rule_identifier_markup(value: str, available_width: float) -> str:
    """Wrap identifiers only at underscore boundaries, preserving each token."""
    tokens = clean(value).split("_")
    lines: list[str] = []
    current = ""
    for token in tokens:
        candidate = f"{current}_{token}" if current else token
        if current and pdfmetrics.stringWidth(candidate, "Methods", 7.3) > available_width:
            lines.append(current + "_")
            current = token
        else:
            current = candidate
    if current:
        lines.append(current)
    return "<br/>".join(escape(line) for line in lines)


def make_table(node: Tag) -> list:
    rows = []
    for row_index, tr in enumerate(node.find_all("tr")):
        cells = []
        for cell in tr.find_all(["th", "td"], recursive=False):
            style = styles["MethodsTableHeader"] if row_index == 0 else styles["MethodsTable"]
            # Keep identifiers readable; split at semantic underscore boundaries.
            for code in cell.find_all("code"):
                code.insert_before(BeautifulSoup("<br/>", "html.parser"))
                if "rule-table" in node.get("class", []) and code.get_text().startswith("LEVEL_"):
                    wrapped = rule_identifier_markup(code.get_text(), 134)
                    code.clear()
                    code.append(BeautifulSoup(wrapped, "html.parser"))
            cells.append(Paragraph(inline(cell), style))
        rows.append(cells)
    count = len(rows[0])
    if "rule-table" in node.get("class", []):
        widths = [34, 316, 154]
    elif "rss-table" in node.get("class", []):
        widths = [195, 55, 254]
    elif count == 2:
        widths = [137, 367]
    else:
        widths = [112, 190, 202]
    caption_rows = 1 if node.caption else 0
    if node.caption:
        rows.insert(0, [Paragraph(inline(node.caption), styles["MethodsSmall"]), *([""] * (count - 1))])
    table = Table(rows, colWidths=widths, repeatRows=1 + caption_rows, hAlign="LEFT")
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, caption_rows), colors.HexColor("#F3ECEE")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LINEBELOW", (0, 0), (-1, -1), .4, LINE),
        ("LINEABOVE", (0, 0), (-1, 0), .4, LINE),
    ]))
    if caption_rows:
        table.setStyle(TableStyle([("SPAN", (0, 0), (-1, 0))]))
    return [table, Spacer(1, 13)]


def walk(node: Tag) -> list:
    result = []
    for child in node.children:
        if not isinstance(child, Tag):
            continue
        classes = child.get("class", [])
        if "contact-card" in classes or "section-number" in classes or "evaluation-band" in classes:
            continue
        if child.name in {"h2", "h3", "h4", "summary"}:
            style = {"h2": "MethodsH2", "h3": "MethodsH3", "h4": "MethodsH4", "summary": "MethodsH3"}[child.name]
            result.append(Paragraph(inline(child), styles[style]))
        elif child.name == "p":
            result.append(Paragraph(inline(child), styles["MethodsBody"]))
        elif child.name in {"ul", "ol"}:
            for index, item in enumerate(child.find_all("li", recursive=False), 1):
                prefix = f"{index}. " if child.name == "ol" else "• "
                result.append(Paragraph(prefix + inline(item), styles["MethodsBody"]))
        elif child.name == "table":
            result.extend(make_table(child))
        elif "equation" in classes:
            for code in child.find_all("code", recursive=False):
                result.append(Paragraph(inline(code), styles["MethodsBody"]))
            result.append(Spacer(1, 8))
        elif child.name in {"div", "details", "aside"}:
            result.extend(walk(child))
    return result


def decoration(canvas, doc) -> None:
    canvas.saveState()
    canvas.setFillColor(GARNET)
    for index, radius in enumerate((1.5, 2.3, 3.1, 3.9, 4.7)):
        canvas.circle(55 + 13 * index, 756, radius, stroke=0, fill=1)
    canvas.setFont("Methods-Bold", 7.5)
    canvas.setFillColor(INK)
    canvas.drawString(128, 753, "RISK CONTINUUM HEALTH")
    canvas.setStrokeColor(LINE)
    canvas.line(54, 740, 558, 740)
    canvas.line(54, 47, 558, 47)
    canvas.setFont("Methods", 7)
    canvas.setFillColor(MUTED)
    canvas.drawString(54, 34, "Methods & evidence v1.0  |  Engine reference 18baf7a  |  November 4, 2026")
    canvas.drawRightString(558, 34, str(doc.page))
    canvas.restoreState()


def main() -> None:
    soup = BeautifulSoup((ROOT / "methods.html").read_text(), "html.parser")
    story = [Spacer(1, 36), Paragraph("METHODS &amp; EVIDENCE", styles["MethodsCaption"]),
             Paragraph("The logic behind<br/>the conversation.", styles["MethodsTitle"]),
             Paragraph("Risk Continuum CKM", styles["MethodsH3"]),
             Paragraph("Clinical logic, Level rules, RSS weights, simulator methods, engineering and dated evaluation evidence.", styles["MethodsBody"]),
             Spacer(1, 18),
             Paragraph("Document version 1.0 · November 4, 2026<br/>Engine reference: 18baf7a8651b10cb4f047072590a5c8699e293c5<br/>RSS methodology: rss-methodology-v2", styles["MethodsSmall"]),
             Spacer(1, 18), HRFlowable(width="100%", thickness=.5, color=LINE), Spacer(1, 18),
             Paragraph("This appendix includes the full technical sections available on the methods page, including the ordered Level rules and every RSS band. It describes implementation and software verification. Independent prospective clinical effectiveness and external prognostic validation of RCCKM-specific frameworks have not been established.", styles["MethodsBody"]),
             Paragraph('<link href="https://riskcontinuum.health/methods.html" color="#861327">riskcontinuum.health/methods.html</link>', styles["MethodsBody"]),
             Spacer(1, 18), Paragraph("CONTENTS", styles["MethodsCaption"])]
    sections = soup.select("section[data-export]")
    for index, section in enumerate(sections, 1):
        story.append(Paragraph(f"{index:02d}  {escape(section.h2.get_text())}", styles["MethodsSmall"]))
    story.append(PageBreak())
    for index, section in enumerate(sections):
        if index:
            story.append(Spacer(1, 22))
        story.extend(walk(section))
    target = ROOT / "downloads/RCCKM_Methods_and_Evidence_v1.pdf"
    doc = SimpleDocTemplate(str(target), pagesize=letter, rightMargin=54, leftMargin=54,
                            topMargin=66, bottomMargin=62, title="Risk Continuum CKM: Methods & Evidence v1.0",
                            author="Shereef El-Ibiary, MD | Risk Continuum Health LLC")
    doc.build(story, onFirstPage=decoration, onLaterPages=decoration)
    print(f"Built {target.name} ({target.stat().st_size:,} bytes).")


if __name__ == "__main__":
    main()
