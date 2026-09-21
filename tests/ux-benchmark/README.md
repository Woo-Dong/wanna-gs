# ADR003 편의성 측정 장치 — 준비 단계

소유 파일은 이 디렉터리뿐이다. 제품 UI/DB/schema/package 수정 없음. 보호 holdout 접근 없음. `run.mts` 기본값은 fixture다. `--live --budget-config /명시적/승인.json`에서만 실제 응답 경로를 사용하며, 조정자가 허용한 run ID·호출수·남은 필수 예비량이 없으면 실행을 거절한다. 실제 모델 실행은 아직 하지 않았다. 현재 수치는 사람 대상 사용성 연구도 출시 live 편의성 PASS도 아니다.

## 고정 workload

각 3회, 총24회, 반복마다 격리 browser context/IndexedDB. 고객390×844, 경영주 및 cross-role1440×900. 좁은360/768·접근성은 독립 역할 UX QA 범위이며 이 측정으로 대체하지 않는다.

1. 공개 상품 `쫀득버터떡빵` 명확 요청.
2. 공개 상품 `라라스윗 망고 쫀득바` 명확 요청.
3. 공개 상품 `혜자로운 단팥크림빵` 명확 요청.
4. `그 쫀득한 빵 찾아요` → 실제 응답 표시 후 정확 상품명 확인 답변.
5. 가격 2000→2100원 변경으로 review_required가 된 기존 요청에 새 동의.
6. 동일 점포10SKU/각2개 수요를 한 화면에서 검토하고 한 번에 승인.
7. 승인된 정책/수요0에서 고객 UI 요청 → 자동발주 → 경영주 주문 요약. 고객 activation·역할전환·경영주 건별승인0을 분리. 시간 측정 종료 뒤 변화 없는 검토 재실행으로 중복 order/notification0 확인.
8. 10SKU 중 1개 capacity0, 다른1개 MOQ3/수요2. 2개 보류를 보존하고 나머지8SKU 묶음 승인.

7번 경계는 root가 채택한 구체화다. 이미 초기화에서 자동발주가 끝난 상태를 준비해 0초 성과로 보고하지 않는다. 모든 금액/수요/공급은 명시적 합성 시나리오다. seed 준비에서만 DomainEngine/SQL을 사용하고 측정 경로의 변경은 실제 UI activation으로 수행한다. prepare 진입마다 실제 실행하는 로컬 engine/contract의 SHA256와 --app-root의 두 소스가 일치해야 하며, 다르면 브라우저/모델 실행 전에 거절한다. seedEngineBinding을 결과에 기록한다. 검증 시 SQLite를 읽기 전용으로 열어 FK/integrity·동의·수량·발주를 대조한다.

## 계수와 시각

- 시작: 자연어 입력 준비 완료. 재동의는 고객 기본 화면, 경영주는 10SKU 검토 화면 준비 완료. 입력이 없는 업무는 첫 명시 activation 직전. 타이핑과 자동화 도구 실행시간도 전체 경과시간에 포함한다.
- 끝: 내구 저장 완료 후 표시하는 고객 저장 알림/경영주 실행 결과 요약. 그 직후 IndexedDB 실제 SQLite를 열어 결과를 확인한다. post-timing DB 검사/스크린샷/자동정책 중복 검사 시간은 완료시간에 합산하지 않는다.
- 의사결정 activation: 실제 버튼·상품·점포·동의 조작별1. 문자 키별 카운트0, 자연어 제출1. 현재 workload의 기본 수량을 변경하지 않으며 수량변경 workload가 추가되면 입력확정을1로 계수해야 한다.
- screenTransitions: 상품→조건→내요청과 탭/역할 전환 등 의미 화면 이동. 자동 focus와 같은 화면 데이터 갱신은0. event log에 정의된 경계를 기록한다.
- 스크롤 이벤트는 별도 계수한다. Playwright가 클릭하려고 자동 스크롤한 이벤트도 포함하므로 사람의 스크롤 의사결정 수로 해석하지 않는다.
- modelNetworkMs: Playwright request→requestfinished/requestfailed 구간의 합집합. 중첩을 이중 합산하지 않는다. budgetInstrumentationMs는 예약/정산 bridge 시간을 별도로 기록한다. nonModelMs=전체−모델/네트워크−budgetInstrumentationMs; 이 잔여값에는 자동화·타이핑·앱 처리·도구 대기가 포함되며 사람 생각시간으로 표시하지 않는다.
- clock `2026-09-21T03:00:00Z` 고정. 페이지 Date.now와 표식 query를 붙인 Worker JS 응답의 Date.now를 계측 context에서만 고정한다. timer/performance clock은 실제 경과시간이다. 각 run 최초 Worker snapshot.clock.now를 정확히 대조하고 다르면 실패한다. 제품 파일에는 시계 코드를 쓰지 않는다.
- 실패 실행도 결과에 남기며 workload별 expected3/executed/failed/missing를 표시한다. 편의성 성공은 correctness 검증 PASS만. 조작/이동은 실행 전체의 최댓값, 시간은 성공 run 중앙값이며 고정 8종 업무와 반복번호1·2·3의 유일성을 검사하고 누락·중복·범위 밖 반복을 숨기지 않는다. 3회 모두 성공하지 않으면 complete=false. 느린 run을 삭제/자동재시도하지 않는다.

