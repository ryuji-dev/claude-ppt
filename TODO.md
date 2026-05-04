# TODO — claude-ppt 작업 순서

페이즈별 체크리스트. 진행 시 매 커밋마다 박스를 업데이트한다.
페이즈 완료 시 git tag (`phase-N-done`).

설계 원본: [`docs/superpowers/specs/2026-05-04-claude-ppt-design.md`](docs/superpowers/specs/2026-05-04-claude-ppt-design.md)

---

## Phase 0 — 부트스트랩 (현재 PR)

- [x] `git switch -c feat/project-bootstrap`
- [x] `README.md` — 사용법 문서
- [x] `CLAUDE.md` — 프로젝트 헌장 (자율 워크플로우 §9 포함)
- [x] `TODO.md` — 본 파일
- [x] `docs/superpowers/specs/2026-05-04-claude-ppt-design.md` — 설계 사본
- [x] 빈 `claude_ppt/` 디렉토리 (`.gitkeep`, Phase 1에서 실제 모듈로 교체됨)
- [x] 빈 `tests/` 디렉토리 (`.gitkeep`, Phase 1에서 실제 테스트로 교체됨)
- [x] PR #1 생성 → 머지 (squash, branch deleted)

---

## Phase 1 — 파이썬 변환기 골격

- [x] 브랜치: `feat/pptx-renderer-skeleton`
- [x] `pyproject.toml` 생성 (Python ≥ 3.10, `python-pptx`, `pytest`, hatchling 빌드)
- [x] `claude_ppt/__init__.py`
- [x] `claude_ppt/theme.py` — `SKILL.md` §B 컬러 상수 미러 (`RGBColor`)
- [x] `claude_ppt/render.py` — argparse CLI 진입점, outline.json 로드, 16:9 다크 슬라이드 생성
- [x] `tests/fixtures/sample-outline.json` — hero-cards 1장 최소 픽스처
- [x] `tests/test_render.py` — 4개 테스트 (RED → GREEN 확인)
- [x] `claude_ppt/layouts/__init__.py` + 디스패처
- [x] `claude_ppt/layouts/hero_cards.py` — 첫 레이아웃, TDD 사이클 완료
- [x] `pytest -q` 전체 통과 (4 passed)
- [ ] PR → 머지 → `phase-1-done` 태그

---

## Phase 2 — 나머지 레이아웃 7개

- [x] `_common.py` 분리 — 타이틀·카드 헬퍼 공유
- [x] `roadmap.py` + 등록
- [x] `comparison_2col.py` + 등록
- [x] `step_flow.py` + 등록
- [x] `diagram_box.py` + 등록 (중앙↔하위 노드 커넥터 포함)
- [x] `grid_2x2.py` + 등록 (4개=2x2, 5~6개=3x2 자동)
- [x] `three_stage_flow.py` + 등록 (정확히 3단계 강제, 화살표 커넥터 포함)
- [x] `summary_grid.py` + 등록 (6개 카드 + 결론 박스)
- [x] `tests/fixtures/sample-outline.json` 8개 레이아웃 전체 커버리지로 확장
- [x] 통합 테스트: `LAYOUTS` 레지스트리 8개 일치 + 픽스처 8개 사용 + 8장 .pptx 산출
- [x] `pytest -q` → 7 passed
- [ ] PR → 머지 → `phase-2-done` 태그

---

## Phase 3 — outline.json 스키마 안정화

- [ ] 브랜치: `feat/outline-schema`
- [ ] `claude_ppt/schema.py` — pydantic 모델 또는 jsonschema
- [ ] `render.py`에 스키마 검증 단계 추가 (불일치 시 명확한 에러)
- [ ] 회귀 테스트: 잘못된 outline 입력 시 검증 실패 확인
- [ ] `references/pptx-layouts.md`에 스키마 문서화
- [ ] PR → 머지 → `phase-3-done` 태그

---

## Phase 4 — SKILL.md 확장

- [x] 브랜치: `feat/skill-pptx-output`
- [x] `SKILL.md` frontmatter description 갱신 (PPTX 트리거 키워드 + 산출물 설명)
- [x] `SKILL.md` 인트로 단락 갱신 (HTML + PPTX 동시 생성 명시)
- [x] `SKILL.md` §H 워크플로우에 outline.json 작성 + PPTX 생성 단계 삽입 (6 → 8단계)
- [x] `SKILL.md` §L PPTX 출력 절차 신설 (L-1 outline.json 작성 / L-2 변환기 실행 / L-3 검증 / L-4 산출물 트리 / L-5 환경 전제 / L-6 실패 보고)
- [x] `SKILL.md` §I 품질 체크리스트에 PPTX 항목 추가 (HTML / outline.json + PPTX 두 묶음)
- [x] `SKILL.md` §E에서 `pptx-layouts.md` 레퍼런스 가리킴
- [x] `references/pptx-layouts.md` 신설 — outline.json 최상위 스키마 + 8개 레이아웃별 content 스키마/예시/구현 파일
- [x] `pytest -q` 회귀 없음 (7 passed)
- [ ] PR → 머지 → `phase-4-done` 태그

---

## Phase 5 — 엔드투엔드 검증 (CLI 흐름)

