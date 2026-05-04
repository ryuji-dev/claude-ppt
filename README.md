# claude-ppt

YouTube 영상 요약 텍스트를 **다크 테마 HTML 슬라이드 세트** + **편집 가능한 .pptx 파일**로 동시에 변환하는 개인용 도구입니다.

> 같은 입력에서 두 가지 산출물을 한 번에 만듭니다.
> - **HTML**: 키보드 네비, 페이지 전환 애니메이션이 포함된 웹 미리보기·공유용
> - **PPTX**: PowerPoint·Keynote에서 열어 직접 편집·발표 가능한 파일

---

## 동작 방식

```
대본/요약 텍스트 ─▶  Claude Code 세션 (presentation_slides 스킬)
                         │
                         ├─▶ outline.json   (공통 슬라이드 구조)
                         │
                         ├─▶ slides/*.html + index.html  (스킬이 직접 생성)
                         │
                         └─▶ slides.pptx                 (python-pptx로 렌더)
```

Claude는 *Claude Code 세션 안에서만* 호출되며, 외부 API 키가 필요하지 않습니다.
파이썬 패키지 `claude_ppt`는 `outline.json` → `.pptx`로 변환하는 결정론적 변환기 역할만 합니다.

---

## 빠른 시작

### 1. 의존성 설치

```bash
# uv 사용 (권장)
uv sync

# 또는 pip
pip install -e .
```

### 2. 입력 준비

`{채널}/epNN-슬러그/script.md`에 대본 또는 요약 노트를 붙여넣습니다.
폴더 컨벤션은 [폴더 컨벤션](#폴더-컨벤션) 섹션을 참고하세요.

```text
클로드코드/
└── ep05-코워크/
    └── script.md
```

### 3. Claude Code 세션에서 스킬 트리거

```
프레젠테이션 슬라이드 만들어줘. 대본은 클로드코드/ep05-코워크/script.md
```

스킬이 다음을 자동 수행합니다:

1. 대본 파싱 (정돈된 대본 vs 거친 노트 자동 판단)
2. 섹션·슬라이드 목록 제안 → 사용자 확인
3. `outline.json` 작성
4. `slides/*.html` + `index.html` 생성
5. `python -m claude_ppt.render outline.json slides.pptx` 실행
6. 결과 보고

### 4. 결과 확인

```text
클로드코드/ep05-코워크/
├── script.md
├── outline.json
├── slides.pptx           ← PowerPoint·Keynote에서 열어 편집
└── slides/
    ├── index.html        ← 브라우저로 열어 미리보기
    ├── 01-intro-hook.html
    ├── 02-...html
    └── ...
```

---

## 폴더 컨벤션

`{채널}/epNN-슬러그/` 패턴을 따릅니다.

| 요소 | 예시 | 설명 |
|------|------|------|
| `채널` | `클로드코드` | 한글 가능 |
| `epNN` | `ep05` | 2자리 제로패딩 |
| `슬러그` | `코워크` | 영문 kebab 또는 한글 |

각 에피소드 폴더 안:
- `script.md` — 대본/요약 (입력)
- `outline.json` — 슬라이드 구조 (스킬이 생성)
- `slides.pptx` — 발표용 (스킬이 생성, gitignore 권장)
- `slides/` — HTML 세트 (스킬이 생성)

---

## 입력 예시

`script.md`는 두 가지 형태를 모두 받습니다.

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

**거친 요약 노트** (불릿 섞임): 스킬이 재구조화합니다.

```markdown
- 클로드 코워크 모드 핵심
- 자동 PR 생성
- 브랜치 격리
- 설치 3단계
```

---

## 트러블슈팅

**한글 폰트가 .pptx에서 깨짐**
→ python-pptx는 시스템 폰트를 참조합니다. macOS는 기본 'Apple SD Gothic Neo'가 잡혀 정상 표시됩니다. Windows에서 열 때 폰트가 없으면 자동 대체됩니다.

**`python-pptx` 설치 실패**
→ Python 3.10+ 필요. 가상환경 사용을 권장합니다 (`uv venv` 또는 `python -m venv .venv`).

**PowerPoint에서 "복구해야 합니다" 메시지**
→ `python -m claude_ppt.render`가 정상 종료되었는지 확인. 비정상 종료 시 `.pptx`가 손상될 수 있습니다.

---

## 라이선스

개인용 프로젝트.
