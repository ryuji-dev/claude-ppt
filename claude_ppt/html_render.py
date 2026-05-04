"""outline.json → HTML 슬라이드 세트 변환기.

`render_html_set(outline)` → `dict[filename, html]` 반환.
PPTX 렌더러와 동일한 outline.json IR을 입력으로 받아, 다크 테마 +
8개 레이아웃 + prev/next 키보드 네비를 포함한 HTML 세트를 산출.

보일러플레이트는 `.claude/skills/presentation_slides/SKILL.md` §C/§D와
`references/index-template.md`의 미러. 원본을 수정하면 본 모듈도 같은 PR에서
갱신할 것 (CLAUDE.md §6 SSOT 표 참조).
"""

from __future__ import annotations

import html as _html
from typing import Callable

# === 공통 보일러플레이트 ====================================================

_BASE_CSS = """\
* { margin: 0; padding: 0; box-sizing: border-box; }
body {
  background: #0a0f1a;
  font-family: 'Noto Sans KR', sans-serif;
  color: #e6edf3;
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  padding-bottom: 50px;
  opacity: 0;
  animation: fadeIn 0.4s ease forwards;
}
body.fade-out { animation: fadeOut 0.3s ease forwards; }
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(12px); }
  to { opacity: 1; transform: translateY(0); }
}
@keyframes fadeOut {
  from { opacity: 1; transform: translateY(0); }
  to { opacity: 0; transform: translateY(-12px); }
}
.container {
  width: 1280px; padding: 44px 80px;
  display: flex; flex-direction: column; align-items: center;
}
.title {
  font-size: 48px; font-weight: 900;
  background: linear-gradient(135deg, #7c3aed, #38bdf8);
  -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
  text-align: center; margin-bottom: 44px; line-height: 1.3;
}
.slide-nav {
  position: fixed; bottom: 0; left: 0; right: 0; height: 50px;
  background: rgba(10, 15, 26, 0.95);
  backdrop-filter: blur(12px); -webkit-backdrop-filter: blur(12px);
  border-top: 1px solid rgba(124, 58, 237, 0.2);
  display: flex; align-items: center; justify-content: center;
  z-index: 9999; font-family: 'Noto Sans KR', sans-serif;
}
.slide-nav-inner {
  width: 1280px; display: flex; align-items: center;
  justify-content: space-between; padding: 0 60px;
}
.slide-nav a {
  text-decoration: none; font-size: 14px; font-weight: 700;
  color: #7c3aed; transition: color 0.2s;
}
.slide-nav a:hover { color: #a78bfa; }
.slide-nav .nav-disabled { font-size: 14px; font-weight: 700; color: #484f58; cursor: default; }
.slide-nav .nav-center a { color: #8b949e; font-size: 13px; font-weight: 400; }
.slide-nav .nav-center a:hover { color: #e6edf3; }
"""

# === 레이아웃별 CSS ==========================================================

_HERO_CARDS_CSS = """\
.cards { display: flex; gap: 32px; margin-bottom: 40px; width: 100%; }
.card {
  flex: 1;
  background: linear-gradient(145deg, rgba(124, 58, 237, 0.1), rgba(56, 189, 248, 0.05));
  border: 1px solid rgba(124, 58, 237, 0.25);
  border-radius: 20px; padding: 40px 28px; text-align: center;
  position: relative; overflow: hidden;
  opacity: 0; transform: translateY(30px);
  animation: cardAppear 0.6s ease-out forwards;
}
.card:nth-child(1) { animation-delay: 0.2s; }
.card:nth-child(2) { animation-delay: 0.6s; }
.card:nth-child(3) { animation-delay: 1.0s; }
@keyframes cardAppear { to { opacity: 1; transform: translateY(0); } }
.card::before {
  content: ''; position: absolute; top: 0; left: 0; right: 0;
  height: 3px; background: linear-gradient(90deg, #7c3aed, #38bdf8);
}
.card-icon { font-size: 48px; margin-bottom: 20px; display: block; position: relative; z-index: 1; }
.card-text { font-size: 17px; font-weight: 500; line-height: 1.7; color: #c9d1d9; position: relative; z-index: 1; }
.card-label {
  display: inline-block; margin-top: 14px; padding: 4px 14px; border-radius: 20px;
  font-size: 12px; font-weight: 700; position: relative; z-index: 1;
  background: rgba(124, 58, 237, 0.2); color: #a78bfa;
}
"""

