"""Render ``Resumen de Trabajo Final.md`` as a styled A4 PDF."""

from __future__ import annotations

import html
import re
import tempfile
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib import font_manager
from PIL import Image as PILImage
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    Image,
    KeepTogether,
    ListFlowable,
    ListItem,
    Paragraph,
    Preformatted,
    SimpleDocTemplate,
    Spacer,
)


ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "Resumen de Trabajo Final.md"
TARGET = ROOT / "Resumen de Trabajo Final.pdf"
INK = colors.HexColor("#17263a")
MUTED = colors.HexColor("#52657a")
ACCENT = colors.HexColor("#167d9a")
SOFT = colors.HexColor("#f1f6f8")


def register_fonts():
    """Register Unicode fonts bundled with the Matplotlib installation."""
    regular = font_manager.findfont("DejaVu Sans")
    bold = font_manager.findfont(font_manager.FontProperties(family="DejaVu Sans", weight="bold"))
    italic = font_manager.findfont(font_manager.FontProperties(family="DejaVu Sans", style="italic"))
    mono = font_manager.findfont("DejaVu Sans Mono")
    pdfmetrics.registerFont(TTFont("DejaVuSans", regular))
    pdfmetrics.registerFont(TTFont("DejaVuSans-Bold", bold))
    pdfmetrics.registerFont(TTFont("DejaVuSans-Italic", italic))
    pdfmetrics.registerFont(TTFont("DejaVuSansMono", mono))
    pdfmetrics.registerFontFamily(
        "DejaVuSans", normal="DejaVuSans", bold="DejaVuSans-Bold", italic="DejaVuSans-Italic"
    )


def inline_markup(text):
    """Convert the small Markdown inline subset used by the report."""
    code_fragments = []

    def store_code(match):
        code_fragments.append(match.group(1))
        return f"@@CODE{len(code_fragments) - 1}@@"

    text = re.sub(r"`([^`]+)`", store_code, text)
    text = html.escape(text, quote=True)
    text = re.sub(
        r"\[([^\]]+)\]\((https?://[^)]+)\)",
        r'<a href="\2" color="#0b6983">\1</a>',
        text,
    )
    text = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", text)
    text = re.sub(r"(?<!\*)\*([^*]+)\*", r"<i>\1</i>", text)
    for index, fragment in enumerate(code_fragments):
        replacement = f'<font name="DejaVuSansMono" color="#28465c">{html.escape(fragment)}</font>'
        text = text.replace(f"@@CODE{index}@@", replacement)
    return text


def make_styles():
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle(
            "Title", parent=base["Title"], fontName="DejaVuSans-Bold", fontSize=24,
            leading=29, textColor=INK, alignment=TA_LEFT, spaceAfter=11 * mm,
            borderColor=ACCENT, borderWidth=0, borderPadding=0,
        ),
        "subtitle": ParagraphStyle(
            "Subtitle", parent=base["Heading2"], fontName="DejaVuSans-Bold", fontSize=16,
            leading=20, textColor=ACCENT, spaceAfter=8 * mm,
        ),
        "h2": ParagraphStyle(
            "H2", parent=base["Heading2"], fontName="DejaVuSans-Bold", fontSize=15,
            leading=19, textColor=INK, spaceBefore=7 * mm, spaceAfter=3 * mm,
            keepWithNext=True,
        ),
        "h3": ParagraphStyle(
            "H3", parent=base["Heading3"], fontName="DejaVuSans-Bold", fontSize=11.5,
            leading=15, textColor=ACCENT, spaceBefore=4 * mm, spaceAfter=2 * mm,
            keepWithNext=True,
        ),
        "body": ParagraphStyle(
            "Body", parent=base["BodyText"], fontName="DejaVuSans", fontSize=9.6,
            leading=14.2, textColor=INK, spaceAfter=3.1 * mm, alignment=TA_LEFT,
            allowWidows=0, allowOrphans=0,
        ),
        "bullet": ParagraphStyle(
            "Bullet", parent=base["BodyText"], fontName="DejaVuSans", fontSize=9.4,
            leading=13.6, textColor=INK, leftIndent=0, spaceAfter=1.1 * mm,
        ),
        "numbered": ParagraphStyle(
            "Numbered", parent=base["BodyText"], fontName="DejaVuSans", fontSize=9.5,
            leading=14, textColor=INK, leftIndent=5 * mm, firstLineIndent=-5 * mm,
            spaceAfter=3 * mm,
        ),
        "code": ParagraphStyle(
            "Code", parent=base["Code"], fontName="DejaVuSansMono", fontSize=8.1,
            leading=11.2, textColor=colors.HexColor("#24394f"), backColor=SOFT,
            borderColor=colors.HexColor("#cbd6df"), borderWidth=0.7,
            borderPadding=8, leftIndent=2 * mm, rightIndent=2 * mm,
            spaceBefore=2 * mm, spaceAfter=4 * mm,
        ),
    }


