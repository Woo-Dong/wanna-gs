# goal 전 환경·외부 연동 사전점검

상태: 최초 구현 기준. 전용 스킬과 로컬 검사 스크립트를 제공한다. 실제 외부 기본 동작 검사는 사용자가 스킬을 실행할 때 수행한다. 앱 외부 연동은 아직 미검증이다. 문서 저장소의 Git 연결과 실제 검사 이력은 PROGRESS에서 확인한다. 목표는 한 번의 goal이 사소한 설정/정책 질문 때문에 멈추지 않도록 실제 가능한 경로와 부족한 준비를 미리 보여주는 것이다.

## 1. 먼저 준비할 것

| 항목 | 미리 구성할 내용 | 확인 기준 |
|---|---|---|
| 프로젝트 | 이 폴더를 GitHub repo의 clone/worktree로 열기, remote·Git 작성자 설정 | docs와 루트 AGENTS, 프로젝트 스킬이 같은 repo에 존재 |
| GitHub | 올바른 계정 로그인, 지정 repo push/PR/merge, Actions 실행과 workflow 수정 권한 | CLI 예시는 gh, 같은 능력의 connector도 가능 |
| GitHub 정책 | 실제 통합/제출 branch·required checks·ruleset·CODEOWNERS·환경 승인 | 인간 승인 필수면 별도 허용 경로 필요. 에이전트가 보호 규칙을 해제하지 않음 |
| Vercel | 대상 팀/프로젝트 로그인·GitHub repo 연결·Production branch 확인 | Preview/배포·환경변수 조회/설정에 필요한 허용 권한 |
| SQLite | 외부 계정 없이 로컬 seed builder와 sql.js/WASM 의존성 준비 | P06 실제 SQL·파일 export/import, P07 Preview 한 탭·역할 전환·IndexedDB 복원 |
| 앱 모델 | 사용자가 발급한 OpenAI API 키·사용 가능한 모델·API 결제/한도 확인 | 로컬 `.env.local`과 Vercel 서버 secret 설정, P08 실제 호출·구조화 응답 확인 |
| 런타임 | 지원 Node LTS·패키지 관리자·Git·Python 3, 테스트 브라우저 설치/실행 | 정확한 버전은 확인 후 lockfile로 고정 |
| Codex 도구 | goal 지원, 파일·shell·네트워크·브라우저·서브 에이전트 접근 | API 키나 새 계정 없이 현재 개발 환경에서 실제 작업 수행 |
| 비밀값 | 서버용 model 인증은 환경변수/플랫폼 비밀 저장소 | 채팅/README/commit/클라이언트 번들에 값 저장 금지 |

GitHub/Vercel 인증에는 현재 CLI 도움말이나 제공 connector의 인증 절차를 사용한다. GitHub에서는 auth·repo 조회, Vercel에서는 identity·프로젝트 연결을 확인한다. 입력 토큰을 문서로 제출할 필요는 없다. 로컬 `.vercel/project.json`은 연결 방법 중 하나이며 connector/명시적 대상 정보로 대체할 수 있다.

D-44에 따라 DB 계정·연결 URL은 필요 없다. OpenAI API 인증은 local/Preview/Production에서 실제 호출 경로별로 확인한다. 환경변수 이름만 예시 파일에 적고 값은 해당 환경에 저장한다. 앱 실행의 정확한 인증 방식은 실제 지원 경로로 확인한다. CI가 로컬 로그인 상태를 자동 상속한다고 가정하지 않는다.

제품 코드·package.json·workflow가 아직 없다는 것은 정상 docs-only 시작이다. 이를 설치 실패로 보고하지 않고 초기 구축 대상으로 표시한다.

## 2. 사용 방법

프로젝트를 연 뒤 다음 중 하나를 Codex에 요청한다. 스킬 선택 목록에 보이지 않으면 명시한 SKILL.md를 읽고 실행하도록 한다.

읽기 전용 점검:

```text
$wanna-gs-preflight 이 프로젝트를 inspect 모드로 점검하고 부족한 설정을 알려줘. GitHub/Vercel 인증 상태도 읽기 전용으로 확인해줘.
```

실제 연동 시험:

```text
$wanna-gs-preflight 이 프로젝트를 live 모드로 사전점검해줘. docs/18-environment-preflight.md 범위의 임시 GitHub 브랜치·PR·CI·Vercel Preview·SQLite 파일/브라우저 저장·실제 모델·브라우저·서브 에이전트 시험과 정리를 진행하고, goal 시작 준비 상태와 미검증 릴리스 조건을 보고해줘.
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

`--output /tmp/<새로운-보고서이름>.json`으로 새 파일을 만들 수 있다. 기존 파일은 덮어쓰지 않는다. `.env`를 읽거나 값을 출력하지 않는다. `--check-auth`는 gh/Vercel의 읽기 전용 네트워크 조회를 추가한다. 종료 코드 2는 관찰만 완료한 PARTIAL, 1은 확인된 로컬 BLOCKED, 3은 보고서 쓰기 실패다. CLI가 없으면 사용할 수 있는 connector를 스킬이 검증할 수 있다. 검사기는 Python의 메모리 SQLite 연결 가능 여부만 관찰할 수 있다. 프로젝트 DB를 열거나 바꾸지 않으며 sql.js/WASM·seed·IndexedDB를 검증하지 않는다. live 루프를 수행하지 않으므로 그 자체로 READY를 반환하지 않는다.

스킬 폴더와 참조 docs를 함께 관리한다. SKILL.md 하나만 다른 폴더에 복사하면 참조 경로가 깨질 수 있다. 글로벌 설치를 별도 선행조건으로 만들지 않는다.

## 3. live 시험 범위

기존 작업 트리를 건드리지 않고 run-id별 임시 worktree와 `preflight/<run-id>/base`, `preflight/<run-id>/probe` 같은 두 branch를 사용한다. PR은 임시 base ← 임시 probe다. 기본/통합/제출 branch로 merge하지 않는다. 실제 Production 배포·설정·데이터는 변경하지 않는다.

처음에 ledger에 repo·project·namespace·예정 작업을 기록하고 생성 후 PR/branch SHA/deployment/임시 SQLite 파일·브라우저 저장 namespace를 연결한다. 이미 있는 사용자 리소스를 임시 리소스로 취급하지 않는다. 외부 쓰기는 live 모드 실행 지시 범위이며 같은 임시 시험 단계마다 다시 승인받지 않는다. 실제 sandbox/조직 권한 요청이 필요한 경우에는 그 제한을 따른다.

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
| P06 sqlite-local | 임시 SQLite seed에 schema·insert/read·제약·rollback을 적용하고 실제 sql.js로 export/import | 재로딩 후 기대값·제약 및 rollback 후 미존재 확인. Python sqlite3 성공만으로 PASS 금지 |
| P07 sqlite-browser | Preview 한 탭에서 WASM/seed 로드→SQLite 쓰기→IndexedDB snapshot→새로고침→역할 전환→reset | 저장 후 같은 값 복원, 역할 전환 시 유지, reset 후 초기 상태. 파일 사본/버전과 UI 비교. 서버 DB 접속 검사 없음 |
| P08 model | 로컬 서버와 Preview 서버에서 OpenAI API로 작은 한국어 요청 | 실제 인증·설정 모델·구조화 출력·오류 계약 확인. 환경변수 존재만으로 PASS 금지. 제품 품질은 후속 G4/G5에서 검증 |
| P09 browser | 브라우저 입력→서버 LLM API→구조화 응답→로컬 서비스/SQLite→화면, 오류 입력 1건 | 브라우저 실행기 실제 실행, 응답 검증·로컬 저장/표시·오류 회복 대조. 키는 서버에만 존재 |
| P10 준비 상태 | 원격/배포/DB/모델/agent 증거 집계 및 두 관점 확인 | 검사 누락·상태 오표시·known blocker가 없는지 독립 검토 |
| P11 cleanup | 임시 PR/branch/worktree/Preview/SQLite 파일·브라우저 namespace 정리 | 생성 ledger와 일치하는 ID만 처리, 정리/보존/실패 내역 명시 |

실행 순서는 의존성을 따른다. P04 CI는 같은 sql.js 의존성으로 임시 SQLite 파일을 검사한다. P06은 실제 SQL·export/import, P07은 실제 배포 자산과 브라우저 저장 경로를 확인한다. DB 서비스 컨테이너·Neon 연결·다중 기기 경합 검사는 요구하지 않는다. 권한 실패 때문에 하나를 못 해도 독립 항목은 계속한다. 실제 앱 품질 eval·도메인 E2E는 goal의 G1~G6 작업이며 기본 동작 검사를 그 증거로 재사용하지 않는다.

## 5. 기본 동작 검사 구현 규칙

- 테스트 앱에는 상품/예약 기능 대신 작은 입력·저장·조회와 제한된 모델 응답만 둔다. 후속 구현 재사용은 검토 후 진행한다.
- 임시 파일과 브라우저 프로필/IndexedDB namespace는 run-id로 식별한다. 사용자 시연 snapshot이나 다른 origin의 저장소를 지우지 않는다. 정적 seed를 수정하는 거래 서버 API를 만들지 않는다.
- 복구 테스트는 실제 sql.js 트랜잭션을 실패/취소시켜 write가 남지 않는지 확인한다. export/import 뒤 외래 키 설정을 다시 적용·검증한다. P07에서 snapshot 저장 실패가 성공 UI로 표시되지 않고 직전 저장본으로 회복하는지도 확인한다. 자세한 계약은 [29번](29-browser-sqlite-demo.md)을 따른다.
- 모델 호출은 최소 성공·오류 흐름으로 제한하고 사용자가 설정한 API 한도/승인된 예산을 확인한다. 무제한 eval을 돌리지 않는다.
- 임시 모델 probe API는 보호된 Preview와 서버 측 호출 제한으로 보호한다. SQLite 조작은 브라우저에서 수행한다. 임의 SQL·URL·모델/토큰 수를 요청 입력으로 받아 실행하지 않는다. 공개 비용 소진 endpoint를 만들지 않는다.
- GitHub Actions는 검증된 신뢰 branch 코드에만 필요한 비밀을 제공한다. 외부 fork 코드를 높은 권한으로 실행하는 우회 경로를 만들지 않는다.
- 도구 응답·Git remote·오류 로그에 토큰이 섞일 수 있으므로 원본 전체를 보고서에 붙이지 않는다. 실행 명령에도 비밀값을 인자로 넣지 않는다.

## 6. 판정과 미검증 범위

[보고서 양식](templates/preflight-report.md)에 다음을 구분한다.

- `READY` / `ready_for_goal: true`: 목표 시작 필수 P00~P11에 실제 증거가 있고 알려진 필수 차단이 없다. 테스트 리소스를 의도적으로 보존했다면 소유·영향·정리 방법을 기록한다.
- `PARTIAL`: 일부 검사 미실행/불명확, connector 대체 미확인, 정리 잔여 영향 미확인. 독립 준비는 가능하나 전체 사전점검 성공은 아니다.
- `BLOCKED`: 필수 repo/auth/CI/Preview/SQLite 실행·저장/모델/도구 또는 확인된 실제 릴리스 보호 정책이 현재 무인 경로를 막는다. 필요한 설정을 우선순위별로 한 번에 제시한다.

`production_execution_verified: false`를 기본으로 둔다. 이 스킬은 Production을 변경하지 않으므로 실제 보호 branch merge·Production 배포·최종 제출 G6는 release_only_checks다. READY는 goal을 시작할 수 있는 증거이지 마지막 배포까지 권한 문제가 전혀 없다는 보장이 아니다. 해당 정책을 조회할 권한마저 없어 필수 경로를 판단할 수 없으면 PARTIAL이다. 실제 보호 정책의 차단을 발견하면 BLOCKED다.

직접 Production 시험까지 필요한 경우 별도 명시된 시험 범위와 기존 배포 보존 계획을 마련한 후에만 수행한다. 기본 live 스킬이 그 권한까지 조용히 넓히지 않는다.

## 7. 실패·정리·재실행

timeout이면 같은 run-id의 branch/PR/CI/deployment/SQLite 파일·snapshot 상태를 먼저 조회한다. 재시도로 새 리소스를 계속 만들지 않는다. 실패 유형별 조치 목록과 검사 증거를 남기고 비밀값은 제외한다. 정리는 resource ledger의 정확한 ID에 한정하고 실패했다고 삭제 범위를 넓히지 않는다. PR/CI 이력은 서비스에 남을 수 있으며 이를 완전 삭제했다고 주장하지 않는다.

기본/통합 branch에 기본 동작 검사를 자동 병합하지 않는다. 사용자가 재사용하도록 선택한 scaffold는 검사 artifact/임시 branch로 보존 가능하다. 그 보존 사유와 다음 정리 방법을 기록한다. 잔여 리소스가 열려 있거나 비용/보안 영향이 미확인이면 READY 불가다.

같은 환경은 검사 시각·repo SHA·project/환경·runtime·sql.js/WASM·schema/seed·브라우저·모델·권한 fingerprint로 증거를 식별한다. 설정이 바뀌면 해당 검사와 의존 경로만 재실행한다. 목표 시작 시 release_only 조건을 다시 확인하고, 실제 릴리스에서 최종 검증한다.

## 조사·모델 선택·지도 추가 점검

- P00/P02: 실제 제공 모델 목록/선택 기능을 확인하고 가능한 범위에서 작업자·독립 검증자를 배정한다. 모델 이름/가격을 문서 가정만으로 확정하지 않는다. 특정 고가 모델 부재만으로 불가능이라 하지 말고 적합한 대체와 검증 강도를 기록한다.
- P00/P09/P10: 실행 시점 웹 조사·공식 문서/상품·점포 출처 열람과 브라우저 접근을 소량 확인한다. 검색 결과만 보이고 원문을 읽지 못하면 근거 확보가 미완료라고 표시한다. 필요한 조사 접근이 전혀 없으면 관련 준비를 PARTIAL/BLOCKED로 보고한다.
- 지도 provider를 선택한 경우에만 필요한 키/도메인·사용 조건·좌표/표기·네트워크를 검사한다. 새 유료 지도 계정을 기본 필수로 하지 않는다. 실제 점포 근거와 지도 기능 검증은 19번을 따른다.
- 모델 접근/API 한도는 최소 기본 동작 검사에 충분한지와 후속 eval 계획을 감당할 수 있는지를 구분한다. preflight 성공은 무제한 API나 전체 품질 평가 예산을 보장하지 않는다.

기존 Git repo가 있으면 새 git init이나 remote 덮어쓰기를 하지 않는다. 사전점검이 성공한 후에도 goal의 PLAN-READY·조사·SEED-READY·제품 검증은 별도 수행한다.

## 외부 검토 반영: 무인 실행을 막는 실제 조건

### 실행 정책·CI·브라우저

P00는 설정 파일 문구뿐 아니라 현재 적용된 파일 쓰기/Git 보호 경로·네트워크·패키지 설치·인증 cache·브라우저 설치 권한을 확인한다. 관리형 조직 정책이 우선한다. `approval_policy=never`는 질문을 생략할 뿐 실패한 작업에 권한을 부여하지 않는다. 프로젝트 지침에서 sandbox 해제·전역 full access를 강제하지 않는다. 필요한 범위는 goal 전에 환경 소유자가 준비하고 실제 실패는 재시도 대신 접근 차단으로 분류한다. 현재 가용 서브 에이전트 슬롯/모델 선택도 실측한다. 참고: [공식 구성 참조](https://developers.openai.com/ko-KR/docs/config-file/config-reference), 로컬 `codex --help` 확인(2026-09-20).

P01은 실제 required check 이름과 초기 구축 workflow가 호환되는지 확인한다. 새 aggregate check 기본 이름은 `gate`; 기존 규칙 이름이 다르면 호환 mapping/검사 job을 설계한다. 기존 보호 규칙을 해제하지 않는다. workflow가 아직 없는 docs-only repo는 최초 도입의 허용된 경로도 검사한다. 경로가 없으면 알려진 환경 차단이다.

P05/P09는 Vercel 로그인 화면을 제품 성공으로 보지 않는다. 보호된 Preview에는 허용된 automation bypass secret을 테스트 실행기에서 해당 Vercel origin에만 헤더로 전달한다. 브라우저 후속 요청/쿠키 동작도 확인하고 외부 지도/상품 사이트에는 헤더를 보내지 않는다. secret을 URL·스크린샷·trace·로그·클라이언트 번들에 남기지 않는다. 제출 URL은 심사자에게 의도한 접근 방식으로 별도 검사한다. 기본 설정을 무조건 해제하는 처방은 사용하지 않는다. [Vercel automation bypass](https://vercel.com/docs/deployment-protection/methods-to-bypass-deployment-protection/protection-bypass-automation).

### SQLite·모델·비밀값 준비표

| 대상 | goal 전 준비 / 실제 사용 시 확인 |
|---|---|
| SQLite 자산 | 로컬 seed builder·sql.js/WASM·manifest를 구현 단계에서 준비. 파일/SQLite snapshot은 테스트별로 분리. DB 계정·연결 secret 없음 |
| 브라우저 저장 | 시연 PC의 일반 브라우저에서 IndexedDB 사용 가능 여부와 같은 origin의 저장·복원 확인. Preview와 Production 상태는 자동 공유되지 않음 |
| `OPENAI_API_KEY` | 사용자가 로컬 `.env.local`과 Vercel 대상 환경의 서버 secret에 주입. 값·접두사·길이만으로 인증 성공 판정 금지 |
| `OPENAI_MODEL` / `LLM_MODE` | 모델은 사용자가 변경 가능. 예시 모델의 계정 접근 가능 여부를 실제 확인. `live`와 `fixture`를 구분하며 fixture는 P08 성공을 대신하지 않음 |
| `VERCEL_AUTOMATION_BYPASS_SECRET` | 보호된 Preview 테스트를 선택한 경우에만 runner/CI의 비밀 저장소에 설정 |
| 모델 ID·출력 | 선택한 OpenAI 모델의 한국어·structured output·접근 권한과 한도를 확인. 모델 변경 후 해당 평가 증거 갱신 |
| 설치 | CI에서 lockfile 설치 및 선택된 Playwright/browser dependency 설치·실행 확인. 예: `npx playwright install --with-deps`는 실제 runner/버전에 맞춰 실행 |

OpenAI API의 결제·한도·모델 접근은 API 프로젝트 계정에서 확인한다. ChatGPT Workspace/Codex 구독을 앱 API 크레딧으로 간주하지 않는다. 필요한 계정/키 설정은 goal 전에 끝내되 API 키 값을 채팅으로 요구하지 않는다. 이미 허용된 자격증명을 secret 저장소에 등록할 권한이 있으면 에이전트가 마스킹된 안전한 경로로 처리할 수 있다.

P01/P08은 OpenAI API 프로젝트의 허용 비용·rate limit과 평가 계획을 대조한다. 전체 live 비용은 대략 `사례 수 × 반복수 × (baseline+후보 실행) × 사례별 실제 모델 호출 수 + 재시도/최종 검증 여유`로 추정한다. 전체 420개를 매 후보마다 실행하는 방식으로 고정하지 말고 dev 선별·validation·최종 holdout에 맞춰 산출한다. 429는 제한된 backoff/재개로 다루고 일/월 한도 소진은 계속 재시도하지 않는다. 새 결제·자동 충전·한도 상향은 별도 승인 없이 수행하지 않는다. 부족하면 선택 실험부터 줄이되 필수 live 증거를 fixture로 바꾸지 않는다.

Vercel 플랜/repo 연결·비상업적 이용 조건·함수 시간 제한은 실제 행사 계정/프로젝트 기준으로 확인한다. Hobby가 모든 기업 해커톤/조직 repo에 맞는다고 가정하지 않는다. [Vercel Hobby](https://vercel.com/docs/plans/hobby). 승인된 기존 조직 플랜 등 가능한 경로를 검토하고 새 결제를 임의로 실행하지 않는다.

## OpenAI API 설정과 준비 판정

[25번](25-openai-api-and-budget.md)의 OpenAI API 단일 경로를 따른다. Gateway/Gemini 계정·예비 키·자동 전환 시험은 요구하지 않는다. 현재 사용자는 키를 아직 주입하지 않았으므로 실제 호출은 미검증이다.

1. 저장소 루트의 `.env.example`을 참고해 `.env.local`에 `OPENAI_API_KEY`를 직접 입력한다. 키는 공개 문서·채팅·스크린샷·로그·커밋에 남기지 않는다. `.env.local`은 Git 추적 대상에서 제외한다.
2. `OPENAI_MODEL`을 사용할 모델 ID로 설정한다. 예시 `gpt-5-mini`는 계정 사용 가능성을 검증한 결과가 아니며 사용자가 변경할 수 있다. 실제 모델 시험은 `LLM_MODE=live`로 수행한다.
3. Vercel 대상 환경에 같은 이름의 서버 환경변수를 설정하고 반영된 배포를 확인한다. `NEXT_PUBLIC_` 접두사를 사용하지 않는다. CI가 키 없이 fixture 검사만 수행하는 경우 live 검사는 인증된 별도 경로에서 실행한다.
4. 제공된 `scripts/check_openai_env.py`의 기본 실행은 `.env.local`·프로세스 환경의 존재·형식을 비밀값 없이 확인한다. `--live`는 소량 실제 API 호출이며 P08의 로컬 증거로 연결한다. Preview 호출과 구조화 출력 검사는 별도로 필요하다.

키 미설정이면 P08은 `not_run`, 전체 준비는 `PARTIAL`이다. SQLite·UI·fixture 작업은 계속할 수 있다. 실제 인증 거절·모델 접근 불가·한도 소진이 확인되면 live 작업의 외부 차단으로 기록한다. 값 존재나 키 접두사는 인증 성공 증거가 아니며 비용 조회가 불가능하면 `unknown`으로 남긴다. 모델 API 비용을 지출할 수 있는 계정 상태와 승인된 한도를 확인하지 않고 무제한 평가를 실행하지 않는다.

## P00: 요청한 설정과 적용된 권한

`approval_policy="never"`는 승인 요청 없이 허용 범위 안에서 실행하는 선택이다. `sandbox_mode="danger-full-access"`를 프로젝트 공통 필수값으로 고정하지 않는다. 프로젝트 config는 신뢰된 프로젝트에서 적용되며 조직 requirements가 허용 값을 제한할 수 있다. P00은 실제 파일/Git 쓰기·설치·네트워크·브라우저·에이전트 실행과 남은 차단을 검증한다. 현재 세션의 제한을 config 편집으로 우회하지 않는다. [공식 구성 우선순위](https://learn.chatgpt.com/docs/config-file/config-basic), [승인 정책과 샌드박스](https://learn.chatgpt.com/docs/agent-approvals-security) (2026-09-21 확인).

사람이 처리할 계정·약관·키·카드 요구는 README 순서로 준비한다. API 결제·한도는 실제 계정 조건을 기록하며 미확인을 사용 가능으로 표시하지 않는다. 최초 Git docs commit/push 성공은 PR·Actions·Vercel·DB·모델 전체 preflight 성공과 구분한다.

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

## SQLite 전환 이후 판정

D-44과 [29번](29-browser-sqlite-demo.md)이 현재 저장 방식이다. [28번](28-neon-setup-guide.md)은 이전 설정 기록이며 Neon 계정·CLI·MCP·DB URL 부재는 차단 사유가 아니다. sql.js/WASM·SQLite 자산·IndexedDB 저장 경로는 실제 검사해야 한다. 역할 전환은 같은 탭에서 수행하고 별도 심사자 접근 확인용 브라우저는 자기 초기 상태를 사용한다. 로컬 역할 제한을 서버 인증으로, 한 탭 성공을 여러 기기 상태 공유로 보고하지 않는다.

## Vercel CLI와 계정 연결 순서

프로젝트 루트에서 설치·인증·연결을 차례로 진행한다. 이미 설치/로그인/연결됐다면 해당 상태를 먼저 확인하고 재사용한다.

```bash
npm install -g vercel@latest
vercel --version
vercel login
vercel whoami
vercel teams ls
vercel project ls
```

`vercel login`이 안내하는 브라우저에서 사용자가 계정 로그인·기기 인증을 완료한다. 계정 비밀번호나 인증 토큰을 채팅에 전달하지 않는다. 여러 팀이 있으면 이 프로젝트를 둘 팀을 확인하고 기존 wanna-gs 프로젝트가 있는지 먼저 조회한다.

```bash
vercel link --project wanna-gs
vercel project inspect
vercel git connect https://github.com/Woo-Dong/wanna-gs.git
vercel env ls
```

프로젝트/팀 이름은 실제 조회 결과에 맞춘다. 여러 공간이 있으면 명령에 `--scope <선택한-scope>`를 지정해 같은 공간을 사용한다. 로컬 `.vercel/` 연결과 Vercel↔GitHub 저장소 연결은 별개다. `Login Connection` 누락 오류가 나오면 사용자가 [계정 Authentication](https://vercel.com/account/authentication)에서 저장소에 접근 가능한 GitHub 계정을 연결한 뒤 `vercel git connect`를 다시 실행한다. 이후 GitHub 앱 설치·저장소 접근 승인이 요구되면 해당 저장소 권한을 부여한다. `.vercel/`은 Git에서 제외하며 다른 clone에서는 다시 link한다. [공식 계정 연결 안내](https://vercel.com/docs/accounts#login-methods-and-connections).

환경변수는 25번대로 Preview/Production에 설정한다. `OPENAI_MODEL`·`LLM_MODE`는 일반 설정으로, `OPENAI_API_KEY`는 서버 비밀값으로 구분한다. 비어 있는 키를 원격에 등록하지 않는다. 기존 `.env.local`을 덮어쓸 수 있는 env pull은 준비 과정에서 무조건 실행하지 않는다. CLI 59.23.2에서는 `vercel link`도 OIDC 토큰을 내려받아 `.env.local`을 갱신했다. 연결 전후 기존 설정의 보존과 Git 제외 여부를 값 출력 없이 확인한다. CLI가 `.gitignore` 끝에 `.env*`를 추가하면 `.env.example` 허용 규칙을 덮지 않도록 정리한다. 문서만 있는 상태의 CLI 인증·프로젝트 생성은 실제 앱 배포 성공이 아니다. Next.js 코드·빌드 설정은 초기 구축 시 맞추고 P05/P08/P09에서 Preview·모델·브라우저를 별도로 검증한다.

2026-09-21 공식 근거: [CLI 설치](https://vercel.com/docs/cli), [로그인](https://vercel.com/docs/cli/login), [로컬 연결](https://vercel.com/docs/cli/link), [Git 연결](https://vercel.com/docs/cli/git). 실제 설치 버전과 계정 결과는 PROGRESS에 기록한다.

현재 PC에서는 Node 22 LTS가 설치돼 있으므로 CLI를 해당 런타임으로 실행할 수 있다. 예: `PATH="/opt/homebrew/opt/node@22/bin:$PATH" vercel whoami`. 이는 이 PC의 관측 예시이며 다른 장비의 고정 경로 요건이 아니다. 목표 구현 시 로컬/CI/Vercel의 지원 Node LTS를 맞추고 lockfile과 실행 버전을 기록한다.
