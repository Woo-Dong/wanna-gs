# C10 — 명시 규격에 맞는 고객 후보 생성

D48 위임에 따른 제한 복구. 기준 integration51240e8, 고객 구현 preflight_builder, 독립 기술검증 research, 독립 live평가 method_auditor, 통합/배포 root. CORE02/03/11/17/18/21/23/25와 기존 최소95/90·mandatory/incomplete0·C5 대응 반복 핵심범주/정상회귀0를 유지한다.

## 목적과 원인

명확히 요청한 상품의 규격을 지키면서 모호한 설명·정정·대안·알레르기 확인 등 정상 탐색은 유지한다. C9 dev30/30, validation83/84의 최소PASS/채택FAIL을 보존한다. C02-validation-007에서는500ml 요청에340ml를 조건 차이로 설명하면서도 primary로 생성했다. 프롬프트 지시는 있지만 모든 공급 SKU를 허용하는 생성 enum은 이 모순을 제한하지 않았다.

## 구현 경계

고객 전용 규격 증명 helper는 확실한 긍정 단일 규격 요청만 인증한다. ml/L/g/kg 정규화로 확인되는 다른 규격의 ID만 모든 candidate kind의 생성 enum에서 제외한다. 공급 catalog 원문과 모든 데이터/정답을 유지하고 모델 출력은 무손실 변환한다. 불명확 문법·부정·비교·범위·복수규격·대체 허용·정정·미지원 단위는 원래 전체 허용으로 돌아간다. catalog의 미상/복합 규격과 비교불가 차원도 유지한다. verifyCustomer/verifyMerchant, 경영주v9, 모델/provider/packing/retrieval/domain/UI는 유지한다.

같은500ml의 중복표기행은 원제조사 prod_idx가 달라 동일 SKU라는 근거가 없다. 강제중복제거·데이터/oracle보정·정답ID특례를 하지 않는다. 규격 제한만으로 남은 중복ID 실패까지 해결됐다고 주장하지 않으며 실제 고정평가로 확인한다. 출처 검토 결과로 추가 범위가 필요하면 구현/평가 전에 별도 근거와 독립 검토를 남긴다.

## 검증

일반화한 긍정 규격/단위 동등성·known mismatch 모든kind 차단·unknown/복합유지·부정/정정/모호/거절/대안/알레르기/count2·이전SKU참조·외부실행 경계·merchant불변·실제SDK mock/enum한도·사용량 오류보존을 검사한다. 자기검증과 독립 검증을 분리한다. 기술CI/정확Production → 고정dev30 → validation84 두회 → freeze → 신규holdout84 최초1회 → ADR007 UX56×2/과거48보존 → 실제두역할QA/두정책관점/G5 → main병합/최종Production G6. 실패 후 같은 설정을 좋은 결과가 나올 때까지 반복하지 않는다.

## 필수 후속 예약

공유 upper1476/$9.2915701, prior50/$2.50 및 기존unknown$.05를 유지한다. 전체 $20/2400, 현재stage 남은turn×3 및 원래retry상한3은 불변이다. 미래NL은 각turn 필수1+선택retry여유1로 예약한다: dev후속648=validation368+holdout184+UX84+QA/G612, 두validation 동일후속464=후속validation184+holdout184+96, holdout후속96. 필수 분모나 품질은 변경하지 않는다.

root는 [평가자 검토](c10-reservation-evaluator-review.md)와 별도 research 검토(private c10-reservation-independent/review.md, SHA3540cde54610dedc10009fff9f7b181d3506669e99eda5f127e2cf87db21da50)를 대조해 이 예약을 채택한다. 정상 dev/val01/val02/holdout 진입 합계2226/2250/2342/2066, val02 전 추가retry58은2400 허용·59는2401 STOP을 임시Budget으로 독립 재현했다. 모든 단계 최대retry 또는 모든미래2attempt 완주를 보장하지 않는다. 실제usage/unknown/pending/auth/총액에 따른 STOP, 같은config 두validation, 보호본문 격리·구매/자동충전 금지를 유지한다. 선택 retry 여유를 재산정한 것이며 기존 실패·장부/한도를 초기화하지 않는다.

## 출처 모호성과 선택 경로

공식 원본/최신 응답 해시를 research가 대조했고 method_auditor와 final_ux_state도 원본을 독립 확인했다. 두500ml는 무라벨 family41/prod273과 기본 family42/prod271로, 현 catalog는 포장 구분을 담지 못했다. 공개 C02-007 및 C06-006 첫턴은 이 구분을 명시하지 않는다. 원래 단일허용 정답은 유효한 상품을 포함하지만 다른 유효500ml도 실패로 판정할 수 있는 보수적인 한계가 있다. 이것으로340ml 오류나83/84·핵심범주회귀FAIL을 소급PASS로 바꾸지 않는다.

별도catalog/평가 revision은 출처 정보 복원, 두 영향턴의 명확한 포장조건, 같은새데이터의B0/C5대조군 및 UX두arm seed결속·보호셋독립영향검토가 필요하다는 두 관점 의견을 보존했다. 이는 채택된 데이터 변경이 아니다. root는 우선 일반적인 명시규격 제한만 실행하고 **현재 고정 데이터·채점·회귀 기준을 그대로 적용**한다. 특정500ml SKU나 짧은 이름을 우선하는 특례를 만들지 않는다. C10이 원래 게이트를 정직하게 통과하면 그 증거를 사용하고, 실패하면 그대로 실패다. 데이터 revision은 별도 범위/예산/기구 검토 없이 자동 적용하지 않는다.
