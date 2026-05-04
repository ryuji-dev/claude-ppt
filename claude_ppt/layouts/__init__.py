"""레이아웃 디스패처 — outline의 `layout` 문자열을 렌더 함수로 매핑."""

from typing import Callable

from pptx.slide import Slide

from . import hero_cards

LayoutRenderer = Callable[[Slide, dict, str], None]

LAYOUTS: dict[str, LayoutRenderer] = {
    "hero-cards": hero_cards.render,
}


def get_renderer(layout: str) -> LayoutRenderer:
    if layout not in LAYOUTS:
        raise ValueError(
            f"Unknown layout: {layout!r}. Known layouts: {sorted(LAYOUTS)}"
        )
    return LAYOUTS[layout]
