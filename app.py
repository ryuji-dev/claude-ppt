"""claude-ppt — Streamlit 웹 UI.

실행: streamlit run app.py
브라우저: http://localhost:8501
"""

from __future__ import annotations

import io
import json
import os
import tempfile
from pathlib import Path

import streamlit as st

from claude_ppt.llm import DEFAULT_MAX_TOKENS, text_to_outline
from claude_ppt.render import render

st.set_page_config(page_title="claude-ppt", page_icon="🎬", layout="centered")

st.title("🎬 claude-ppt")
st.caption("YouTube 영상 요약 텍스트 → 편집 가능한 .pptx로 변환")

# --- 사이드바 ----------------------------------------------------------------
with st.sidebar:
    st.header("⚙️ 설정")
    api_key = st.text_input(
        "Anthropic API Key",
        type="password",
        value=os.environ.get("ANTHROPIC_API_KEY", ""),
        help="발급: https://console.anthropic.com → API Keys",
        placeholder="sk-ant-...",
    )
    model = st.selectbox(
        "모델",
        ["claude-opus-4-7", "claude-sonnet-4-6", "claude-haiku-4-5"],
        index=0,
        help="Opus가 품질 가장 좋음. 비용 민감하면 Sonnet/Haiku.",
    )

    st.divider()
    st.subheader("📋 메타데이터")
    title = st.text_input("프레젠테이션 제목", value="새 프레젠테이션")
    channel = st.text_input("채널", value="samples")
    episode = st.text_input("에피소드 슬러그", value="ep00-new")

    st.divider()
    with st.expander("고급 설정"):
        max_tokens = st.number_input(
            "max_tokens", min_value=2000, max_value=64000, value=DEFAULT_MAX_TOKENS, step=1000
        )

# --- 입력 ---------------------------------------------------------------------
st.subheader("1️⃣ 입력")
tab1, tab2 = st.tabs(["📝 텍스트 붙여넣기", "📎 파일 업로드"])

with tab1:
    pasted = st.text_area(
        "대본 또는 요약 노트",
        height=300,
        placeholder="여기에 영상 대본이나 요약 노트를 붙여넣으세요.\n\n예시:\n# 인트로\n오늘은 ...\n\n## 섹션 1: 무엇\n...\n\n## 섹션 2: 어떻게\n[데모] ...",
    )

with tab2:
    uploaded = st.file_uploader("문서 업로드", type=["txt", "md"])
    uploaded_text = ""
    if uploaded is not None:
        uploaded_text = uploaded.read().decode("utf-8")
        st.success(f"업로드됨: {uploaded.name} ({len(uploaded_text):,} 글자)")
        with st.expander("미리보기"):
            st.text(uploaded_text[:2000] + ("..." if len(uploaded_text) > 2000 else ""))

text = pasted.strip() or uploaded_text.strip()

# --- 생성 버튼 ----------------------------------------------------------------
st.subheader("2️⃣ 생성")
disabled_reason = []
if not text:
    disabled_reason.append("입력 텍스트")
if not api_key:
    disabled_reason.append("API Key")
if disabled_reason:
    st.info(f"필요한 항목: {', '.join(disabled_reason)}")

if st.button(
    "🚀 슬라이드 생성",
    type="primary",
    disabled=bool(disabled_reason),
    use_container_width=True,
):
    with st.spinner("Claude가 슬라이드 구조를 만드는 중... (수십 초 소요)"):
        try:
            outline = text_to_outline(
                text,
                title=title,
                channel=channel,
                episode=episode,
                api_key=api_key,
                model=model,
                max_tokens=int(max_tokens),
            )
        except Exception as e:
            st.error(f"❌ outline 생성 실패: {type(e).__name__}: {e}")
            st.stop()

    n_slides = len(outline.slides)
    st.success(f"✅ {n_slides}장의 슬라이드 outline이 만들어졌어요")

    # outline 미리보기
    with st.expander("📋 outline.json 미리보기"):
        st.json(outline.model_dump(mode="json"))

    # 슬라이드 목록 표
    st.markdown("**슬라이드 목록**")
    rows = [
        {
            "번호": s.n,
            "slug": s.slug,
            "제목": s.title,
            "섹션": s.section,
            "레이아웃": s.layout,
        }
        for s in outline.slides
    ]
    st.dataframe(rows, use_container_width=True, hide_index=True)

    # PPTX 렌더 + 다운로드
    with st.spinner("PPTX 렌더링 중..."):
        with tempfile.TemporaryDirectory() as tmp:
            pptx_path = Path(tmp) / "slides.pptx"
            render(outline.model_dump(mode="json"), pptx_path)
            pptx_bytes = pptx_path.read_bytes()
            outline_bytes = json.dumps(
                outline.model_dump(mode="json"), ensure_ascii=False, indent=2
            ).encode("utf-8")

    st.subheader("3️⃣ 다운로드")
    col1, col2 = st.columns(2)
    with col1:
        st.download_button(
            label="📥 .pptx 다운로드",
            data=pptx_bytes,
            file_name=f"{episode}.pptx",
            mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
            use_container_width=True,
        )
    with col2:
        st.download_button(
            label="📋 outline.json 다운로드",
            data=outline_bytes,
            file_name=f"{episode}-outline.json",
            mime="application/json",
            use_container_width=True,
        )

    st.info(
        f"💡 PowerPoint·Keynote에서 `{episode}.pptx`를 열어 텍스트를 직접 편집할 수 있습니다. "
        "HTML 슬라이드 세트는 다음 단계(Phase 6b)에서 추가 예정."
    )

st.divider()
st.caption(
    "🔒 API Key는 세션 메모리에만 보관됩니다 (디스크 저장 X). "
    "탭을 닫으면 사라집니다."
)
