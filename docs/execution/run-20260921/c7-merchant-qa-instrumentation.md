# C7 경영주 QA 준비 장치 독립 delta 검토

초기 판정: **FAIL — MIP01 모의 결제 실패 상태에 대한 잘못된 SQL 기대값 1건**. 실제 경영주 QA는 **NOT_RUN**. C7 validation01 83/84·incomplete1 FAIL과 D47 후보 종료를 유지하며, 이 준비 검토는 paid 평가·UX·G5/G6의 재개 근거가 아니다.

검토자 preflight_builder. 준비 장치의 research 변경분을 검토했다. 과거 본인이 작성/관여한 generic budget bridge 전체를 이번 독립 검증으로 다시 포장하지 않는다. 검토 범위는 C5→C7의 합성 cap seed·현재안/미래복사/undo 검증·실제 SQL 테이블·11분모·출처/실행승인 결속·외부요청 guard 연결·뷰포트/font/keyboard 추가다. 소스 수정0, 실제 브라우저/모델/HTTP/공유 장부 읽기·쓰기0, 보호 평가 원문 접근0. 임시 config와 public seed의 메모리 SQLite만 사용했다.

## 동결 대상과 실행 경계

`artifacts/private/run-20260921/c7-merchant-qa-preparation/execution-hashes.json` SHA256 `7914cca470c37a22bee85518d598dd16c897408adc90eb0d97c617bd8a610562`, 목록16파일의 현재 bytes 모두 직접 일치 확인. 주요 caller `b2328f6cdaad3e5cf29f6f5136f371c5135c45518a6e00c5257406d342d93382`, binding `825a8adc59ea6c929a6af2d6d37c39a40107c656a551aaed271418af642d7f7b`.

초안 source `88ae1a431f8691790069487dc70f2519698bd122`, runtime `4de25bb543fb1167df644a1da2859184462fc0ea371a89e6f933079b13cab64e`, source32/runtime47. binding 정상 재실행은 현재 파일 및 exact git source 전체 대조를 수행한다. approved=false이며 실제 두 CLI 가드에서 승인 전 실행 차단, output 미생성을 확인했다. 승인된 실제 config로 바꾸지 않았다. `--execute` 또는 승인 여부만으로 NL 선행 실패가 해제된다고 해석하지 않는다.

## MIP01 — 실패 예약은 없어진 예약이 아님

`merchant-browser.mjs`의 “모의 결제 실패 성공오표시0·고객 명시 재시도·역할복귀” journey에서 `db('payment-failed')` 다음 `assert.equal(d.rows.reservations.length,0)`가 실행된다.

공개 seed와 실제 DomainEngine/실제 loadDemoScenario를 연결한 메모리 실행에서:

1. `loadDemoScenario(...,'paymentFailure',true)`는 정상 성공했다.
2. `mock_payments`에는 failed1, succeeded0이다.
3. `reservations`에는 **1개**, status=`payment_failed`가 존재한다. 성공한 예약/픽업 상태라는 뜻이 아니다.
4. 실제 caller의 해당 assertion 블록을 VM으로 추출해 이 SQL rows에 적용하면 **1 !== 0**으로 실패한다.
5. 인접 정상 동작으로 실제 고객 `payment.retry` 명령을 호출하면 같은 예약은 confirmed로 전이하고 결제 시도는 총2개, pickup_deadline_at은 null이다.

따라서 예약 개수0은 성공 오표시 방지의 올바른 기대값이 아니다. 필요한 교정은 실패 결제와 실패 예약 상태·성공 예약/픽업 없음·명시 재시도 이후 정상 전이를 확인하는 것이다. 도메인/제품 정책 변경은 필요하지 않다. 현재 검토자는 caller를 수정하지 않았다. 원래 준비 실행이라 해도 실제3호출 뒤 해당 journey가 항상 잘못 실패할 수 있으므로 실제 GO 전 수정·독립 delta 재검증이 필요하다.

원본 재현 코드/관측은 `artifacts/private/run-20260921/c7-merchant-instrument-independent/probes.mts` 및 `probes.json`에 보존했다. 모델/원격 페이지/IndexedDB/실장부를 사용한 결과가 아니다.

## 통과한 준비 검사와 한계

