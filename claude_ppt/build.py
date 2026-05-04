"""outline.json → HTML 세트 + slides.pptx 통합 진입점.

스킬 워크플로우의 마지막 단계에서 한 번 호출하면 두 산출물이 같이 만들어진다.

    python -m claude_ppt.build outline.json output_dir/

산출:
    output_dir/
    ├── index.html
    ├── slides.pptx
    └── slides/
        ├── 01-slug.html
        ├── ...
        └── NN-slug.html
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .html_render import render_to_dir
from .render import render


def build(outline: dict, output_dir: str | Path) -> Path:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    render_to_dir(outline, output_dir)
    render(outline, output_dir / "slides.pptx")
    return output_dir


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="claude-ppt-build",
        description="Render outline.json into HTML slides + editable .pptx in one step.",
    )
    parser.add_argument("outline", type=Path, help="Path to outline.json")
    parser.add_argument(
        "output_dir",
        type=Path,
        help="Directory to write index.html + slides/*.html + slides.pptx",
    )
    args = parser.parse_args(argv)

    outline = json.loads(args.outline.read_text(encoding="utf-8"))
    written = build(outline, args.output_dir)
    n = len(outline["slides"])
    print(f"Wrote {1 + n} HTML files + slides.pptx under {written}/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
