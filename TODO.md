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

각 레이아웃은 *독립 PR* 또는 *작은 묶음 PR*로. 병렬 작업 가능.

- [ ] `roadmap.py` + 테스트
- [ ] `comparison_2col.py` + 테스트
- [ ] `step_flow.py` + 테스트
- [ ] `diagram_box.py` + 테스트
- [ ] `grid_2x2.py` + 테스트
- [ ] `three_stage_flow.py` + 테스트
- [ ] `summary_grid.py` + 테스트
- [ ] `tests/fixtures/sample-outline.json` 확장 (8개 모두 포함)
- [ ] 통합 테스트: 8장짜리 outline → 8장 .pptx 산출
- [ ] `phase-2-done` 태그

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

- [ ] 브랜치: `feat/skill-pptx-output`
- [ ] `SKILL.md`에 §L. PPTX 출력 절차 추가
- [ ] outline.json 스키마 문서화 (스킬이 어떤 형태로 산출해야 하는지)
- [ ] 파이썬 호출 흐름 명시 (`python -m claude_ppt.render ...`)
- [ ] `references/pptx-layouts.md` — 8개 레이아웃별 PPTX 도형 매핑
- [ ] §I 품질 체크리스트에 PPTX 항목 추가
- [ ] PR → 머지 → `phase-4-done` 태그

---

## Phase 5 — 엔드투엔드 검증

- [ ] 브랜치: `feat/e2e-validation`
- [ ] 샘플 `script.md` 작성 (`samples/ep00-demo/script.md`, 인트로 + 섹션 2 + 마무리)
- [ ] Claude Code 세션에서 스킬 트리거 → 산출물 확인
- [ ] 브라우저: HTML 키보드 네비, 페이지 전환 정상
- [ ] PowerPoint·Keynote: PPTX 텍스트 편집 가능 확인
- [ ] HTML과 PPTX의 *메시지·구조 일치* 수동 확인 (1:1 픽셀 매칭은 목표 X)
- [ ] 발견된 이슈 → GitHub Issues로 등록
- [ ] PR → 머지 → `phase-5-done` 태그
- [ ] `v0.1.0` 릴리스 (`gh release create v0.1.0`)

---

## 백로그 (해당 페이즈 후 검토)

- [ ] settings.json hook으로 자동 커밋·자동 PR 흐름 (`update-config` 스킬)
- [ ] PPTX 슬라이드 마스터 템플릿 도입 (현재는 빈 슬라이드 + 도형 직접 생성)
- [ ] 다국어 지원 (현재 한국어 고정)
- [ ] PPTX → HTML 역변환 (PowerPoint에서 편집한 결과를 HTML로 동기화)