def equation_image(formula, directory, index, max_width):
    """Render one display equation with Matplotlib mathtext."""
    formula = " ".join(part.strip() for part in formula.splitlines() if part.strip())
    path = Path(directory) / f"equation_{index:02d}.png"
    figure = plt.figure(figsize=(9, 0.8), facecolor="white")
    figure.text(0.5, 0.5, f"${formula}$", ha="center", va="center", fontsize=17, color="#17263a")
    figure.savefig(path, dpi=220, bbox_inches="tight", pad_inches=0.12, transparent=False)
    plt.close(figure)
    with PILImage.open(path) as image:
        width, height = image.size
    render_width = min(max_width, width / 220 * 72)
    render_height = render_width * height / width
    return Image(str(path), width=render_width, height=render_height)


def is_special(line):
    stripped = line.strip()
    return (
        not stripped
        or stripped.startswith("#")
        or stripped.startswith("```")
        or stripped == r"\["
        or stripped.startswith("- ")
        or bool(re.match(r"^\d+\.\s", stripped))
    )


def parse_markdown(text, styles, equation_dir, content_width):
    lines = text.splitlines()
    story = []
    index = 0
    equation_index = 0
    first_h2 = True

    while index < len(lines):
        line = lines[index]
        stripped = line.strip()
        if not stripped:
            index += 1
            continue

        if stripped.startswith("```"):
            index += 1
            block = []
            while index < len(lines) and not lines[index].strip().startswith("```"):
                block.append(lines[index])
                index += 1
            index += 1
            story.append(Preformatted("\n".join(block), styles["code"], maxLineLength=100))
            continue

        if stripped == r"\[":
            index += 1
            formula = []
            while index < len(lines) and lines[index].strip() != r"\]":
                formula.append(lines[index])
                index += 1
            index += 1
            image = equation_image("\n".join(formula), equation_dir, equation_index, content_width * 0.88)
            equation_index += 1
            story.extend([Spacer(1, 1.5 * mm), KeepTogether([image]), Spacer(1, 3 * mm)])
            continue

        heading = re.match(r"^(#{1,3})\s+(.+)$", stripped)
        if heading:
            level = len(heading.group(1))
            content = inline_markup(heading.group(2))
            if level == 1:
                story.append(Paragraph(content, styles["title"]))
            elif level == 2 and first_h2:
                story.append(Paragraph(content, styles["subtitle"]))
                first_h2 = False
            elif level == 2:
                story.append(Paragraph(content, styles["h2"]))
            else:
                story.append(Paragraph(content, styles["h3"]))
            index += 1
            continue

        if stripped.startswith("- "):
            items = []
            while index < len(lines) and lines[index].strip().startswith("- "):
                item = lines[index].strip()[2:].strip()
                items.append(ListItem(Paragraph(inline_markup(item), styles["bullet"]), leftIndent=4 * mm))
                index += 1
            story.append(
                ListFlowable(
                    items, bulletType="bullet", start="circle", leftIndent=8 * mm,
                    bulletFontName="DejaVuSans", bulletFontSize=7, spaceAfter=3 * mm,
                )
            )
            continue

        numbered = re.match(r"^(\d+)\.\s+(.+)$", stripped)
        if numbered:
            content = f"<b>{numbered.group(1)}.</b> {inline_markup(numbered.group(2))}"
            story.append(Paragraph(content, styles["numbered"]))
            index += 1
            continue

        paragraph = [stripped]
        index += 1
        while index < len(lines) and not is_special(lines[index]):
            paragraph.append(lines[index].strip())
            index += 1
        story.append(Paragraph(inline_markup(" ".join(paragraph)), styles["body"]))

    return story


def draw_page(canvas, document):
    """Add a discreet running header and page number."""
    canvas.saveState()
    page = canvas.getPageNumber()
    width, height = A4
    if page > 1:
        canvas.setStrokeColor(colors.HexColor("#cbd6df"))
        canvas.setLineWidth(0.5)
        canvas.line(18 * mm, height - 13 * mm, width - 18 * mm, height - 13 * mm)
        canvas.setFont("DejaVuSans", 7.5)
        canvas.setFillColor(MUTED)
        canvas.drawString(18 * mm, height - 10.5 * mm, "Resumen de Trabajo Final")
    canvas.setFont("DejaVuSans", 8)
    canvas.setFillColor(MUTED)
    canvas.drawCentredString(width / 2, 10 * mm, str(page))
    canvas.restoreState()


def build_pdf(source=SOURCE, target=TARGET):
    register_fonts()
    styles = make_styles()
    document = SimpleDocTemplate(
        str(target), pagesize=A4,
        leftMargin=18 * mm, rightMargin=18 * mm,
        topMargin=19 * mm, bottomMargin=18 * mm,
        title="Resumen de Trabajo Final",
        author="Neural Network Exploration",
        subject="Metodología de simulación neuromotora con neuronas de Izhikevich",
    )
    with tempfile.TemporaryDirectory(prefix="summary_pdf_") as temporary:
        story = parse_markdown(source.read_text(encoding="utf-8"), styles, temporary, document.width)
        document.build(story, onFirstPage=draw_page, onLaterPages=draw_page)
    return target


if __name__ == "__main__":
    print(build_pdf())
