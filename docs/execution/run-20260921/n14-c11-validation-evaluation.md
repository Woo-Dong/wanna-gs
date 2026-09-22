# C11 validation 독립 평가

## 목적 보존과 결속

C11의 고정 공개 validation 84사례/92사용자턴을 실제 모델로 평가한다. 원래 95%/90% 역할별 최소, 필수 오류 0, 미완료 0, B0 대비 오류 감소와 C5 대응 반복의 핵심·정상 회귀 0을 유지한다. 답·분모·채점기는 변경하지 않았다. C11부터 사전 채택한 max_attempts=1을 적용하며 실패를 재호출로 대체하지 않는다.

- 정확 소스: `cd29a2bc3be8c80fa00c03c2985f06819bef7255`, Production `dpl_4p4q7iHyuQ1mgMzDDbwcKnzuBGHU`.
- 모델 `gpt-4.1-mini-2025-04-14`, prompt `customer-classification-v11`. 실제 응답은 실행기의 모델/버전 envelope 검사를 통과했다. 모델 문자열의 별도 원격 텔레메트리 보존이나 암호학적 원격 소스 증명은 주장하지 않는다.
- source 38개 및 runtime 50개 결속을 확인했다. runtime hash `d49c13dcbe3f5b358b8f7fb80d4316a68fd738c9f83a0e6395ec6f56a5dfbb9d`.
- 두 반복 공통 config SHA `55692b96b3a8a87e496a0933a57068bee7d1707be203534bdf789cd680adef89`; future 280회/$6.732 예약을 두 번째에도 그대로 유지한다.

## 첫 반복 — PASS

run `729d6477-6db9-4fd7-a9d0-960de3286b69`, fingerprint `c314dd23413ad31362a8c6408a13f855b0c39a9a877f19364d36039d25ff1d73`.

84/84 통과, 고객 명확 40/40·불명확 20/20, 경영주 명확 15/15·불명확 9/9. 18개 범주 전부 통과했다. 미완료·필수 오류·실패 attempt·unknown usage/provider·pending 모두 0, stop=null이다. B0의 58/84 대비 오류 26개 감소·회귀 0, C5 첫 반복 84/84 대비 회귀 0, C10 대응 반복 대비 회귀 0이다. C7/C8/C9 첫 반복 대비 각각 1/5/1건 개선·회귀 0으로 이전 실패는 원본 그대로 보존한다.

실제 92회 호출/92턴, retry 0, 총 1,213,260 tokens, 알려진 비용 $0.499704. 지연 P50 2,218ms/P95 4,840ms. 누적 장부 상한은 1,912회/$11.6929541이며 prior 50회/$2.50 및 과거 unknown usage $0.05를 유지한다. 이는 과거 불확실성을 지운 실비 주장이 아니다.

원본은 `artifacts/private/run-20260921/n14-c11-validation-01/`, 채점·paired 분석은 같은 접두어 `-analysis/`에 보존했다. 공개 비식별 집계는 `quality/release/evidence/c11-validation-01/{report,execution,binding,bundle}.json`이다.

## 후속 경계

첫 반복은 부모가 지정한 두 번째 실행 조건을 모두 충족했다. 동일 config의 별도 run으로 두 번째 84/92를 실행하며 첫 응답을 재사용하지 않는다. 두 번째 결과는 아직 미실행 시점의 본 기록에서 PASS로 세지 않는다. 보호 holdout-v3, 역할 브라우저 QA, UX, G5/G6는 별도 승인·실제 증거 전까지 미실행이다. 이 평가는 고객 saveNeed/SQLite 영속화 수리나 최종 제품 완료를 검증하지 않는다.

## 두 번째 반복 — 역할 최소 PASS, 후보 채택 FAIL

run `3acf1e6a-caee-4275-8c88-a1abc1a9f2c9`, fingerprint는 첫 반복과 동일한 `c314dd23413ad31362a8c6408a13f855b0c39a9a877f19364d36039d25ff1d73`이다. 첫 반복 원본 보존·조건 확인 후 별도의 84사례/92턴을 전부 다시 실행했다.

83/84 통과: 고객 명확 39/40(97.5%)·불명확 20/20, 경영주 명확 15/15·불명확 9/9. C02는 7/8, 나머지 17범주는 전부 통과했다. 원래 역할별 95%/90% 최소와 incomplete=0, mandatory_errors=0은 충족했지만 **C5 대응 두 번째 반복 대비 C02 핵심 정상 회귀 1건으로 채택 FAIL**이다. scorer의 `stage_ready=true`는 전체 분모·최소 기준 충족이며 후보 채택·출시 PASS를 의미하지 않는다.

B0 대비 개선 25·회귀 0이다. C5 대응 반복 대비 C08 개선 1·C02 회귀 1, C10 대응 반복 대비 개선 0·C02 회귀 1이다. C7 첫 반복 대비 개선 1·회귀 1, C8 첫 반복 대비 개선 4·회귀 0, C9 첫 반복 대비 개선 0·회귀 0을 보존한다. 총점이 같거나 최소 기준을 넘는 것으로 핵심 정상 회귀를 면제하지 않는다.

### 공개 실패의 최소 진단

고정 공개 사례 `C02-validation-007`에서 첫 반복은 고정 기대 SKU 하나만 primary로 반환해 통과했다. 두 번째는 기대 SKU에 다른 SKU를 primary로 추가하여 `incorrect_candidate`로 실패했다. 추가 SKU의 동결 catalog 규격도 500ml이며 이름에 500ml가 두 번 기록돼 있다. 따라서 이번 실패를 340ml 수량 불일치로 설명하지 않는다. 기존 공식 source의 포장 구분 누락·동일 500ml 정체성 모호성 조사와 관련될 가능성은 있으나, 모델의 내부 선택 원인을 확정할 증거는 없다. 고정 기대·점수·회귀 판정은 변경하지 않았고 사후 정답 확대나 기존 결과 재채점도 하지 않았다.

92회 실제 호출/92턴, retry·실패 attempt·unknown usage/provider·pending 모두 0, stop=null이다. 알려진 tokens 1,213,919, 비용 $0.500108, P50 2,325ms/P95 5,018ms이다. 두 validation 합계 184회/$0.999812이며, 종료 누적 장부 상한은 **2,004회/$12.1930621**(알려진 provider 1,954회/$9.6430621)이다. 과거 prior 50회/$2.50와 unknown usage $0.05는 그대로 남는다.

원본은 `artifacts/private/run-20260921/n14-c11-validation-02/`, 채점·paired 분석은 같은 접두어 `-analysis/`, 비식별 export는 `quality/release/evidence/c11-validation-02/{report,execution,binding,bundle}.json`에 보존했다. 두 export 모두 실제 결과만 담고 실패를 제거하지 않았다. source 38개·runtime 50개 및 공통 config 해시 불변을 종료 후 확인했다.

## 종료 판정

**C11 채택 FAIL / freeze 미실행 / fresh holdout-v3·역할 QA·UX·G5/G6 미실행.** 첫 반복 성공으로 두 번째 실패를 대체하거나 세 번째 반복을 추가하지 않는다. 남은 총 호출 여유는 396회이며, 추가 후보의 원래 전체 단계 34+184+92+96=406회는 이를 10회 초과하므로 자동 실행 권한이나 완주 가능한 예약이 있다고 주장하지 않는다. 원장·예산·정답·분모·기준을 변경하지 않고 부모에게 실제 결과를 전달한 뒤 추가 호출을 중단했다.
