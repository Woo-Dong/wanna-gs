# 환경 준비·SQLite 운영·배포

현재 기준은 D-43의 한 PC·한 탭 SQLite 데모와 D-44의 OpenAI API 직접 호출이다. 앱 구현·배포·실제 모델 호출은 아직 검증하지 않았다. goal 전에 [18번 사전점검](18-environment-preflight.md)으로 실제 접근을 확인한다.

## 사용자가 준비할 것

| 항목 | 준비 | 확인 |
|---|---|---|
| Codex | 프로젝트 쓰기·설치·네트워크·브라우저·서브 에이전트 실행 권한 | P00 실제 작업. 설정 문구만으로 판단하지 않음 |
| GitHub | 지정 repo·작성자·인증·push/PR/merge·Actions 권한 | 보호 규칙과 초기 workflow 도입 경로 |
| Vercel | 계정·대상 프로젝트·Git 연결·배포 권한 | Preview 자동화 접근과 심사자 접근을 별도로 검사 |
| OpenAI API | 사용자 API 키·모델 접근·API 사용량 한도 | 루트 `.env.local` 및 Vercel Preview/Production 서버 변수, P08 실제 호출 |
| 로컬 런타임 | Node·패키지 관리자·Python 3·테스트 브라우저 | 실제 버전과 lockfile |
| 브라우저 | 한 PC의 일반 브라우저, WASM·IndexedDB 사용 가능 | 파일 사본 저장/복원, 동일 탭 역할 전환 |

외부 DB 계정·Marketplace·DB URL은 필요 없다. 사용자 로그인·최초 약관·조직 인증은 미리 준비한다. Codex/ChatGPT Workspace 인증은 앱 API 키가 아니다. 계정 구매·자동 충전·한도 상향·보호 규칙 해제는 자동으로 수행하지 않는다.

## 모델 환경변수

루트 [.env.example](../.env.example)을 참고해 `.env.local`의 `OPENAI_API_KEY`를 사용자가 입력한다. `OPENAI_MODEL`의 초기 예시는 `gpt-5-mini`, `LLM_MODE`는 `live`다. Vercel Settings → Environment Variables에도 동일한 변수를 등록하고 새 배포를 만든다. 로컬 파일은 Git에 포함하지 않는다. 서버 키에 `NEXT_PUBLIC_`을 붙이지 않는다.

[25번](25-openai-api-and-budget.md)에 정확한 입력 위치·형식·오류 분류·비용 기준을 정리했다. `python3 scripts/check_openai_env.py`는 설정만 확인하고, `--live`를 추가하면 실제 Responses 호출 한 번의 사용량이 발생한다. 연결 성공과 앱의 구조화 출력·자연어 품질 성공은 별개다.

## 초기 환경 검사

1. 실제 저장소·권한·Git/Vercel 대상과 설정을 확인한다.
2. 임시 PR·CI·최소 페이지/API를 Preview로 배포한다.
3. P06에서 실제 sql.js로 SQL·제약·rollback·export/import를 실행한다.
4. P07에서 Preview의 WASM/seed 로드·SQLite 쓰기·IndexedDB 사본 저장·새로고침·역할 전환·reset·저장 실패를 검사한다.
5. P08/P09에서 서버 OpenAI 호출·한국어 구조화 응답·브라우저 적용을 확인한다.
6. 임시 자산을 정리하고 실제 검사와 미실행 항목을 구분해 보고한다.

Python SQLite 성공만으로 WASM 브라우저 검사를 대신하지 않는다. 실제 앱의 200개 이상 상품·업무 통합·자연어 eval은 후속 goal 작업이다.

## DB와 배포 자산 관리

[29번](29-browser-sqlite-demo.md)에 따라 로컬 스크립트가 마이그레이션·seed를 실제 SQLite 파일로 생성한다. 같은 입력에서 서버용 정적 카탈로그와 manifest를 생성한다. 앱·WASM·초기 DB를 Vercel 정적 자산으로 배포하며, 런타임 서버가 이 파일에 거래를 쓰지 않는다.

브라우저 sql.js가 거래 DB를 메모리에서 실행하고 SQLite export 바이트를 IndexedDB에 저장한다. 저장 완료 뒤에 성공을 표시하며 실패하면 마지막 저장본으로 복구한다. schema/seed/build 버전을 검사하고 교체 시 무조건 초기화하지 않는다. 개발·테스트는 파일/브라우저 namespace로 격리한다. Preview와 Production은 origin이 달라 상태를 공유하지 않는다.

reset은 현재 데모 namespace만 대상으로 하며 초기 seed에서 재시작한다. 키·실제 개인정보·holdout 정답을 공개 DB/카탈로그에 넣지 않는다. 앱 rollback이 브라우저 snapshot을 자동으로 복구한다고 가정하지 않는다.

## 릴리스

타입·단위·SQLite 통합·빌드 → Preview의 실제 브라우저/모델 검사 → G5와 정책 감사 → 제출 PR 병합·Production 배포 → 실제 URL의 G6 순서를 따른다. [16번 Git/릴리스](16-git-and-release-workflow.md)의 SHA·CI·배포 증거를 유지한다. DB 서버용 migration job이나 cloud backup은 필요 없다.

G6는 제출 URL의 WASM/seed/catalog 일치·역할 전환·저장/복원·reset·48시간·live OpenAI·키 비노출·심사자 접근을 확인한다. env 변경 뒤에는 새 배포의 설정으로 검사한다. Vercel 배포 Ready만으로 앱 성공을 선언하지 않는다.

## 시간·자동 처리와 인계

데모 clock 하나로 픽업 알림 생성부터 정확히 48시간을 비교한다. 자동발주·재검토·모의 알림은 앱이 열린 동안 실행하고 다시 열면 기한을 재검사한다. 종료 후 서버 작업이나 푸시는 이번 범위가 아니다.

코드·lockfile·마이그레이션·seed 생성/검증 명령·환경변수 양식·실행/초기화/복원 방법·배포 URL·현재 모델/데이터 버전·실제 테스트 증거를 인계한다. 여러 기기/탭 공유나 영구 서버 저장을 구현했다고 설명하지 않는다.
