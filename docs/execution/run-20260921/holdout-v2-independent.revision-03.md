# 새 보호 평가셋 독립 데이터 검토

최종 판정은 **revision-03 데이터 검토 PASS**다. 앱 구현과 분리된 `/root/holdout_revision_review`가 `wanna-gs-nl-experiment`, docs21/23/24, ADR003과 C6 복구 계약을 적용했다. 실제 모델 품질·runner 호환성·출시는 판정하지 않았다.

84사례를 전수 읽고 이전 공개·은퇴 보호셋 및 시연 자료와 대조했다. 마지막 수정19건의 원문·정답·문맥을 재확인했으며, 나머지65건은 앞선 검토와 같은 의미 필드임을 확인했다. 단순 상품명·숫자·어순 치환으로 지적했던 항목은 실제 상태·표시 정보·조건 관계를 구별하는 사례로 바뀌었다. 검토한 비교 범위에서 의미 family 중복은0건이다. 정확명 조회라는 범주 전체를 한 family로 취급하지 않았다.

| 독립 재계산 항목 | 기존 / 최종 |
|---|---|
| 사례·모델 발화 | 84 / 84 · 92 / 92 |
| 고객·경영주 | 60/24 · 동일 |
| 명확 / 불확실 | 고객40/20·경영주15/9 · 동일 |
| 범주·단턴/다턴 | 18범주·76/8 · 동일 |
| 경영주 명확 조건1/2/3개 분포 | 6/4/5 · 동일 |
| 카탈로그 | 동일248상품·실제 hash 대조 |

스키마84건, 모든 다턴 정답, 카탈로그 후보·수치·scope·문맥, 출처와 파생 시나리오84건의 대응을 확인했다. 난도 동등성은 분포와 실제 판별 내용을 대조한 사전 데이터 검토 판단이다. 통계적인 모델 난도 동등성이나 이전 세트 대비 paired 개선을 입증한 것은 아니다.

최종 canonical hash는 `18f2a373dc48b372f166e6dd6f51fd97687a406e33f8f601fe814bbeafd6c305`다. [최종 메타데이터](holdout-v2-independent.json)에 근거 hash를 기록했다. [revision-01 FAIL](holdout-v2-independent.revision-01.md)·[메타](holdout-v2-independent.revision-01.json), [revision-02 FAIL](holdout-v2-independent.revision-02.md)·[메타](holdout-v2-independent.revision-02.json), [최종 메타 사본](holdout-v2-independent.revision-03.json)을 보존한다. 원문·정답·상품·사례 식별자를 담은 상세 근거는 `artifacts/private/run-20260921/holdout-v2-independent/`에만 있다.

기존 공개 평가셋·은퇴 보호 원본·scorer·출시 기준은 불변이다. 실제 모델 호출·장부 수정은0건이며 C6 기술검토·dev·두 validation·버전 동결과 새 revision 실행기 검증은 별도 선행조건이다. 이 PASS는 제품 품질·G5/G6 통과나 보호셋 실행 승인이 아니다.
