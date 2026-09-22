# ADR008 독립 상태·실패·검증 검토

- reviewer: final_ux_state
- reviewed draft SHA-256: `36965326ac8717222b70c4f02bce2e438acc29354578d0f3c1fe2aa8c1e525bd`
- 판정: **조건부 채택 동의**. 원명세에 근거한 두 공개 oracle의 과소포함 정정과 기존 두 실제 실행의 파생 재채점은 허용할 수 있다. 아래 검증 조건은 최종 PASS 전에 실행기로 강제해야 한다. 이 의견은 구현·재채점 결과·G5/G6 PASS가 아니다.
- 독립성: 제안자 root·상품 사실 조사 research·후속 데이터/정규화 구현 method_auditor와 다른 검토자다. 상대 최종 결론을 읽기 전에 원명세·공개 입력·기존 출처 사실로 초기 의견을 작성했다. 이번 검토의 모델/브라우저/공유 원장/보호 원문 접근·앱 수정은0이다.

## 원명세와 오류의 성격

[AC-02](../../09-verification-and-evals.md)는 모호함에서 후보 선택 또는 질문과 고객 확인을 허용한다. [05번](../../05-agents-and-search.md)의 show_candidates 예시는 복수 후보이고, [09번](../../09-verification-and-evals.md)은 허용 후보/질문/미식별 집합을 정답으로 정의한다. [27번](../../27-service-values-and-guardrails.md)은 임의 확정·강제 선택을 금지하면서 차이·미확인을 설명하고 확인받도록 한다. 모든 비유일한 입력에 clarification만 해야 한다는 계약은 아니다.

공식 출처 진단은 포장 구분이 현재 catalog에서 누락됐고 두 항목이 모두 이름·브랜드·500ml 조건을 충족함을 C10 실행 전에 확인했다. 해당 공개 입력들은 포장을 지정하지 않는다. 이름에 용량이 두 번 나타난다는 이유나 평가 SKU ID만으로 한쪽을 유일 정답으로 삼을 수 없다. 따라서 두500ml를 동등한 확인 후보 집합으로 인정하는 근거는 C11 점수와 독립적이다. 동일한 거래 SKU로 합치거나 사용자가 포장을 선택한 것으로 간주하지는 않는다.

C02 본 oracle와 C06 첫 turn oracle의 `required_any_skus`·`candidate_pool` 모두를 대칭 any-of로 정정한다. 한쪽만 필수로 남기고 다른 항목의 추가 출력만 허용하는 비대칭 수리는 반대한다. 명시500ml에340ml primary, 다른 조건 위반, 허구 SKU, 고객 확인 없는 확정은 계속 FAIL이다. C06 최종 정정상품도 그대로다. 분모·label·95/90·회귀0·mandatory0·정상 동작·UX 기준을 바꾸지 않는다. 포장 정보 누락과 최종 실제 화면의 설명 적절성은 별도 QA의 대상이며 oracle 정정으로 해결됐다고 주장하지 않는다.

## 기존 두 실제 반복을 파생 증거로 인정하는 조건

[ADR003](../../decisions/ADR-003-evaluation-and-demo-boundaries.md)의 두 실제 validation 반복은 모델 변동과 동일 조건의 결과를 각각 검증하려는 요구다. 이미 별개로 수행한 두 run 전체를 보존하고 모델이 받은 입력이 완전히 같다면, 정답 집합의 사실 오류를 바로잡기 위해 같은 호출을 다시 만들 필요는 없다. 이는 두 반복을 한 번으로 줄이거나 새 source에 과거 PASS를 붙이는 방식이 아니다. [23번](../../23-nl-experiment-loop.md)의 데이터 오류 정정과 평가 버전 간 점수 직접 비교 금지를 함께 적용한다.

1. 두 원래 run ID·fingerprint·execution dataset hash·시각·provider 시도·usage/cost·관측 바이트·원래 FAIL을 immutable 원본으로 보존한다. 파생 bundle은 `kind=derived`로 명시하고 원본 실행과 새 oracle/score를 각각 연결한다. 새 oracle가 과거 실제 호출 당시에 사용됐다고 표시하지 않는다.
2. 각 반복의84사례/92turn 전체를 재채점한다. 두 run은 실제 서로 다르고 원래 같은 설정이어야 한다. 서로 다른 반복에서 성공한 행을 모으거나 부족한 관측을 합성하지 않는다. 두 파생 반복 각각 원래 최소/핵심 정상 회귀·필수 기준을 통과해야 한다.
3. 모델이 받은 text/history/state/catalog/prompt와 현재 앱 runtime이 원 실행과 동일함을 직접 검증한다. oracle 두 slot 외 의미 diff0, dev/seed/보호셋/은퇴 이력 불변을 검사한다. 새 평가 실행기 source는 원 실행의 source와 구분한다. 앱/prompt/runtime 변경이 생기면 이 재사용 논리는 무효다.
4. B0와 영향을 받는 모든 과거 후보·반복에도 동일 revision을 대칭 적용한다. 원래83/84 FAIL 등은 원래 버전의 결과로 남는다. 파생 점수 변화는 평가 오류 정정이며 모델 개선이나 새로운 성공 실행이 아니다. baseline-candidate 비교는 같은 새 oracle에서만 한다.
5. 아직 실행하지 않은 보호v3는 원문 접근·고정 hash·기존 동결시각·claim을 유지하고, 정정 동결과 두 파생 반복 검증 이후 처음 실행한다. 보호 정답을 이용해 공개 정정을 넓히지 않는다. 최종 독립 역할 QA·UX 양 arm·G5/G6도 그대로 필요하다.

## 공개 정규화 관측과 검증 경계

제안된 공개 최소 범위(case/run ID, action/SKU 집합, 구조화 경영주 명령, 확인 flag, 전송/시도 상태, usage/cost/latency, 이전 turn 구조)는 재채점에 필요한 범위로 제한할 수 있다. 자유 발화·이유·설명·질문 원문·인증/헤더/URL·private payload는 공개하지 않는다. 보호 holdout 행은 이 공개 경로에 포함하지 않는다.

- 필드와 값 모두 allowlist를 검사한다. SKU/카테고리/intent/constraint에는 공개 catalog·계약의 값만 공개하며, 임의 문자열이 끼면 자동 게시하지 말고 fail-closed로 별도 검토한다. 파일 크기/행수/깊이와 경로·symlink 경계도 지킨다.
- 질문은 원문 대신 null/빈 문자열/공백뿐/비공백 형태를 구분해야 한다. scorer는 `.strip()`과 truthiness를 둘 다 사용하므로 단일 존재 boolean으로 뭉쳐 판정을 바꾸면 안 된다. 고정 placeholder를 사용하더라도 old/new 모든 사례 판정·이유·mandatory·전체 metrics가 원본과 완전히 같아야 한다.
- prior observations, 실패/미완료, 중복/누락, candidate/alternative 구분, confirmed_sku, mandatory/domain 오류, 시도 횟수·토큰·unknown·지연을 보존한다. 안전하게 표현할 수 없는 채점 의존 필드를 삭제해 통과시키지 않는다. scorer/adapter 원본은 변경하지 않는다.
- 이전 공개 export에 결속된 비공개 원관측 SHA를 먼저 확인하고, 원본→정규화 대응·old/new 동일 채점은 별도 독립 로컬 검토로 증명한다. CI는 정규화+공개 old/new oracle로 재계산하고 선언된 파생 점수와 일치해야 통과한다. 질문·관측·원본 hash·허용 diff·runtime·실행 횟수의 변조 반례를 포함한다.
- 공개 normalized hash만으로 실제 원격 실행이나 원본과의 동등성이 암호학적으로 증명되는 것은 아니다. CI의 재현성 검사와 독립 비공개 원본 검토의 신뢰 경계를 보고한다. 익명화 도구나 세션 로그 공개 승인으로 확대 해석하지 않는다.

## 자원·STOP

현재 root가 보고한 upper2004에서 보호92+UI96=188, 정상 후속 계획은2192회다. 새 두 validation184를 실행하지 않으므로 그 경로의 과도한 두 번째 반복 예약 문제도 새로 발생하지 않는다. 이미 포함된 prior/unknown/과거 실패·비용을 빼지 않고 기존$20/2400, pending·unknown $.05 및 후속 예약을 유지한다. 새188은 무조건 지출 허가나 성공 보증이 아니며 각 실제 호출의 fresh guard와 STOP이 우선한다. 미응답2500 요청을 승인으로 간주하지 않는다.

본 의견으로 정책 채택 단계는 진행할 수 있다. 실제 derived 결과 사용은 새 manifest/파생 계보·정규화 동등성·CI checker의 독립 기술 검증이 통과한 뒤에만 가능하다. 검증 실패 시 원래 FAIL과 NOT_READY를 보존하고 모델 호출을 시작하지 않는다.
