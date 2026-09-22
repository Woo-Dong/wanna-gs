# ADR-008 — 공개 상품 후보 정답의 동등 조건 복구

- status: adopted (implementation verification pending)
- authority: user-delegated (D48)
- proposer: root
- scope: CORE03/11/21/25, 공개 평가의 정답 오류. 앱·catalog·사용자 입력·보호셋·합격선 변경 없음.

## 문제와 목적 보존

C11 validation02의 C02-validation-007은500ml 요청에 같은 이름/브랜드/용량의 두500ml를 확인 후보로 냈으나 단일 SKU 허용 정답 때문에 실패했다. 공식 제조사 출처 검토는 두 상품의 포장 구분이 현재 catalog에서 소실됐으며 주어진 발화가 양쪽에 부합함을 C10 실행 전에 이미 확인했다. 이름의 용량 반복 횟수나 평가용 ID는 소비자가 말하지 않은 식별 근거가 아니다. 다른 용량340ml를 포함한 과거 오류는 별개이며 실패로 보존한다.

## 제안

공개 전체에서 같은 결함을 사전 조사한다. 현재 확인 범위는 C02-validation-007의 expected와 C06-validation-006의 expected_prior 첫턴이다. 해당 required_any_skus와 candidate_pool을 둘 다 두 유효500ml SKU의 집합으로 바꾼 새 파일/manifest revision을 만든다. 확인 후보 제시는 구매 확정이 아니며 SKU 확인·새 동의는 불변이다. 원래 최종 정정상품·다른 상품·용량·모호성·분모·반복수·95/90·회귀0·오류0은 유지한다. 두 상품을 동일 거래 SKU로 합치거나 답 ID를 프롬프트에 넣지 않는다.

원본 평가·manifest·원관측·실패·비용은 덮어쓰지 않는다. 같은 공개 사례를 포함한 모든 기존 후보/반복을 새 정답으로 대칭 재채점해 원본 결과와 구분하여 보존한다. 새 dataset을 옛 실제 호출에서 사용했다고 표시하지 않는다. 앱/runtime/prompt/dev는 불변이며 새 보호 v3 원문은 구현자/조정자에게 공개하지 않는다.

최종 채택 증거는 원본 두 독립 실제 validation의 전체 관측을 새 정답으로 대칭 재채점하는 파생 증거로 구성한다. 모델이 본 입력·history·state·catalog·prompt·앱 runtime은 바뀌지 않으므로 같은 호출을 새 정답 때문에 반복하지 않는다. 원본 run ID/fingerprint/실행 dataset hash/시각/사용량/FAIL을 유지하고, 별도 새 oracle hash·파생 report·원본 관측 해시·독립 감사의 계보를 검사한다. 원래 두 번의 독립 실제 호출을 한 번으로 합치거나 새 호출로 재표시하지 않는다. 과거 B0와 모든 비교 후보에도 동일한 교정을 적용한다.

manifest-v4는 public_oracle_correction으로 v3를 해시 연결한다. dev·보호v3·은퇴 이력·보호 동결시각은 그대로이며 validation/baseline은 별도 새 파일과 coverage를 둔다. 정확 두 oracle slot의 required_any_skus/candidate_pool 외 의미 diff0을 검사한다. 파생 평가 경로는 checker가 원본 execution과 새 score를 구분하고 공개 사례의 비공개 원관측 해시 검증 및 정규화 관측의 결정적 재채점·고정 허용diff·독립 감사·현재와 원래 앱runtime 동일성을 검증해야만 허용한다. 채택·최종 동결 후 미실행 보호v3 최초1회 및 모든 QA/UX/G5/G6는 여전히 필수다.

추가 유료 호출은 보호92+UI96=188 정상 경로이며 현재2004에서2192회다. 기존$20/2400 안에서 예약할 수 있으므로 호출 상한 확대는 이 경로의 선행조건이 아니다. 사용자에게 이미 요청한2500회 승인은 현재 미응답이며 예산을 변경하지 않는다. 구매/자동충전 금지는 유지한다.

정규화 공개 관측에는 case/run 식별자, action/SKU 집합, 구조화 경영주 명령, 확인 flag, 전송 상태, 토큰 수/비용/지연과 이전 턴 구조만 허용한다. 사용자 발화·설명·이유·질문 원문·인증/헤더/URL은 게시하지 않으며 질문은 존재/공백 여부의 형태값으로 대체한다. 비공개 원본과 정규화 관측의 old/new 모든 채점 결과가 같음을 로컬 독립 검토하고, CI는 정규화 관측으로 재현한다. 정규화 검증은 익명화 보장이나 암호학적 원격 실행 증명이 아니다.

## 기각 대안과 검증

특정 SKU/짧은 이름 우선 규칙은 관측 근거가 없어 기각한다. 단순 재호출해서 운 좋게 옛 단일정답만 나오는 반복도 복구가 아니다. 옛 실패 덮어쓰기, 해당 사례 삭제, threshold 완화는 금지한다. 두 독립 관점은 제품 가치/명세와 평가·실패 보존을 확인한다. 공개 전체 범위 감사, 두 oracle slot 외 diff0, 실제입력/관측 불변,340ml 및 다른 실패 보존, source/manifest 결속과 독립 checker 검증을 통과한 뒤 채택한다.

## 독립 검토

- 제품/출처: research — [동의](../execution/run-20260921/adr008-product-review.md). C11 작성자이므로 C11 독립 품질 승격 승인으로 세지 않는다.
- 상태/명세: final_ux_state — [독립 동의](../execution/run-20260921/adr008-state-review.md).
- 평가 실행 정합성: method_auditor — [독립 동의](../execution/run-20260921/oracle-v4-evaluator-review.md). 구현 전 의견이며 구현 후 별도 독립 기술 검증이 필요하다.

채택: 2026-09-22, root. 제품 근거와 두 독립 관점의 중대한 반례가 해소되어 D48 위임으로 채택한다. 기술 구현·정규화/재채점 검증·실제 후속 모델 실행은 이 정책 채택과 별개이며 아직 완료하지 않았다.
