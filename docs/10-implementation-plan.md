# 구현 순서와 단계별 완료 기준

상태: 실행 계획. 이 문서는 구현 순서와 완료 증거를 정의할 뿐, 앱·게이트·Preview·데이터가 이미 존재하거나 통과했다는 뜻이 아니다. 상세 task DAG와 소유권은 [WORKPLAN.md](WORKPLAN.md), 게이트 권위는 [14번](14-agent-development-loop.md), Git/릴리스 권위는 [16번](16-git-and-release-workflow.md)이다.

## 실행 원칙

1. 같은 저장소·remote·브랜치·유효한 preflight 증거가 있으면 먼저 재사용한다. 기존 Git 상태를 버리고 새 저장소를 만드는 것을 시작 절차로 삼지 않는다.
2. preflight를 현재 revision/인증/환경에 맞춰 갱신한 뒤, 최소 앱 shell을 실제 Preview에 배포해 Git→CI→Vercel 경로와 런타임을 관측한다. 이 기본 동작 검사는 제품 G5/G6가 아니다.
3. shell 증거를 반영해 task/의존성/소유권/검증/결정 시점을 고정하고 `PLAN-READY`를 판정한다. 계획 문서가 있다는 이유만으로 판정하지 않는다.
4. goal 실행 당시 담당 agent가 시장·사용자 필요와 최근 관심 상품을 직접 조사하고, 그 결과로 카탈로그와 현실적인 자연어 시나리오·평가 데이터를 함께 설계한다. 각 기능 설계 전에도 필요한 고객/경영주 필요, UX·오류/복구, 기술 통합·테스트 공식 자료를 제한된 질문으로 확인한다. 출처 사실과 합성 발화를 분리한다.
5. 단일 DBA가 schema/migration을 확정한 뒤 재현 가능한 seed를 삽입한다. 약 200개 상품, 8~12개 검증된 실제 GS25 점포 좌표, 합성 actor, 보호된 grouped holdout이 `SEED-READY`의 한 묶음이다.
6. 기능은 영역 단위 G1 → 실제 DB G2 → 경계 G3 → 고객/경영주 수직 UX G4로 넓힌다. 예외는 마지막에 몰아 만들지 않고 각 단위부터 검증한다.
7. 자연어 품질은 기준선을 먼저 측정하고 제한된 후보 실험과 필수 결함 복구로 개선한다. 출시 최소 기준 충족과 선택 개선 목표 달성을 구분한다. 통과 중인 최선 버전을 보존하고 필수 오류를 최적화 중단으로 면제하지 않는다.
8. 정확한 릴리스 후보 head와 최신 `main` 기반 조합에 G5/필수 checks를 고정하고, 그 상태가 바뀌지 않았을 때만 `main`에 병합한다. 병합 뒤 실제 Production deployment에서 G6를 새로 실행한다.

## M0. 기존 상태 재확인과 최소 실제 Preview

### M0-A: repeat/reuse preflight

- [18번](18-environment-preflight.md)에 따라 repo/remote, 현재 branch와 사용자 변경, 인증, GitHub 권한·보호 규칙, Vercel project/Production branch, Preview/Production 환경 분리, Neon, Gateway, 브라우저 도구를 다시 관측한다.
- 유효한 기존 repo·remote·프로젝트·검사 결과를 재사용하고 증거 revision/만료 조건을 기록한다. 불일치만 재검사하며 비밀값은 저장하지 않는다.
- 설정 완료 가정이 틀리면 `external-blocked`로 정확히 기록하고, 차단되지 않은 연구·계약·fixture 작업은 계속한다.

### M0-B: 최소 실제 Preview shell

- 현재 저장소에 최소 Next.js shell, health/runtime 표기, fixture 고객/경영주 진입점, 기본 build/test를 만든다.
- 작업 branch push→CI→Vercel Preview를 실제로 통과시키고 deployment ID/source SHA, HTTP/browser 기본 동작 검사, 환경 분리 여부를 기록한다.
- DB/model은 가장 작은 read/call 기본 동작 검사만 수행한다. 연결 실패를 고정 성공 응답으로 숨기지 않는다.
- 완료 증거: 실제 Preview URL과 exact source SHA, CI 결과, 브라우저 관측, 연결별 `pass/blocked/not_run`.
- 이 단계는 제품 기능·live 자연어·G4~G6 통과가 아니다.

### M0-C: PLAN-READY와 GATE-BOOTSTRAP

