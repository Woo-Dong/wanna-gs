# UX 평가 보고서 템플릿

빈 양식, 정적 fixture 화면만의 제시, screenshot 한 장, API-only 확인은 브라우저 UX PASS 증거가 아니다. 실제 브라우저가 fixture 모드 앱을 조작한 검사는 G4의 해당 모드 증거가 될 수 있으나 필수 live/G6를 대체하지 않는다.

## 실행 대상

- 보고서 ID / gate / 실행 시각:
- URL / deployment ID / source SHA:
- CORE·ADR / context hash / 스키마·seed·clock / model·프롬프트·mode:
- 브라우저·버전 / viewport / locale / network 조건:
- 시장 조사·시나리오 ID / source-backed 사실·표현 / synthetic persona·발화 표시:
- 증거 root / trace·video·screenshot / console·network / DB·event 경로:

## 고객 독립 QA

- customer-qa agent ID / 고객 기능 구현자 ID / 독립성 확인:
- browser profile/context ID / 모바일 viewport:
- persona 목적 / 시작 상태 / 실제 자연어 입력:
- 실제 행동 순서와 화면 관측:
- 식별·정정·상품/점포 확인·동의·요청·상태·픽업 결과:
- 빈/로딩/오류/새로고침/연타/지연·만료 회복:
- 서버 상태·event와 화면 일치 / 다른 세션 격리:
- 판정: PASS | FAIL | BLOCKED | not_run

## 경영주 독립 QA

- merchant-qa agent ID / 경영주 기능 구현자 ID / customer-qa와 다른 agent 확인:
- browser profile/context ID / 데스크톱 viewport:
- persona 목적 / 시작 상태 / 실제 자연어 입력:
- 실제 행동 순서와 화면 관측:
- 묶음 수요·미식별·자연어 수정·이번만/지속 정책·예산·발주·입고·수령 결과:
- stale·상충 조건·중복 승인·부분 실패·동시 예산·재개 회복:
- 고객 화면/DB/event와 상태 일치 / 역할·점포 권한:
- 판정: PASS | FAIL | BLOCKED | not_run

## 발견과 재검증

| defect ID | 역할·시나리오 | 기대 / 실제 | 빈도 | 심각도·릴리스 차단 | 증거 | 수정 PR | 독립 재검증 |
|---|---|---|---|---|---|---|---|
|  |  |  |  |  |  |  |  |

- 필수 여정·정합성·회복·접근성 종합 판정:
- 미실행/차단 범위와 이유:
- 장식 개선 후속 과제 / 필수 수정과 구분:
- 최종 gate 판정 / 판정자:

고객과 경영주 검사는 순차 실행할 수 있으나 합쳐서 한 agent의 자기 검증으로 대체하지 않는다. 실제 브라우저 도구가 없으면 완료가 아니라 BLOCKED/not_run이다.
