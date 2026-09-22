# N06 C5 고정 validation 독립 평가

최종 반복 판정: **첫84/84·두 번째83/84, 각각 출시 NL 최소 충족 / repeat_ready=true**. 첫 반복 timeout 1회 복구·사용량 미확정1건, 두 번째 범위밖 의미 오류1건을 보존한다. best 선정/holdout 진행의 근거이며 최종 제품 게이트 통과는 아니다. 재시도 전 첫 시도 정상 응답은91/92발화이고, 전체93시도 중 성공92·실패1이다. 복구 성공이 최초 실패를 삭제하지 않는다.

## 동일 설정 결속

- exact source `f6a34def5dd6cc6287c3dedba805824974d67db8`, Preview `dpl_8YECM1r2msmSCtjLKGNSPvVYqKKV` / `https://wanna-qcrmzotip-beatrain-4635s-projects.vercel.app`, target null/READY.
- validation config SHA `c7dd835ba324dff51d60de141da23a65c0d05eeab90e2c145cda3b4da4baac04`, source28 각각 root/exact git bytes 일치. dev config와 미래 예약 이외 동일함을 비교했다. proof SHA `615e8189e16cd383beae095f7281d5755dbf0abc03f4c85217d3f19c613d4df5`.
- model `gpt-4.1-mini-2025-04-14`, prompt `packed-refs-v5`, catalog248/state 변동0. context-v13 ACK 유지. 공개 validation84/92발화 dataset SHA `180e1ef3890bbde535e4be29a75698b5fa42d9e77a915da9d3d3646c9e486f46`.
- PLAN_VALID84/92/future708 확인 후 첫 실행만 명시 GO로 진행했다. future708=후속 validation276+holdout276+UX96+G5G660, 추정 예약$7.434, prior50/unknown$.05/2400calls/$20 유지.
- run_id `9080bbf2-82a6-44a9-a8bc-938d389e9efc`, fingerprint `91a7a7695062aec19f504217f98104fde9aa3a4c4a394fe812c33ffceb6f95c2`. 원본 `n06-c5-validation-01`, 분석 `n06-c5-validation-01-analysis`, driver 로그를 private 작업 공간에 보존했다.

## 첫 반복 결과와 실제 실패

84/84 최종 의미 채점 PASS, 미완료0·mandatory0, 고객 명확40/40·불확실20/20, 경영주 명확15/15·불확실9/9이다. 각 범주 전체 분모도 보존하고 최소 기준을 충족했다. B0 동일84개58/84 대비 개선26·회귀0, C4 첫 반복과 동률·회귀0, C4 두 번째 대비 M06-validation-002 개선1·회귀0이다. 해당 stale 사례는 실제 clarify 및 최신 제안 확인 질문을 반환했다. C4 실패 원본은 불변이며 다른 후보의 실패 반복을 C5 평가 횟수로 계산하지 않는다.

실행 예외는 C09-validation-001의 첫 시도다. 서버 HTTP504 `LLM_TIMEOUT`, provider_called=true, usage/cost=null, latency45275ms가 반환됐다. 기존 동결 실행기는 응답을 journal/장부에 보존한 뒤 TRANSIENT 규칙에 따라 한 번 재시도했고 HTTP200/usage가 있는 실제 응답으로 완료했다. 최초 실패1·재시도1·usage미확정1을 모두 보존했다. 이는 응답 없이 journal pending인 요청의 자동 재실행이 아니며 종료 pending=false/stop=null이다.

채택 ADR003 오류 처리 항목과 evals/README의 기존 NL 계약은 timeout 최초 포함 최대3회를 허용하고 unknown usage를 원본에 남기도록 한다. 따라서 이번 첫 반복의 의미 채점 PASS는 그 계약 범위다. **첫 시도100% 성공으로 표현하지 않는다.** ADR007 UX v3의 unknown 시 전체STOP/첫 시도 정상 성공 요건을 NL 계약 대신 적용하거나 이 결과로 UX 통과를 주장하지 않는다. 실패/불확실성 분류를 조정자에게 즉시 알렸으며 추가 모델 호출 없이 계약을 대조했다.

## 비용·지연·한계

실제93attempt, 알려진 토큰1,034,785, 알려진 추정 비용$0.42592에 usage 미확정 timeout1건의$.05 예약을 별도 유지한다. 최대 알려진 attempt$0.0055204이며 모델 입력/출력은 동결 상한 내다. 종료 장부 upper880calls / known_provider830 / unknown_provider0, 알려진 비용$3.8060565 + prior계획$2.50 + 미확정usage$.05 = upper$6.3560565다. provider 호출 여부와 usage 알려짐 여부는 서로 다른 지표이며 prior50/비용은 실측이 아니다.

채점기의 P50 2503ms/P95 5187ms, 실패 시도 최대45275ms를 함께 공개한다. B0 같은84개 P95 4052ms보다 높아 지연 개선이라고 주장하지 않는다. 재시도된 발화는 timeout+다음시도3855ms+backoff를 겪었으며 성공 응답 지연만으로 원래 사용자 대기시간을 축소하지 않는다. G5 UX 조작·완료시간 측정의 대체가 아니다.

본 보고서는 root 구현 C5의 독립 실제 평가다. 본인 작성 평가 장치의 독립 검증은 research/builder의 기존 별도 보고서로 구분한다. 정답·소스·표본·분모 변경0, 원본 실패 삭제0, 분석 재호출0, 보호 holdout 접근/호출0이다. 현재 첫 반복만 실행했고 두 번째 동일 config 반복은 별도 GO 뒤 진행한다. best 미선정·holdout 미실행·UX v3 미실행·최종 G5/G6 미완료를 유지한다.

조정자도 ADR003/README 원문과 기존 stop 계약을 확인해, 알려진 provider의 종료된 HTTP504 1회 재시도가 기존 NL 허용 범위이며 별도 사용자 무재시도 강화가 없음을 확인했다. 기준·코드 변경 없이 첫 반복 판정을 확정한다.


## 두 번째 동일 설정 반복 완료

config SHA `c7dd835ba324dff51d60de141da23a65c0d05eeab90e2c145cda3b4da4baac04`, 같은28source/exact git bytes·모델·prompt·catalog·state·84/92발화·미래708/$7.434를 다시 확인하고 PLAN_VALID 뒤 별도 GO로 새 실행했다. 첫 성공 응답을 재사용하지 않았다. 두 번째 run_id `c504135a-b5e0-459d-8158-12ca73d99697`, fingerprint `91a7a7695062aec19f504217f98104fde9aa3a4c4a394fe812c33ffceb6f95c2`로 첫 실행과 동일하며 run_id는 다르다.

| 항목 | 첫 반복 | 두 번째 반복 |
|---|---:|---:|
| 전체 의미 성공 |84/84|83/84|
| 고객 명확 |40/40|40/40|
| 고객 불확실 |20/20|19/20(95%)|
| 경영주 명확 |15/15|15/15|
| 경영주 불확실 |9/9|9/9|
| 미완료/mandatory |0/0|0/0|
| actual attempts |93|92|
| 재시도/usage미확정 |1/1|0/0|
| known tokens |1,034,785|1,033,697|
| known 추정 비용 |$0.42592|$0.4253168|
| P50/P95(ms) |2503/5187|2393/5356|
| 최소·stage_ready |true|true|

두 번째 실패 `C08-validation-002`는 실제 카드 결제와 본부 보고서를 요구한 범위밖 발화다. 허용 정답 clarify/unidentified 대신 실제 카탈로그 SKU의 show_candidates를 반환했다. raw reason도 상품 등록 사실만 설명했다. **wrong_action 오류로 그대로 보존한다.** 실제 카드결제·보고 전송 실행 또는 모델 SKU 최종확정은 없으며 mandatory 오류로 재분류할 근거는 없다. 고객 불확실19/20=95%로 사전90% 최소는 충족한다. C08 범주 자체는2/3이며 범주별 결과도 보존했다. 오류를 정답으로 바꾸거나 분모에서 제거하지 않았다.

두 번째 B0 동일표본 대비 개선25/회귀0, 첫 C5 반복 대비 의미 회귀1이다. C4 첫 반복 대비도 이 범위밖1건은 회귀이고 C4 두 번째의 stale 오류는 해결됐다. 안정성이 완전하다고 주장하지 않는다. 두 반복 각각 최소 기준을 충족하며 합산167/168로 실패를 상쇄하지 않았다. 실제 scorer.repeat_ready=true를 서로 다른run_id·같은dataset/fingerprint/report hash와 함께 `n06-c5-validation-repeat-verdict.json`에 기록했다.

두 번째 최대 알려진 attempt$0.0053724/input12825/output216, 재시도0·usage미확정0·pending=false·stop=null이다. 누적 장부 upper972calls / known_provider922 / unknown_provider0, 알려진 추정 비용$4.2313733 + prior계획$2.50 + 첫 반복 미확정usage$.05 = upper$6.7813733. 기존 미확정 비용을 다음 성공으로 상쇄하지 않았다. 분석·비교는 추가 모델 호출0이다.

첫·두 번째 report 및 모든 raw attempt/실패는 각각 private `n06-c5-validation-01`/`-02`와 분석 폴더에 보존했다. 보호 holdout 접근·호출0, 아직 best 최종 동결·holdout GO는 없다. 최종 C5 고객 브라우저 QA는 private `c5-customer-qa-preparation/execution-plan.md`에 최대live3/approved=false 계획만 준비했으며 실행0·장부쓰기0이다. 후속 순서는 best 동결 검토→별도 승인된 holdout1회→두 역할 실제 브라우저/UXv3/G5G6이고 모든 필수 결과가 나오기 전 완료를 선언하지 않는다.
