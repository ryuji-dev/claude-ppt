# claude-ppt

YouTube 영상 요약 텍스트를 **편집 가능한 .pptx 파일**(향후 HTML 슬라이드 세트도 포함)로 변환하는 개인용 도구입니다.

> ChatGPT·Gemini·Claude.ai처럼 **웹 인터페이스에 문서를 올리거나 텍스트를 붙여넣기**만 하면 슬라이드가 만들어집니다.

| 인터페이스 | 출력물 | 상태 |
|----------|--------|------|
| 🌐 **Streamlit 웹 UI** (`app.py`) | `.pptx` | ✅ Phase 6a |
| 🌐 Streamlit + HTML 다운로드 | `.pptx` + `slides/*.html` | 🚧 Phase 6b |
| 🖥️ Claude Code 스킬 (`.claude/skills/presentation_slides/`) | `.pptx` + HTML | ✅ 가능 (CLI 워크플로우 익숙한 사용자) |

---

## 빠른 시작 — 웹 UI

### 1. 의존성 설치

```bash
git clone git@github.com:ryuji-dev/claude-ppt.git
cd claude-ppt

python3.11 -m venv .venv          # Python 3.10+
.venv/bin/pip install -e ".[web]"   # streamlit + anthropic + python-pptx
```

### 2. Anthropic API Key 준비

[console.anthropic.com](https://console.anthropic.com) → **API Keys**에서 키 발급. 종량제 비용이 발생합니다 (Claude Opus 4.7 기준 입력 $5/M·출력 $25/M 토큰).

### 3. Streamlit 실행

```bash
.venv/bin/streamlit run app.py
```

브라우저가 자동으로 `http://localhost:8501`에 열립니다.

### 4. 사용

1. 사이드바에 **API Key** 입력 (세션 메모리에만 저장됨, 디스크 저장 X)
2. **메타데이터** 입력 (제목·채널·에피소드)
3. **텍스트 붙여넣기** 또는 `.txt`/`.md` **파일 업로드**
4. 🚀 **슬라이드 생성** 클릭 → 수십 초 대기
5. 생성된 outline 확인 → 📥 **`.pptx` 다운로드**
6. PowerPoint·Keynote에서 열어 직접 편집·발표

---

## 동작 원리

```
사용자 입력 (텍스트 or 파일)
        │
        ▼
┌──────────────────────────────────────┐
│  Streamlit 웹 UI (app.py)             │
│  - 텍스트 입력 / 파일 업로드            │
│  - 메타데이터 (제목, 채널, 에피소드)    │
│  - API Key 관리                        │
└──────────────────────────────────────┘
        │
        ▼
┌──────────────────────────────────────┐
│  Claude API (Anthropic SDK)           │
│  → text_to_outline()                  │
│  - 시스템 프롬프트: 8개 레이아웃 스펙   │
│  - 프롬프트 캐싱으로 비용 90% 절감     │
│  - JSON outline 반환                   │
└──────────────────────────────────────┘
        │
        ▼
┌──────────────────────────────────────┐
│  Pydantic 검증 (claude_ppt.schema)    │
│  - 슬라이드 번호 연속성                │
│  - layout enum 8개 중 하나             │
│  - 섹션 ID 일관성                      │
└──────────────────────────────────────┘
        │
        ▼
┌──────────────────────────────────────┐
│  PPTX 렌더 (claude_ppt.render)        │
│  - python-pptx로 16:9 다크 슬라이드    │
│  - 8개 레이아웃 1:1 매핑               │
└──────────────────────────────────────┘
        │
        ▼
   📥 slides.pptx (다운로드)
```

지원 레이아웃 (8개): `hero-cards`, `roadmap`, `comparison-2col`, `step-flow`, `diagram-box`, `grid-2x2`, `three-stage-flow`, `summary-grid`. 자세한 스키마는 [`.claude/skills/presentation_slides/references/pptx-layouts.md`](.claude/skills/presentation_slides/references/pptx-layouts.md).

---

## 입력 예시

웹 UI에 다음 두 형태 모두 붙여넣을 수 있습니다.

**정돈된 대본** (섹션 헤더 + [데모] 태그):

```markdown
# 인트로
오늘은 클로드 코드의 새 기능을 살펴봅니다.

## 섹션 1: 코워크 모드란?
[데모] 클로드와 사용자가 함께 코드를 작성하는 모습

## 섹션 2: 설치 방법
1. 설치 명령
2. 인증
3. 첫 실행
```

**거친 요약 노트** (불릿 섞임): Claude가 재구조화합니다.

```markdown
- 클로드 코워크 모드 핵심
- 자동 PR 생성
- 브랜치 격리
- 설치 3단계
```

`samples/ep00-demo/script.md`에 8개 레이아웃을 모두 사용한 데모 대본이 있습니다.

---

## CLI 워크플로우 (개발자용)

API 키 없이 Claude Code 세션 안에서 동작합니다. `outline.json`을 직접 작성하거나 스킬이 만들도록 지시하면 됩니다.

```bash
# outline.json → slides.pptx 변환
python -m claude_ppt.render samples/ep00-demo/outline.json out.pptx
```

또는 Claude Code 세션에서:

```
프레젠테이션 슬라이드 만들어줘. 대본은 클로드코드/ep05-코워크/script.md
```

스킬이 `outline.json` 작성 + HTML 생성 + PPTX 변환을 모두 처리합니다. 자세한 절차는 [`.claude/skills/presentation_slides/SKILL.md`](.claude/skills/presentation_slides/SKILL.md) §H 워크플로우 참조.

---

## 트러블슈팅

**API Key 입력했는데 401 에러**
→ 키가 유효한지 확인 (`https://console.anthropic.com/settings/keys`). `sk-ant-` 접두사 확인.

**Streamlit이 안 켜짐**
→ `.venv/bin/pip install -e ".[web]"` 재실행. Python 3.10+ 필요.

**한글 폰트가 .pptx에서 깨짐**
→ python-pptx는 시스템 폰트를 참조합니다. macOS는 'Apple SD Gothic Neo' 자동 적용. Windows에서 열 때 폰트가 없으면 자동 대체.

**`python-pptx` 설치 실패**
→ Python 3.10+ 필요. 가상환경 권장 (`python3.11 -m venv .venv`).

**PowerPoint에서 "복구해야 합니다" 메시지**
→ 변환기 비정상 종료 시 발생. Streamlit 콘솔에 traceback이 있는지 확인.

---

## 라이선스

개인용 프로젝트.