_ROADMAP_CSS = """\
.progress-section { text-align: center; width: 100%; }
.progress-bar { display: flex; gap: 8px; justify-content: center; align-items: center; }
.progress-segment { width: 180px; height: 12px; border-radius: 6px;
  background: rgba(124, 58, 237, 0.15); border: 1px solid rgba(124, 58, 237, 0.2); }
.progress-segment.filled { background: #7c3aed; border-color: #7c3aed; }
.progress-labels { display: flex; gap: 8px; justify-content: center; margin-top: 12px; }
.progress-labels span { width: 180px; text-align: center; font-size: 13px; color: #8b949e; }
"""

_COMPARISON_CSS = """\
.comparison { width: 100%; max-width: 1000px; }
.comparison-headers { display: grid; grid-template-columns: 1fr 1fr; gap: 32px; margin-bottom: 18px; }
.comp-h { text-align: center; font-size: 22px; font-weight: 700; }
.comp-h.old { color: #8b949e; }
.comp-h.new { color: #a78bfa; }
.comparison-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 32px; }
.comp-col { display: flex; flex-direction: column; gap: 12px; }
.comp-old, .comp-new {
  border-radius: 12px; padding: 16px 20px; font-size: 16px;
}
.comp-old {
  background: rgba(139, 148, 158, 0.06); border: 1px solid rgba(139, 148, 158, 0.15);
  color: #8b949e;
}
.comp-new {
  background: rgba(124, 58, 237, 0.08); border: 1px solid rgba(124, 58, 237, 0.3);
  color: #e6edf3; font-weight: 600;
}
"""

_STEP_FLOW_CSS = """\
.steps { display: flex; flex-direction: column; gap: 16px; width: 100%; max-width: 900px; }
.step {
  display: flex; align-items: flex-start; gap: 20px;
  background: rgba(139, 148, 158, 0.04); border: 1px solid rgba(139, 148, 158, 0.1);
  border-radius: 16px; padding: 24px 28px;
  opacity: 0; transform: translateX(-20px);
  animation: stepIn 0.5s ease-out forwards;
}
.step:nth-child(1) { animation-delay: 0.2s; }
.step:nth-child(2) { animation-delay: 0.4s; }
.step:nth-child(3) { animation-delay: 0.6s; }
.step:nth-child(4) { animation-delay: 0.8s; }
.step:nth-child(5) { animation-delay: 1.0s; }
@keyframes stepIn { to { opacity: 1; transform: translateX(0); } }
.step-num {
  width: 40px; height: 40px; border-radius: 50%;
  background: linear-gradient(135deg, #7c3aed, #38bdf8);
  display: flex; align-items: center; justify-content: center;
  font-weight: 900; font-size: 18px; flex-shrink: 0;
}
.step-content { flex: 1; }
.step-title { font-size: 20px; font-weight: 700; margin-bottom: 6px; }
.step-desc { font-size: 15px; color: #8b949e; line-height: 1.6; }
"""

_DIAGRAM_CSS = """\
.diagram {
  width: 100%; max-width: 900px;
  background: rgba(22, 27, 40, 0.6); border: 1px solid rgba(124, 58, 237, 0.2);
  border-radius: 20px; padding: 40px; text-align: center; margin-bottom: 30px;
}
.diagram-center {
  display: inline-block; padding: 16px 32px; border-radius: 12px;
  background: linear-gradient(135deg, rgba(124, 58, 237, 0.2), rgba(56, 189, 248, 0.1));
  border: 2px solid #7c3aed;
  font-size: 24px; font-weight: 900; margin-bottom: 20px;
}
.diagram-arrows { font-size: 28px; color: #7c3aed; margin: 12px 0; }
.diagram-row { display: flex; gap: 16px; justify-content: center; flex-wrap: wrap; }
.diagram-node {
  background: rgba(139, 148, 158, 0.06); border: 1px solid rgba(139, 148, 158, 0.15);
  border-radius: 12px; padding: 16px 20px; min-width: 140px;
  white-space: pre-line; font-size: 15px;
}
"""

_GRID_CSS = """\
.grid {
  display: grid; grid-template-columns: repeat(2, 1fr);
  gap: 20px; width: 100%; max-width: 1000px;
}
.feature-card {
  background: rgba(139, 148, 158, 0.04); border: 1px solid rgba(139, 148, 158, 0.1);
  border-radius: 16px; padding: 28px 24px; transition: all 0.25s ease;
}
.feature-card:hover { transform: translateY(-3px); }
.feature-icon { font-size: 36px; margin-bottom: 12px; display: block; }
.feature-name { font-size: 20px; font-weight: 700; margin-bottom: 6px; }
.feature-desc { font-size: 15px; color: #8b949e; line-height: 1.5; }
"""

