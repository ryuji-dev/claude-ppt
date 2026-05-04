"""다크 테마 색상 상수 — SKILL.md §B의 미러.

원본은 .claude/skills/presentation_slides/SKILL.md §B. 색상을 변경하려면
원본을 먼저 갱신한 뒤 본 모듈을 동기화한다.
"""

from pptx.dml.color import RGBColor


def _hex(code: str) -> RGBColor:
    code = code.lstrip("#")
    return RGBColor(int(code[0:2], 16), int(code[2:4], 16), int(code[4:6], 16))


# Backgrounds & text
BG = _hex("0a0f1a")
TEXT_PRIMARY = _hex("e6edf3")
TEXT_SECONDARY = _hex("8b949e")
TEXT_MUTED = _hex("484f58")
TEXT_SUB = _hex("c9d1d9")

# Accents
ACCENT_PURPLE = _hex("7c3aed")
ACCENT_PURPLE_HOVER = _hex("a78bfa")
ACCENT_BLUE = _hex("38bdf8")

# Cards
CARD_BG = _hex("16202c")
CARD_BORDER = _hex("232c39")

# Section colors (SKILL.md §B 섹션 컬러 표)
SECTION_INTRO = _hex("7c3aed")
SECTION_1 = _hex("38bdf8")
SECTION_2 = _hex("34d399")
SECTION_3 = _hex("f97316")
SECTION_4 = _hex("ec4899")
SECTION_5 = _hex("fbbf24")
SECTION_OUTRO = _hex("e879f9")

# Typography
FONT_FAMILY = "Noto Sans KR"
TITLE_SIZE_PT = 40
LABEL_SIZE_PT = 14
TEXT_SIZE_PT = 16
EMOJI_SIZE_PT = 48
