# claude-ppt 설계 사양 (2026-05-04)

> 본 문서는 brainstorming 단계에서 합의된 설계의 *영구 사본*이다. 실제 구현은 [`TODO.md`](../../../TODO.md)의 페이즈별 체크리스트를 따른다.

## Context

**문제**: 사용자는 YouTube 영상 요약 텍스트를 프레젠테이션으로 변환하고 싶어함. 기존 `presentation_slides` 스킬은 HTML 슬라이드 세트만 생성. 발표·다운로드용 *편집 가능한 .pptx*가 필요.

**왜 지금**:
- 시청자에게 자료 공유 시 .pptx로 다운로드받아 자체 편집·발표할 수 있어야 함
- HTML은 웹 미리보기·키보드 네비용으로 유지하고 싶음

**의도하는 결과**:
- 같은 입력(대본/요약 텍스트) → **HTML 세트 + .pptx 파일** 동시 산출
- 두 포맷 모두 *편집 가능* 상태 유지 (이미지 캡처 방식 X)
- 개인용 로컬 도구. API 키 없이 Claude Code 세션 안에서 동작
- 작업 자체는 git 브랜치 + 커밋 + PR 워크플로우로 관리

## 브레인스토밍 결정 요약

| # | 질문 | 결정 |
|---|------|------|
| 1 | 기존 스킬과의 관계 | **확장** (별도 스킬 X). 한 스킬이 HTML+PPTX 둘 다 출력 |
| 2 | 두 포맷의 관계 | **공통 슬라이드 윤곽 + 포맷별 네이티브 렌더링**. HTML은 8개 레이아웃 그대로, PPTX는 python-pptx 도형으로 동등 재현 |
| 3 | Claude 동작 위치 | **Claude Code 세션 안 (스킬)**. 파이썬은 결정론적 변환기 (JSON → PPTX). API 키 불필요 |
| 4 | 입출력 구조 | **기존 `{채널}/epNN-슬러그/` 컨벤션 유지** + 입력 형태(정돈된 대본 vs 거친 노트) 자동 판단 |

## 아키텍처

```
사용자 입력 (script.md or 세션 텍스트)
            │
            ▼
┌───────────────────────────────────┐
│  presentation_slides 스킬 (확장)  │  ← 기존 SKILL.md 수정
│  - 입력 형태 자동 판단             │
│  - 섹션·슬라이드 구조화            │
│  - 레이아웃 타입 매핑              │
│  - outline.json 산출 (공통 IR)    │ ← 신규: 공통 중간 표현
└───────────────────────────────────┘
            │
            ├──────────────┐
            ▼              ▼
   HTML 렌더링        PPTX 렌더링
   (스킬이 직접       (파이썬 호출:
    HTML 파일 생성)    python -m claude_ppt.render outline.json)
            │              │
            ▼              ▼
  {epNN}/slides/*.html   {epNN}/slides.pptx
  + index.html
```

### 공통 중간 표현 (outline.json) 스키마

```json
{
  "title": "에피소드 제목",
  "channel": "클로드코드",
  "episode": "ep05-코워크",
  "sections": [
    {"id": "intro", "name": "인트로", "color": "#7c3aed"},
    {"id": "section-1", "name": "섹션 1", "color": "#38bdf8"}
  ],
  "slides": [
    {
      "n": 1,
      "slug": "intro-hook",
      "title": "오늘의 훅",
      "section": "intro",
      "layout": "hero-cards",
      "content": {
        "cards": [
          {"emoji": "🚀", "label": "1줄 라벨", "text": "2줄 설명"}
        ]
      }
    }
  ]
}
```

레이아웃 타입은 8개로 고정: `hero-cards`, `roadmap`, `comparison-2col`, `step-flow`, `diagram-box`, `grid-2x2`, `three-stage-flow`, `summary-grid`. PPTX 렌더러도 같은 8개를 python-pptx 도형으로 1:1 매핑한다.

## 의존성

- Python ≥ 3.10
- `python-pptx` (PPTX 생성)
- `pytest` (테스트)
- 패키지 매니저: `uv` 우선, `pip` 폴백

## 사용자 워크플로우

1. `클로드코드/ep05-코워크/script.md`에 대본·요약을 붙여넣음 (또는 세션에서 텍스트 직접 입력)
2. Claude Code 세션에서 "프레젠테이션 슬라이드 만들어줘" 등으로 스킬 트리거
3. 스킬이 입력 파싱 → 슬라이드 목록 제안 → 사용자 확인
4. 스킬이 `outline.json`을 epNN 폴더에 작성
5. 스킬이 HTML 세트(`slides/*.html` + `index.html`)를 직접 생성
6. 스킬이 `python -m claude_ppt.render <outline.json> <output.pptx>` 실행
7. 결과: 같은 폴더에 `slides/` (HTML) + `slides.pptx` 둘 다

## 개발 워크플로우

- **브랜치 전략**: 기능 단위 feature branch (`feat/...`, `fix/...`, `chore/...`, `docs/...`).
- **커밋**: 의미 단위 커밋. 메시지는 [Conventional Commits](https://www.conventionalcommits.org/).
- **PR**: 작업 완료 시 `superpowers:finishing-a-development-branch` 또는 `gh pr create`로 자동 생성. main 직접 푸시 금지.
- **자동화 한계**: 완전 무인 자동화(커밋마다 자동 PR)는 settings.json hook으로 가능하나 *지금 단계에서는 과잉*. 프로젝트가 안정된 후 `update-config` 스킬로 추가 검토.

## 핵심 재사용 자산

- `.claude/skills/presentation_slides/SKILL.md` §B(컬러 테마) → `claude_ppt/theme.py`로 미러
- `.claude/skills/presentation_slides/SKILL.md` §E(레이아웃 카탈로그), §J(선택 가이드) → outline.json 레이아웃 enum의 단일 진실 공급원
- `.claude/skills/presentation_slides/references/layouts.md` → PPTX 매핑 시 시각 참조
- 기존 입력 파싱 로직(§A의 script.md 파싱, [데모] 태그 추출) → outline 생성 단계에서 재사용

## Verification

**자동화 (테스트)**:
1. `pytest tests/` — 모든 레이아웃 렌더 함수가 픽스처 outline에서 예외 없이 .pptx 산출
2. 산출 .pptx의 슬라이드 수 = outline.json `slides` 길이
3. 각 슬라이드의 제목 텍스트가 outline `slides[i].title`과 정확히 일치 (python-pptx로 역검증)

**수동 (엔드투엔드)**:
1. 샘플 `script.md` 작성 (인트로 + 섹션 2개 + 마무리, 약 6슬라이드)
2. Claude Code 세션에서 스킬 트리거
3. `slides/*.html` + `index.html` 생성 확인 → 브라우저에서 키보드 네비 동작 확인
4. `slides.pptx` 생성 확인 → PowerPoint(또는 Keynote)에서 열어 *텍스트 편집 가능*한지 확인
5. PPTX 슬라이드 1장의 시각이 동일 인덱스 HTML과 *유사한 메시지/구조*인지 (1:1 픽셀 매칭은 목표 X)
