---
name: wanna-gs-decide
description: Resolve unspecified WANNA GS prototype policies under the user's delegated authority, using two independent agent reviews, decision records, and regression checks. Use when implementation or integration uncovers business-rule gaps without changing explicit requirements or expanding the demo scope.
---

# 원하GS 위임 정책 결정

[자율 결정 프로토콜](../../../docs/17-autonomous-decisions.md)과 [결정 원장](../../../docs/02-decisions-and-open-questions.md)을 읽는다. 사용자가 세부 데모 결정을 위임했으므로 O/R 항목이 미정이라는 이유로 사람에게 묻고 기다리지 않는다.

1. 기존 사용자 정의·불변식·제외 범위와 발견한 입력을 대조한다. 앱 고객/경영주 동의는 개발 정책 위임과 별개다.
2. 최소 정책 초안을 [ADR 양식](../../../docs/templates/decision-record.md)에 기록한다. 기한/상한이면 기산점·경계·실패 행동을 명시한다. 실제 운영 기능을 늘리지 않는다.
3. 제안자 외 서로 다른 두 서브 에이전트에게 제품 원칙/범위와 상태/실패/검증 관점을 독립적으로 검토시킨다. 슬롯이 적으면 순차 실행한다. 같은 에이전트 역할 이름만 바꿔 두 검토로 세지 않는다.
4. 조정자는 중대한 반례를 해소하고 `authority: user-delegated`로 채택한다. 단순 다수결로 불변식을 변경하지 않는다. 취향 차이는 더 단순하고 보수적인 안으로 정하고 근거를 남긴다.
5. 정책·설정·상태/API·UI·seed·기대값을 함께 갱신하고 해당 게이트와 영향 통합을 검증한다. 실패에 맞춰 인수 기준을 낮추지 않는다.
6. 최종 통합 감사에서도 발견→결정→구현→재검증을 반복하되 범위 밖 개선은 후속 과제로 둔다. 실제 인증/비용/권한 장벽이나 충돌하는 확정 요구는 꾸며 해결하지 않는다.

복구와 검증의 상세 경로는 [15번](../../../docs/15-failure-recovery.md), [14번](../../../docs/14-agent-development-loop.md)을 따른다. 이 스킬은 설정값을 런타임 LLM이 즉석에서 바꾸게 하는 권한이 아니다.

## 이전 결정과 재발 방지

초안 전에 [CORE](../../../docs/CORE_REQUIREMENTS.md)와 [DECISION_INDEX](../../../docs/DECISION_INDEX.md)의 현재 유효 정책·기각 이력·의존 관계를 읽는다. context revision/hash를 남기고 policy_key/scope 충돌·supersedes·영향 테스트를 확인한다. 채택 시 index·관련 명세·기대값과 작업자 ACK를 함께 갱신한다. 사용자 고정 정의는 위임 ADR로 대체하지 않는다. 기계적 명령마다 ADR을 만들지 말고 의미 있는 제품/계약/평가/운영 변경을 추적한다.