- [WORKPLAN.md](WORKPLAN.md)의 DAG를 실제 저장소 구조·도구·Preview 결과에 맞게 확정한다. 각 task에 CORE/결정, Context Manifest hash, 소유 파일, 선행 task, 산출물, 독립 검증자, 적용 G0~G6, 실패/중단 조건을 둔다.
- 공통 schema/migration/lockfile/CI/seed/eval manifest에는 단일 작성자를 정한다. customer-qa와 merchant-qa는 서로 및 구현자와 분리하고, method-auditor는 depth 1로만 배정한다.
- gate manifest/runner, 결과 수집, 누락·실패·stale·0개·fixture-only live·자기 검증 차단을 구현하고 CI aggregate check에 연결한다.
- `PLAN-READY` 조건: 유효 preflight+실제 Preview, 결정/계약 시점, 전체 필수 CORE의 task/검증 연결, 순환 없는 DAG, 충돌 없는 소유권, 데이터/eval 보호 계획, G5→main→G6 경로, 실제 blocker와 우회 없는 대체 작업이 모두 기록됨.
- PLAN-READY는 G0을 대체하지 않는다. 각 task는 시작할 때 현재 Context Manifest와 적용 결정으로 G0을 별도 통과한다.

## M1. 조사에서 SEED-READY까지

### M1-A: 시장·사용자 필요·최근 트렌드 조사

- 공개 자료로 편의점 상품을 찾기 어려운 상황, 점포별 수요 표현, 경영주의 묶음 판단 부담, 최근 관심/신상품 표현을 조사한다. 실제 GS 정책이나 판매량으로 확인되지 않은 주장은 가설로 표시한다.
- `민음사 빵`은 24번에서 과거 보도 근거를 확인한 예시이며 goal 실행 시점 최신성·seed 채택은 미검증인 후보 하나다. 정확한 상품/협업/시기/GS25 관련성을 출처로 확인하기 전에는 실재·인기 SKU로 넣지 않는다. 근거가 없으면 `unverified_candidate`/미식별 평가 사례로 보존한다. 이 사례나 다른 소수 예시를 약 200개 데이터의 고정 축·복제 원본으로 삼지 않는다.
- 연구 산출물에는 URL, 발행/사건 시각, 확인 시각, 주장 단위, 신뢰 상태, 사용할 상품/사용자 필요/발화 family를 연결한다.

### M1-B: 카탈로그·점포·발화 데이터 설계

- 약 200개 다양한 SKU와 그중 20~30개 최근 관심 후보를 만든다. 실제 근거가 있는 필드와 현실적인 합성 상품/가격/재고/발주 조건을 구분한다.
- 한 지역의 GS25 8~12개 점포명·주소·WGS84 좌표를 공개 근거와 주소 정합성 검사로 각각 검증한다. 운영 중 여부를 확인하지 못했으면 별도 표시한다.
- 고객 약 20명·점포별 합성 경영주 1명(8~12명)과 거래 상태는 synthetic only로 만든다.
- 연구에서 관측한 표현은 `evidence_backed`와 출처를 붙이고, 테스트 다양성을 위해 만든 표현은 `synthetic_utterance`와 생성 규칙을 붙인다. 합성 표현을 실제 사용자 발화로 보고하지 않는다.
- 같은 의도·상품·표현의 패러프레이즈 family에 `group_id`를 부여한 뒤 dev/validation/holdout을 그룹 단위로 분할한다. 평가자만 최종 holdout 정답을 관리하며 실험자·프롬프트·별칭 사전에 노출하지 않는다.

### M1-C: 스키마 먼저, 재현 가능한 seed 다음

- DBA가 출처 이력, catalog/store/actor, session/role, request/consent, order/allocation/payment/reservation/event, policy, prompt/model/eval version을 수용하는 스키마와 마이그레이션을 먼저 구현한다.
- 데이터/eval 담당은 스키마 contract를 검토하되 마이그레이션 작성자는 한 명이다. 마이그레이션 dry-run/rollback과 실제 격리 PostgreSQL을 검증한다.
- 이후 버전 관리 원본에서 재현 가능한 seed importer와 domain factory를 구현한다. 동일 seed 재실행은 중복 actor/request/order를 만들지 않아야 한다.
- 핵심 성공, 모호/미식별, 공급 부족, 예산/권한 제한, 결제 실패, 재전송, 정확히 48시간 경계 preset을 만든다.

### SEED-READY 판정

아래를 모두 만족해야 최종 자연어 기준선·정식 독립 QA·G5가 전체 데이터를 사용한다. F00과 기능 개발은 ADR-001의 최소 seed 검증 후 시작할 수 있다.

- 약 200개 SKU의 다양성·중복·필수 필드·provenance/합성 구분 검사 통과.
- 최근 관심 주장과 `민음사 빵`을 포함한 미검증 후보의 상태가 근거에 맞게 분리됨.
- 8~12개 실제 GS25 점포 각각의 점포명·주소·좌표·출처·확인일 검증.
- 합성 actor/세션/시나리오, 스키마 마이그레이션, 결정적·반복 안전 seed의 실제 DB G2 통과.
- 고객/경영주 eval의 범주·분모·정답 스키마, family group 분할, split hash, holdout 접근자와 누수 검사 고정.
- catalog/seed/eval/scenario/policy 출처·변경 이력과 checksum이 기록되고 DB 직접 조회·기반 reader 및 보호된 평가 산출물 검사로 확인됨. F00·FS·U01·N01·Q01 완료나 앱 화면/API를 선행조건으로 요구하지 않음.

