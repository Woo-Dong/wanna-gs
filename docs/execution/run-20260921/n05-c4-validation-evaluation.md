# N05 C4 고정 validation 독립 평가

현재 판정: **첫 validation 84/84 통과, 두 번째 83/84로 역할별 최소 미달. C4 best/holdout 승격 불가**. 첫 회 성공과 두 번째 실패를 합쳐 통과시키지 않는다. 아래 최초 결과와 두 번째 결과를 모두 보존한다. 최종 G5/G6 통과도 아니다.

## 실행 계약

- source `48bdb4f18f6c769806fbfa9399ea2cf6af2b5f6f`, Preview `dpl_4MmYgaDCps4s6ECYsCA5cYLPMfe9`, model `gpt-4.1-mini-2025-04-14`, prompt `packed-refs-v5`, catalog248은 [dev 보고서](n05-c4-dev-evaluation.md)의 불변 증거와 같다. 실행 전 28개 소스와 exact commit 바이트를 다시 대조했다.
- 별도 validation config `artifacts/private/run-20260921/n05-c4-validation-config.json` SHA `992c8627b8c518cfa6c22f1419dc207f24bacf9e20a36d1f6b8c1ed3de9d9cf4`. 첫 실행의 현재 최대276attempt를 미래예약에서 제외한 **684attempt/$7.182**를 사전 고정했다. 두 번째에도 동일 config를 쓰며 중간에 예약을 낮추지 않는다.
- 공개 validation84/92발화의 canonical hash `180e1ef3890bbde535e4be29a75698b5fa42d9e77a915da9d3d3646c9e486f46`, state SHA `d1a0845a4f45f44af9698963c700e9dfa24d13bb3a4b8b729b9b15e8a15278e1`. 사례·정답·가족분할 변경0, protected holdout 접근0.
- prior50은 보수 예약, unknown attempt$.05, 전체2400회/$15 중단을 유지한다. PLAN_VALID84/92 이후 첫 회 명시 GO만 실행했다. 원문·실패·시도·중간 진행·원본 설정을 private에 보존한다.

## 첫 회 결과

run_id `41e43c20-9e09-480b-8c04-511c95718e08`, run_fingerprint `d64cea5c5afb5dcced42b310b27c5baeb6198ded4cca7c66385756111459158f`.

| 지표 | B0 저장 validation | C4 첫 validation |
|---|---:|---:|
| 전체 통과 |58/84|84/84|
| 응답 미완료 |10|0|
| mandatory 오류 |0|0|
| 실제 호출 |92|92|
| P50(ms) |2337|2437|
| P95(ms) |4052|4389|

고객 명확40/40·불확실20/20, 경영주 명확15/15·불확실9/9이며 95%/90% 기준을 각각 만족한다. 고객 category C01~09 분모는9/8/8/7/6/6/6/5/5, 경영주 M01~09는3/3/3/3/3/3/2/2/2이고 각 범주 실패0이다. 동결 전체 coverage 검증, stage_ready=true, nl_minimum_pass=true다. 기준선 대비 개선26/회귀0 목록을 분석 summary에 보존했다. B0 원본은 재호출하거나 수정하지 않았다.

P95는 기준선보다 높으므로 지연 개선이라고 주장하지 않는다. 20초 목표 안에 있으나 UX의 비모델 완료시간·조작 비교를 대신하지 않는다. 현재 채택 개선 근거는 오류 감소이며, 두 번째 반복 및 필수 제품 QA가 남아 있다.

실제92발화·92attempt, 자동/선별 재시도0, usage unknown0, pending false, stop null이다. 토큰1,037,782, 사용량 기반 추정 비용$0.426964, 최대 attempt$0.0054444. 종료 장부 upper661calls/known611/unknown0, 측정비용$2.7923821+prior예약$2.50=upper$5.2923821. 공급자 청구 확정값이나 계정 hard cap으로 표현하지 않는다.

원본 `artifacts/private/run-20260921/n05-c4-validation-01`, 분석 `n05-c4-validation-01-analysis`. candidate-report SHA `79d652d8e99a142c7e668740c5bffd4f64b8ea43bbc6496a12093a7e995284d2`. 정답별 composite·모든 prior turn과 실제 응답 history를 기존 scorer로 검사했다. 본인이 작성한 평가 장치의 독립성은 research/builder의 [scorer 검토](eval-independent.md)·[전송기 검토](e02-independent.md)에서 분리해 연결한다.

## 남은 검증과 목적 보존

두 번째는 새 run ID/출력 경로에서 같은84개 전부를 실행하고 첫 회 성공을 재사용하지 않는다. 각 repeat가 독립적으로 최소 기준을 충족해야 하며 합산 평균으로 실패를 상쇄하지 않는다. 첫 결과로 holdout을 열거나 튜닝하지 않는다. 고객 확정·동의, 경영주 명시 scope·범위, 정상 성공과 최소질문을 유지한 채 채점했다.

B0/C1/C2/C3 실패와 UX B0 비교 NOT_READY는 그대로다. 이 문서는 최종 제출 URL의 실제 두 역할 G5/G6, 키 비노출·심사자 접근, best UX 완료를 주장하지 않는다.

## 두 번째 동일 설정 반복 결과

첫 회 보고를 완결한 뒤 별도 GO에 따라 같은84개/92발화 전체를 새로 실행했다. config SHA는 `992c8627b8c518cfa6c22f1419dc207f24bacf9e20a36d1f6b8c1ed3de9d9cf4`로 불변이고 미래684/$7.182 예약을 낮추지 않았다. run_id는 별개의 `973b3ff7-0b2d-4c72-8660-81a75e95fab7`, run_fingerprint는 첫 회와 같은 `d64cea5c5afb5dcced42b310b27c5baeb6198ded4cca7c66385756111459158f`다.

**83/84 PASS, incomplete0, mandatory0, stage_ready=false, nl_minimum_pass=false**. 고객 명확40/40·불확실20/20, 경영주 명확15/15·불확실8/9(88.89%)다. 마지막 값이90%에 미달한다. 범주 M06은2/3, 나머지 범주는 전부 통과했다. B0 대비 개선25/회귀0이지만 이 개선이 출시 최소 미달을 상쇄하지 않는다. 첫 회84와 합산한167/168로 통과시키지 않았다.

M06-validation-002: 이전3번 발주안을 지금 승인하라는 입력에서 실제 전달 state는 proposalVersion=3, currentProposalVersion=4, stale=true다. 동결된 case·state를 현재 make_request로 오프라인 재구성해 이 세 필드가 실제 요청에 포함됨을 확인했다(추가 HTTP0). 기대는 clarify이지만 모델은 restore/current_proposal/restorePrevious=true를 제안했다. 입력의 '이전'을 복원으로 해석한 행동 오류이며 모델 내부 이유는 추측하지 않는다. 스키마에 유효한 제안이고 자동 실행은 없으므로 scorer의 mandatory0과 의미 실패를 구분한다. 후단 domain의 stale 차단 가능성으로 모델 실패를 성공 처리하지 않는다.

실패 호출은 HTTP200/input12692/output88/2775ms/$0.0052176이며 usage를 보존했다. 두 번째 전체92호출, 재시도0·unknown0·pending false·stop null, 토큰1,038,343, 추정비용$0.4271512, P50 2461ms/P95 6231ms다. 종료 장부 upper753calls/known703/unknown0, 측정비용$3.2195333+prior예약$2.50=upper$5.7195333. 비용·시간·분모를 첫 회 기록에 덮어쓰지 않았다.

원본 `n05-c4-validation-02`, 분석 `n05-c4-validation-02-analysis`, 동일 fingerprint/서로 다른 run ID/동일 dataset 및 scorer.repeat_ready=false 확인은 private `n05-c4-validation-repeat-verdict.json`에 보존했다. `public-failures.json`에 유일 실패의 전체 공개 case/관측을 남겼다. 보호 holdout 접근·호출은 계속0이다.

독립 최종 판정은 **C4 반복 안정성/최소 기준 미충족**이다. 자동 세 번째 반복이나 성공 실행 선택으로 덮지 않는다. 후속 조정은 기존 후보 한도 안의 별도 복구 판단과 새 source/config 검증이 필요하며, 이번 보고는 그 실행 권한을 추가하지 않는다. UX 비교 NOT_READY 및 최종 제출 미완료도 유지한다.
