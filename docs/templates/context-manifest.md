# Context Manifest 템플릿

상태: 작업 입력 계약. 빈 필드나 오래된 manifest는 현재 맥락의 증거가 아니다.

## 식별·무결성

- manifest ID / 생성 시각 / 작성자:
- manifest revision / hash 알고리즘 / content hash:
- task ID / branch / base SHA / 대상 환경:
- 이전 manifest / 변경 이유 / stale 처리할 결과:

## 요구·결정

- 적용 `CORE-*`와 기대 증거:
- 사용자 직접 결정 / 원장 revision:
- active ADR ID·상태·effective scope·content hash:
- superseded/conflicting ADR / 금지·폐기 동작:
- 관련 AC/BR/게이트 / 출시 최소 기준:

## 범위·소유권

- 목적 / 포함 범위 / 제외 범위 / 종료 조건:
- 수정 소유 파일 / 공통 파일 단일 작성자 / 읽기 전용 영역:
- 선행·후행 task / 담당 역할 / 독립 검증자:
- API/schema/state/config/seed/clock/prompt/eval 계약 버전:

## 최신 조사 brief

각 행은 goal 실행 시 실제로 조사한다. 해당 없는 영역은 근거를 적고 `not_applicable`로 표시하며, 빈칸을 조사 완료로 보지 않는다.

| 기능 영역 / applicable | 조사 질문·현실적 필요 | source / checked_at | 확인 결과·한계 | 연결 decision ID | scenario/test ID |
|---|---|---|---|---|---|
|  |  |  |  |  |  |

- 모든 적용 기능 영역 검증 범위 확인:
- source-backed 사실·발화와 synthetic persona·utterance 구분:
- 새 실패로 다시 조사할 조건 / 조사 revision:

## 모델·도구의 실제 가용성

- 실행 주체: 개발 agent | 고객 runtime | 경영주 runtime | 평가자
- tool/catalog에서 실제 확인한 시각과 방법:
- 실제 사용 가능 모델 / provider / reasoning 옵션 / override 지원 여부:
- 선택 model·reasoning / 선택 이유 / 상속이면 실제 상속값:
- 앱 runtime 인증·quota·비용 상태 / fixture·live 구분:
- 필요한 브라우저·DB·GitHub·Vercel 도구와 확인 상태:

## 전달과 ACK

| 역할 / agent ID | 받은 hash | 확인한 active ADR·scope | ACK 시각 | 차이·차단 |
|---|---|---|---|---|
|  |  |  |  |  |

- 변경 통지 대상 / 통지 증거:
- ACK 전 진행 가능한 독립 작업:
- 결과가 반환할 `consumed_context_hash`:

모델 이름을 계획에 적은 것과 실제 사용할 수 있는 것은 구분한다. CORE/ADR/계약 변경 뒤 영향받은 작업이 새 hash를 ACK하지 않으면 이전 결과는 stale이며, 영향 없는 증거까지 자동 폐기하지 않는다.

## 목적 보존

- card.md / 관련 CORE·원장·ADR의 현재 hash:
- 사용자에게 남아야 할 결과 / 유지할 정상 사례 / 금지할 변화:
