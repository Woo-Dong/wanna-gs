# 새 보호 평가셋 독립 데이터 검토

현재 판정은 **revision-02 FAIL / NOT_READY**다. 앱 구현과 분리된 `/root/holdout_revision_review`가 `wanna-gs-nl-experiment`, docs21/23/24, ADR003과 C6 복구 계약을 적용했다. 원문·정답·상품·사례 식별자는 비공개 근거에 보관한다.

84행을 직접 읽었으며, 고객60/경영주24·명확40/15·불확실20/9·기존18범주와 단턴76/다턴8의92발화, 동일248상품 catalog binding을 재계산했다. 기존 JSON schema84건 검사와 메타 sidecar 대응도 통과했다. 명확한 경영주 명령의 제한조건 수 분포는 이전6/4/5로 복원됐다.

그러나 **기존 명령에서 상품·숫자·어순만 바꾼 의미 family 중복을 최소2건 확정**했다. 추가적인 말투 변형과 긴 입력의 반복 패딩도 새 family라 할 근거가 부족하다. 일부 불확실 사례에서 안전한 미식별 행동을 정답에서 제외할 근거도 더 필요해 정답·난도 동등성 전체 승인은 보류했다. ID·동일문장 교집합0은 의미 독립성을 대신하지 않는다.

현재 canonical hash는 `a036b8b1a8bc0846dbf1716b91decb5aeca1200c6791ca2fec3d2c556ed19b66`이다. [현재 메타데이터](holdout-v2-independent.json), [revision-01 FAIL](holdout-v2-independent.revision-01.md)·[메타](holdout-v2-independent.revision-01.json), [revision-02 메타](holdout-v2-independent.revision-02.json)를 보존한다. 상세 입력·검사·비교 근거는 `artifacts/private/run-20260921/holdout-v2-independent/` 아래 revision별로 남긴다.

수정본은 새 hash로 독립 재검토해야 한다. 기존 dev/validation·은퇴 보호 원본·scorer·출시 기준은 변경하지 않았고 실제 모델 호출·비용장부 수정은0건이다. 이 판정은 데이터 준비 검토이며 runner 호환성·실제 제품 품질·G5/G6 통과를 뜻하지 않는다.
