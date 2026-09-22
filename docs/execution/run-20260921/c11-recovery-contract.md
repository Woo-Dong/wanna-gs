# C11 고객 행동 분류 복구 계약

- authority: 사용자 D48/D49, 기존 ADR003의 최대3회 범위 안에서 선택적 재시도 축소. 제품 정책·정답·합격선 변경 없음.
- parent: C10 source a7adafc0381e9ad069030b1cd13b181790763e89. C10 공개 dev30/30·validation84/84 두 번 PASS, 보호 v2 76/84 FAIL 보존.
- 목적 보존: 정상 상품의 오타/별칭/규격·조건부 후보는 성공하고, 모호/미등록/범위밖 요청에서 근거 없이 후보를 만들지 않는다. 대체 후보는 새 확인·동의가 필요하며 경영주 거래/UI·단일 모델 호출·C10 보수적 규격 경계를 유지한다. CORE03/11/17/21/23/25.
- 가설: 고객 생성 프롬프트에서 wire/candidate 형태 설명보다 요청의 범위·상품 정체성 판단을 먼저 수행한다. prompt-only 국소 변경, 새로운 데이터/예시 정답 하드코딩 없음. 구현 research, 독립 제품 기술 검토 final_ux_state; 공통 runner/release checker 작성 root, 독립 검토 final_ux_state.

## 사전 고정 실행 계획

두 [평가 검토](c11-retry-reservation-evaluator-review.md)·[상태 검토](c11-retry-reservation-state-review.md)의 조건을 채택한다. 신규 C11의 dev·동일 config validation 두 회·fresh holdout에 max_attempts=1을 명시한다. 기존 생략값3과 과거 모든 파일/hash는 보존한다. 1회 실패는 그대로 실패/incomplete이며 재호출하지 않는다. 제품 성능 개선으로 재시도 축소 효과를 주장하지 않는다.

현재 upper1786/$11.0094737. 고정 dev30/34turn, validation84/92turn 두 회, holdout84/92turn의 분모·95/90·incomplete0·mandatory0·대응 C5 핵심범주/정상회귀0를 유지한다. 후속 호출 예약 dev372, 동일 validation280, holdout96이다. 정상 경로 계획406회/누적2192, 가장 큰 val02 진입 예약2284로2400 이하이다.

후속 비용은 NL 미실행 turn당$.0105의 운영 추정과 UI96×$.05=$4.80을 합산한다. dev $7.698, 동일 validation $6.732, holdout $4.80을 명시한다. 최초 guard는11.0094737+.05+7.698=18.7574737<20이며 실제 누적/unknown/비용STOP은 매호출 확인한다. 이는 공급자 청구 상한 보장이 아니다. UI96에는 UX84·고객QA3·경영주QA3·최종G62·여유4가 포함되며 여유가 자동 재실행 권한은 아니다.

## 독립 보호셋·증거

v1/C5와 v2/C10 실패·claim·원본manifest를 은퇴 보존한다. 새 v3은 평가자가 후보 프롬프트를 보지 않고 제작하며 별도 검토자가 모든 공개/은퇴 family와 동등 난도·정답·84/92·clear40/15·uncertain20/9·18범주를 확인한다. root/구현자는 보호 원문을 보지 않는다. v3는 v2를 해시로 연결하고 두 실패를 그대로 포함한다. 실제 실행은 최종 후보의 공개 두 반복 PASS·freeze 이후 최초 한 번만 허용한다.

runner/checker의 max1/default3/유효형식/resume/pending/holdout 결속·과거 실패 누락 거절을 독립 mock 검사한 뒤 컨텍스트와 source hash를 갱신한다. source가 바뀐 과거 실행/UX/QA 준비파일은 현재 결과로 재사용하지 않는다.

## 단계와 완료 경계

기술 검사→독립 검토→commit/PR/CI→Production 유지 배포→고정 dev·두validation→freeze·freshholdout→두 역할 실제 QA·UX 양 arm→최종 정책/증거 G5→main 병합/CI→정확한 Production G6다. 기술검사나 READY만으로 최종 완료를 선언하지 않는다. 실패하면 원인을 기록하고 남은 필수 호출·비용을 재산정한다. 구매·상한 확대·기준 완화·보호 우회는 하지 않는다.

## 병행 발견 — 니즈 근거 보존

제품 감사에서 기존 CustomerView.saveNeed가 extractedClues=[]로 저장해, 후보의 sharedEvidence/differences/unknownConditions가 reason에 반복되지 않으면 SQL export/import 후 소실됨을 합성 roundtrip으로 재현했다. docs07·27의 명시된 보존 요구에 따른 C11-NEED 버그 수리이며 새 정책·새 스키마가 아니다. research가 기존 string[] 필드에 SKU·후보종류·모델 관측근거·차이·미확인을 구분해 보존하고, 별도 검토자가 실제 SQLite roundtrip 및 기존 동의/추천·확약 분리를 검증한다. 프롬프트 실험과 별도 수정이며 추가 모델 호출·UI 의사결정은 없다. 최종 후보 source/runtime·역할QA/UX에 함께 결속한다.
