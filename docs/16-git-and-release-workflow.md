# GitHub 기반 단계별 개발·커밋·배포

상태: 실행 계약. 사용자 최신 지시에 따라 GitHub 저장소·인증·Vercel 연결 등 시작 설정이 완료됐다고 가정한다. 실제 실행 때 현재 상태를 재검증하되 매 단계 사용자 승인 절차로 바꾸지 않는다. 초기 docs 저장소와 커밋은 사용자 요청으로 생성했다. push는 현재 GitHub 쓰기 인증이 없어 차단됐으며 결과·재개 방법은 PROGRESS에서 확인한다. 이 상태는 향후 goal의 설정 완료 가정과 구분한다. 앱 PR·CI·배포는 별도 구현 단계다.

## 권한과 개발 환경

사용자가 [GOAL.md](GOAL.md)의 구현 목표를 시작하면 지정 저장소의 작업 브랜치, commit/push, PR 작성/수정, 검증된 PR 병합, 연결된 Vercel Preview/제출 배포를 이 계약에 따라 반복 확인 없이 수행한다. 이미 승인된 비용·권한 범위 안에서 테스트 DB migration/seed도 수행한다. 다른 저장소·새 유료 결제·권한 우회·사용자 데이터 파괴로 확대하지 않는다.

개발 조정자와 서브 에이전트는 현재 Codex 목표 안에서 동작한다. GitHub Actions는 결정적 테스트와 배포 검사를 실행한다. Actions 안에서 Codex/LLM 개발 에이전트를 새 API로 호스팅하는 것을 필수로 만들지 않는다.

시작 확인은 repo/remote, 현재 branch와 사용자 변경, 인증된 대상, PR/merge/Actions 권한, 보호 규칙, Vercel Production branch, Preview/Production SQLite 자산·브라우저 저장·모델 접근이다. 비밀값은 출력하지 않는다. 같은 대상의 기존 Git/Vercel 상태와 유효 preflight 증거가 있으면 재사용하고, 불일치·만료·관련 변경만 갱신한다. 저장소가 있다는 이유로 새 repo나 orphan 이력을 만들지 않는다. 설정 완료 가정이 실제 실패하면 환경 블로커로 기록하고 독립 작업을 계속한다.

문서 초기 커밋 이후 첫 앱 작업은 최소 shell과 기본 검사로 실제 Preview를 만든다. deployment ID/source SHA와 브라우저 기본 동작 검사를 관측한 다음 [WORKPLAN](WORKPLAN.md)의 DAG를 실제 branch/check/deployment 조건에 맞춰 `PLAN-READY`로 고정한다. Preview Ready는 제품 기능, G5, Production 또는 G6 통과가 아니다.

## 브랜치 역할

| 역할 | 이름 예시 | 수명과 사용 |
|---|---|---|
| 제출 | `main` | Vercel Production에 연결된 안정된 제출 기준 |
| 누적 통합 | `codex/integration` | 검증한 기능을 순서대로 통합, Preview에서 반복 검사 |
| 작업 | `codex/<task-id>-<summary>` | 한 기능/수정/기반 작업, 짧게 유지 후 PR 병합 |

이름은 예시다. 실제 기본/Production 브랜치를 탐지해 역할을 매핑하고 기존 브랜치를 임의로 이름 변경하거나 덮어쓰지 않는다. 별도 develop/release/hotfix 계층을 상시 만들지 않는다. 최종 릴리스는 통합→제출 PR로 표현한다.

동시 구현자는 각자 격리 worktree와 작업 브랜치를 사용하고 통합 담당자만 누적 브랜치에 변경을 합친다. 격리 작업 트리 생성 권한이 없으면 파일 소유권으로 순차 작업하며 같은 checkout에서 동시에 branch 전환하지 않는다. 공통 schema/migration/lockfile/CI에는 단일 작성자를 유지한다. SQLite 테스트 파일과 브라우저 namespace도 작업별로 분리한다.

작업→통합 PR은 저장소가 허용하면 squash merge로 한 논리 단위를 정리할 수 있다. 통합→`main` 릴리스는 검증한 누적 이력과 ancestry를 보존하는 merge commit 또는 fast-forward를 사용한다. 실제 repo 정책이 다른 허용 방식을 강제하면 그 방식을 기록하고 exact tree/SHA를 검증한다. 릴리스 뒤 `main` 결과를 통합 branch에 fast-forward/back-merge하고 같은 ancestry 및 필수 checks를 확인해 다음 작업이 병합 전 기반으로 갈라지지 않게 한다.

