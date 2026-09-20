# 게이트 보고서 템플릿

빈 양식은 PASS 증거가 아니다. 실제 명령과 원본 결과를 연결한다.

- 증거 ID / task / gate / 실행 시각:
- 게이트 판정: PASS | FAIL | BLOCKED | not_applicable
- 증거 유효성: valid | stale | 미확인
- 원본 테스트 실행 결과와 현재 판정의 차이:
- 적용 AC/BR / 기대값 / 실제 결과:
- 코드 revision / 미커밋 content hash 또는 파일 manifest:
- 계약 / DB 스키마·마이그레이션 / seed / clock 버전:
- 환경 / 모델·프롬프트 / live 또는 fixture:
- 자식 게이트 증거 ID 및 유효성:
- 명령 / 종료 코드 / 실행·성공·실패·skip 수:
- 원본 결과·로그·브라우저/DB 증거 경로:
- 구현자 / 독립 검증자 / 독립 확인한 내용:
- 미실행·제외 사유와 상위 검증 경로:
- 알려진 한계 / 실패 보고서 / 다음 게이트:
- 변경 영향으로 무효화한 증거와 재검증 범위:

PASS 조건: 필수 기대 테스트 실행, 결과와 현재 대상 일치, 필요한 자식 및 독립 검증 유효. 계획한 명령만 적은 상태, 0개 테스트, fixture-only인 live 요구, 필수 skip은 PASS 불가.

## 추적

- 위임 ADR / 정책 버전 / 두 정책 검토 근거:
- branch / PR URL / head·대상 기반 / CI / 통합 SHA:
- Preview/Production deployment ID와 검사 source SHA:

정책 공백은 17번으로 해결한다. 정책 검토와 구현 테스트, 위임 채택과 사용자 직접 확정을 구분한다.

## 품질 증거

- CORE/유효 ADR/context와 검사 대상 revision:
- research→시나리오→case 매핑·dataset/seed/split hash:
- 해당 NL baseline/best-known/실험 결과·출시 최소 기준:
- 고객·경영주 독립 UX report / 미실행 범주:
- PLAN-READY/SEED-READY/운영 감사 적용 여부·근거:

선택 개선 종료와 필수 게이트 통과는 별도 판정이다.

## 목적 보존

- 원래 사용자 결과 / CORE·AC:
- 유지된 정상 사례 / 수정한 실패 사례 / 인접 기능 증거:
- 기능 축소·기준 완화 여부 / 독립 검증자 판정·근거:
