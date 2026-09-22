# N09 C7 고정 validation 첫 반복 독립 평가

판정: **첫 반복 FAIL / 두 번째 반복 not_run / best 승격·holdout 진행 불가**. 83/84 통과, incomplete1·mandatory0이다. 역할별 정확도 최소는 각각 만족하지만 모델 응답 계약 실패1건으로 ADR003의 최종 완료 조건인 누락0/스키마오류0을 만족하지 못했다. 실제 scorer의 `nl_minimum_pass=false`, `stage_ready=false`를 유지한다. 83/84라는 합산 수치나 오류를 차단한 서버 동작으로 평가 실패를 PASS로 바꾸지 않는다.

## 권한·소스 결속

D47 고객 전용 추가 후보7·경영주6·합계13을 유지한다. C7 dev가 통과한 source636의 결과는 그대로 보존했다. 별도 경영주 UI 수량상한 adapter P1 수정이 포함된 새 runtime에 validation을 결속했으며, dev가 이 수정까지 시험한 것으로 표시하지 않는다. root/builder의 SQL 재현·수정 및 별도 독립 기술 증거와 본 API 평가를 구분한다.

- exact source `88ae1a431f8691790069487dc70f2519698bd122`, Preview `dpl_65MVJmqazoi8UT5GtfJvnH1rGJtK`, URL `https://wanna-rbnpger37-beatrain-4635s-projects.vercel.app`, READY/target null. 새 source32를 현재 및 exact git과 대조해 전부 일치했고 C7 dev의 source32와도 바이트 동일했다.
- runtime47 hash `4de25bb543fb1167df644a1da2859184462fc0ea371a89e6f933079b13cab64e`, exact git 일치. dev source636와 비교한 유일 runtime 차이는 `src/components/merchant/model.ts`였다. 이 변화는 새 자연어 후보나 경영주 후보 슬롯 초기화가 아니다.
- context-merchant-cap-v17 SHA `b5b15a4eff6c8ead11313ca6908f35f223a8ccbcad11855afa115953789fed42` ACK, 입력64개 현재 해시 일치.
- config SHA `f163d1e746cccae13de89fdc68449df42a864de2d68801857714a7e498ba4dd9`, proof SHA `11eab416eb63f8a13f9ba49138f451185e56925fe5b979abcfff493df18718e9`. 독립 PLAN_VALID84/92/future708 후 첫 반복만 명시 GO로 실행했다.
- model `gpt-4.1-mini-2025-04-14`, prompt `customer-identity-v7`/SHA `02334ef1e86a4707db47280e607194ccde0de91b817b480c2b5672db4f7d1be4`, catalog248 SHA `f2696abe92521e3ff8f9ab43cb36a1d297a6fd23d272e239605b49fab4343b1e`, SQL 합성 업무 state SHA `d1a0845a4f45f44af9698963c700e9dfa24d13bb3a4b8b729b9b15e8a15278e1` 유지. 실제 반환 envelope의 모델/버전/identity를 실행기가 검사했다.
- 원래 validation84/92 dataset SHA `180e1ef3890bbde535e4be29a75698b5fa42d9e77a915da9d3d3646c9e486f46`. run_id `4780469d-7be7-4ddf-a050-67e416727439`, fingerprint `c41b6fb3815b987d82e0d044f58cd4521fd969fa4e50cd6bf057407a31af2339`.
- private 원본 `n09-c7-validation-01`, 분석 `n09-c7-validation-01-analysis`, 로그 `n09-c7-validation-01-driver.log` 보존. 종료 source32 재대조도 불일치0이다.

## 결과와 고정 비교

| 항목 | 첫 반복 |
|---|---:|
| 전체 통과/분모 |83/84|
| 고객 명확 |40/40|
| 고객 불확실 전체분모 |19/20 (95%)|
| 고객 불확실 완료분모 |19/19 (100%)|
| 경영주 명확 |15/15|
| 경영주 불확실 |9/9|
| incomplete / mandatory |1 / 0|
| 실제 attempts / 성공 / 실패 |92 / 91 / 1|
| 재시도 / unknown usage |0 / 0|
| minimum / stage_ready |false / false|

C04 범주6/7, 나머지17범주 전부 통과했다. transport failure를 성공으로 포함하지 않았으며 전체84와 실제 완료83의 분모를 구분한다. 성공 응답만의100%가 원래 분모를 대체하지 않는다.

B0 같은 validation84의58/84 대비 개선25·정상 회귀0이다. 원래 B0 incomplete10을 그대로 남기며, B0가 불완전하므로 compare_candidate의 invalid_baseline을 PASS라고 표현하지 않는다. D47 이전에 고정한 C5 대응 첫 반복84/84와 비교하면 개선0·회귀1이다. C5의 약한 두 번째 반복을 골라 비교하지 않는다. B0의 순개선이 있어도 불완전 결과와 핵심 모호/다후보 범주의 C5 대비 회귀를 상쇄할 수 없다.

## 실제 실패와 원인 해석의 한계

공개 `C04-validation-001`에서 HTTP502 `INVALID_MODEL_RESPONSE`와 allowlist 진단 `CANDIDATE_ACTION_CONTRACT`가 반환됐다. provider_called=true, input12849/output335/total13184, 비용$0.0056756, latency7281ms로 사용량은 알려져 있다. 서버가 후보 action 계약에 맞지 않는 출력을 거절했고 실행기는 transport error/schema_valid=false/response null로 기록했다.

원래 retry 규칙상 이 오류는 transient timeout/429가 아니므로 재시도하지 않았다. 실패를 기록한 뒤 동일 고정 표본의 나머지 승인된 사례를 수행했으며 원본1건을 삭제하거나 다른 응답으로 대체하지 않았다. 종료 stop=null은 평가 프로세스가 계획을 끝냈다는 뜻이지 모든 모델 응답이 정상이라는 뜻이 아니다. `cases_recorded=84`, `turns_recorded=92`와 의미/스키마 완료83/84를 구분한다.

이 관측에는 provider의 원문 응답이 없으므로 어느 구체 필드 조합이 틀렸는지, prompt의 어느 문장이 원인인지 확정하지 않는다. 단순 재호출·서버 출력 후처리·정답 변경으로 성공 처리하지 않는다. 허구 SKU 거래·무권한 실행 등 mandatory 실제 위반이 발생했다고 주장하지도 않는다. 실패 출력을 차단한 안전 동작과 필수 정상 해석 성공은 별개다.

## 사용량·예약·목적 보존

92회 모두 호출/usage 확인, 재시도0·provider unknown0·usage unknown0·pending false·stop null. 토큰1,051,923, 알려진 추정 비용$0.4339848. 최대 attempt$0.0056756, 최대 input13033/output335, P50 2600ms/P95 5470ms다. B0 P95 4052ms보다 높으며 지연 개선 또는 UX 완료시간 개선으로 주장하지 않는다. 실제 청구 확정액도 아니다.

종료 장부 upper1224calls / known1174 / provider unknown0. 알려진 비용$5.4077773 + prior 계획$2.50 + 이전 validation unknown usage$0.05 = upper$7.9577773. prior50은 과거 실측이 아니다. 미래708calls/$7.434(두 번째 validation276+holdout276+UX96+G5/G660), 다음unknown$.05, 전체2400/$20을 실행 중 유지했다. 이전 비용과 불확실 비용을 이번 정상 usage로 지우지 않았다. 보수적 중복 예약을 줄이거나 장부를 새로 만들지 않았다.

고객 정상 탐색·미식별·확인/동의, 경영주 명시 범위·수량과48시간이라는 목적을 유지했다. 평가셋/정답/범주/최소기준/모델/소스를 실행 중 바꾸지 않았다. 앱 비구현 평가자의 실제 평가이며 본인 작성 scorer/runner 자체를 독립 검증으로 세지 않는다. 평가장치의 기존 별도 research/builder 검토와 구분한다.

## 종료와 미실행

첫 반복의 incomplete0 조건 실패로 두 번째 반복은 시작하지 않았다. D47은 고객 후보 하나만 추가하는 승인이지 실패 후 무제한 복구·재실행·C8 승인도 아니다. 실제 추가 호출0, 신규 보호 원문 접근/모델 실행0, 새 holdout claim0을 유지한다. 이미 동결된 새 보호셋 데이터 검토 PASS는 제품 품질 증거가 아니다.

C5 원래 holdout FAIL·C6 dev FAIL·C7 현재 FAIL을 모두 보존한다. 새 보호 평가·ADR007 UX v3·현재 두 역할 최종 브라우저 QA·정책/운영 최종 판정·G5/G6는 완료되지 않았다. 기존 UI adapter 수리의 기술 증거도 이 자연어 실패를 면제하지 않는다. source/작업 공간/세션/원본/실패/보호 파일을 보존하며 별도 지시 없이 평가를 자동 반복하지 않는다.