## 매 작업 루프

1. 계약: task ID, 정책 ADR, CORE/AC/BR, Context Manifest hash, 조사 근거와 출처·변경 이력, 수정 파일, 선행 작업과 적용 게이트를 확정한다. 미정 정책은 [자율 결정 절차](17-autonomous-decisions.md)로 해결한다.
2. 구현: 현재 통합 기반에서 작업 branch/worktree를 만든다. 기능과 해당 테스트를 같은 작업으로 개발한다.
3. 로컬 검증: 자체 단위·적용 영역 통합을 실행하고 별도 검증자가 결과/반례를 확인한다. 첫 기반 작업에는 초기 구축 검사를 적용하며 미구현 기능의 전체 AC를 요구하지 않는다.
4. 체크포인트: 통과한 논리적 단위로 commit하고 지정 remote에 push한다. 파일을 명시적으로 stage하고 diff를 검토한다. 관련 없는 사용자 변경, 비밀값, `.env`, 실제 개인정보, 덩치 큰 원본 로그를 포함하지 않는다.
5. PR: 작업→통합 PR에 문제와 바뀐 동작, 정책 결정, 검증 결과와 제한을 적는다. 기존 PR이 있으면 갱신한다. 제공되는 task 산출물 도구가 있으면 만든 PR URL을 현재 작업에 연결한다.
6. CI/Preview: 정확한 PR head SHA의 required checks를 기다리고 필요한 Preview 브라우저 검증을 수행한다. Ready 표시만으로 E2E를 대체하지 않는다. 실패하면 같은 작업에서 복구한다.
7. 최신 기반: 통합 branch가 바뀌면 최신 기반을 작업에 merge하고 충돌을 해결한다. 새 조합에 영향받은 검사·리뷰를 다시 실행한다. 공유 이력 재작성 없이 일반 merge를 기본으로 한다.
8. 병합: 유효한 독립 검증·현재 head/대상 기반 checks가 갖춰지면 통합 담당자가 직렬로 병합한다. 작업→통합에는 squash merge를 기본 제안으로 사용하고, 통합→`main`에는 위 릴리스 ancestry 규칙을 적용한다. 검증한 SHA와 병합 대상이 바뀌면 다시 확인한다.
9. 누적 검증: 실제 통합 결과에서 영향받은 G2/G3/G4를 실행한다. 누적 결과 실패 시 후속 병합을 막고 수정 또는 안전한 revert를 수행한다.
10. 기록: research claim→task/context→ADR→schema/seed/eval/prompt/config→commit→PR→CI→통합 결과→Preview를 연결한다. PROGRESS 상단 task/branch/PR/마지막 유효 게이트/Production/다음 행동 포인터를 갱신하고 다음 작업으로 이동한다.

모든 함수나 테스트 하나마다 commit하지 않는다. 독립적으로 설명·검증·되돌릴 수 있는 단위마다 만든다. 예: `feat(requests): persist confirmed product requests`, `test(allocation): cover concurrent supply claims`, `fix(pickup): reject collection at deadline`. commit 전에 돌린 테스트와 push 뒤에만 가능한 CI/Preview를 구별한다.

실패 상태도 작업 복구를 위해 remote에 보존할 필요가 있으면 명시적 WIP/draft로 올릴 수 있으나 통과한 단계나 merge 후보로 세지 않는다. 기본 체크포인트는 테스트가 통과한 상태다.

## CI와 검증 게이트

GATE-BOOTSTRAP의 첫 작업에서 lockfile/runtime, 단위/통합 실행기, 결과 수집, `.github/workflows/`를 만든다. 다음 검사를 구현한다.

| 검사 | 실행 시점 | 요구 |
|---|---|---|
| docs/contracts | 관련 PR | 링크·결정 추적·API/상태/정책 일치 |
| quality | 코드 PR | 타입·정적 검사·build·적용 단위 검사 |
| db-integration | 거래/DB/권한 변경 PR | 실제 격리 sql.js SQLite·마이그레이션·seed·순차 상태 변경 |
| boundary/e2e-fixture | 영향 경계 PR와 통합 결과 | 해당 연결과 브라우저 상태 검증 |
| preview/live | 필요한 AI/배포 변경, 릴리스 후보 | 정확한 deployment+SHA의 실제 연결·eval/E2E 증거 |
| release | 통합→제출 PR | G5, 최종 정책 감사, 관련 모든 필수 증거 |

