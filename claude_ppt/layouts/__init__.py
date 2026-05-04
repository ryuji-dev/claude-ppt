"""레이아웃 디스패처 — outline의 `layout` 문자열을 렌더 함수로 매핑."""

from typing import Callable

from pptx.slide import Slide

from . import (
    comparison_2col,
    diagram_box,
    grid_2x2,
    hero_cards,
    roadmap,
    step_flow,
    summary_grid,
    three_stage_flow,
)

LayoutRenderer = Callable[[Slide, dict, str], None]

LAYOUTS: dict[str, LayoutRenderer] = {
    "hero-cards": hero_cards.render,
    "roadmap": roadmap.render,
    "comparison-2col": comparison_2col.render,
    "step-flow": step_flow.render,
    "diagram-box": diagram_box.render,
    "grid-2x2": grid_2x2.render,
    "three-stage-flow": three_stage_flow.render,
    "summary-grid": summary_grid.render,
}


def get_renderer(layout: str) -> LayoutRenderer:
    if layout not in LAYOUTS:
        raise ValueError(
            f"Unknown layout: {layout!r}. Known layouts: {sorted(LAYOUTS)}"
        )
    return LAYOUTS[layout]
