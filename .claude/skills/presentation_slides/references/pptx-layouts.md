# PPTX 레이아웃 매핑 명세

이 문서는 `outline.json`이 따라야 하는 스키마와, 8개 레이아웃 각각이 PPTX에서 어떻게 렌더링되는지를 정의한다.
`SKILL.md` §E의 *시각적* 카탈로그와 짝을 이룬다 — 본 문서는 *데이터 구조* 카탈로그.

**단일 진실 공급원**: 레이아웃 이름과 의미는 `SKILL.md` §E가 원본. 본 문서는 그 데이터 표현을 정의한다.
구현 코드: `claude_ppt/layouts/<slug>.py` (1파일 1렌더 함수).

---

## outline.json 최상위 스키마

```json
{
  "title": "에피소드 제목",
  "channel": "클로드코드",
  "episode": "ep05-코워크",
  "sections": [
    {"id": "intro", "name": "인트로", "color": "#7c3aed"}
  ],
  "slides": [
    {
      "n": 1,
      "slug": "intro-hook",
      "title": "오늘의 훅",
      "section": "intro",
      "layout": "hero-cards",
      "content": { /* 레이아웃별 스키마 */ }
    }
  ]
}
```

| 필드 | 타입 | 필수 | 설명 |
|------|------|-----|------|
| `title` | string | ✓ | 프레젠테이션 전체 제목 (index.html 페이지 타이틀과 일치) |
| `channel` | string | ✓ | 채널 이름 (폴더 컨벤션의 `{채널}` 부분) |
| `episode` | string | ✓ | 에피소드 슬러그 (`epNN-슬러그`) |
| `sections` | array | ✓ | 섹션 정의 (id, name, color) |
| `slides` | array | ✓ | 슬라이드 정의. 순서대로 렌더 |
| `slides[].n` | int | ✓ | 1부터 시작하는 슬라이드 번호 |
| `slides[].slug` | string | ✓ | 영문 kebab-case (HTML 파일명에 사용) |
| `slides[].title` | string | ✓ | 슬라이드 제목 (HTML·PPTX 모두에 사용) |
| `slides[].section` | string | ✓ | `sections[].id` 중 하나 |
| `slides[].layout` | string | ✓ | 8개 레이아웃 enum 중 하나 (아래 참조) |
| `slides[].content` | object | ✓ | 레이아웃별 데이터 (아래 참조) |

---

## 레이아웃 enum

다음 8개 문자열만 허용된다. 다른 값은 `ValueError`.

```
hero-cards
roadmap
comparison-2col
step-flow
diagram-box
grid-2x2
three-stage-flow
summary-grid
```

`claude_ppt/layouts/__init__.py`의 `LAYOUTS` 딕셔너리가 단일 진실 공급원.

---

## 1. `hero-cards`

**용도**: 오프닝 훅, 핵심 포인트 강조.
**구조**: 2~3개 카드 가로 배치, 카드당 이모지 + 라벨 + 본문.
**구현**: `claude_ppt/layouts/hero_cards.py`

```json
{
  "cards": [
    {"emoji": "🚀", "label": "빠른 시작", "text": "한 줄 요약"},
    {"emoji": "✨", "label": "쉬운 사용", "text": "두 번째 카드"}
  ]
}
```

- `cards`: 2~3개 권장. 1개도 허용되나 비주얼 단조로움.
- `emoji`, `label`, `text`는 모두 string. 빈 문자열도 허용.

---

## 2. `roadmap`

**용도**: 에피소드 개요, 시리즈 진행률.
**구조**: 3~6개 단계를 가로 진행 표로. 카드마다 번호 + 라벨.
**구현**: `claude_ppt/layouts/roadmap.py`

```json
{
  "steps": [
    {"label": "문제 정의"},
    {"label": "도구 비교"},
    {"label": "설치"},
    {"label": "데모"},
    {"label": "정리"}
  ]
}
```

- `steps`: 3~6개. 더 많으면 카드가 좁아져 가독성 ↓.

---

## 3. `comparison-2col`

**용도**: vs 슬라이드, before/after, 도구 비교.
**구조**: 좌·우 2열, 각 컬럼은 헤더 + 불릿 리스트.
**구현**: `claude_ppt/layouts/comparison_2col.py`

```json
{
  "left":  {"title": "Before", "items": ["수동 작업", "느린 피드백"]},
  "right": {"title": "After",  "items": ["자동화", "즉시 검증"]}
}
```

- `items` 권장 1~3개.
- 좌측 컬럼은 보라(`#7c3aed`), 우측은 파랑(`#38bdf8`)으로 강조.

---

## 4. `step-flow`