## M2. 영역 단위 기능: G1

- F: 세션·역할·시계·스키마 adapter·seed/reset·gate runner.
- S: 상품 후보 검색, 확인 질문, 후보 거절/정정, 미식별, structured output.
- C: 상품 확인 뒤 수량·점포·가격·자동 구매 동의와 요청 생성/조회/허용된 변경.
- M: 미확보/미식별 묶음, 자연어 수정, 이번만/지속 정책, 수동 승인.
- O: 수요 연결 발주, 예산/최소량/중복/동시 실행 보호.
- R: 공급 확보, FIFO 배정, 모의 자동 결제, 예약, 입고, 알림, 정확히 48시간 수령.
- U: 고객 모바일과 경영주 데스크톱의 빈/로딩/오류/회복 상태.

각 영역은 자체 단위 테스트 뒤 별도 검증자의 반례 검토를 받는다. 공통 정책을 영역별로 복제하지 않고 서버 domain/DB 제약을 권위로 둔다.

## M3. 실제 DB와 경계 통합: G2/G3

1. 각 서비스+route+권한을 실제 격리 PostgreSQL에 연결해 constraint, transaction, 복구, idempotency, 세션 격리를 검증한다.
2. 요청↔발주, 발주↔공급, 공급↔FIFO 배정, 배정↔모의 결제, 예약↔입고/알림↔수령을 한 경계씩 연결한다.
3. 성공뿐 아니라 timeout/결과 미확인, 재전송, stale 제안, 조건 변경, 동시 예산, 공급 부족, 결제 실패에서 수량·금액·상태가 보존되는지 본다.
4. policy/schema/seed/prompt/eval 변경은 Context Manifest와 출처·변경 이력을 갱신하고 영향받는 증거만 stale 처리한다.

## M4. 역할별 수직 UX와 live 기준선: G4

- 좁은 전체 흐름을 고객→경영주→고객으로 실제 브라우저에서 연결한다. 고객과 경영주 QA는 서로 다른 agent/profile이며 각 구현자와도 분리한다.
- customer-qa는 모바일 입력·질문·후보 확인·점포/지도·동의·상태·알림·기한·오류 회복을, merchant-qa는 묶음 수요·미식별·자연어 수정·승인/정책·입고/수령·예외 부담을 각각 검사한다.
- 같은 데모 session의 UI/DB/event를 대조하고 다른 세션·역할 접근을 거절한다. API로 사전 상태를 준비할 수 있으나 평가할 사용자 경로를 건너뛰지 않는다.
- fixture G4와 선택한 제공자의 Preview live 기준선을 구분해 기록한다. 실제 모델 실패를 fixture 성공으로 덮지 않는다.

## M5. 자연어 품질 최적화와 전체 회귀: G5 전

### 명시적 최적화 목적

현재 기준선을 먼저 측정하고 최소 기준 미달도 기록한다. 필수 결함 복구와 선택적 품질 최적화를 구분하며, 통과 버전을 확보한 뒤에는 그 기준을 보존한다. 같은 validation에서 고객 상품 식별/확인/미식별과 경영주 intent/scope/조건 해석의 사전 정의 지표를 개선한다. 전체 평균뿐 아니라 최악 범주, 과도한 확정/거절, latency/usage를 함께 비교한다. 정확한 문턱과 의미 있는 개선 폭은 기준선 결과를 보기 전 PLAN-READY ADR로 고정한다.

- 기준선 뒤 고객 역할 후보 최대 6개, 경영주 역할 후보 최대 6개, 전체 최대 12개다.
- 같은 역할에서 연속 3개 후보가 사전 개선 기준을 충족하지 못하면 그 역할의 추가 최적화를 중단한다.
- 후보는 격리해 dev로 선별하고 같은 validation/모델 설정/반복수로 독립 평가자가 비교한다. 최종 holdout은 후보 선정 후 한 번 사용하며 노출 시 교체 이력을 남긴다.
- 현재 출시 최소 기준을 통과한 최선 버전을 항상 보존한다. 새 후보가 회귀하거나 의미 있게 낫지 않으면 기각하고 출시 기준을 통과한 최선 버전으로 돌아간다.
- 허구 SKU, 무권한 도구, 동의 없는 요청/결제, 수량·금액·48시간 위반은 허용 0건이며 후보 한도·정체·일정으로 면제할 수 없다. 모든 버전이 최소 기준 미달이면 G5/goal 완료가 아니다.
- 최적화가 plateau/budget-stop이어도 출시 기준을 통과한 최선 버전이 최소 기준을 만족하면 알려진 한계와 후보 이력을 남기고 나머지 제품 릴리스를 계속한다.