검사 이름·실행 도구는 초기 구축에서 고정한다. 새 aggregate check의 기본 contract name은 `gate`로 하고 실제 GitHub ruleset/branch protection의 required check와 정확히 매핑한다. 기존 보호 규칙·checks를 자동 비활성화하거나 이름만 같은 로컬 결과로 대체하지 않는다. path filter 때문에 required check가 사라져 무한 pending이 되지 않도록 aggregate check는 항상 결과를 내되, 현재 phase/task manifest에 적용 가능한 검사만 실행하고 `not_applicable` 근거를 검증한다. 아직 구현하지 않은 완제품 검사를 초기 구축에 요구하지 않으며, 필수 기능 제외를 `not_applicable`로 위장하지 않는다. 테스트 0개·누락·stale 결과는 통과하지 않는다.

GitHub Actions에서 실제 모델 인증이 불가능하면 승인된 Codex 실행 환경이 정확한 Preview 대상으로 live 검사를 수행하고 검증 가능한 artifact/check로 연결할 수 있다. CI 결과가 아닌 실행을 CI 성공이라고 부르지 않는다. 로컬 서명 없는 보고서만으로 악의적 증거 위조 방지까지 보장하지 않는다.

첫 docs-only 저장소의 shell/bootstrap PR은 실제 존재하는 기반 검사로만 통과시킨다. 이후 milestone별 manifest에 적용 검사와 필수 phase를 명시해 검사 집합을 늘리고, 릴리스 시 전체 필수 AC를 요구한다. CI 실행기를 만드는 첫 PR에 아직 존재하지 않는 완제품 검사를 요구하는 순환을 만들지 않는다. shell/bootstrap 성공을 이후 제품 게이트에 복사하지 않는다.

## 독립 리뷰와 GitHub 승인 구분

서로 다른 서브 에이전트의 검토는 개발 과정의 독립 검토다. 동일 GitHub 계정으로 올린 PR을 그 계정이 공식 승인한 것처럼 기록하지 않는다. 무인 흐름의 사전 설정은 필수 status checks 및 PR 사용을 중심으로 두고, 인간 승인 필수 규칙이 있으면 실제 별도 자격을 갖춘 승인 경로가 있어야 한다.

설정된 보호 규칙·환경 승인·CODEOWNERS가 권한을 막으면 관리자 bypass, 보호 해제, 가짜 approval로 통과하지 않는다. 외부 설정 불일치로 기록한다. 사용자의 자율 개발 지시를 매 PR마다 다시 확인할 이유는 없으며 실제 권한 장벽만 구별한다.

## Vercel과 최종 릴리스

작업/통합 branch push의 Preview는 개발 검사에 사용한다. 제출 branch 병합은 Production 배포를 유발할 수 있으므로 통합용 branch를 제출 branch와 구분한다. 실제 프로젝트의 branch/환경 연결은 시작 시 확인한다. 초기 연결 smoke/Preview는 G5 이전에도 가능하다.

- 기능 PR: 그 시점에 적용되는 G0~G4와 독립 검증. 전체 제품 완료를 요구하지 않는다.
- 릴리스 PR: 최종 정책 감사와 G5를 먼저 통과하고 최신 제출 기반과 조합한 내용을 검사한다. AC-19의 최종 URL 검증은 아직 G6 대기다.
- 병합 후: 생성된 정확한 Production deployment ID·source SHA·DB/schema/seed·모델 모드를 읽는다. 가변 branch 별칭 URL만으로 과거 결과와 혼동하지 않는다.
- G6: 최종 제출 URL에서 live 모델·실제 DB·브라우저 정상/대표 예외·reset·접근성을 확인한다. 이후에만 goal 완료다.

### 검증 대상 커밋과 일치하는 `main` gate

`main` 병합은 다음 식별자가 모두 고정된 한 릴리스 후보에만 허용한다.

- release PR head SHA와 최신 `main` base SHA.
- 둘을 결합해 검사한 exact candidate/merge result SHA 또는 저장소가 제공하는 동등한 merge queue SHA.
- 그 SHA의 required aggregate checks, G5, 최종 정책/운영 감사, 릴리스 Preview deployment ID/source SHA, DB schema/seed와 model/prompt/eval 버전.
- 독립 customer-qa와 merchant-qa의 대상 URL/SHA.

병합 직전에 원격에서 head/base/check/review/deployment를 다시 읽는다. head나 base가 이동했거나 check가 다른 SHA에 붙었거나 새 commit이 생기면 이전 성공을 재사용하지 않고 영향받은 검사를 새 검증 대상 커밋에서 실행한다. branch 이름, 최신 Preview 별칭, 과거 green check는 검증 대상 커밋 기준 증거가 아니다.