_THREE_STAGE_CSS = """\
.flow {
  display: flex; gap: 0; align-items: stretch; width: 100%; max-width: 1000px;
}
.flow-stage {
  flex: 1; padding: 32px 24px; text-align: center;
  background: rgba(139, 148, 158, 0.04); border: 1px solid rgba(139, 148, 158, 0.1);
}
.flow-stage:first-child { border-radius: 16px 0 0 16px; }
.flow-stage:last-child { border-radius: 0 16px 16px 0; }
.flow-arrow {
  display: flex; align-items: center; font-size: 24px; color: #7c3aed; padding: 0 8px;
}
.flow-stage-num { font-size: 14px; color: #8b949e; font-weight: 700; margin-bottom: 8px; }
.flow-stage-title { font-size: 18px; font-weight: 700; margin-bottom: 6px; }
.flow-stage-desc { font-size: 14px; color: #8b949e; line-height: 1.5; }
"""

_SUMMARY_GRID_CSS = """\
.summary-grid {
  display: grid; grid-template-columns: repeat(3, 1fr);
  gap: 20px; width: 100%; margin-bottom: 44px;
}
.summary-card {
  background: rgba(22, 27, 40, 0.8); border: 1px solid rgba(139, 148, 158, 0.1);
  border-radius: 16px; padding: 32px 24px; text-align: center;
  position: relative; overflow: hidden;
  opacity: 0; transform: translateY(20px);
  animation: cardIn 0.5s ease-out forwards;
}
@keyframes cardIn { to { opacity: 1; transform: translateY(0); } }
.summary-card::before {
  content: ''; position: absolute; top: 0; left: 0; right: 0; height: 3px;
  background: linear-gradient(90deg, #7c3aed, #38bdf8);
}
.summary-card .card-label {
  font-size: 14px; font-weight: 700; color: #a78bfa; margin-bottom: 8px; display: block;
}
.summary-card .card-text { font-size: 16px; color: #c9d1d9; line-height: 1.5; }
.conclusion {
  text-align: center; padding: 28px 40px;
  background: rgba(22, 27, 40, 0.6); border: 1px solid rgba(124, 58, 237, 0.2);
  border-radius: 16px; width: 100%; max-width: 900px;
}
.conclusion-line {
  font-size: 22px; font-weight: 900; line-height: 1.8;
  background: linear-gradient(90deg, #7c3aed, #38bdf8, #34d399, #f97316, #ec4899, #fbbf24);
  background-size: 400% 400%;
  -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
  animation: gradient-shift 5s ease infinite;
}
@keyframes gradient-shift {
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}
"""


def _esc(text: str) -> str:
    return _html.escape(str(text), quote=True)


# === 레이아웃별 body 렌더러 =================================================

def _render_hero_cards(content: dict) -> str:
    cards = content.get("cards", [])
    items = "\n".join(
        f'    <div class="card">'
        f'<span class="card-icon">{_esc(c.get("emoji", ""))}</span>'
        f'<div class="card-text">{_esc(c.get("text", ""))}</div>'
        f'<span class="card-label">{_esc(c.get("label", ""))}</span>'
        f'</div>'
        for c in cards
    )
    return f'<div class="cards">\n{items}\n</div>'


def _render_roadmap(content: dict) -> str:
    steps = content.get("steps", [])
    segments = "\n".join(
        f'    <div class="progress-segment filled"></div>' for _ in steps
    )
    labels = "\n".join(f'    <span>{_esc(s.get("label", ""))}</span>' for s in steps)
    return (
        '<div class="progress-section">\n'
        '  <div class="progress-bar">\n'
        f'{segments}\n'
        '  </div>\n'
        '  <div class="progress-labels">\n'
        f'{labels}\n'
        '  </div>\n'
        '</div>'
    )


def _render_comparison_2col(content: dict) -> str:
    left = content.get("left", {})
    right = content.get("right", {})
    left_items = "\n".join(
        f'    <div class="comp-old">{_esc(item)}</div>'
        for item in left.get("items", [])
    )
    right_items = "\n".join(
        f'    <div class="comp-new">{_esc(item)}</div>'
        for item in right.get("items", [])
    )
    return (
        '<div class="comparison">\n'
        '  <div class="comparison-headers">\n'
        f'    <div class="comp-h old">{_esc(left.get("title", ""))}</div>\n'
        f'    <div class="comp-h new">{_esc(right.get("title", ""))}</div>\n'
        '  </div>\n'
        '  <div class="comparison-grid">\n'
        '    <div class="comp-col">\n'
        f'{left_items}\n'
        '    </div>\n'
        '    <div class="comp-col">\n'
        f'{right_items}\n'
        '    </div>\n'
        '  </div>\n'
        '</div>'
    )


