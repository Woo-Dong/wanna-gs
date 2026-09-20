# ADR-번호: 정책 제목

- 상태: proposed | adopted | verified | superseded
- 권한 근거: user-delegated / 사용자 직접 지시인 경우 해당 근거
- 관련 O/R·AC/BR / 발견한 입력·공백:
- 날짜 / 제안자 / 조정자 / 정책 버전:
- 지켜야 할 사용자 정의·서비스 가치·불변식:
- 선택지와 권장안 / 구현 복잡도·데모 효과:
- 채택한 규칙: 조건·기산점·기한/수량/횟수·경계·예외:
- 제품/범위 검토자와 독립 의견:
- 상태/실패/검증 검토자와 독립 의견:
- 제기한 반례·해결 / 소수 의견 / 채택 근거:
- 변경할 문서·config·상태/API·UI·seed·테스트:
- 정상·경계·실패 기대값 / 영향 통합 검사:
- 검증 증거 / 코드·PR·게이트 연결:
- 지원하지 않는 범위와 사용자 표시:
- 대체한/대체하는 ADR / 재개 시 확인:

빈 양식이나 찬성 의견만으로 채택/검증을 완료 처리하지 않는다. 사용자 위임에 따른 결정과 사용자가 직접 고른 정책을 구분한다.

## 유효성·컨텍스트

- policy_key / effective_scope / 관련 CORE ID:
- 현재 유효한 선행 ADR과 읽은 index revision/hash:
- depends_on / supersedes / conflicts_with / 기각한 대안:
- 적용 branch·범위 / proposed→adopted→verified 시점:
- 영향받는 작업·코드·테스트·seed·eval / 무효화할 이전 증거:
- 이전 실패 재발 방지 case ID / 마이그레이션·복구:
- index 동기화 / 관련 작업자의 context ACK:

기존 사용자 정의는 위임 ADR로 대체할 수 없다. 같은 policy_key/scope의 충돌하는 활성 결정을 동시에 유지하지 않는다. 과거 결정은 삭제하지 않는다.
