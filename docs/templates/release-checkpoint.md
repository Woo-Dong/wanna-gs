# Git/배포 체크포인트

- task/milestone / 상태 / 다음 작업:
- repo / remote 이름 / branch 역할·이름 / worktree / 수정 소유자:
- 선행 통합 SHA / 작업 commit SHA / PR URL / 현재 PR head:
- 정책 ADR / 작업 계약 / 독립 검증자:
- 로컬 검사와 code fingerprint / 원본 결과 경로:
- CI run/check 및 검사 SHA / 실패·skip·적용 제외:
- 병합 대상 SHA / 병합 결과 SHA / 누적 통합 검사:
- Preview URL·deployment ID / source SHA / 환경·DB/schema/seed/model:
- G5 / 최종 정책 감사 / 릴리스 PR / Production deployment·검증 SHA / G6:
- push/merge/deploy 응답 유실 시 조회한 실제 상태:
- 미해결 실패·외부 차단 / 보존한 사용자 변경 / 재개 행동:

자기 commit에 그 commit SHA를 적으려 하지 않는다. 실행 당시 fingerprint와 후속 CI/artifact를 연결한다. Preview Ready와 최종 제품 검증 성공을 구분한다.

- 선택 제공자·모델·설정 버전 / 전환 이유·관련 평가·G5/G6:
- OpenAI 사용량·한도 관측 시각·시연 예비량 / 배포 환경변수·모델 복구 설정:
