# C6 마지막 후보의 한정 복구 계약

상태: 기존 docs21/23·ADR003의 복구 경로 적용. 새 품질 기준이나 후보/비용 한도 변경이 아니다. C5 최종82/84 실패 및 원본 실행은 보존한다. 제품 검토 research와 평가 검토 method_auditor가 기존 경로 해석에 동의했다. 구현/실제 품질 PASS는 별도다.

## 목적·소유권

고객의 정상 상품 탐색·명시 확인/동의, 경영주의 현재 수정·미래 정책 초안·명시 복사·복원과 카테고리/혼합 제외를 유지한다. SKU 하나를 제외하면서 전체 카테고리를 덧붙이거나 실제 카드결제/본부 보고를 상품 검색으로 바꾸는 오류를 줄인다. CORE02/03/05/12/17/18/21/23/25, D44/45/46, ADR002/003/007은 불변이다.

root: 서버 통합/고객 경계/공통 schema·prompt/config·Git. preflight_builder: merchant-grounding 양성 문법 및 자체 단위. research: 독립 서버 검증. method_auditor: 독립 NL 평가·새 보호 holdout 소유. 구현자/실험자는 원래/새 보호 원문과 정답을 읽지 않는다. 별도 데이터 검토자는 앱 구현과 독립이어야 한다.

C6는 두 역할 각각 여섯 번째/마지막 후보다. C1~3의 dev 선별 실패·미완료 validation을 성공으로 바꾸지 않는다. C4 validation은 B0 대비26/25개 오류 감소·회귀0으로 정체가 아니었으나 두 번째 출시최소 미달이었다. C5는 B0 대비26/25 감소와 마지막 평가 실패를 함께 보존한다. 실패한 릴리스를 연속 세 번의 측정 개선 없음과 혼동하지 않으며 C6 종료 후 슬롯 초기화는 없다.

## 기술 가설

두 역할에서 기존의 명시된 범위를 모델 생성 schema로 제한하는 한 후보다. 명확한 입력에 대해서만 좁혀지며, 일반 자유 표현을 전부 거절하지 않는다. 실제 응답을 채점 정답으로 덮어쓰거나 잘못된 조건을 후단에서 삭제하지 않는다. 모델·catalog·검색·도메인·평가정답은 유지한다.

- 경영주: 전체 문장을 소비하는 양성 문법으로 완전 SKU 이름/ID만 제외하는 지시를 증명할 때만 excludeCategories를 빈 배열로 제한한다. 모호 별칭·category-only/mixed·부정/인용·참조 복사·미소비 문구는 기존 schema로 돌아간다. 범용 한국어 parser라고 주장하지 않는다.
- 고객: 명시 실제 거래/본부 보고 실행 요구가 확실하고 부정·인용·정정이 없는 좁은 경우에만 scope 경계 action을 제한한다. 일반 상품 탐색·명시 비실행·인용은 기존 경로다. clarificationCount=2이면 추가 질문을 금지한다.
- ablation: 각 certificate 분기 on/off의 schema와 정상·경계 fixture를 독립 검증한다. 유료 후보를 추가해 ablation하지 않는다. 실제 효과는 고정 dev와 두 validation 및 새 holdout에서만 평가한다.

## 사전 비교·한도

기존 공개 dev252/validation84·정답·scorer·95/90/mandatory0은 변경하지 않는다. 기존 선택 dev30/34turn을 유지하고 통과 후 동일 validation84/92turn을 두 번 실행한다. C6 repeat01↔C5 repeat01, repeat02↔repeat02 대응을 고정한다. 각 반복에서 B0 동일84 대비 오류2건 이상 감소와 기존 B0 정상 회귀0을 보고하고, C5 대비 핵심범주·mandatory·필수 정상 회귀0을 별도로 검사한다. 두 repeat 최소 기준을 각각 만족해야 하며 합산/좋은 repeat 선택 금지다. B0 incomplete를 보존하며 compare_candidate 함수의 invalid_baseline을 PASS로 부르지 않는다.

호출 총2400·D46 추정$20, prior50/$2.50·기존unknown$.05, 현재 upper1064/$7.1995789를 유지한다. dev 전 필수 후속 validation552+새holdout276+UX96+G5G660=984attempt/$10.332와 다음unknown$.05를 예약하면 $17.5815789다. 현재 dev최대102까지 포함한 전체상한2150회다. 실제 runner는 매 호출에서 공유 장부·pending·가격·출처를 재검사한다. quota/권한·예산벽을 fixture나 새 장부로 우회하지 않는다.

## 보호 평가 교체

집계와 일반 실패 분류가 후속 가설에 쓰였으므로 원래84를 은퇴한 보호 regression 이력으로 분류한다. 원본·정답·hash·실패·비용은 수정/삭제하지 않으며 이번 목표에서 같은 holdout을 다시 호출하지 않는다. 이관은 공개 dev/validation에 원문을 합치거나 기존 분모를 바꾸는 행위가 아니다.

새 독립 holdout은 84개(고객60/경영주24), clear40/15 및 uncertain20/9, 기존18범주 분모, 단턴76·다턴8=92발화를 유지한다. 이전 모든 public/retired/시연 family와 의미상 비중복이어야 한다. ID·상품명·어미만 바꾼 표현은 새 family가 아니다. SKU/속성·명령 복합성·대화·모호성·stale/권한·긴입력 등 난도 지표와 독립 정답 검토를 실제 호출 전에 고정한다. 만들 수 없으면 NOT_READY다. 구현자가 원문을 열람하지 않는 별도 검토·공개 집계 metadata·hash로 출처를 남긴다. 기존 manifest를 덮지 않고 별도 revision을 만들며 실행기/릴리스 검사가 새 revision을 지원하는지 검증한다.

C6 기술검토·dev·두 validation 후 source/model/prompt/schema/catalog를 동결한 경우에만 새 holdout을 평가자가 한 번 실행한다. 결과를 C5 원래 holdout과 paired 개선치로 주장하지 않는다. 새 holdout도 미달이면 C7/다른세트/동일세트 추가실행은 자동 시작하지 않는다. 필수미달은 면제하지 않는다.

## 후속

C6 전체 최소 기준 통과 후 ADR007의 고정 새 UX 양 arm, 독립 고객/경영주 실제 브라우저 QA, 두 관점 정책·운영 검토→G5→main/Production→익명 제출 URL G6를 수행한다. C5 approved=false 준비 config·과거 결과를 새 후보 실제 결과로 재표기하지 않는다. 모든 작업 공간과 로그를 보존한다.
