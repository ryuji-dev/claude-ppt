"""통합 build (HTML + PPTX 한 번에) 회귀 테스트."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from pptx import Presentation

from claude_ppt.build import build, main as build_main

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def sample_outline() -> dict:
    return json.loads((FIXTURES / "sample-outline.json").read_text(encoding="utf-8"))


def test_build_produces_html_set_and_pptx(tmp_path: Path, sample_outline: dict) -> None:
    out = tmp_path / "ep"
    build(sample_outline, out)
    assert (out / "index.html").exists()
    assert (out / "slides.pptx").exists()
    pres = Presentation(str(out / "slides.pptx"))
    assert len(pres.slides) == len(sample_outline["slides"])
    for slide in sample_outline["slides"]:
        assert (out / "slides" / f"{slide['n']:02d}-{slide['slug']}.html").exists()


def test_build_cli(tmp_path: Path, sample_outline: dict) -> None:
    outline_path = tmp_path / "outline.json"
    outline_path.write_text(json.dumps(sample_outline, ensure_ascii=False), encoding="utf-8")
    out = tmp_path / "ep"
    rc = build_main([str(outline_path), str(out)])
    assert rc == 0
    assert (out / "slides.pptx").stat().st_size > 0
    assert (out / "index.html").exists()
