# goal 전 환경·외부 연동 사전점검

상태: 최초 구현 기준. 전용 스킬과 로컬 검사 스크립트를 제공한다. 실제 외부 기본 동작 검사는 사용자가 스킬을 실행할 때 수행한다. 앱 외부 연동은 아직 미검증이다. 문서 저장소의 Git 연결과 실제 검사 이력은 PROGRESS에서 확인한다. 목표는 한 번의 goal이 사소한 설정/정책 질문 때문에 멈추지 않도록 실제 가능한 경로와 부족한 준비를 미리 보여주는 것이다.

## 1. 먼저 준비할 것

| 항목 | 미리 구성할 내용 | 확인 기준 |
|---|---|---|
| 프로젝트 | 이 폴더를 GitHub repo의 clone/worktree로 열기, remote·Git 작성자 설정 | docs와 루트 AGENTS, 프로젝트 스킬이 같은 repo에 존재 |
| GitHub | 올바른 계정 로그인, 지정 repo push/PR/merge, Actions 실행과 workflow 수정 권한 | CLI 예시는 gh, 같은 능력의 connector도 가능 |
| GitHub 정책 | 실제 통합/제출 branch·required checks·ruleset·CODEOWNERS·환경 승인 | 인간 승인 필수면 별도 허용 경로 필요. 에이전트가 보호 규칙을 해제하지 않음 |
| Vercel | 대상 팀/프로젝트 로그인·GitHub repo 연결·Production branch 확인 | Preview/배포·환경변수 조회/설정에 필요한 허용 권한 |
| DB | 무료/허용된 PostgreSQL, 테스트·Preview·제출 범위 분리 | 로컬 및 배포 서버 연결, 격리 schema/branch/table 생성·CRUD·transaction 권한 |
| 앱 모델 | Gateway 인증·잔액, 사용자가 발급·주입한 Gemini 키·무료 한도, 양쪽 모델 ID | 로컬/배포 실제 호출과 25번 전환 준비 확인 |
| 런타임 | 지원 Node LTS·패키지 관리자·Git·Python 3, 테스트 브라우저 설치/실행 | 정확한 버전은 확인 후 lockfile로 고정 |
| Codex 도구 | goal 지원, 파일·shell·네트워크·브라우저·서브 에이전트 접근 | API 키나 새 계정 없이 현재 개발 환경에서 실제 작업 수행 |
| 비밀값 | 서버용 DB/model 인증은 환경변수/플랫폼 비밀 저장소 | 채팅/README/commit/클라이언트 번들에 값 저장 금지 |

GitHub/Vercel 인증에는 현재 CLI 도움말이나 제공 connector의 인증 절차를 사용한다. GitHub에서는 auth·repo 조회, Vercel에서는 identity·프로젝트 연결을 확인한다. 입력 토큰을 문서로 제출할 필요는 없다. 로컬 `.vercel/project.json`은 연결 방법 중 하나이며 connector/명시적 대상 정보로 대체할 수 있다.

DB URL과 Gateway 인증은 local/Preview/Production 각각 필요할 수 있다. 환경변수 이름만 예시 파일에 적고 값은 해당 환경에 저장한다. 앱 실행의 정확한 인증 방식은 실제 지원 경로로 확인한다. CI가 로컬 로그인 상태를 자동 상속한다고 가정하지 않는다.

제품 코드·package.json·workflow가 아직 없다는 것은 정상 docs-only 시작이다. 이를 설치 실패로 보고하지 않고 초기 구축 대상으로 표시한다.

## 2. 사용 방법

프로젝트를 연 뒤 다음 중 하나를 Codex에 요청한다. 스킬 선택 목록에 보이지 않으면 명시한 SKILL.md를 읽고 실행하도록 한다.

읽기 전용 점검:

```text
$wanna-gs-preflight 이 프로젝트를 inspect 모드로 점검하고 부족한 설정을 알려줘. GitHub/Vercel 인증 상태도 읽기 전용으로 확인해줘.
```

실제 연동 시험:

```text
$wanna-gs-preflight 이 프로젝트를 live 모드로 사전점검해줘. docs/18-environment-preflight.md 범위의 임시 GitHub 브랜치·PR·CI·Vercel Preview·격리 DB·실제 모델·브라우저·서브 에이전트 시험과 정리를 진행하고, goal 시작 준비 상태와 미검증 릴리스 조건을 보고해줘.
```

자동 발견이 안 되면:

```text
.agents/skills/wanna-gs-preflight/SKILL.md를 읽고 이 프로젝트에서 live 사전점검을 실행해줘.
```

터미널에서는 로컬 검사기만 직접 실행할 수 있다. 아래 명령은 프로젝트 루트 기준이다.

```bash
python3 .agents/skills/wanna-gs-preflight/scripts/inspect_environment.py --project .
python3 .agents/skills/wanna-gs-preflight/scripts/inspect_environment.py --project . --check-auth
```

`--output /tmp/<새로운-보고서이름>.json`으로 새 파일을 만들 수 있다. 기존 파일은 덮어쓰지 않는다. `.env`를 읽거나 값을 출력하지 않는다. `--check-auth`는 gh/Vercel의 읽기 전용 네트워크 조회를 추가한다. 종료 코드 2는 관찰만 완료한 PARTIAL, 1은 확인된 로컬 BLOCKED, 3은 보고서 쓰기 실패다. CLI가 없으면 사용할 수 있는 connector를 스킬이 검증할 수 있다. 검사기는 live 루프를 수행하지 않으며 그 자체로 READY를 반환하지 않는다.

스킬 폴더와 참조 docs를 함께 관리한다. SKILL.md 하나만 다른 폴더에 복사하면 참조 경로가 깨질 수 있다. 글로벌 설치를 별도 선행조건으로 만들지 않는다.

## 3. live 시험 범위

기존 작업 트리를 건드리지 않고 run-id별 임시 worktree와 `preflight/<run-id>/base`, `preflight/<run-id>/probe` 같은 두 branch를 사용한다. PR은 임시 base ← 임시 probe다. 기본/통합/제출 branch로 merge하지 않는다. 실제 Production 배포·설정·데이터는 변경하지 않는다.

처음에 ledger에 repo·project·namespace·예정 작업을 기록하고 생성 후 PR/branch SHA/deployment/DB 객체 ID를 연결한다. 이미 있는 사용자 리소스를 임시 리소스로 취급하지 않는다. 외부 쓰기는 live 모드 실행 지시 범위이며 같은 임시 시험 단계마다 다시 승인받지 않는다. 실제 sandbox/조직 권한 요청이 필요한 경우에는 그 제한을 따른다.

Preview가 해당 프로젝트 설정상 Production을 유발할 수 있으면 실제 실행을 멈추고 격리 경로를 확인한다. 별도 기본 동작 검사 프로젝트를 만들었다면 본 프로젝트의 연결을 검증한 것으로 보고하지 않는다. 환경변수 변경이 필요하면 소유가 명확한 시험 범위에서만 하며 기존 값을 덮어쓰지 않는다.

## 4. 실제 검사 목록

| ID | 실행과 관측 | PASS 조건 |
|---|---|---|
| P00 local | repo/remote·사용자 변경·tool/version·auth·목표 도구 | 올바른 대상, 필요한 실행 수단과 인증 확인; CLI 대체 경로 명시 |
| P01 permissions | GitHub ruleset/branch/환경 정책, Vercel branch mapping, 실제 모델 잔량 | 알려진 무인 흐름 차단 없음, 미검증 권한 별도 표시 |
| P02 agents | 기본 동작 검사 담당과 별도 검증 에이전트, 서로 다른 두 정책 검토 역할을 실제 배정 | 서로 다른 ID의 결과·최소 반례 검토·인계 확인, 슬롯 적으면 순차 수행 |
| P03 scaffold | 임시 최소 페이지/API·고정 fixture·테스트 실행기 구성 | lockfile/runtime 일치, 단위/실패 검사·build 실행. 제품 기능 구현 아님 |
| P04 github | 두 임시 branch push, PR, workflow/Actions, 임시 base merge | 정확한 SHA의 CI 성공·원격 merge 확인. 실제 제출 보호 branch 권한을 증명한 것은 아님 |
| P05 preview | 연결된 Vercel 프로젝트의 비 Production 배포 | deployment/source SHA 일치, health HTTP 및 브라우저 확인. Ready만으로 PASS 금지 |
| P06 db-local | 격리된 DB/schema에 마이그레이션·insert/read·transaction 복구·경합 최소 검사 | write/read 기대값·복구 후 미존재·동시 수량/한도 보존. 마이그레이션 역변환을 검증했다는 뜻 아님 |
| P07 db-server | Preview API에서 같은 격리 DB 왕복 | 배포 서버 write/read 확인, 서버 비밀값 브라우저 미노출, local 결과와 분리 |
| P08 model | Preview 서버에서 Gateway와 Gemini 직접 호출로 각각 작은 한국어 요청 | 양쪽 연결 상태·한도·설정 전환 증거, Gemini와 선택한 경로의 실제 구조화 응답. Gateway 소진 시 아래 판정 적용. 제품 품질은 후속 G4/G5에서 검증 |
| P09 browser | 브라우저 입력→API→DB/모델→화면, 오류 입력 1건 | 브라우저 실행기 실제 실행, 저장 결과/표시/오류 회복 대조 |
| P10 준비 상태 | 원격/배포/DB/모델/agent 증거 집계 및 두 관점 확인 | 검사 누락·상태 오표시·known blocker가 없는지 독립 검토 |
| P11 cleanup | 임시 PR/branch/worktree/Preview/DB 객체 정리 | 생성 ledger와 일치하는 ID만 처리, 정리/보존/실패 내역 명시 |

실행 순서는 의존성을 따른다. P04 CI의 DB 검사는 격리된 CI 서비스 DB로 실행할 수 있고, P06/P07은 실제 선택 DB 드라이버와 배포 경로를 확인한다. 권한 실패 때문에 하나를 못 해도 독립 항목은 계속한다. 실제 앱 품질 eval·도메인 E2E는 goal의 G1~G6 작업이며 기본 동작 검사를 그 증거로 재사용하지 않는다.

## 5. 기본 동작 검사 구현 규칙

- 테스트 앱에는 상품/예약 기능 대신 작은 입력·저장·조회와 제한된 모델 응답만 둔다. 후속 구현 재사용은 검토 후 진행한다.
- DB는 이미 승인된 테스트 DB 또는 격리 자원을 사용한다. run-id로 소유가 확인되는 namespace/table만 생성·삭제한다. 제출 스키마에 무작정 마이그레이션하거나 전체 DB reset을 하지 않는다.
- 복구 테스트는 실제 트랜잭션을 실패/취소시켜 write가 남지 않는지 확인한다. 드라이버의 트랜잭션 지원 여부를 API 이름만 보고 추정하지 않는다.
- 모델 호출은 최소 성공·오류 흐름으로 제한하고 무료/승인 잔량을 확인한다. 무제한 eval을 돌리지 않는다.
- 임시 DB/모델 probe API는 인증된 시험 세션이나 서버 전용 일회 키로 보호한다. 임의 SQL·URL·모델/토큰 수를 요청 입력으로 받아 실행하지 않는다. 공개 비용 소진 endpoint를 만들지 않는다.
- GitHub Actions는 검증된 신뢰 branch 코드에만 필요한 비밀을 제공한다. 외부 fork 코드를 높은 권한으로 실행하는 우회 경로를 만들지 않는다.
- 도구 응답·Git remote·오류 로그에 토큰이 섞일 수 있으므로 원본 전체를 보고서에 붙이지 않는다. 실행 명령에도 비밀값을 인자로 넣지 않는다.

## 6. 판정과 미검증 범위

[보고서 양식](templates/preflight-report.md)에 다음을 구분한다.

