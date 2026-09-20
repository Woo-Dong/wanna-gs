---
name: wanna-gs-orchestration-audit
description: Audit and improve WANNA GS agent roles, context propagation, gates, and stopping rules with one bounded method-auditor layer. Use at planning, integration, repeated-failure, or release checkpoints; do not create recursive managers or substitute process review for product verification.
---

# 원하GS 운영 감사

[운영 감사 기준](../../../docs/22-orchestration-audit.md), [역할·맥락 계약](../../../docs/20-agent-roles-and-context.md), [결정 인덱스](../../../docs/DECISION_INDEX.md)를 읽는다. 결과는 [운영 실험](../../../docs/templates/method-experiment.md)에 기록한다.

1. coordinator와 다른 method-auditor 한 명이 요구 추적, manifest/hash·변경 ACK, 역할/파일 소유권, 의존성, 실제 모델 가용성, 게이트 증거, 실험 누수·종료 규칙을 읽기/관측 중심으로 감사한다.
2. 관리 깊이는 `coordinator → worker/reviewer/method-auditor` 한 단계다. auditor가 manager/auditor를 추가 생성하거나 무한 자체 개선 루프를 만들지 않는다. 필요한 독립 작업은 coordinator의 기존 DAG에 편입한다.
3. 문제마다 실제 실패·재작업 증거, 기준선, 단일 최소 변경, 사전 성공 조건·관찰 구간·부작용·복구를 정한다. 에이전트 수 증가 자체를 개선으로 세지 않는다.
4. 제안자 외 독립 검토를 거쳐 한정 시험한다. 초안과 보완을 합쳐 두 검토 안에 `현행 유지 | 제한 시험 | 변경 채택 | 기각·기록`으로 끝내고, 새 실제 반례가 없으면 같은 의견을 다시 열지 않는다.
5. 결과가 좋아지고 필수 보호가 유지된 경우만 ADR/계약/CI 변경으로 채택한다. 불명확하면 미검증, 악화하면 복구한다.

운영 개선은 사용자 불변식, 독립 QA, G1~G6, 자연어 출시 최소 기준, 권한·비용 경계를 완화할 수 없다. 중대한 운영 모순을 해소·검증하거나 범위 밖 제안을 근거와 함께 후속 과제로 넘기면 감사를 종료한다.
