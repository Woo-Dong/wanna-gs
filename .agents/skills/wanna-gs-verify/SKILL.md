---
name: wanna-gs-verify
description: Verify WANNA GS implementation tasks with independent review and staged unit, integration, E2E, and live-model gates. Use for this project's feature implementation, integration, or release evidence; distinguish planned checks from executed checks.
---

# 원하GS 단계 검증

프로젝트 루트는 이 파일에서 `../../..`이다. [개발 루프](../../../docs/14-agent-development-loop.md)의 게이트·증거·소유권 규칙을 읽고 해당 작업에 적용한다. [인수 기준](../../../docs/09-verification-and-evals.md)과 [검토 목록](../../../docs/13-review-checklist.md)에서 정답과 미정 정책을 확인한다.

1. 작업 계약과 실제 가용 도구를 확인한다. 구현자는 자체 단위 테스트를 수행하고, 별도 에이전트가 독립 검증한다. 같은 구현자의 두 번째 의견을 독립 검증으로 표시하지 않는다.
2. 검증자는 구현자의 결론에 의존하지 말고 요구사항·입출력·반례·실행 결과를 확인한다. code fingerprint와 schema/seed/model/mode를 대조한다.
3. 하위 PASS만으로 상위 PASS를 부여하지 않는다. 영역 통합은 실제 DB, 단계적 연결은 경계 실패/중복/경합, 브라우저는 서버 저장 상태까지 확인한다. 상품별 경영주 집계에서 고객별 요청 상세로 내려갈 때 상품·수량·가격·동의 여부/시각·접수 순번·발주 연결·확보/배정/결제/예약/픽업 상태와 actor/session/store 권한을 대조한다. fixture와 live를 별도 판정한다.
4. 보고서에는 PASS/FAIL/BLOCKED/stale/not_applicable을 정확히 남긴다. 미실행·0개 테스트·필수 skip·누락/오래된 증거는 PASS가 아니다. not_applicable은 사유와 상위 검증을 제시하며 필수 AC 제외 수단으로 쓰지 않는다.
5. 실패하면 [복구 절차](../../../docs/15-failure-recovery.md)를 따르고 해당 경로의 다음 통합을 보류한다. 무관한 작업은 계속한다. 검증 기준을 조용히 낮추지 않는다.
6. [게이트 보고서](../../../docs/templates/gate-report.md)와 PROGRESS를 갱신한다. 실행기/CI가 없으면 구현된 것처럼 보고하지 않는다.

이 스킬은 검증 지침이다. 실제 명령은 설치된 프로젝트와 테스트 실행기에서 확인한다. 미정 정책은 [17번](../../../docs/17-autonomous-decisions.md)으로 자율 채택한다. 사용자 불변식이나 외부 권한을 임의로 만들지 않는다.

GitHub 검사는 현재 PR head·대상 기반·통합 결과와 증거를 대조한다. ADR 변경 시 정책 검토와 영향 검사를 갱신한다. G5에 최종 정책 빈틈 감사, G6에 정확한 제출 deployment 검증을 포함한다.

## 모델 전환 검사

AC-29와 [25번](../../../docs/25-model-budget-and-fallback.md)의 두 경로 연결·전환·실패 처리·무료 예산을 검증한다. 최종 제공자 설정이 바뀌면 관련 평가와 G5/G6 증거를 갱신한다. 실제 한도를 고갈시키지 말고 소진·조회 불가·429는 모의 오류로 주입한다.

## 목적 보존

작업·복구·재개 시 [card.md](../../../card.md)와 관련 CORE/유효 ADR을 확인한다. 원래 사용자 결과·유지할 정상 사례·인접 기능 영향을 보고서에 연결하고 수정한 실패 사례와 함께 독립 검증한다. 정상 요청을 모두 거절하거나 필수 기능을 제거해 얻은 PASS는 인정하지 않는다. 정책 변경은 17번을 따르며 단순 수정에 새로운 정책 승인 절차를 추가하지 않는다.