def _render_step_flow(content: dict) -> str:
    steps = content.get("steps", [])
    items = "\n".join(
        f'  <div class="step">\n'
        f'    <div class="step-num">{i}</div>\n'
        f'    <div class="step-content">\n'
        f'      <div class="step-title">{_esc(s.get("title", ""))}</div>\n'
        f'      <div class="step-desc">{_esc(s.get("description", ""))}</div>\n'
        f'    </div>\n'
        f'  </div>'
        for i, s in enumerate(steps, start=1)
    )
    return f'<div class="steps">\n{items}\n</div>'


def _render_diagram_box(content: dict) -> str:
    center = content.get("center", {})
    nodes = content.get("nodes", [])
    nodes_html = "\n".join(
        f'    <div class="diagram-node">{_esc(n.get("label", ""))}</div>'
        for n in nodes
    )
    return (
        '<div class="diagram">\n'
        f'  <div class="diagram-center">{_esc(center.get("label", ""))}</div>\n'
        '  <div class="diagram-arrows">↓</div>\n'
        '  <div class="diagram-row">\n'
        f'{nodes_html}\n'
        '  </div>\n'
        '</div>'
    )


def _render_grid_2x2(content: dict) -> str:
    cards = content.get("cards", [])
    items = "\n".join(
        f'  <div class="feature-card">\n'
        f'    <span class="feature-icon">{_esc(c.get("emoji", ""))}</span>\n'
        f'    <div class="feature-name">{_esc(c.get("title", ""))}</div>\n'
        f'    <div class="feature-desc">{_esc(c.get("description", ""))}</div>\n'
        f'  </div>'
        for c in cards
    )
    return f'<div class="grid">\n{items}\n</div>'


def _render_three_stage_flow(content: dict) -> str:
    stages = content.get("stages", [])
    if len(stages) != 3:
        raise ValueError(
            f"three-stage-flow expects exactly 3 stages, got {len(stages)}"
        )
    parts: list[str] = []
    for i, stage in enumerate(stages, start=1):
        parts.append(
            f'  <div class="flow-stage">\n'
            f'    <div class="flow-stage-num">STAGE {i}</div>\n'
            f'    <div class="flow-stage-title">{_esc(stage.get("title", ""))}</div>\n'
            f'    <div class="flow-stage-desc">{_esc(stage.get("description", ""))}</div>\n'
            f'  </div>'
        )
        if i < 3:
            parts.append('  <div class="flow-arrow">→</div>')
    return '<div class="flow">\n' + "\n".join(parts) + "\n</div>"


def _render_summary_grid(content: dict) -> str:
    cards = content.get("cards", [])
    conclusion = content.get("conclusion", "")
    cards_html = "\n".join(
        f'  <div class="summary-card">\n'
        f'    <span class="card-label">{_esc(c.get("label", ""))}</span>\n'
        f'    <div class="card-text">{_esc(c.get("text", ""))}</div>\n'
        f'  </div>'
        for c in cards
    )
    return (
        f'<div class="summary-grid">\n{cards_html}\n</div>\n'
        f'<div class="conclusion">\n'
        f'  <div class="conclusion-line">{_esc(conclusion)}</div>\n'
        f'</div>'
    )


_LAYOUT_RENDERERS: dict[str, tuple[Callable[[dict], str], str]] = {
    "hero-cards": (_render_hero_cards, _HERO_CARDS_CSS),
    "roadmap": (_render_roadmap, _ROADMAP_CSS),
    "comparison-2col": (_render_comparison_2col, _COMPARISON_CSS),
    "step-flow": (_render_step_flow, _STEP_FLOW_CSS),
    "diagram-box": (_render_diagram_box, _DIAGRAM_CSS),
    "grid-2x2": (_render_grid_2x2, _GRID_CSS),
    "three-stage-flow": (_render_three_stage_flow, _THREE_STAGE_CSS),
    "summary-grid": (_render_summary_grid, _SUMMARY_GRID_CSS),
}


# === 슬라이드 / 인덱스 조립 =================================================

