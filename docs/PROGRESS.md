# 진행 기록

최종 갱신: 2026-09-21. 앱 goal은 아직 시작하지 않았다.

## 현재 포인터

```text
현재 task: 문서 검증·초기 커밋 완료, GitHub push 인증 차단
branch: main (원격 tracking 미설정)
PR: 없음
마지막 유효 게이트: 제품 게이트 미실행
마지막 Production deployment: 없음
다음 한 가지: GitHub 쓰기 인증 구성 후 기존 main push
```

## 현재 상태

| 항목 | 상태 | 증거 |
|---|---|---|
| 요구사항·실행 계약·스킬·템플릿 | 최신 지시 반영·문서 검증 완료 | README·card·02·WORKPLAN·GOAL |
| 위임 운영 결정 | ADR-001 채택, 실행 검증 전 | DECISION_INDEX·ADR-001 |
| GitHub | origin 연결·main 초기 커밋 완료. push는 인증 차단 | 초기 커밋 `940c31b`, 아래 실제 결과 |
| 로컬 사전점검 검사기 | 기존 7개 테스트 재실행 통과 | `.agents/skills/wanna-gs-preflight/scripts/` |
| 앱·CI·게이트 실행기·DB seed | 미구현 | 기능 개발 goal 미시작 |
| Vercel·Neon·Gateway·Gemini | 인증·실제 호출·잔량·배포 미검증 | 환경 준비 후 preflight 필요 |
| 앱 단위·통합·E2E·실제 모델 평가 | 미실행 | 문서 검사와 구분 |
| 최종 제출 URL | 없음 | 실제 배포 전 |

## 반영한 기준

- 자연어 요청부터 한 점포 수요, 보수적 발주, 공급 확보 후 모의 결제, 입고·픽업 알림부터 정확히 48시간 수령까지 연결한다. 세부 요구는 CORE와 02번을 따른다.
- 문서는 최초 구현의 현재 기준으로 관리하고 Git/결정 이력으로 변경을 추적한다. 재현용 schema·seed·모델·평가 식별값은 유지한다.
- clone/worktree 경로를 실행 시 확인한다. 특정 사용자 홈 경로에 의존하지 않는다.
- card.md의 목적 보존 기준을 시작·인계·복구와 작업/실패/검증 보고서에 연결한다. 실행기·CI 강제는 초기 구현에 포함한다.
- ADR-001에 따라 최소 seed 이후 기능 구현과 전체 자료 수집을 병행한다. 정식 QA·자연어 기준선·최종 게이트는 전체 seed를 요구한다.
- 무료 Gateway 기본과 사용자 키의 Gemini 예비 경로를 유지한다. 실제 잔량·품질·최종 배포 검증은 남아 있다.
- 강제 full-access 설정과 fixture 기반 중간 Production 제안은 현 실행 계약으로 채택하지 않았다. 중간 공유는 Preview, 최종 Production은 G5 후 G6 검증이다.
- 중복된 과거 리뷰 5개는 [통합 검토 기록](reviews/2026-09-21-execution-proposals.md)에 결론·기존 검사 범위를 보존하고 삭제했다. `.gitignore`로 비밀값·로컬 연결·테스트 부산물·임시 파일을 제외했다.

## 현재 검증

2026-09-21 실제 실행 결과:

- Markdown 56개: 로컬 링크 242개와 코드 블록 검사 통과. 고정 사용자 홈 경로·문서 릴리스 번호 잔재 없음.
- D 34개·CORE 23개·AC 29개·O 12개·R 44개 ID 순서·중복·누락 검사 통과.
- WORKPLAN Mermaid DAG 35개 노드·55개 간선: 순환 없음. F00은 전체 수집/D05를 기다리지 않고 N01/Q01/Q02/G5는 D05에 의존함을 확인.
- 프로젝트 스킬 8개 `quick_validate.py` 통과.
- `python3 .agents/skills/wanna-gs-preflight/scripts/test_inspect_environment.py -v`: 7개 테스트 통과. 비밀값 정제, docs-only의 READY 오판 방지, timeout, 기존 보고서 보존, 임시 Git 관찰 등을 검사.
- 게시 대상 59개 텍스트 파일의 알려진 토큰·개인키·DB 인증 URL 패턴 검사: 후보 없음. 패턴 검사로 모든 비밀정보 부재를 보증하지 않음.
- 두 독립 검토자 `review_release_proposals`, `review_seed_proposals`가 실행/데이터 의존성과 제품/목적 보존을 검토. README의 전체 seed 대기 표현과 10번의 미구현 화면/API 의존을 수정한 뒤 재검토에서 추가 필수 문제 없음.

문서·스킬과 로컬 검사기 검증이다. 앱 기능·실제 외부 연동·CI 강제·배포 게이트 PASS를 뜻하지 않는다.

## 다음 작업

1. GitHub 쓰기 인증을 구성한 뒤 기존 main을 push한다. Git init이나 초기 커밋을 다시 만들 필요는 없다.
2. README의 계정·키·연동 준비 후 preflight inspect/live를 수행한다.
3. 실제 연동 결과를 확인한 뒤 별도 `/goal`로 앱 개발을 시작한다.

## 기록 원칙

작업 ID·사용자 목적·변경·적용 결정·실제 검증·증거·미실행/차단·다음 행동을 남긴다. 오래된 세부 기록은 통합할 수 있으나 실패·블로커를 지우거나 실행 전인 기능을 완료로 표시하지 않는다. 이전 문서 감사와 로컬 검사 이력은 통합 검토 기록에서 확인한다.

## Git 초기화·커밋과 게시 상태

문서 검증과 독립 재검토를 마친 뒤 `git init -b main`을 실행했다. origin은 `https://github.com/Woo-Dong/wanna-gs.git`이다. 59개 파일을 대상으로 `git diff --cached --check`를 통과한 뒤 초기 커밋 `940c31b` (`docs: initialize WANNA GS implementation plan`)을 만들었다.

`GIT_TERMINAL_PROMPT=0 git push -u origin main`은 `could not read Username`으로 실패했다. 현재 Git은 osxkeychain credential helper를 사용하지만 이 실행에서 사용할 HTTPS 인증을 얻지 못했다. 기존 SSH 경로도 BatchMode·StrictHostKeyChecking을 유지해 확인했으나 `Permission denied (publickey)`였다. 계정·키를 새로 만들거나 읽어 출력하지 않았고 원격 이력은 변경하지 않았다. GitHub CLI도 현재 설치돼 있지 않다.

사용자가 이 환경에 저장소 쓰기 권한이 있는 GitHub 인증을 연결하면 현재 프로젝트 루트에서 아래 명령으로 이어간다. push 직전 원격이 바뀌었다면 먼저 내용을 확인하고 보존하며 force push하지 않는다.

```bash
git ls-remote origin
git push -u origin main
```

인증이 필요한 외부 단계만 남았으며 문서·스킬·로컬 검증과 초기 커밋은 완료됐다. 이 상태 기록도 후속 로컬 커밋으로 보존한다. 앱 preflight와 Vercel 배포가 성공한 것으로 해석하지 않는다.