- 작성자 selftest19개를 독립 재실행: **19/19 PASS**, 실패/skip0. 원본 결과 `repeated19.tap`. 이 중10개는 기존 transport helper 회귀 재실행으로만 분류하며 새 generic 구현 독립 판정으로 세지 않는다.
- 실제 caller CLI2개: execute 미지정은 QA_EXECUTE_FLAG_REQUIRED, false draft+execute는 QA_EXPLICIT_APPROVAL_REQUIRED. 둘 다 exit1, 새 QA output0.
- 실제 finalizer 분모 루프를 VM으로 실행: setup 실패 상황의11개가 전부 NOT_RUN이며 가짜 PASS0. 기존 selfcheck의 첫 FAIL+10NOT_RUN 검사도 재실행했다.
- 합성 cap seed의 request50/10SKU/예산0/deferred10/order0/payment0, batch seed의request20/order0, command_results/events 및 FK 확인. 이는 승인/주문을 사전 성공시킨 seed가 아니다.
- fixture 정상 해석을 실제 adapter+SQLite에 적용한 cap2/exclude1→9×2/상한map10/order0→undo 예산0/deferred10 통과. 해당 결과는 실제 모델 해석 또는 UI 성공이 아니다.
- 정상 batch10×2 journey는 고정된 별도 사례로만 재시작하며 첫 cap journey FAIL/STOP이면 check guard로 NOT_RUN. 성공 사례만 골라 재실행하는 분기가 없다.
- source/runtime/plan/hash/seed helper/v2 manifest/출력 경로의 누락·변조·재사용 반례 거절 재실행 PASS. 변경된 mock_payments/command_results 테이블은 실제 schema에 존재하고 조회 오류를 삼키지 않는다. 그러나 위 MIP01은 테이블명 수정만으로 잡히지 않은 의미 오류다.
- 실제 context callback은 foreign resource guard를 API/static 분기보다 먼저 호출한다. 외부 POST가 budget 밖으로 나가지 못하고 abort/STOP되며 다음 API도 막히는 mock 통과. 허용된 OSM 숫자 tile GET image는 credential 헤더 제거/redirect0/retry0. same-origin merchant POST만 기존 bridge 경로로 전달된다.
- responsive journey는1440/1280/768/390/360과 computed font200 적용, Space toggle/Tab focus, 미동의·주문0을 실제 DOM에서 확인하도록 작성돼 있다. 현재는 코드 검토뿐이며 화면 넘침·가독성·포커스와 시각 비교의 성공을 주장하지 않는다.

원래11개 journey/최대 live3/재시도0/unknown STOP, 동일 Budget20/prior50 및 후속 예약은 유지된다. 초안 예약값은 실제 미래 실행 승인이나 충분한 잔량의 증명이 아니다. C7 필수 품질 실패로 현재 실제 실행은 금지 상태다.

최종 후속: 작성자에게 MIP01 전달 → 별도 준비 수정 계약이 유지되는 범위에서 수정본 동결 → 독립 delta 재검증. 실제 고객/경영주 QA·ADR007 UX·정책 최종 처분·G5/main/Production/G6는 미완료로 남긴다.

## MIP01 수정 후 독립 delta 재검증 — 준비 범위 PASS

최종 **준비 장치 delta PASS**, 초기 FAIL/원본 반례는 위에 그대로 보존한다. 실제 경영주 QA는 여전히 **NOT_RUN**이며, C7 validation01 FAIL 및 paid/후속 평가·UX·G5/G6 실행 금지를 바꾸지 않는다.

수정본 inventory SHA256 `724e48ad638dbbde2277943d5adf243732b62f31c8240621a4928bcf3506ff97`, 목록22파일 전체 bytes를 직접 대조했다. 새 caller SHA256 `a6034d84c14ac282231225335513eb692f61664cdc5a1783595b191864b48a22`. 이전 caller와 inventory는 각각 before-MIP01 파일로 보존됐다. 코드 diff는 journey8의 실패/수령 차단/재시도 SQL 기대값 및 UI 차단 조작에 한정된다. generic budget/route/binding/seed와 다른 journey의 의미를 수정하지 않았다.

독립 재실행:

- 전체 준비 검사 **21/21 PASS**, 실패0/skip0 (`repeated21.tap`). 이전19개에 새 payment contract2개를 추가한 수다. 이전 generic helper 회귀는 동일하게 회귀 재실행으로만 분류한다.
- 별도 작성한 `mip01-delta.mts`가 실제 public seed·DomainEngine·loadDemoScenario를 사용하고 caller의 FAILED/BLOCKED/RETRIED assertion 블록을 직접 추출해 세 상태를 검증했다. 실패 예약1/payment_failed·held/10분·기한null·성공알림0 → 수령명령 PICKUP_NOT_READY/SQL export bytes 불변 → 명시 retry 후 동일 id/code의 confirmed·결제2·paid·확정알림1/픽업알림0을 확인했다.
- 같은 정상 실패 상태에 **보존된 옛 예약0 기대값은 여전히 실패**한다. 실제 상태를 바꿔 과거 실패를 숨기지 않았다.
- 추가 독립 변형6개: 재시도 후 예약 id 변경, code 변경, 조기 픽업기한, 실패 결제 기록 삭제, 예약 중복, 조기 픽업알림. 모두 실제 RETRIED assertion 블록에서 거절됐다.
- 최신 caller CLI 가드2개 재실행 PASS. config approved=false, QA output 미생성 유지. 새 테스트·검토는 실제 브라우저/모델/HTTP/공유 장부 접근0이다.

별도 재검증 요약은 `artifacts/private/run-20260921/c7-merchant-instrument-independent/mip01-delta.json`에 보존했다. 변경된 UI locator·시각·원격3회 정상 여부는 실제 브라우저를 실행하지 않았으므로 미검증이다. 준비 장치 결함 MIP01은 이 범위에서 닫혔지만 최종 역할 QA나 제품 완료로 승격하지 않는다.