전체 회귀에는 유효한 CORE/ADR 추적, G1~G4, 두 UX QA, 자연어 eval, 실제 DB 경합, build, 보안/권한, 운영 감사가 포함된다. 단일 method-auditor가 첫 G4 뒤와 G5 직전에 역할/맥락/누수/가짜 PASS를 depth 1에서 감사한다.

## M6. 검증 대상 커밋과 일치하는 `main` gate와 실제 G6

1. 통합 branch의 최신 릴리스 후보를 최신 `main` 기반과 결합한 exact release head를 만든다.
2. 그 SHA에 G5, 최종 정책 감사, required aggregate checks, 릴리스 Preview의 고객/경영주 UX와 live model/DB 증거를 연결한다.
3. 병합 직전에 PR head SHA, `main` base SHA, checks, 리뷰, deployment source가 기록값과 같은지 다시 조회한다. 하나라도 바뀌면 영향 검사를 다시 수행한다.
4. 검증된 PR만 `main`에 병합하고 실제 merge SHA/main HEAD를 기록한다. 다른 SHA의 성공을 가져와 main gate를 통과시키지 않는다.
5. 연결된 Vercel Production이 그 merge SHA를 배포했는지 확인한 뒤, 실제 제출 URL에서 G6를 새로 실행한다: live 모델, 실제 DB/schema/seed, reset, 고객/경영주 정상 흐름, 대표 예외, 48시간 경계, 접근성.
6. G6 실패는 main gate 과거 성공으로 덮지 않고 복구→새 검증 대상 커밋→Production→G6 순서로 반복한다.

## 병렬 작업 배정과 중단 없는 진행

- 실제 Preview 후 data-research/eval taxonomy와 DBA 스키마 skeleton, GATE-BOOTSTRAP을 소유권이 겹치지 않게 병렬화할 수 있다.
- 스키마 contract 전에는 원본 조사·발화 family 설계까지 가능하지만 DB seed 완료를 선언하지 않는다.
- SEED-MIN-READY와 P04 뒤 F00을 시작하고 S/C/M/O/R/U를 확정 계약 단위로 배정한다. 전체 데이터 구축은 병행하며 공통 DB/파일·merge는 직렬화한다. 정식 QA·자연어 기준선·G5는 SEED-READY 뒤 수행한다.
- 외부 연구/지도/model 차단은 정확히 표시하고 synthetic 기능 작업을 계속하되, 8~12개 verified 좌표나 live 필수 기준을 충족했다고 바꾸지 않는다.
- 실패는 [15번](15-failure-recovery.md)으로 복구한다. 성공한 무관 증거를 반복하지 않고 변경 출처·변경 이력이 닿는 부모 게이트만 재검증한다.

## 완료 선언

문서 작성, PLAN-READY, SEED-READY, Preview Ready, G5, `main` 병합, G6는 서로 다른 상태다. 현재 유효한 모든 CORE이 유효 결정→코드/데이터/config→단위/DB/경계/UX/eval→exact SHA/Production evidence로 이어지고 실제 G6까지 통과해야 제품 완료를 선언한다.

조사와 계획의 순서: PLAN-READY 전에는 각 영역의 문제·자료 접근·위험을 파악하는 초기 탐색과 연구 질문/출처 계획을 검토한다. M1에서는 그 계획으로 본격 조사·데이터 생성·독립 평가셋 구축을 마쳐 SEED-READY를 판정한다. 전 상품 수집을 PLAN-READY의 선행조건으로 만들거나 조사를 계획 이후에만 허용하는 순환은 없다. 각 기능 G0의 추가 조사는 해당 결정에 필요한 범위로 제한한다.

모델 호출은 [25번](25-model-budget-and-fallback.md)의 Gateway 기본·Gemini 직접 호출 예비 경로로 구현한다. 단계별 배정과 AC-29 증거는 [WORKPLAN](WORKPLAN.md)의 D-31 작업표를 따른다.

## 자료 수집과 기능 개발의 병행

[ADR-001](decisions/ADR-001-minimal-seed-development.md)에 따라 D02A 자료 계약과 D02B 전체 수집, D04A 최소 seed와 D04B 전체 import를 나눈다. D03은 자료 계약만 기다린다. 최소 seed의 실제 DB 검사와 독립 검토 후 F00을 시작한다. 실제 좌표와 무관한 G1~G3 및 합성 위치를 표시한 사전 브라우저 검사는 계속할 수 있다. 실제 점포·지도 검증은 blocked/not_run으로 남기고 정식 G4·G5/G6에서 충족한다.