검증된 PR을 병합한 뒤 실제 `main` HEAD/merge SHA를 기록하고 Vercel Production deployment의 `source SHA == main merge SHA`를 확인한다. 저장소 merge 방식 때문에 사전 candidate와 merge SHA가 달라지면 동일 tree 확인과 main용 필수 결정적 검사를 수행하되, Production G6를 생략하지 않는다. 배포가 다른 SHA를 가리키면 G6를 시작하지 않는다.

Preview/Test 파일·브라우저 namespace와 제출 origin을 분리한다. 로컬 seed builder의 마이그레이션과 배포 자산 생성을 단일 담당자가 관리한다. 기존 브라우저 snapshot의 호환성은 로드 시 확인하며 서버 함수가 DB migration을 실행하지 않는다. 앱 복구와 브라우저 snapshot 복구는 별도로 판단한다. 실패 시 이미 작동하는 배포를 보존하면서 수정/호환 복구를 수행하고 다시 G6를 검증한다.

## 실패와 재개

- push timeout: 원격 branch SHA부터 조회해 이미 반영된 push를 중복/force 실행하지 않는다.
- PR/merge/deployment timeout: 기존 PR 상태·merge SHA·deployment ID를 조회하고 이어간다.
- 충돌: 원래 의도를 대조해 필요한 부분만 해결하고 재검증한다. 파일 전체 ours/theirs 또는 사용자 작업 삭제로 해결하지 않는다.
- 통합 실패: 영향받은 후속 병합만 중단하고 복구 담당에게 넘긴다. git revert는 영향/DB 호환성을 확인한 새 commit으로 수행한다.
- 중단/재개: PROGRESS와 작업 계약 → 실제 local/remote SHA → 열린 PR/CI → 배포/DB 상태 → 유효한 게이트 순으로 대조한다.

force push, reset --hard, 공유 이력 삭제, 사용자 변경 자동 stash/폐기는 기본 경로에 없다. 실제 명령은 현재 도구/저장소 상태에 맞춰 결정한다.

## 증거의 저장

[체크포인트 양식](templates/release-checkpoint.md)을 사용한다. SHA를 자기 자신의 commit 문서에 넣으려는 순환을 만들지 않는다. 검사 당시 content fingerprint를 기록하고 commit/CI/deployment SHA는 외부 artifact/check 또는 다음 기록에서 연결한다. research/decision/context/schema/seed/eval/prompt/config의 입력 버전과 결과 SHA를 함께 남겨 어떤 변경이 증거를 stale로 만드는지 추적한다. 최종 보고서만 추가한 변경과 실행 코드 변경을 영향도로 구분하며, 실제 제출 deployment 검증은 항상 그 배포의 revision을 기준으로 한다. 최종 기록 갱신 때문에 불필요한 Production 배포/검증을 무한 반복하지 않도록 evidence 저장 경로와 문서 전용 변경 규칙을 초기 구축에서 정한다.

## 공식 참고

2026-09-20 확인. 짧은 branch와 PR 흐름은 [GitHub flow](https://docs.github.com/en/get-started/using-github/github-flow), required checks와 리뷰 제약은 [보호 브랜치](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches)를 참고했다. Git 연동의 Preview/Production 동작은 [Vercel GitHub 배포](https://vercel.com/docs/git/vercel-for-github)를 확인했다. 통합 branch·게이트·에이전트 역할은 이 프로젝트의 자체 설계다.

## 초기 문서 커밋과 중간 릴리스 제안

아직 Git 이력이 없는 docs-only 폴더를 빈 원격 저장소에 연결하는 초기 커밋은 문서 링크·ID·스킬 형식·기존 검사기 테스트로 검증한다. 앱 G5를 요구하지 않으며, 이 커밋을 앱 릴리스로 보고하지 않는다. 원격 이력이 생겼으면 먼저 조회하고 보존한다. 초기 push에 force를 사용하지 않는다.

fixture G4 이후 중간 Production을 허용하자는 외부 제안은 [검토 기록](reviews/2026-09-21-execution-proposals.md)의 조건부 제안으로 남긴다. 현재 실행 정책은 Preview 중간 확인과 최종 G5→main→Production→G6를 유지한다. 중간 배포를 채택할 때는 CP5/CP6 등 별도 상태·잔여 AC·모드 표시·복구·정확한 SHA 검증을 정의하고 관련 정책을 함께 갱신해야 한다. fixture 성공을 기존 최종 G5/G6로 바꾸지 않는다.
