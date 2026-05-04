"""LLM 변환 모듈 테스트 — 실제 API 호출 없이 mock client로 검증."""

from __future__ import annotations

import json
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest

from claude_ppt.llm import _extract_text, _system_blocks, _user_message, text_to_outline
from claude_ppt.schema import Outline


def _fake_response(text: str) -> SimpleNamespace:
    block = SimpleNamespace(type="text", text=text)
    return SimpleNamespace(content=[block])


def _valid_outline_json() -> str:
    return json.dumps(
        {
            "title": "테스트",
            "channel": "ch",
            "episode": "ep01",
            "sections": [{"id": "intro", "name": "인트로", "color": "#7c3aed"}],
            "slides": [
                {
                    "n": 1,
                    "slug": "intro-hook",
                    "title": "테스트 슬라이드",
                    "section": "intro",
                    "layout": "hero-cards",
                    "content": {
                        "cards": [
                            {"emoji": "🚀", "label": "L", "text": "T"},
                            {"emoji": "✨", "label": "L2", "text": "T2"},
                        ]
                    },
                }
            ],
        },
        ensure_ascii=False,
    )


def test_system_blocks_includes_layout_spec_and_cache_control() -> None:
    blocks = _system_blocks()
    assert len(blocks) == 1
    block = blocks[0]
    assert block["type"] == "text"
    assert block["cache_control"] == {"type": "ephemeral"}
    # 레이아웃 스펙 핵심 키워드가 시스템 프롬프트에 들어가 있어야 함
    assert "hero-cards" in block["text"]
    assert "summary-grid" in block["text"]
    assert "outline.json" in block["text"]


def test_user_message_contains_metadata_and_body() -> None:
    msg = _user_message("본문 내용", title="T", channel="C", episode="ep01")
    assert "T" in msg
    assert "C" in msg
    assert "ep01" in msg
    assert "본문 내용" in msg
    assert "JSON만" in msg


def test_extract_text_strips_markdown_fences() -> None:
    response = _fake_response("```json\n{\"a\": 1}\n```")
    assert _extract_text(response) == '{"a": 1}'


def test_extract_text_returns_plain_json() -> None:
    response = _fake_response('{"a": 1}')
    assert _extract_text(response) == '{"a": 1}'


def test_extract_text_raises_when_no_text_block() -> None:
    response = SimpleNamespace(content=[])
    with pytest.raises(ValueError, match="text 블록이 없습니다"):
        _extract_text(response)


def test_text_to_outline_happy_path() -> None:
    client = MagicMock()
    client.messages.create.return_value = _fake_response(_valid_outline_json())

    outline = text_to_outline(
        "본문",
        title="테스트",
        channel="ch",
        episode="ep01",
        client=client,
    )

    assert isinstance(outline, Outline)
    assert len(outline.slides) == 1
    assert outline.slides[0].layout == "hero-cards"

    # 호출 인자 검증 — system은 캐시 가능한 블록 리스트
    kwargs = client.messages.create.call_args.kwargs
    assert kwargs["model"] == "claude-opus-4-7"
    assert isinstance(kwargs["system"], list)
    assert kwargs["system"][0]["cache_control"] == {"type": "ephemeral"}


def test_text_to_outline_handles_fenced_response() -> None:
    client = MagicMock()
    fenced = "```json\n" + _valid_outline_json() + "\n```"
    client.messages.create.return_value = _fake_response(fenced)
    outline = text_to_outline("본문", title="T", channel="c", episode="e", client=client)
    assert len(outline.slides) == 1


def test_text_to_outline_rejects_unknown_layout() -> None:
    client = MagicMock()
    bad = json.loads(_valid_outline_json())
    bad["slides"][0]["layout"] = "totally-invalid-layout"
    client.messages.create.return_value = _fake_response(
        json.dumps(bad, ensure_ascii=False)
    )
    with pytest.raises(Exception):  # pydantic ValidationError or our ValueError
        text_to_outline("본문", title="T", channel="c", episode="e", client=client)


def test_text_to_outline_rejects_non_consecutive_slide_numbers() -> None:
    client = MagicMock()
    bad = json.loads(_valid_outline_json())
    bad["slides"][0]["n"] = 5  # should be 1
    client.messages.create.return_value = _fake_response(
        json.dumps(bad, ensure_ascii=False)
    )
    with pytest.raises(Exception):
        text_to_outline("본문", title="T", channel="c", episode="e", client=client)


def test_text_to_outline_rejects_unknown_section_id() -> None:
    client = MagicMock()
    bad = json.loads(_valid_outline_json())
    bad["slides"][0]["section"] = "ghost-section"
    client.messages.create.return_value = _fake_response(
        json.dumps(bad, ensure_ascii=False)
    )
    with pytest.raises(ValueError, match="ghost-section"):
        text_to_outline("본문", title="T", channel="c", episode="e", client=client)