- `READY` / `ready_for_goal: true`: 목표 시작 필수 P00~P11에 실제 증거가 있고 알려진 필수 차단이 없다. 테스트 리소스를 의도적으로 보존했다면 소유·영향·정리 방법을 기록한다.
- `PARTIAL`: 일부 검사 미실행/불명확, connector 대체 미확인, 정리 잔여 영향 미확인. 독립 준비는 가능하나 전체 사전점검 성공은 아니다.
- `BLOCKED`: 필수 repo/auth/CI/Preview/DB/모델/도구 또는 확인된 실제 릴리스 보호 정책이 현재 무인 경로를 막는다. 필요한 설정을 우선순위별로 한 번에 제시한다.

`production_execution_verified: false`를 기본으로 둔다. 이 스킬은 Production을 변경하지 않으므로 실제 보호 branch merge·Production 배포·최종 제출 G6는 release_only_checks다. READY는 goal을 시작할 수 있는 증거이지 마지막 배포까지 권한 문제가 전혀 없다는 보장이 아니다. 해당 정책을 조회할 권한마저 없어 필수 경로를 판단할 수 없으면 PARTIAL이다. 실제 보호 정책의 차단을 발견하면 BLOCKED다.

직접 Production 시험까지 필요한 경우 별도 명시된 시험 범위와 기존 배포 보존 계획을 마련한 후에만 수행한다. 기본 live 스킬이 그 권한까지 조용히 넓히지 않는다.

## 7. 실패·정리·재실행

timeout이면 같은 run-id의 branch/PR/CI/deployment/DB 상태를 먼저 조회한다. 재시도로 새 리소스를 계속 만들지 않는다. 실패 유형별 조치 목록과 검사 증거를 남기고 비밀값은 제외한다. 정리는 resource ledger의 정확한 ID에 한정하고 실패했다고 삭제 범위를 넓히지 않는다. PR/CI 이력은 서비스에 남을 수 있으며 이를 완전 삭제했다고 주장하지 않는다.

기본/통합 branch에 기본 동작 검사를 자동 병합하지 않는다. 사용자가 재사용하도록 선택한 scaffold는 검사 artifact/임시 branch로 보존 가능하다. 그 보존 사유와 다음 정리 방법을 기록한다. 잔여 리소스가 열려 있거나 비용/보안 영향이 미확인이면 READY 불가다.

같은 환경은 검사 시각·repo SHA·project/환경·runtime·DB driver·모델·권한 fingerprint로 증거를 식별한다. 설정이 바뀌면 해당 검사와 의존 경로만 재실행한다. 목표 시작 시 release_only 조건을 다시 확인하고, 실제 릴리스에서 최종 검증한다.

## 조사·모델 선택·지도 추가 점검

- P00/P02: 실제 제공 모델 목록/선택 기능을 확인하고 가능한 범위에서 작업자·독립 검증자를 배정한다. 모델 이름/가격을 문서 가정만으로 확정하지 않는다. 특정 고가 모델 부재만으로 불가능이라 하지 말고 적합한 대체와 검증 강도를 기록한다.
- P00/P09/P10: 실행 시점 웹 조사·공식 문서/상품·점포 출처 열람과 브라우저 접근을 소량 확인한다. 검색 결과만 보이고 원문을 읽지 못하면 근거 확보가 미완료라고 표시한다. 필요한 조사 접근이 전혀 없으면 관련 준비를 PARTIAL/BLOCKED로 보고한다.
- 지도 provider를 선택한 경우에만 필요한 키/도메인·사용 조건·좌표/표기·네트워크를 검사한다. 새 유료 지도 계정을 기본 필수로 하지 않는다. 실제 점포 근거와 지도 기능 검증은 19번을 따른다.
- 모델/무료 잔량은 최소 기본 동작 검사에 충분한지와 후속 eval 계획을 감당할 수 있는지를 구분한다. preflight 성공은 무제한 API나 전체 품질 평가 예산을 보장하지 않는다.

기존 Git repo가 있으면 새 git init이나 remote 덮어쓰기를 하지 않는다. 사전점검이 성공한 후에도 goal의 PLAN-READY·조사·SEED-READY·제품 검증은 별도 수행한다.

## 외부 검토 반영: 무인 실행을 막는 실제 조건