- [x] 브랜치: `feat/e2e-validation`
- [x] 샘플 `samples/ep00-demo/script.md` 작성 (인트로 + 섹션 2개 + 마무리)
- [x] `samples/ep00-demo/outline.json` 8장 레이아웃 모두 사용한 골든 레퍼런스
- [x] `python -m claude_ppt.render` 실행 → 8장 PPTX 정상 생성 (39KB, 슬라이드 수·제목 일치)
- [x] `.gitignore`에 `samples/**/outline.json` 예외 추가
- [ ] PR → 머지 → `phase-5-done` 태그
- [ ] (수동) PowerPoint·Keynote에서 텍스트 편집 가능 검증 — 사용자 작업
- [ ] (수동) 브라우저 HTML 검증은 *Phase 6에서 웹 UI가 HTML을 산출하면* 같이

---

## Phase 6 — 웹 UI (Streamlit + Claude API)

방향 전환: GPT/Gemini/Claude.ai처럼 **문서 업로드 + 텍스트 입력 → HTML/PPTX 다운로드** 웹 인터페이스.
스택: Streamlit + Anthropic SDK + 기존 `claude_ppt` 변환기 + 신규 Python HTML 렌더러.

### Phase 6a — Streamlit 골격 + PPTX 출력 (MVP)

- [x] 브랜치: `feat/web-ui-pptx`
- [x] `pyproject.toml`에 `streamlit` (web extras), `anthropic`, `pydantic` 의존성 추가
- [x] `claude_ppt/schema.py` — Pydantic Outline 모델 (필드 검증 + 슬라이드 번호 연속성 + 레이아웃 enum + 섹션 ID 일관성)
- [x] `claude_ppt/llm.py` — Anthropic SDK로 텍스트 → outline.json 변환. 시스템 프롬프트에 `pptx-layouts.md` 임베드 + `cache_control` ephemeral로 90% 비용 절감
- [x] `app.py` Streamlit 진입점 — 텍스트 입력 + 파일 업로드 + 메타데이터 + outline 미리보기 + .pptx/outline.json 다운로드
- [x] API 키 처리 — 사이드바 password 입력, 환경변수 fallback, 세션 메모리만 사용 (디스크 저장 X)
- [x] 마크다운 펜스(```json) 자동 제거
- [x] LLM 모듈 회귀 테스트 10개 (mock client)
- [x] `pytest -q` → 17 passed (회귀 없음)
- [x] README.md 웹 UI 우선으로 재작성
- [x] PR #6 → 머지 → `phase-6a-done` 태그

### Phase 6b — HTML 렌더러 (Python 모듈 + zip 다운로드)

- [x] 브랜치: `feat/web-ui-html`
- [x] `claude_ppt/html_render.py` — outline.json → `{filename: html}`. SKILL.md §C/§D/§F 보일러플레이트 미러
- [x] 8개 레이아웃 함수 + 공통 base CSS + 레이아웃별 CSS 상수
- [x] index.html 생성 (섹션 색상 코딩, 4열 그리드)
- [x] 슬라이드 prev/next 네비 + 첫·끝 슬라이드 경계 처리 + ArrowLeft/Right 키 핸들러
- [x] 회귀 테스트 9개 (전체 26 passed)
- [x] PR #7 → 머지 → `phase-6b-done` 태그

### Phase 6c — 무료 경로 회귀: 웹 UI 제거 + 변환기 통합 진입점

비용 발생 없는 사용 흐름으로 회귀. Streamlit 웹 UI를 제거하고
Claude Code 스킬이 `outline.json`만 작성하면 단일 명령으로 HTML+PPTX가 산출되도록.

- [x] 브랜치: `chore/remove-web-ui`
- [x] `claude_ppt/html_render.py`에 `render_to_dir()` + CLI 진입점 (`python -m claude_ppt.html_render`)
- [x] `claude_ppt/build.py` 신설 — HTML + PPTX 한 번에 (`python -m claude_ppt.build`)
- [x] 회귀 테스트 4개 추가 (build, build CLI, render_to_dir, html CLI)
- [x] `app.py`, `claude_ppt/llm.py`, `tests/test_llm.py` 삭제
- [x] `pyproject.toml`: `anthropic`, `streamlit`, `[web]` extras 제거. console scripts에 `claude-ppt-html`, `claude-ppt-build` 추가
- [x] `SKILL.md` 워크플로우 단순화: 8단계 → 6단계 (HTML 손코딩 단계 제거, build 명령 한 줄로 통합)
- [x] `SKILL.md` §I 품질 체크리스트 단순화 (변환기 자동 강제 항목 제거)
- [x] `README.md` 전면 재작성 (웹 UI 언급 제거, 스킬 모드 우선, "완전 무료" 강조)
- [ ] PR → 머지 → `phase-6c-done` 태그

---

## Phase 7 — outline.json 스키마 안정화 (구 Phase 3, 후순위)

- [x] pydantic 모델 도입 (Phase 6a에서 `claude_ppt/schema.py`로 완료)
- [ ] `references/pptx-layouts.md` 자동 동기화 (현재는 수동 미러)
- [ ] outline 작성 시 `Outline.validate_full()` 호출 추가 (현재는 LLM 흐름에서만 호출됨, build CLI에서도 호출하도록)

---

## 백로그 (해당 페이즈 후 검토)

- [ ] settings.json hook으로 자동 커밋·자동 PR 흐름 (`update-config` 스킬)
- [ ] PPTX 슬라이드 마스터 템플릿 도입 (현재는 빈 슬라이드 + 도형 직접 생성)
- [ ] 다국어 지원 (현재 한국어 고정)
- [ ] PPTX → HTML 역변환 (PowerPoint에서 편집한 결과를 HTML로 동기화)
- [ ] `v0.1.0` 릴리스 — Phase 6c 머지 후