**용도**: 설치 과정, 프로세스 설명.
**구조**: 3~5개 단계 가로 배치. 카드마다 STEP 번호 + 제목 + 1~2줄 설명.
**구현**: `claude_ppt/layouts/step_flow.py`

```json
{
  "steps": [
    {"title": "다운로드", "description": "공식 사이트에서 받기"},
    {"title": "인증", "description": "API 키 등록"},
    {"title": "첫 실행", "description": "샘플 명령으로 검증"}
  ]
}
```

- `description`은 길어도 카드 안에서 자동 줄바꿈.

---

## 5. `diagram-box`

**용도**: 아키텍처, 보안 모델, 시스템 구조.
**구조**: 중앙 노드 1개 + 하위 3~6개 노드. 중앙에서 각 하위 노드로 직선 커넥터.
**구현**: `claude_ppt/layouts/diagram_box.py`

```json
{
  "center": {"label": "코어 엔진"},
  "nodes": [
    {"label": "입력 파서"},
    {"label": "스토리지"},
    {"label": "렌더러"},
    {"label": "API"}
  ]
}
```

- 중앙 노드는 보라 채움(`#7c3aed`), 하위는 다크 카드.
- 커넥터는 보라 직선.

---

## 6. `grid-2x2`

**용도**: 기능 목록, 커넥터, 도구 소개.
**구조**: 4~6개 카드 격자 (4개=2×2, 5~6개=3×2). 카드당 이모지 + 제목 + 설명.
**구현**: `claude_ppt/layouts/grid_2x2.py`

```json
{
  "cards": [
    {"emoji": "⚡", "title": "빠름",   "description": "1초 내 응답"},
    {"emoji": "🛡️", "title": "안전",   "description": "샌드박스 격리"},
    {"emoji": "🎨", "title": "예쁨",   "description": "다크 테마"},
    {"emoji": "🧩", "title": "확장성", "description": "플러그인 지원"}
  ]
}
```

---

## 7. `three-stage-flow`

**용도**: 발전 과정, 워크플로우, 레벨업.
**구조**: **정확히** 3단계. 각 단계는 번호 + 제목 + 설명. 단계 간 화살표 커넥터.
**구현**: `claude_ppt/layouts/three_stage_flow.py`

```json
{
  "stages": [
    {"title": "기본",  "description": "최소 기능"},
    {"title": "표준",  "description": "상용 수준"},
    {"title": "고급",  "description": "엔터프라이즈"}
  ]
}
```

- ⚠️ `stages` 길이가 3이 아니면 `ValueError`. 다른 단계 수가 필요하면 `step-flow` 사용.
- 단계별 누적 색상: 보라 → 파랑 → 초록 (인트로/섹션1/섹션2 색).

---

## 8. `summary-grid`

**용도**: 마무리 슬라이드, 총정리.
**구조**: 6개 요약 카드 (3×2 그리드) + 하단 결론 박스.
**구현**: `claude_ppt/layouts/summary_grid.py`

```json
{
  "cards": [
    {"label": "01", "text": "문제 정의"},
    {"label": "02", "text": "도구 선정"},
    {"label": "03", "text": "설치"},
    {"label": "04", "text": "구조 이해"},
    {"label": "05", "text": "실전 데모"},
    {"label": "06", "text": "회고"}
  ],
  "conclusion": "다음 영상에서 계속됩니다"
}
```

- `cards`는 정확히 6개 권장. 적으면 그리드가 비어 보이고, 많으면 잘릴 수 있음.
- `conclusion`은 단일 문장. 빈 문자열이면 결론 박스 생략.

---

## 검증 (회귀 방지)

`tests/fixtures/sample-outline.json`은 8개 레이아웃을 모두 사용한다.
새 레이아웃을 추가할 때:

1. `claude_ppt/layouts/<slug>.py` 신설 (TDD)
2. `claude_ppt/layouts/__init__.py`의 `LAYOUTS`에 등록
3. 본 문서에 §N. 항목 추가 (스키마 + 예시)
4. `SKILL.md` §E·§J에 시각적 설명 추가
5. 픽스처에 슬라이드 1장 추가
6. `tests/test_render.py`의 `EXPECTED_LAYOUTS` 갱신

---

## CLI 호출 (스킬 → 파이썬 변환기)

스킬은 outline.json을 작성한 뒤 다음을 실행한다:

```bash
python -m claude_ppt.render <outline.json> <output.pptx>
```

- 종료 코드 0이면 성공. 비-0이면 stderr에 에러 메시지가 있음.
- 출력 파일 경로의 부모 디렉토리는 자동 생성.
- `console_scripts` 진입점도 같은 동작: `claude-ppt-render <outline.json> <output.pptx>`.
