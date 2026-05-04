"""hero-cards 레이아웃 — 2~3개의 강조 카드를 가로로 배치.

content 스키마:
    {"cards": [{"emoji": "🚀", "label": "라벨", "text": "설명"}, ...]}
"""

from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN
from pptx.slide import Slide
from pptx.util import Inches, Pt

from .. import theme

SLIDE_WIDTH = Inches(13.333)
TITLE_TOP = Inches(0.6)
TITLE_HEIGHT = Inches(1.2)

CARDS_TOP = Inches(2.4)
CARDS_HEIGHT = Inches(4.0)
CARDS_GAP = Inches(0.4)
CARDS_MARGIN_X = Inches(0.8)


def render(slide: Slide, content: dict, title: str) -> None:
    _add_title(slide, title)
    cards = content.get("cards", [])
    if not cards:
        return
    _add_cards(slide, cards)


def _add_title(slide: Slide, title: str) -> None:
    box = slide.shapes.add_textbox(
        left=Inches(0.5),
        top=TITLE_TOP,
        width=SLIDE_WIDTH - Inches(1.0),
        height=TITLE_HEIGHT,
    )
    tf = box.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.alignment = PP_ALIGN.CENTER
    run = p.add_run()
    run.text = title
    run.font.name = theme.FONT_FAMILY
    run.font.size = Pt(theme.TITLE_SIZE_PT)
    run.font.bold = True
    run.font.color.rgb = theme.ACCENT_PURPLE


def _add_cards(slide: Slide, cards: list[dict]) -> None:
    n = len(cards)
    available = int(SLIDE_WIDTH) - 2 * int(CARDS_MARGIN_X) - int(CARDS_GAP) * (n - 1)
    card_w = available // n
    for i, card in enumerate(cards):
        left = int(CARDS_MARGIN_X) + (card_w + int(CARDS_GAP)) * i
        _add_card(slide, left, card_w, card)


def _add_card(slide: Slide, left, width, card: dict) -> None:
    shape = slide.shapes.add_shape(
        MSO_SHAPE.ROUNDED_RECTANGLE,
        left=left,
        top=CARDS_TOP,
        width=width,
        height=CARDS_HEIGHT,
    )
    shape.fill.solid()
    shape.fill.fore_color.rgb = theme.CARD_BG
    shape.line.color.rgb = theme.CARD_BORDER
    shape.line.width = Pt(1.0)
    shape.shadow.inherit = False

    tf = shape.text_frame
    tf.word_wrap = True
    tf.margin_left = Inches(0.3)
    tf.margin_right = Inches(0.3)
    tf.margin_top = Inches(0.3)
    tf.margin_bottom = Inches(0.3)

    emoji_p = tf.paragraphs[0]
    emoji_p.alignment = PP_ALIGN.CENTER
    emoji_run = emoji_p.add_run()
    emoji_run.text = card.get("emoji", "")
    emoji_run.font.size = Pt(theme.EMOJI_SIZE_PT)

    label_p = tf.add_paragraph()
    label_p.alignment = PP_ALIGN.CENTER
    label_run = label_p.add_run()
    label_run.text = card.get("label", "")
    label_run.font.name = theme.FONT_FAMILY
    label_run.font.size = Pt(theme.LABEL_SIZE_PT)
    label_run.font.color.rgb = theme.TEXT_SECONDARY

    text_p = tf.add_paragraph()
    text_p.alignment = PP_ALIGN.CENTER
    text_run = text_p.add_run()
    text_run.text = card.get("text", "")
    text_run.font.name = theme.FONT_FAMILY
    text_run.font.size = Pt(theme.TEXT_SIZE_PT)
    text_run.font.color.rgb = theme.TEXT_PRIMARY