### 실행 정책·CI·브라우저

P00는 설정 파일 문구뿐 아니라 현재 적용된 파일 쓰기/Git 보호 경로·네트워크·패키지 설치·인증 cache·브라우저 설치 권한을 확인한다. 관리형 조직 정책이 우선한다. `approval_policy=never`는 질문을 생략할 뿐 실패한 작업에 권한을 부여하지 않는다. 프로젝트 지침에서 sandbox 해제·전역 full access를 강제하지 않는다. 필요한 범위는 goal 전에 환경 소유자가 준비하고 실제 실패는 재시도 대신 접근 차단으로 분류한다. 현재 가용 서브 에이전트 슬롯/모델 선택도 실측한다. 참고: [공식 구성 참조](https://developers.openai.com/ko-KR/docs/config-file/config-reference), 로컬 `codex --help` 확인(2026-09-20).

P01은 실제 required check 이름과 초기 구축 workflow가 호환되는지 확인한다. 새 aggregate check 기본 이름은 `gate`; 기존 규칙 이름이 다르면 호환 mapping/검사 job을 설계한다. 기존 보호 규칙을 해제하지 않는다. workflow가 아직 없는 docs-only repo는 최초 도입의 허용된 경로도 검사한다. 경로가 없으면 알려진 환경 차단이다.

P05/P09는 Vercel 로그인 화면을 제품 성공으로 보지 않는다. 보호된 Preview에는 허용된 automation bypass secret을 테스트 실행기에서 해당 Vercel origin에만 헤더로 전달한다. 브라우저 후속 요청/쿠키 동작도 확인하고 외부 지도/상품 사이트에는 헤더를 보내지 않는다. secret을 URL·스크린샷·trace·로그·클라이언트 번들에 남기지 않는다. 제출 URL은 심사자에게 의도한 접근 방식으로 별도 검사한다. 기본 설정을 무조건 해제하는 처방은 사용하지 않는다. [Vercel automation bypass](https://vercel.com/docs/deployment-protection/methods-to-bypass-deployment-protection/protection-bypass-automation).

### DB·모델·비밀값 준비표

| 대상 | goal 전 준비 / 실제 사용 시 확인 |
|---|---|
| DB | 허용된 Neon/Postgres 프로젝트·격리 자원 생성 권한·약관/계정 준비. 제출/Preview/test는 branch 또는 동등한 schema/DB 격리로 분리; 반드시 branch 3개 구매/생성을 요구하지 않음 |
| `DATABASE_URL` | 환경별 서버 연결, Preview와 제출을 구분 |
| `DATABASE_URL_TEST` | 격리 CI/test DB를 쓰는 경우 secret. CI 서비스 Postgres이면 그 방식과 실제 Neon 경로 별도 검증 |
| `AI_GATEWAY_API_KEY` | 로컬/외부 CI 인증에 사용할 수 있는 방법. Vercel 배포는 지원 OIDC를 우선 검증. 모든 환경에 같은 장기 키 복사 필수 아님 |
| `GEMINI_API_KEY` / `GEMINI_MODEL_ID` / `LLM_PROVIDER` | 키는 사용자가 서버 비밀 저장소에 주입. 무료 프로젝트와 모델을 검증하고 기본값은 Gateway. SDK의 키 변수명은 어댑터에서 연결 |
| `VERCEL_AUTOMATION_BYPASS_SECRET` | 보호된 Preview 테스트를 선택한 경우에만 runner/CI의 비밀 저장소에 설정 |
| 모델 ID·대체 | 실제 무료/허용 모델 목록에서 한국어·도구/structured output을 확인하고 1차·가능한 대체 모델과 한도를 기록; 대체 결과는 별도 평가 |
| 설치 | CI에서 lockfile 설치 및 선택된 Playwright/browser dependency 설치·실행 확인. 예: `npx playwright install --with-deps`는 실제 runner/버전에 맞춰 실행 |

앱 모델의 카드/본인 확인 요구는 계정 화면에서 확인한다. 공식 가격 문서로 모든 계정의 카드 필수 여부를 단정하지 않는다. 필요한 사람 계정/키 설정은 goal 전에 끝내되 API 키 값을 채팅으로 요구하지 않는다. 이미 허용된 자격증명을 secret 저장소에 등록할 권한이 있으면 에이전트가 마스킹된 안전한 경로로 처리할 수 있다.

P01/P08은 무료 모델/잔량·rate limit과 평가 계획을 대조한다. 전체 live 비용은 대략 `사례 수 × 반복수 × (baseline+후보 실행) × 사례별 실제 모델 호출 수 + 재시도/최종 검증 여유`로 추정한다. 전체 420개를 매 후보마다 실행하는 방식으로 고정하지 말고 dev 선별·validation·최종 holdout에 맞춰 산출한다. 429는 제한된 backoff/재개로 다루고 일/월 한도 소진은 계속 재시도하지 않는다. paid 자동 충전·새 credit 구매는 하지 않는다. 부족하면 선택 실험부터 줄이되 필수 live 증거를 fixture로 바꾸지 않는다.

Vercel 플랜/repo 연결·비상업적 이용 조건·함수 시간 제한은 실제 행사 계정/프로젝트 기준으로 확인한다. Hobby가 모든 기업 해커톤/조직 repo에 맞는다고 가정하지 않는다. [Vercel Hobby](https://vercel.com/docs/plans/hobby). 승인된 기존 조직 플랜 등 가능한 경로를 검토하고 새 결제를 임의로 실행하지 않는다.

## 예비 모델 준비 판정

[25번](25-model-budget-and-fallback.md)에 따라 P01은 양쪽 무료 용량과 남은 평가·데모 예산을 기록하고 P08은 두 경로를 실제 호출한다. Gemini가 미설정이면 예비 경로는 `not_run`, 사전점검 전체는 `PARTIAL`로 남긴다. Gateway가 동작하면 독립 개발은 계속할 수 있지만, 예비 경로를 포함한 준비 완료로 보고하지 않는다. 양쪽 모두 사용할 수 없으면 필수 모델 작업은 `BLOCKED`다. 기존 단일 경로 점검 결과에는 이 추가 검사를 수행한다. 크레딧 조회 실패는 `unknown`으로 남기며 무료 용량으로 간주하지 않는다.

Gateway가 이미 소진됐으면 해당 실패와 잔량을 기록한다. Gemini 무료 용량·실제 응답이 통과하고 전환 오류 검사가 검증되면 P08은 Gemini를 선택한 상태로 통과할 수 있다. Gateway 복귀는 실제 연결·품질 검증 후 허용한다. 이 예외로 unavailable 상태의 Gateway를 PASS로 표시하지 않는다.

## P00: 요청한 설정과 적용된 권한

`approval_policy="never"`는 승인 요청 없이 허용 범위 안에서 실행하는 선택이다. `sandbox_mode="danger-full-access"`를 프로젝트 공통 필수값으로 고정하지 않는다. 프로젝트 config는 신뢰된 프로젝트에서 적용되며 조직 requirements가 허용 값을 제한할 수 있다. P00은 실제 파일/Git 쓰기·설치·네트워크·브라우저·에이전트 실행과 남은 차단을 검증한다. 현재 세션의 제한을 config 편집으로 우회하지 않는다. [공식 구성 우선순위](https://learn.chatgpt.com/docs/config-file/config-basic), [승인 정책과 샌드박스](https://learn.chatgpt.com/docs/agent-approvals-security) (2026-09-21 확인).

사람이 처리할 계정·약관·키·카드 요구는 README 순서로 준비한다. 무료 경로에 카드가 필요하다는 일반 가정을 두지 않고 실제 계정 조건을 기록한다. 최초 Git docs commit/push 성공은 PR·Actions·Vercel·DB·모델 전체 preflight 성공과 구분한다.

## 새 장비에서 Codex 설정을 준비할 때

2026-09-21 [공식 설정 참조](https://learn.chatgpt.com/docs/config-file/config-reference)·[설정 우선순위](https://learn.chatgpt.com/docs/config-file/config-basic)를 확인했다. 외부 피드백의 `[projects."경로"]` 아래 `approval_policy`·`sandbox_mode`를 넣는 예시는 공식 프로젝트별 키로 확인되지 않았다. 프로젝트 신뢰와 실행 정책의 위치를 구분한다.

사용자가 선택한 환경에서 전역 `~/.codex/config.toml`의 프로젝트 신뢰를 등록하는 예시:

```toml
[projects."/실제/clone/루트"]
trust_level = "trusted"
```

위 경로는 `git rev-parse --show-toplevel` 결과로 바꾼다. 해당 프로젝트 설정이 이미 있으면 중복 테이블을 만들지 않고 수정한다. 사용자가 full access 실행을 선택하고 조직 정책이 허용할 때, 신뢰된 프로젝트의 로컬 `.codex/config.toml`에 설정하는 예시는 다음과 같다. 현재 저장소에서는 이 파일이 gitignore 대상이므로 새 장비에 자동 복사되지 않는다.

```toml
approval_policy = "never"
sandbox_mode = "danger-full-access"
```

두 실행 키는 파일 최상위에 둔다. 전역 파일 최상위에 넣으면 다른 프로젝트에도 영향을 줄 수 있으므로 적용 범위를 먼저 구분한다. 이번 문서 작업에서 설정 파일을 만들거나 변경하지 않았다. 파일 변경이 이미 열린 세션에 소급 적용된다고 가정하지 않으며 새 실행 환경에서 실제 적용 모드와 P00 작업을 확인한다. 전체 config·키 값을 로그로 출력하지 않는다.

P00 보고에는 요청한 모드, 실제 적용된 제한, 파일/Git 쓰기·네트워크·설치·브라우저·에이전트 검사와 근거를 남긴다. exact 문자열이 없다는 이유만으로 BLOCKED로 만들지 않는다. 실제 필수 경로가 막히면 BLOCKED, 확인되지 않으면 PARTIAL이다. `never`와 full access가 있어도 외부 인증·조직 정책·사용량 한도는 별도로 검사한다.

## Preview의 자동 시험과 심사자 접근

P05/P09에서 `automation_access`와 `reviewer_access`를 별개로 기록한다. 자동화는 허용된 bypass secret을 해당 배포 origin의 테스트 요청에만 사용한다. 심사자에게는 프로젝트가 허용하는 [공유 링크](https://vercel.com/docs/deployment-protection/methods-to-bypass-deployment-protection/sharable-links), 팀 접근 또는 공개 데모 경로를 준비한다. 프로젝트 보호를 무조건 끄는 것은 필수 조건이 아니다.

일반 URL은 자동화 bypass가 성공했다는 이유만으로 공개되지 않는다. 별도의 로그인하지 않은 브라우저에서 심사자 접근 경로와 후속 페이지/API를 검증한다. bypass secret을 심사자에게 넘기거나 공개 README/URL에 넣지 않는다. 비밀값을 포함한 공유 링크도 공개 로그/증거에 그대로 남기지 않고 deployment ID·검사 시각·접근 방식·결과만 기록한다. 공유 링크/플랜의 실제 사용 가능 여부는 계정에서 확인한다. 심사자 경로 미확인은 PARTIAL, 확인된 접근 불가는 해당 경로 BLOCKED로 보고한다.

## Neon 계정 완료 이후 확인

[28번](28-neon-setup-guide.md)에 사용자 제공 프로젝트와 CLI/선택 skills·MCP/config 안내를 기록했다. 계정 생성은 사용자 완료 보고이며 P06/P07 성공 증거가 아니다. P00은 실제 관리 도구 인증·대상 프로젝트/branch를 확인하고 P06/P07은 격리 DB와 Preview 서버 왕복을 검증한다. `.neon`의 production 연결이 개발 DB 설정으로 오용되지 않도록 환경별 대상과 비밀변수 범위를 기록한다. 필요한 관리/API 접근과 SQL 접속을 각각 확인한다. Neon AI Gateway·Functions·config deploy는 기존 앱의 필수 준비에 포함하지 않는다.
