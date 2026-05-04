"""outline.json 스키마 — Pydantic 모델로 LLM 출력 검증.

LLM이 토해낸 JSON이 `claude_ppt.layouts`가 받아들일 수 있는 형태인지 보장.
content 구조는 layout마다 다르므로 dict로 받아 layout 모듈이 자체 검증한다.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, field_validator

from .layouts import LAYOUTS

LayoutName = Literal[
    "hero-cards",
    "roadmap",
    "comparison-2col",
    "step-flow",
    "diagram-box",
    "grid-2x2",
    "three-stage-flow",
    "summary-grid",
]


class Section(BaseModel):
    id: str
    name: str
    color: str = Field(pattern=r"^#[0-9a-fA-F]{6}$")


class Slide(BaseModel):
    n: int = Field(ge=1)
    slug: str = Field(pattern=r"^[a-z0-9]+(-[a-z0-9]+)*$")
    title: str = Field(min_length=1)
    section: str
    layout: LayoutName
    content: dict


class Outline(BaseModel):
    title: str = Field(min_length=1)
    channel: str = Field(min_length=1)
    episode: str = Field(min_length=1)
    sections: list[Section] = Field(min_length=1)
    slides: list[Slide] = Field(min_length=1)

    @field_validator("slides")
    @classmethod
    def slides_must_be_consecutive(cls, slides: list[Slide]) -> list[Slide]:
        for i, slide in enumerate(slides, start=1):
            if slide.n != i:
                raise ValueError(
                    f"slides[].n must start at 1 and be consecutive; got {slide.n} at index {i - 1}"
                )
        return slides

    def assert_section_ids_consistent(self) -> None:
        section_ids = {s.id for s in self.sections}
        for slide in self.slides:
            if slide.section not in section_ids:
                raise ValueError(
                    f"slide #{slide.n} references unknown section {slide.section!r}; "
                    f"known: {sorted(section_ids)}"
                )

    def assert_layouts_known(self) -> None:
        for slide in self.slides:
            if slide.layout not in LAYOUTS:
                raise ValueError(
                    f"slide #{slide.n} uses unknown layout {slide.layout!r}; "
                    f"known: {sorted(LAYOUTS)}"
                )

    def validate_full(self) -> None:
        """필드 단위 검증 후, 교차 참조 검증을 추가로 수행."""
        self.assert_section_ids_consistent()
        self.assert_layouts_known()
