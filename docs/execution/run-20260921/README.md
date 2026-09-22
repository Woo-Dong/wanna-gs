# 실행 작업 공간과 로그

사용자가 요청한 전체 goal의 작업 공간을 보존한다. 최신 진행/다음 행동은 [PROGRESS](../../PROGRESS.md), 원래 목표는 [GOAL](../../GOAL.md), task DAG/소유권은 [plan](plan.md), 외부 변경·작업 폴더는 [resource-ledger](resource-ledger.json)를 따른다. 이 폴더는 실행 증거이며 이전 단계의 PASS를 현재 제품 전체 완료로 읽지 않는다.

- 루트 프로젝트: `/Users/gsr/Desktop/workspace/2026-ralphton`.
- 기능별 worktree·실행 서버·초기 사용자 변경 patch를 임의로 삭제하지 않는다. 초기 patch는 `artifacts/private/run-20260921/initial-user-changes.patch`.
- 커밋 대상 요약/독립 보고서: 현재 폴더, 정책 ADR은 `docs/decisions/`, 테스트 장치는 `tests/`와 `scripts/`.
- 실제 실행 결과/TAP/SQLite 사본/화면/네트워크 메타데이터: `artifacts/raw/`. 검증 실패와 하네스 실패도 구분하여 남긴다.
- 인증 보조 도구/비밀 bypass/민감 평가 원형: `artifacts/private/run-20260921/`. 이 경로는 Git에서 제외한다. 키를 문서·스크린샷·공개 artifact로 옮기지 않는다.
- 보호 holdout은 evaluator만 접근한다. 구현자/실험자는 내용·정답·생성기를 열거나 출력하지 않는다.
- 앱의 대화 원본 기록과 이 저장소의 명령/시험 증거는 다르다. 이 폴더가 Codex 전체 대화 원본의 완전한 사본이라고 주장하지 않는다.

`git status`, 원격 PR/CI, Vercel deployment/source SHA와 최신 context를 대조한 후 이어서 작업한다. 작업 폴더 보존은 서버/외부 배포의 최종 성공을 의미하지 않는다. 최종 URL·G6·보호평가 결과가 남을 때까지 목표는 진행 중이다.

## 현재 실행 환경

Node22와 Python3.10 이상이 필요하다. 이 Mac의 system Python3.9는 glob의 root_dir 미지원으로 검증기 실행이 실패하므로 bundled Python을 사용한다. 실제 C1 복구 로그는 private c1-local-gate-python313.log에 보존한다. 별도 `2026-ralphton-nl-candidate` 워크트리는 기준선 앱을 변경하지 않고 개선안을 검토·CI·Preview로 만들기 위해 남겨두었다. root 작업 브랜치와 실제 최신 source는 PROGRESS 및 Git 원격으로 확인한다.

## 재개 지점

현재 후보·예산·미완료 게이트·서버 종료와 보존 경로는 [재개 체크포인트](resume-checkpoint.md)를 따른다. Preview READY 및 기술 CI는 실제 모델/최종 제출 통과가 아니다.

현재 context는 `context-merchant-cap-v17.json`이다. D46 budget20·ADR007 UX 기구는 검증됐지만 C5 holdout·C6 dev·D47 C7 validation이 실패했다. 승인된 고객 후보 한 번의 추가를 사용했으며 추가 후보를 자동 시작하지 않는다. 실제 새 UX/최종 QA/G5/G6는 미실행이다. 모든 후보 소스·원본 B0·실패와 미실행 기록을 유지한다.

최신: D47 C7 validation83/84·incomplete1 FAIL. 추가자동평가/후보/배포0, 준비서버종료·파일/빌드/로그보존. PR16 수량상한기술수리PASS와자연어FAIL을구분한다. 최신source·예산·재개조건은 PROGRESS/resume-checkpoint에기록한다.
