# 환경 사전점검 보고서

- run-id / 시각 / 요청 모드: inspect 또는 live
- status: READY | PARTIAL | BLOCKED
- scope: ready_for_goal
- ready_for_goal: true | false
- production_execution_verified: false (기본 live 범위)
- repo/remote·검사 SHA / Vercel project·환경 / runtime·sql.js/WASM·schema/seed/manifest·브라우저·모델:
- 실제 사용 도구: CLI / connector / browser / agent IDs:

## 검사

| ID | expected | observed | PASS/FAIL/BLOCKED/not_run/unverified | 증거: SHA·CI·PR·deployment·명령/결과 |
|---|---|---|---|---|

로그인 성공·Preview Ready와 전체 흐름 성공을 구분한다. 비밀값·원본 환경변수·토큰 포함 로그를 기록하지 않는다.

## 권한·릴리스 미검증

- observed_permissions:
- unverified_permissions:
- release_only_checks: 실제 보호 branch merge / Production deploy / 최종 G6
- 알려진 보호 정책/수동 승인 요구 / 무인 경로:

## 리소스 원장

| 유형 | 생성 전 namespace | 실제 ID/URL | 소유 run-id 확인 | 정리/보존/실패 | 잔여 영향 |
|---|---|---|---|---|---|

## 조치와 다음 단계

- 부족한 설정과 사용자가 해야 하는 최소 조치:
- 에이전트가 바로 해결 가능한 준비:
- 독립 가능한 검사 / 재실행 대상:
- goal 시작 가능 범위와 근거:
- 독립 검토자·반례·판정:

실행 증거 없는 템플릿은 성공 보고서가 아니다. 원본 임시 리소스/Production 변경 없이 시험했는지 확인한다.

## 실행 준비 세부 증거

- 요청된 설정과 실제 적용 파일/Git/네트워크/설치 권한 차이:
- required check/aggregate gate mapping과 최초 초기 구축 허용 경로:
- 보호된 Preview의 허용 접근 방식·origin 제한·secret 로그 비노출:
- local/CI/배포별 모델 인증 경로(값 제외), 외부 DB 설정 불필요 확인:
- eval split/후보/반복/도구 호출량 추정·실제 quota·최종 평가/G6 여유:
- 조사 원문 접근·실제 가용 모델/agent 슬롯·CI 브라우저 확인:

빈 필드는 준비 완료가 아니다. 계획된 후속 eval 비용과 최소 preflight 기본 동작 검사 성공을 구분한다.

## SQLite 저장 준비

- P06: 실제 sql.js SQL·제약·rollback·export/import 명령과 기대값/관측값:
- P07: Preview origin·WASM/seed hash·쓰기/snapshot/새로고침/역할 전환/reset 결과:
- snapshot 저장 실패와 직전 저장본 복구, export/import 후 외래 키 재설정:
- 임시 SQLite 파일·브라우저 namespace 소유/정리 여부:
- Python 메모리 SQLite 관찰과 P06/P07 실제 검증 구분:
- 한 탭 시연 한계, Preview→Production 간 상태 자동 이전 없음 확인:

## OpenAI API 준비와 예산

- OpenAI API: 로컬/Preview 인증·설정 모델·모드·실제 요청 ID·구조화 출력 판정(키 값 제외):
- OpenAI API 프로젝트·결제/허용 예산·모델 접근·호출 한도·관측 시각·조회 실패/불확실성:
- 남은 필수 평가·G5/G6·데모 계획·예비량·계정 rate limit 적합성:
- `.env.local`/Vercel 서버 설정·정적 점검/live 호출 구분·부족한 설정·다음 검증:
