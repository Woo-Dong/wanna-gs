---
name: wanna-gs-recovery
description: Diagnose and recover failed WANNA GS development or verification tasks using reproducible evidence, bounded retries, and regression gates. Use on this project's test, integration, model, or deployment failures without changing unresolved product policy.
---

# 원하GS 실패 복구

프로젝트 루트는 이 파일에서 `../../..`이다. [복구 절차](../../../docs/15-failure-recovery.md)를 읽고 실패 유형에 해당하는 부분을 적용한다. 앱 실행 오류와 개발 과정의 코드 수정을 구분한다.

1. 실패한 입력·기대/실제 결과·task/gate·fingerprint를 확보하고 [실패 보고서](../../../docs/templates/failure-report.md)에 남긴다. 결과가 불명확한 거래 변경은 실행 ID로 상태부터 조회한다.
2. 영향받은 후속 통합만 보류한다. 공통 파일의 작성자와 실행 중인 이전 작업을 확인하고, 수정 소유권 이전 전에는 동시에 고치지 않는다.
3. 최소 재현과 독립적인 기대값을 확보한다. 정책 미정이면 버그로 꾸미지 않고 [17번 위임 결정](../../../docs/17-autonomous-decisions.md)과 wanna-gs-decide로 해결한다. 이 범위의 정책 때문에 사람 답변을 기다리지 않는다. 외부 권한·크레딧 문제를 같은 호출 반복으로 해결하려 하지 않는다.
4. 검증 가능한 원인 가설 하나와 최소 수정안을 만들고 회귀 사례를 확보한다. 원인에 맞는 재시도 한도·멱등성·재개 절차를 사용한다. 테스트 삭제/skip/fixture 몰래 전환은 해결이 아니다.
5. 수정 담당과 독립 검증자를 분리한다. 재현 테스트 → 영향받은 영역 → 상위 통합 경로의 순서로 유효한 증거를 새로 확보한다. 수정으로 영향받은 이전 증거를 현재 PASS로 재사용하지 않는다. 무관한 유효 검사는 이유 없이 반복하지 않는다.
6. 원인·수정·증거·남은 차단과 다음 행동을 PROGRESS에 남긴다. 반복 실패는 가설 재검토와 해당 작업 차단으로 전환한다. goal 상태는 실제 도구 계약을 따르며 임의 paused/complete 처리하지 않는다.

이 스킬 자체는 앱 오류를 자동 수리하는 런타임이 아니며 유료 리소스·파괴적 복구·새 배포 권한을 부여하지 않는다.

## 목적 보존

작업·복구·재개 시 [card.md](../../../card.md)와 관련 CORE/유효 ADR을 확인한다. 원래 사용자 결과·유지할 정상 사례·인접 기능 영향을 보고서에 연결하고 수정한 실패 사례와 함께 독립 검증한다. 정상 요청을 모두 거절하거나 필수 기능을 제거해 얻은 PASS는 인정하지 않는다. 정책 변경은 17번을 따르며 단순 수정에 새로운 정책 승인 절차를 추가하지 않는다.
