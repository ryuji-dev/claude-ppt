"""HTML 렌더러 회귀 테스트.

8개 레이아웃을 모두 포함한 픽스처에서 9개 파일(슬라이드 8 + index)이
생성되는지, 핵심 보일러플레이트와 콘텐츠 키워드가 포함되는지 확인.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from claude_ppt.html_render import main as html_main, render_html_set, render_to_dir

FIXTURES = Path(__file__).parent / "fixtures"


@pytest.fixture
def sample_outline() -> dict:
    return json.loads((FIXTURES / "sample-outline.json").read_text(encoding="utf-8"))


def test_render_html_set_returns_nine_files(sample_outline: dict) -> None:
    files = render_html_set(sample_outline)
    assert len(files) == 9
    assert "index.html" in files
    expected_slide_files = {
        f"{slide['n']:02d}-{slide['slug']}.html" for slide in sample_outline["slides"]
    }
    assert set(files) == {"index.html"} | expected_slide_files


def test_each_slide_includes_title_and_boilerplate(sample_outline: dict) -> None:
    files = render_html_set(sample_outline)
    for slide in sample_outline["slides"]:
        filename = f"{slide['n']:02d}-{slide['slug']}.html"
        html = files[filename]
        assert "<!DOCTYPE html>" in html
        assert "Noto Sans KR" in html
        assert "#0a0f1a" in html  # 다크 배경
        assert slide["title"] in html


def test_first_slide_disables_prev_nav(sample_outline: dict) -> None:
    files = render_html_set(sample_outline)
    first = sample_outline["slides"][0]
    html = files[f"{first['n']:02d}-{first['slug']}.html"]
    assert "nav-disabled" in html  # 이전 비활성화
    assert "&larr; 이전" in html  # 텍스트는 있되 비활성


def test_last_slide_disables_next_nav(sample_outline: dict) -> None:
    files = render_html_set(sample_outline)
    last = sample_outline["slides"][-1]
    html = files[f"{last['n']:02d}-{last['slug']}.html"]
    assert "nav-disabled" in html
    assert "다음 &rarr;" in html


def test_middle_slide_has_both_nav_links(sample_outline: dict) -> None:
    files = render_html_set(sample_outline)
    slides = sample_outline["slides"]
    middle = slides[len(slides) // 2]
    prev = slides[len(slides) // 2 - 1]
    nxt = slides[len(slides) // 2 + 1]
    html = files[f"{middle['n']:02d}-{middle['slug']}.html"]
    prev_filename = f"{prev['n']:02d}-{prev['slug']}.html"
    next_filename = f"{nxt['n']:02d}-{nxt['slug']}.html"
    assert prev_filename in html
    assert next_filename in html


def test_index_lists_all_slides_with_section_blocks(sample_outline: dict) -> None:
    files = render_html_set(sample_outline)
    index = files["index.html"]
    assert sample_outline["title"] in index
    for slide in sample_outline["slides"]:
        filename = f"{slide['n']:02d}-{slide['slug']}.html"
        assert filename in index
        assert slide["title"] in index
    # 섹션 색상 코딩이 적용되어야 함
    for section in sample_outline["sections"]:
        assert f"section-{section['id']}" in index or section["id"] in index


def test_hero_cards_content_keywords_present(sample_outline: dict) -> None:
    files = render_html_set(sample_outline)
    hero = next(s for s in sample_outline["slides"] if s["layout"] == "hero-cards")
    html = files[f"{hero['n']:02d}-{hero['slug']}.html"]
    for card in hero["content"]["cards"]:
        assert card["text"] in html
        assert card["emoji"] in html


def test_summary_grid_includes_conclusion(sample_outline: dict) -> None:
    files = render_html_set(sample_outline)
    summary = next(s for s in sample_outline["slides"] if s["layout"] == "summary-grid")
    html = files[f"{summary['n']:02d}-{summary['slug']}.html"]
    assert summary["content"]["conclusion"] in html
    for card in summary["content"]["cards"]:
        assert card["text"] in html


def test_unknown_layout_raises(sample_outline: dict) -> None:
    sample_outline["slides"][0]["layout"] = "no-such-layout"
    with pytest.raises(ValueError, match="no-such-layout"):
        render_html_set(sample_outline)


def test_render_to_dir_writes_index_at_root_and_slides_in_subdir(
    tmp_path: pytest.TempPathFactory, sample_outline: dict
) -> None:
    out = tmp_path / "out"
    render_to_dir(sample_outline, out)
    assert (out / "index.html").exists()
    slides_dir = out / "slides"
    for slide in sample_outline["slides"]:
        assert (slides_dir / f"{slide['n']:02d}-{slide['slug']}.html").exists()


def test_html_cli_writes_files(tmp_path, sample_outline: dict) -> None:
    outline_path = tmp_path / "outline.json"
    outline_path.write_text(json.dumps(sample_outline, ensure_ascii=False), encoding="utf-8")
    out_dir = tmp_path / "out"
    rc = html_main([str(outline_path), str(out_dir)])
    assert rc == 0
    assert (out_dir / "index.html").exists()
    first = sample_outline["slides"][0]
    assert (out_dir / "slides" / f"{first['n']:02d}-{first['slug']}.html").exists()