## 실행

Node22, 기존 설치 Playwright·Chrome를 사용한다. 서버3217의 실제 앱 빌드가 먼저 준비되어야 한다. 프록시가 모든 assistant API를 fixture로 가로채며 다른 origin 요청은 차단한다. fixture는 live 응답 품질을 검증하지 않는다.

```sh
node --test tests/ux-benchmark/metrics.test.mjs
PLAYWRIGHT_MODULE=/absolute/path/playwright/index.mjs CHROMIUM_EXECUTABLE='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome' node --import tsx tests/ux-benchmark/run.mts --app-root /absolute/path/2026-ralphton --output /absolute/path/new-output-directory
```

출력 디렉터리가 비어 있지 않으면 덮어쓰지 않는다. result.json에 seed/workload/source/build fingerprint·clock·모드·분모·개별 event/기다림·실패를 보존하고 실제 완료 화면 PNG를 남긴다. 비교 함수 `compare`는 workload/seed/clock/mode 불일치를 거절하고, 비어 있지 않은 동일한 고정8종 집합을 요구하고 raw runs에서 요약을 다시 계산한다. 두쪽 모든 반복 성공·activation/화면이동 증가0·nonModel 중앙값10% 이하 악화를 요구한다. 결과를 본 뒤 절대 기준/동의정보를 완화하지 않는다.

## 현재 한계

실제 모델 baseline/best는 not_run. live 모드는 구현되어 있으나 독립 검토 및 조정자의 명시적 호출 허용 config가 필요하다. 정적 source hash와 BUILD_ID 기록은 비교 자료이며 배포 source attestation 자체가 아니다. 최종 실행 조정자가 정확한 빌드/source 연결을 검증해야 한다. 모델 대기와 오류를 실제로 검증할 live 경로가 필요하며 fixture가 이를 대체하지 않는다.

## live 예약·중단 계약

`--live --budget-config /absolute/root-approved-config.json`를 추가한다. 승인 config 필수 필드: approved=true, 고유 run_id, stage=baseline|best, prior_call_reserve=50, authorized_calls(현재 workload 최소18), mandatory_reserve(후속 필수 단계별 호출수), mandatory_cost_reserve_usd, origin, model, prompt_version, catalog_hash. 이 저장소는 실행용 승인 파일을 자동 작성하지 않는다. 승인 호출수는 이 UX 실행의 상한이며 계정/전체goal 상한을 대체하지 않는다.

`budget_bridge.py`는 app-root의 기존 `scripts/run_nl_eval.py` Budget을 직접 사용한다. 장부는 해당 root의 `artifacts/private/run-20260921/nl-budget.json` 하나로 고정하며 기존 장부가 없으면 거절한다. prior reserve50·전체2400·$15 soft stop과 남은 UX허용 호출수/후속 필수 예비량을 함께 보존한다. ledger 수정은 실제 승인된 실행 시에만 한다. 자체 테스트는 임시 디렉터리의 가짜 장부를 사용한다.

각 실제 HTTP 전송 전에 reserve를 내구 기록한다. route.fetch의 maxRetries=0/maxRedirects=0/timeout45000을 고정한다. 원래 서버의 응답 객체를 UI에 그대로 넘기며 상품 후보/정답을 주입하지 않는다. 실제 모델/프롬프트/catalog와 승인 config가 다르거나 오류·usage/cost 불명·전송 불명이면 null을 보존하고 실행 전체의 다음 호출을 중단한다. 실패를 fixture로 대체하지 않는다. ledger finish 자체가 불확실해도 pending을 남기며 재전송하지 않는다.

장부에 실행 ID claim을 한 번만 남긴다. 같은 run ID는 출력 경로를 바꿔도 다시 시작할 수 없다. pending attempt가 있으면 reserve 거절, 중단된 run을 자동 resume하지 않는다. 복구는 조정자가 기존 장부·증거를 검토한 별도 승인으로만 한다. 완료/실패/누락 분모와 outboundAttempts/known·unknown provider calls를 함께 남긴다.

HTTP 실제 네트워크 구간은 예약 이후 route.fetch 시작부터 응답 JSON 수신까지이며, 예산 bridge 시간은 reserve/finish 호출 각각의 직전·직후만 합산한다. UI 응답 전달 대기는 deliveryMs로 기록하고 nonModel 시간에 남긴다. baseline/best는 같은 workload·seed·clock·측정 도구 hash를 써야 한다. fixture와 live 사이를 성능 비교하지 않는다. 측정 도구를 바꾸면 예전 fixture 실행과 새 live 실행은 다른 workload hash를 가진다.

예산/전송 자체 검증:

```sh
UX_BUDGET_TEST_ROOT=/absolute/root python3 -m unittest discover -s tests/ux-benchmark -p 'test_*.py' -v
UX_BUDGET_TEST_ROOT=/absolute/root node --import tsx --test tests/ux-benchmark/live.test.mts tests/ux-benchmark/metrics.test.mjs tests/ux-benchmark/seed.test.mts
```
