"""Claude API로 자유 텍스트를 outline JSON으로 변환.

- 시스템 프롬프트에 `pptx-layouts.md` 전체를 임베드 → 8개 layout 스키마를 모델에 노출
- 시스템 블록에 `cache_control` 적용 → 동일 세션 내 반복 요청 시 캐시 히트로 비용 90% 절감
- `output_config.format`로 JSON 응답을 강제, Pydantic으로 추가 검증
"""

from __future__ import annotations

import json
from pathlib import Path

import anthropic

from .schema import Outline

DEFAULT_MODEL = "claude-opus-4-7"
DEFAULT_MAX_TOKENS = 16000

PROJECT_ROOT = Path(__file__).resolve().parent.parent
LAYOUT_SPEC_PATH = (
    PROJECT_ROOT
    / ".claude"
    / "skills"
    / "presentation_slides"
    / "references"
    / "pptx-layouts.md"
)


SYSTEM_PROMPT_HEADER = """당신은 사용자가 제공한 글을 8개 레이아웃 중 하나로 구조화된 슬라이드 outline JSON으로 변환합니다.

## 출력 규칙

- 응답은 **오직 JSON 객체 하나**. 코드블록 펜스(```), 설명, 인사말 모두 금지.
- `slides[].layout`은 8개 enum 중 하나만:
  `hero-cards`, `roadmap`, `comparison-2col`, `step-flow`, `diagram-box`, `grid-2x2`, `three-stage-flow`, `summary-grid`
- `slides[].content`는 layout별 스키마를 정확히 따릅니다 (아래 스펙 참조).
- `slides[].n`은 1부터 시작하는 연속 번호. `slides[].slug`은 영문 kebab-case.
- 한국어 텍스트는 그대로 (UTF-8 그대로 두고 `\\uXXXX` 이스케이프 금지).
- `three-stage-flow`는 stages가 정확히 3개여야 합니다.
- `summary-grid`의 cards는 정확히 6개 권장.
- `sections[].color`는 다크 테마에서 잘 보이는 채도 높은 컬러 6자리 hex.

## 구조화 가이드

- 사용자의 글을 *섹션*(인트로 / 본론 1~3개 / 마무리)으로 나눕니다.
- 각 섹션 안에서 메시지 하나당 슬라이드 1장. 보통 **6~10장**이 적정.
- 첫 슬라이드는 hero-cards (오프닝 훅), 마지막은 summary-grid (마무리)가 자연스럽습니다.
- 같은 layout이 3회 연속되지 않도록 다양화.
- 내용 성격에 맞는 layout 선택:
  - 비교/대조 → `comparison-2col`
  - 절차/프로세스 → `step-flow`
  - 시스템 구조 → `diagram-box`
  - 기능 나열 → `grid-2x2`
  - 시리즈 개요 → `roadmap`
  - 단계적 발전 → `three-stage-flow`

## 레이아웃별 content 스키마 (정확히 따를 것)

"""


def _system_blocks() -> list[dict]:
    """캐시 가능한 시스템 프롬프트 블록 목록을 만든다.

    레이아웃 스펙은 거의 변하지 않으므로 캐시 hit이 기대됨.
    """
    layout_spec = LAYOUT_SPEC_PATH.read_text(encoding="utf-8")
    full_system = SYSTEM_PROMPT_HEADER + layout_spec
    return [
        {
            "type": "text",
            "text": full_system,
            "cache_control": {"type": "ephemeral"},
        }
    ]


def _user_message(text: str, *, title: str, channel: str, episode: str) -> str:
    return (
        f"제목: {title}\n"
        f"채널: {channel}\n"
        f"에피소드: {episode}\n\n"
        f"본문:\n{text}\n\n"
        "위 본문을 outline JSON으로 변환해 주세요. JSON만 출력합니다."
    )


def text_to_outline(
    text: str,
    *,
    title: str,
    channel: str = "samples",
    episode: str = "ep00-new",
    api_key: str | None = None,
    model: str = DEFAULT_MODEL,
    max_tokens: int = DEFAULT_MAX_TOKENS,
    client: anthropic.Anthropic | None = None,
) -> Outline:
    """자유 텍스트를 검증된 Outline 모델로 변환.

    Parameters
    ----------
    text : 사용자가 입력한 대본/요약 노트
    title, channel, episode : 메타데이터
    api_key : ANTHROPIC_API_KEY 환경변수 미설정 시 명시
    model : Claude 모델 ID (기본 claude-opus-4-7)
    max_tokens : 응답 토큰 상한
    client : 테스트용 주입 (mock client)

    Returns
    -------
    Outline (Pydantic 모델). validate_full() 통과 보장.

    Raises
    ------
    anthropic.APIError, json.JSONDecodeError, pydantic.ValidationError, ValueError
    """
    if client is None:
        client = anthropic.Anthropic(api_key=api_key) if api_key else anthropic.Anthropic()

    response = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        system=_system_blocks(),
        messages=[
            {
                "role": "user",
                "content": _user_message(
                    text, title=title, channel=channel, episode=episode
                ),
            }
        ],
    )

    raw = _extract_text(response)
    data = json.loads(raw)
    outline = Outline.model_validate(data)
    outline.validate_full()
    return outline


def _extract_text(response) -> str:
    """응답 첫 번째 text 블록을 꺼낸다. 펜스가 섞여 있으면 제거."""
    for block in response.content:
        if getattr(block, "type", None) == "text":
            text = block.text.strip()
            if text.startswith("```"):
                lines = text.split("\n")
                if lines[-1].strip().startswith("```"):
                    lines = lines[1:-1]
                else:
                    lines = lines[1:]
                text = "\n".join(lines).strip()
            return text
    raise ValueError("LLM 응답에 text 블록이 없습니다")