def _slide_filename(slide: dict) -> str:
    return f"{slide['n']:02d}-{slide['slug']}.html"


def _render_nav(idx: int, total: int, prev_file: str | None, next_file: str | None) -> tuple[str, str]:
    """nav HTML과 keydown JS를 (nav, js) 튜플로 반환."""
    if prev_file:
        left = (
            f'<div class="nav-left">'
            f'<a href="{prev_file}" onclick="event.preventDefault(); navigateTo(this.href)">&larr; 이전</a>'
            f'</div>'
        )
    else:
        left = '<div class="nav-left"><span class="nav-disabled">&larr; 이전</span></div>'

    if next_file:
        right = (
            f'<div class="nav-right">'
            f'<a href="{next_file}" onclick="event.preventDefault(); navigateTo(this.href)">다음 &rarr;</a>'
            f'</div>'
        )
    else:
        right = '<div class="nav-right"><span class="nav-disabled">다음 &rarr;</span></div>'

    nav = (
        '<nav class="slide-nav">\n'
        '  <div class="slide-nav-inner">\n'
        f'    {left}\n'
        f'    <div class="nav-center"><a href="index.html">{idx:02d} / {total:02d}</a></div>\n'
        f'    {right}\n'
        '  </div>\n'
        '</nav>'
    )

    js_lines = []
    if prev_file:
        js_lines.append(f"  if (e.key === 'ArrowLeft') navigateTo('{prev_file}');")
    if next_file:
        js_lines.append(f"  if (e.key === 'ArrowRight') navigateTo('{next_file}');")
    js = (
        "function navigateTo(url) {\n"
        "  document.body.classList.add('fade-out');\n"
        "  setTimeout(function() { window.location.href = url; }, 300);\n"
        "}\n"
        "document.addEventListener('keydown', function(e) {\n"
        + ("\n".join(js_lines) + "\n" if js_lines else "")
        + "});"
    )
    return nav, js


def _render_slide(slide: dict, prev_file: str | None, next_file: str | None, total: int) -> str:
    layout = slide["layout"]
    if layout not in _LAYOUT_RENDERERS:
        raise ValueError(
            f"Unknown layout: {layout!r}. Known: {sorted(_LAYOUT_RENDERERS)}"
        )
    body_fn, layout_css = _LAYOUT_RENDERERS[layout]
    body = body_fn(slide.get("content", {}))
    nav, js = _render_nav(slide["n"], total, prev_file, next_file)
    title = _esc(slide["title"])
    return (
        '<!DOCTYPE html>\n'
        '<html lang="ko">\n'
        '<head>\n'
        '<meta charset="UTF-8">\n'
        '<meta name="viewport" content="width=1280">\n'
        f'<title>{title}</title>\n'
        '<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700;900&display=swap" rel="stylesheet">\n'
        '<style>\n'
        f'{_BASE_CSS}\n'
        f'{layout_css}\n'
        '</style>\n'
        '</head>\n'
        '<body>\n'
        '<div class="container">\n'
        f'  <h1 class="title">{title}</h1>\n'
        f'{body}\n'
        '</div>\n'
        f'{nav}\n'
        '<script>\n'
        f'{js}\n'
        '</script>\n'
        '</body>\n'
        '</html>\n'
    )


# === Index =================================================================

_INDEX_CSS = """\
* { margin: 0; padding: 0; box-sizing: border-box; }
body {
  background: #0a0f1a;
  font-family: 'Noto Sans KR', sans-serif;
  color: #e6edf3;
  min-height: 100vh;
  display: flex; justify-content: center;
  padding: 60px 0 80px;
  opacity: 0; animation: fadeIn 0.4s ease forwards;
}
body.fade-out { animation: fadeOut 0.3s ease forwards; }
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(12px); }
  to { opacity: 1; transform: translateY(0); }
}
@keyframes fadeOut {
  from { opacity: 1; transform: translateY(0); }
  to { opacity: 0; transform: translateY(-12px); }
}
.container { width: 1280px; padding: 0 80px; }
.page-title {
  font-size: 42px; font-weight: 900;
  background: linear-gradient(135deg, #7c3aed, #38bdf8);
  -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;
  text-align: center; margin-bottom: 10px;
}
.page-subtitle {
  text-align: center; font-size: 16px; color: #8b949e; margin-bottom: 50px;
}
.section { margin-bottom: 36px; }
.section-header {
  font-size: 18px; font-weight: 700; padding: 12px 20px;
  border-left: 4px solid; margin-bottom: 16px;
  display: flex; align-items: center; gap: 12px;
}
.num-range {
  display: inline-block; font-size: 12px; font-weight: 700; color: white;
  padding: 3px 10px; border-radius: 10px;
}
.grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; }
.card {
  display: flex; flex-direction: column; gap: 6px; padding: 18px 20px;
  background: rgba(139,148,158,0.04); border: 1px solid rgba(139,148,158,0.1);
  border-radius: 12px; text-decoration: none; transition: all 0.25s ease;
}
.card:hover { transform: translateY(-3px); }
.card .card-num { font-size: 28px; font-weight: 900; }
.card .card-title { font-size: 14px; font-weight: 700; color: #c9d1d9; }
.card .card-file { font-size: 11px; color: #484f58; font-family: 'Courier New', monospace; }
"""


def _section_css(section_id: str, color: str) -> str:
    """섹션별 색상 코딩 CSS를 동적으로 생성 (outline의 section.color 사용)."""
    cls = f"section-{section_id}"
    return (
        f".{cls} .section-header {{ border-color: {color}; color: {color}; }}\n"
        f".{cls} .num-range {{ background: {color}; }}\n"
        f".{cls} .card:hover {{ border-color: {color}; }}\n"
        f".{cls} .card .card-num {{ color: {color}; }}\n"
    )


def _render_index(outline: dict) -> str:
    title = _esc(outline["title"])
    slides = outline["slides"]
    sections = outline["sections"]
    total = len(slides)

    # 섹션별 색상 CSS
    extra_css = "".join(_section_css(s["id"], s["color"]) for s in sections)

    # 섹션별 슬라이드 그룹
    section_blocks = []
    for section in sections:
        sid = section["id"]
        section_slides = [s for s in slides if s["section"] == sid]
        if not section_slides:
            continue
        nums = [s["n"] for s in section_slides]
        num_range = f"{min(nums):02d}-{max(nums):02d}"
        cards = "\n".join(
            f'      <a class="card" href="{_slide_filename(s)}" onclick="event.preventDefault(); navigateTo(this.href)">\n'
            f'        <span class="card-num">{s["n"]:02d}</span>\n'
            f'        <span class="card-title">{_esc(s["title"])}</span>\n'
            f'        <span class="card-file">{_slide_filename(s)}</span>\n'
            f'      </a>'
            for s in section_slides
        )
        section_blocks.append(
            f'  <div class="section section-{sid}">\n'
            f'    <div class="section-header"><span class="num-range">{num_range}</span> {_esc(section["name"])}</div>\n'
            f'    <div class="grid">\n'
            f'{cards}\n'
            f'    </div>\n'
            f'  </div>'
        )

    sections_html = "\n".join(section_blocks)
    return (
        '<!DOCTYPE html>\n'
        '<html lang="ko">\n'
        '<head>\n'
        '<meta charset="UTF-8">\n'
        '<meta name="viewport" content="width=1280">\n'
        f'<title>{title} — 비주얼 자료</title>\n'
        '<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700;900&display=swap" rel="stylesheet">\n'
        '<style>\n'
        f'{_INDEX_CSS}\n'
        f'{extra_css}'
        '</style>\n'
        '</head>\n'
        '<body>\n'
        '<div class="container">\n'
        f'  <h1 class="page-title">{title} — 비주얼 자료</h1>\n'
        f'  <p class="page-subtitle">전체 {total}개 슬라이드 · 클릭하여 개별 페이지로 이동</p>\n'
        f'{sections_html}\n'
        '</div>\n'
        '<script>\n'
        'function navigateTo(url) {\n'
        "  document.body.classList.add('fade-out');\n"
        '  setTimeout(function() { window.location.href = url; }, 300);\n'
        '}\n'
        '</script>\n'
        '</body>\n'
        '</html>\n'
    )


# === 공개 API ===============================================================

def render_html_set(outline: dict) -> dict[str, str]:
    """outline.json (dict 또는 Outline.model_dump 결과) → {filename: html} 매핑.

    `index.html` + `NN-slug.html` × len(slides)를 산출.
    """
    slides = outline["slides"]
    total = len(slides)
    files: dict[str, str] = {}

    for i, slide in enumerate(slides):
        prev_file = _slide_filename(slides[i - 1]) if i > 0 else None
        next_file = _slide_filename(slides[i + 1]) if i < total - 1 else None
        files[_slide_filename(slide)] = _render_slide(slide, prev_file, next_file, total)

    files["index.html"] = _render_index(outline)
    return files
