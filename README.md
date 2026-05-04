# claude-ppt

YouTube 영상 요약 텍스트를 **다크 테마 HTML 슬라이드 세트 + 편집 가능한 .pptx**로 동시에 변환하는 개인용 도구.

> **완전 무료.** Claude Code 세션 안에서 동작하며, 외부 API 키나 LLM 호출이 필요 없습니다.
> 변환기(`claude_ppt`)는 결정론적 파이썬 코드입니다.

| 산출물 | 용도 |
|--------|------|
| `index.html` + `slides/*.html` | 브라우저로 미리보기·웹 공유. ←/→ 키 네비, 페이드 전환 |
| `slides.pptx` | PowerPoint·Keynote에서 직접 텍스트 편집·발표 |

8가지 레이아웃 지원: `hero-cards`, `roadmap`, `comparison-2col`, `step-flow`, `diagram-box`, `grid-2x2`, `three-stage-flow`, `summary-grid`.

---

## 빠른 시작

### 1. 의존성 설치

```bash
git clone git@github.com:ryuji-dev/claude-ppt.git
cd claude-ppt

python3.11 -m venv .venv          # Python ≥ 3.10
.venv/bin/pip install -e ".[dev]"
```

의존성은 `python-pptx`, `pydantic`, `pytest`뿐. **Anthropic SDK 등 외부 API 의존성 없음.**

### 2. Claude Code에서 스킬 트리거

```bash
mkdir -p 클로드코드/ep05-코워크
# 영상 대본/요약을 클로드코드/ep05-코워크/script.md에 저장
```

Claude Code 세션에서:

> "`클로드코드/ep05-코워크/script.md` 보고 슬라이드 만들어줘"

스킬(`presentation_slides`)이 자동으로:
1. 대본을 섹션·`[데모]` 태그로 파싱
2. 슬라이드 목록(번호·제목·레이아웃) 제안 → 사용자 확인
3. `outline.json` 작성
4. `python -m claude_ppt.build` 실행 → HTML 세트 + `slides.pptx` 동시 생성

### 3. 결과 확인

```
클로드코드/ep05-코워크/
├── script.md          (입력)
├── outline.json       (공통 IR)
├── slides.pptx        (PowerPoint·Keynote 편집 가능)
├── index.html         (허브 페이지)
└── slides/
    ├── 01-intro-hook.html
    ├── 02-roadmap.html
    └── ...
```

`open index.html` → 브라우저에서 ←/→ 키로 슬라이드 넘기기.
`open slides.pptx` → PowerPoint·Keynote에서 텍스트 편집·발표.

---

## 변환기 단독 사용 (CLI)

스킬을 거치지 않고 `outline.json`을 직접 작성한 경우:

```bash
# HTML + PPTX 한 번에
python -m claude_ppt.build outline.json output_dir/
# 또는: claude-ppt-build outline.json output_dir/

# HTML만
python -m claude_ppt.html_render outline.json output_dir/
# 또는: claude-ppt-html outline.json output_dir/

# PPTX만
python -m claude_ppt.render outline.json slides.pptx
# 또는: claude-ppt-render outline.json slides.pptx
```

`outline.json` 스키마는 [`tests/fixtures/sample-outline.json`](tests/fixtures/sample-outline.json) 또는
[`samples/ep00-demo/outline.json`](samples/ep00-demo/outline.json) 참조.

상세 스키마: [`.claude/skills/presentation_slides/references/pptx-layouts.md`](.claude/skills/presentation_slides/references/pptx-layouts.md).

---

## 데모

```bash
python -m claude_ppt.build samples/ep00-demo/outline.json samples/ep00-demo/
open samples/ep00-demo/index.html      # 브라우저
open samples/ep00-demo/slides.pptx     # PowerPoint·Keynote
```

8장의 슬라이드가 8개 레이아웃을 모두 한 번씩 사용한 데모.

---

## 동작 원리

```
사용자 입력 (script.md)
        │
        ▼
┌──────────────────────────────────────┐
│  presentation_slides 스킬             │
│  (Claude Code 세션 안에서 진행)         │
│  - 대본 파싱 + 슬라이드 목록 제안       │
│  - outline.json 작성                  │
└──────────────────────────────────────┘
        │
        ▼
┌──────────────────────────────────────┐
│  claude_ppt.build (Python, 무료)      │
│  - html_render → index.html + slides  │
│  - render → slides.pptx               │
└──────────────────────────────────────┘
        │
        ▼
   {epNN}/index.html, slides/, slides.pptx
```

스킬은 보일러플레이트(HTML CSS, 네비게이션, 레이아웃)를 *손코딩하지 않는다*. 모든 미러는 변환기 안에 박혀 있고, SKILL.md §B/§C/§D/§E는 그 SSOT를 명시한다 (CLAUDE.md §6 SSOT 표 참조).

---

## 입력 예시

스킬은 두 형태 모두 처리합니다.

**정돈된 대본** (섹션 헤더 + `[데모]` 태그):

```markdown
# 인트로
오늘은 클로드 코드의 새 기능을 살펴봅니다.

[데모] 핵심 메시지 3장

## 섹션 1: 코워크 모드란?
[데모] 클로드와 사용자가 함께 코드를 작성하는 모습

## 섹션 2: 설치 방법
1. 설치 명령
2. 인증
3. 첫 실행
```

**거친 요약 노트** (불릿 섞임): 스킬이 재구조화합니다.

`samples/ep00-demo/script.md`에 8개 레이아웃을 모두 사용한 데모 대본이 있습니다.

---

## 폴더 컨벤션

권장: `{채널}/epNN-슬러그/`

```
클로드코드/
└── ep05-코워크/
    ├── script.md
    ├── outline.json
    ├── slides.pptx
    ├── index.html
    └── slides/...
```

채널·에피소드 폴더는 *프로젝트 외부*에 두는 것을 권장 (생성물이 git에 들어가지 않도록).

---

## 트러블슈팅

| 증상 | 원인 / 해결 |
|------|-----------|
| `ModuleNotFoundError: claude_ppt` | `pip install -e ".[dev]"` 재실행 |
| `ValueError: three-stage-flow expects exactly 3 stages` | `three-stage-flow` 레이아웃은 정확히 3단계만 |
| `ValueError: Unknown layout: 'xxx'` | 8개 enum 외 layout 사용. `pptx-layouts.md` 참조 |
| HTML에서 한글이 깨짐 | Google Fonts CDN 로드 필요 — 인터넷 연결 확인 |
| PPTX에서 한글이 □로 보임 | macOS는 'Apple SD Gothic Neo' 자동 적용. 다른 OS는 시스템에 한국어 폰트 설치 |
| PowerPoint에서 "복구해야 합니다" 메시지 | 변환기 비정상 종료 시. stderr traceback 확인 후 outline.json 수정 |

---

## 개발

```bash
.venv/bin/pytest -q                              # 전체 테스트
.venv/bin/pytest tests/test_render.py -k hero    # 특정 레이아웃만
```

자세한 코드 스타일·커밋 규칙·자율 워크플로우는 [`CLAUDE.md`](CLAUDE.md) 참조.
페이즈별 진행 상황은 [`TODO.md`](TODO.md) 참조.

---

## 라이선스

개인용 프로젝트.
