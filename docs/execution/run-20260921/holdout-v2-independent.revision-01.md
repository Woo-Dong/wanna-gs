# 새 보호 평가셋 독립 데이터 검토

현재 판정은 **revision-01 FAIL / NOT_READY**다. 앱 구현과 분리된 `/root/holdout_revision_review`가 `wanna-gs-nl-experiment`, docs21/23/24, ADR003과 C6 복구 계약을 적용했다. 상세 원문·정답·상품·사례 식별자는 비공개 근거에만 보관한다.

고객60/경영주24의84사례, 명확40/15·불확실20/9, 기존18범주 분모와 단턴76/다턴8의92발화, 동일248상품 catalog binding은 재계산해 확인했다. ID·family ID·정규화 동일문장 교집합은0이지만 **공개 시연과 의미상 같은 상품·의도의 철자 변형 family 중복을 최소1건 확정**했다. 여러 범주에서 이름·조건·문체 치환만으로 새 family라 할 근거도 부족했다.

난도 동등성도 인정하지 않았다. 명확한 경영주 사례의 제한조건3개 분모가5→2로 줄었으며, 일부 고객 범주는 허용 행동과 의미 구분을 입력에서 직접 안내한다. 글자 수 증가만으로 이 차이를 상쇄할 수 없다. 정답 근거·신규 파생 시나리오의 추적을 보강하고, case JSON schema에 없는 메타 필드는 별도 기록으로 이동해야 한다.

검토 대상 canonical hash는 `650af94aca1a60408dc8b5a5fb9a5e168b9d6ffa898d8e03236dc74024b1cc71`, 이전 보호셋 hash는 `1f9f938a7eba167ece4dd78f6c1d66a35d419c98a23af20ad4fad2d8b2474323`다. [검토 메타데이터](holdout-v2-independent.json)에 재현 근거 hash와 분모·판정을 남겼다. 입력 사본·정적 결과·비교 근거·FAIL 이력은 `artifacts/private/run-20260921/holdout-v2-independent/revision-01/`에 보존한다.

작성자는 초안을 보존하고 다시 설계 중이다. 수정 revision은 새 hash로 독립 재검토해야 한다. 기존 dev/validation·은퇴 보호 원본·scorer·출시 기준은 변경하지 않았으며, 실제 모델 호출·비용장부 수정은0건이다. 이 검토는 평가 데이터 준비 판정이며 실제 제품 품질·runner 호환성·G5/G6 통과를 뜻하지 않는다.
