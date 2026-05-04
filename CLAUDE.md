# CLAUDE.md — claude-ppt 프로젝트 헌장

이 문서는 본 레포에서 동작하는 **Claude Code 세션**을 위한 운영 지침이다. 매 세션 시작 시 자동으로 컨텍스트에 주입된다.

---

## 1. 프로젝트 한 줄 정의

YouTube 영상 요약 텍스트 → **HTML 슬라이드 세트 + 편집 가능한 .pptx** 동시 생성. Claude Code 세션 안에서만 동작하는 개인용 로컬 도구.

핵심 산출물:
- `slides/*.html` + `index.html` — 다크 테마, 8개 레이아웃, 키보드 네비
- `slides.pptx` — python-pptx로 렌더된 편집 가능한 파워포인트

---

## 2. 활성 스킬

이 프로젝트의 메인 스킬은 `presentation_slides` (`.claude/skills/presentation_slides/SKILL.md`)이다.
*"슬라이드 만들어줘"* 류 요청은 반드시 이 스킬을 트리거해야 한다.

스킬 책임:
- 대본/요약 텍스트 파싱
- 슬라이드 구조화 (섹션, 레이아웃 매핑)
- `outline.json` 작성
- HTML 파일 직접 생성
- 파이썬 변환기 호출 (`python -m claude_ppt.render outline.json slides.pptx`)

---

## 3. 코드 스타일

- **Python 3.10 이상**. type hints 필수.
- 함수당 한 가지 책임. 한 파일이 200줄을 넘으면 분리 검토.
- 8개 레이아웃은 **`claude_ppt/layouts/<slug>.py` 1파일 1렌더 함수** 원칙.
  - 시그니처 통일: `def render(slide: Slide, content: dict, theme: Theme) -> None`
- 외부 의존성 최소화: 표준 라이브러리 + `python-pptx` + `pytest`만 허용.
- 한글 식별자 금지. 한국어는 *문자열 리터럴과 주석에서만*.

---

## 4. 테스트 정책

- 모든 새 레이아웃 함수는 **TDD** (RED → GREEN → REFACTOR).
- 픽스처는 `tests/fixtures/sample-outline.json` 1개에서 시작, 필요 시 분리.
- 검증 항목 (자동):
  1. `pptx` 파일이 깨지지 않고 열림 (python-pptx로 재오픈)
  2. 슬라이드 수 = `outline.slides` 길이
  3. 각 슬라이드 제목 텍스트가 outline과 정확히 일치
- `pytest -q` 통과 후에만 커밋.

---

## 5. 커밋 · 브랜치 · PR 규칙

- **브랜치**: 기능 단위 feature branch (`feat/...`, `fix/...`, `chore/...`, `docs/...`).
- **커밋 메시지**: [Conventional Commits](https://www.conventionalcommits.org/).
  - `feat: add hero-cards layout renderer`
  - `test: cover step-flow edge cases`
  - `docs: clarify outline.json schema`
- **`main` 직접 푸시 금지**. 모든 변경은 PR을 통과한다.
- PR은 `superpowers:finishing-a-development-branch` 스킬 또는 `gh pr create`로 자동 생성.
- PR 본문은 ## Summary, ## Test plan 두 섹션을 포함.
- **커밋 메시지에 `Co-Authored-By` 트레일러를 넣지 않는다.** AI 모델 식별자를 커밋 저자로 명시하지 않는다. 본 레포의 모든 작업은 *사용자 본인의 작업*으로 기록된다.

---

## 6. 단일 진실 공급원 (SSOT)

설계가 두 곳에 흩어지지 않도록:

| 주제 | 원본 | 미러 / 파생 |
|------|------|-------------|
| 컬러 테마 | `.claude/skills/presentation_slides/SKILL.md` §B | `claude_ppt/theme.py` |
| 레이아웃 카탈로그 | `SKILL.md` §E, §J | `outline.json` `layout` enum, `claude_ppt/layouts/` |
| HTML 보일러플레이트 | `SKILL.md` §C, §D | (HTML은 스킬이 직접 생성) |
| PPTX 레이아웃 명세 | `references/pptx-layouts.md` | `claude_ppt/layouts/<slug>.py` |

원본을 수정하면 미러도 같은 PR에서 갱신할 것.

---

## 7. 명령 치트시트

```bash
# 의존성 설치 (uv 권장)
uv sync

# 테스트
pytest -q
pytest tests/test_render.py -k hero_cards   # 특정 레이아웃만

# 변환기 단독 실행
python -m claude_ppt.render path/to/outline.json path/to/slides.pptx

# 새 작업 브랜치
git switch -c feat/<topic>

# PR 생성 (작업 완료 후)
gh pr create --fill
```

---

## 8. 절대 하지 말 것

- ❌ API 키, 토큰, `.env` 커밋
- ❌ 큰 바이너리 커밋 — 산출 `.pptx`, 폰트 파일, 동영상은 모두 `.gitignore`
- ❌ `main` 직접 푸시·강제 푸시
- ❌ 한 PR에서 *기능 + 무관한 리팩토링* 섞기
- ❌ 테스트 없이 새 레이아웃 추가
- ❌ `python-pptx` 외부의 PPTX 라이브러리 추가 (의존성 단순화)

---

## 9. 모르면 멈추고 물어볼 것

- 입력 텍스트가 양쪽 형태 모두에 안 맞을 때 (정돈된 대본도 거친 노트도 아닐 때)
- 8개 레이아웃 어디에도 깔끔히 매핑되지 않는 콘텐츠
- 색상·타이포 변경 요청 — `SKILL.md` 원본을 먼저 갱신해야 하는 결정

이런 경우 임의 추정 대신 사용자에게 명확화를 요청한다.
