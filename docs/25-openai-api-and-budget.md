# OpenAI API 설정·검증·사용량

D-45에 따라 앱 LLM은 OpenAI API를 직접 호출한다. Vercel AI Gateway·Gemini 예비 경로와 무료 크레딧 전환 요구(D-31)는 대체됐다. 개발용 Codex/ChatGPT Workspace와 앱의 OpenAI API 인증·사용량은 별개다. API 키는 사용자가 발급·입력하며 실제 접근·잔액·호출은 아직 검증하지 않았다.

## 로컬 입력 위치

현재 clone/worktree 루트의 `.env.local`에 입력한다. 이 파일은 Git에 포함하지 않는다. 저장소의 [.env.example](../.env.example)은 비밀값이 없는 양식이다. 최초 준비에서 `.env.local`이 없으면 복사하고, 이미 있으면 덮어쓰지 않고 필요한 항목만 편집한다.

```dotenv
OPENAI_API_KEY=
OPENAI_MODEL=gpt-5-mini
LLM_MODE=live
```

- `OPENAI_API_KEY`: 등호 뒤에 사용자가 발급한 실제 키를 넣는다. 채팅·문서·명령 인자에 붙여넣지 않는다.
- `OPENAI_MODEL`: 공식 문서에 있는 모델 ID. `gpt-5-mini`는 Responses/구조화 출력을 지원하는 초기 예시이며 사용자 계정 접근·최종 품질을 보장하지 않는다. goal에서 실제 접근과 한국어/구조화 품질을 확인한 모델로 고정한다.
- `LLM_MODE`: `live`는 실제 API, `fixture`는 고정 테스트 응답. 최종 시연·live 품질 평가는 live다. 키가 없다고 자동 fixture 전환하지 않는다.

`export`나 JSON 중괄호 없이 한 줄에 NAME=value를 쓴다. 공백이 포함된 값은 따옴표로 감싸고 중복 키를 만들지 않는다. 키 이름에 `NEXT_PUBLIC_`을 붙이지 않는다. `.env.local`은 `src/` 안이 아닌 프로젝트 루트에 둔다. Next.js 개발 서버 실행 중 값을 바꾸면 재시작한다. [Next.js 환경변수](https://nextjs.org/docs/app/guides/environment-variables).

## Vercel 입력 위치

Vercel 대상 프로젝트 → **Settings → Environment Variables**에 같은 세 변수를 추가한다. `OPENAI_API_KEY`는 서버 비밀값으로, `OPENAI_MODEL`과 `LLM_MODE=live`는 설정으로 입력한다. 실제 검사/제출 대상인 Preview와 Production에 각각 적용하고 로컬 관리가 필요하면 Development도 설정한다. branch별 override가 있으면 실제 배포가 읽는 값을 확인한다.

`.env.local`을 Git에 올리지 않으며 로컬 파일이 Vercel에 자동 전달된다고 가정하지 않는다. 환경변수를 변경한 뒤 해당 환경에 새 배포를 만들고 그 URL에서 다시 검사한다. 같은 이름을 로컬과 Vercel에서 쓰되 키 문자열 자체를 비교 출력하지 않는다. [Vercel 환경변수](https://vercel.com/docs/environment-variables).

GitHub Actions 기본 unit/SQLite/fixture 검사는 API 키 없이 실행한다. live 검사가 필요할 때만 신뢰된 workflow의 repository/environment secret으로 `OPENAI_API_KEY`를 전달한다. 조직 보호 규칙 때문에 CI에 키를 둘 수 없으면 허용된 개발 환경에서 정확한 Preview URL의 live 증거를 만든다.

## 연결 확인

키 입력 전에도 [환경 검사기](../scripts/check_openai_env.py)의 정적 검사는 실행할 수 있다. 누락을 표시할 뿐 연결 성공을 주장하지 않는다.

```bash
python3 scripts/check_openai_env.py
python3 scripts/check_openai_env.py --live
```

기본 검사는 명시된 `.env.local`과 이미 설정된 프로세스 환경변수만 검사한다(프로세스 값 우선). 키 값·길이·접두사·모델 응답 원문을 출력하지 않는다. Next.js의 모든 `.env*` 우선순위를 재현하는 도구가 아니므로 앱/Preview 실호출은 P08에서 별도 확인한다. 설정에 다른 env 파일을 쓰면 `--env-file <경로>`로 지정한다.

`--live`는 `LLM_MODE=live`일 때 OpenAI Responses API에 작은 요청 한 번을 보낸다. API 사용량이 발생한다. 이것은 연결 시험이며 상품 식별 품질·앱 전체 E2E 통과가 아니다. 로컬 키 성공과 Preview/Production 키 성공도 별개다.

| 검사 | 통과 기준 | 실패 시 처리 |
|---|---|---|
| 정적 설정 | 키가 비어 있지 않고 예시값 아님, 모델/모드 유효 형식 | 파일 위치·변수명·빈값 확인. 값 출력 금지 |
| 로컬 live | 실제 Responses 성공·완료·텍스트 출력 | 401 인증, 403 권한, 404 모델/경로, 429 속도/할당량, timeout을 구분 |
| Preview P08 | 서버의 선택 모델 호출·구조화 응답 파싱·오류 처리 | 배포 환경/override/재배포·모델 접근 확인 |
| G5/G6 | 최종 모델 품질·두 역할 흐름·키 비노출·실제 배포 설정 | 기존 모델의 PASS 재사용 금지 |

키 존재·형식·모델 목록 조회만으로 결제 가능·모델 실행·한국어 품질을 PASS로 판정하지 않는다. 검사 출력은 상태·오류 분류·HTTP 상태·사용량 정도로 제한하고 원본 HTTP 오류/헤더는 출력하지 않는다.

## 앱 구현 계약

- Vercel Node.js 서버에서 공식 `openai` SDK·Responses API를 사용한다. SDK는 `OPENAI_API_KEY`를 읽으며 선택 모델은 `OPENAI_MODEL`로 제한한다. 프런트 입력에서 key/model/base URL을 선택하게 하지 않는다.
- 상품 후보·경영주 제안은 JSON Schema 기반 구조화 출력으로 받고 서버에서 파싱·허용 SKU/필드를 검증한다. refusal·incomplete·오류는 성공으로 바꾸지 않는다.
- `store: false`로 응답 저장을 요청하지 않는 구성을 기본으로 한다. 이것만으로 모든 공급자 로그의 보존 정책이 사라진다고 주장하지 않는다.
- 서버의 거래 DB는 없다. 카탈로그는 정적 seed와 같은 버전이며 모델은 변경 제안만 반환한다. 브라우저 서비스가 SQLite 현재 상태·동의·수량·예산을 다시 검사한다.
- 서버 모듈을 클라이언트 번들에 import하지 않는다. health/모델 API 응답과 로그에 키·Authorization·환경변수 덤프를 넣지 않는다.
- 요청 길이·후보 수·출력 토큰·모델 반복·timeout·재시도 상한을 두고, 보호된 시연 접근 또는 앱의 실제 호출 제한을 P08/G6에서 확인한다. 브라우저 단독 카운터나 서버리스 메모리 카운터를 계정 전체 과금 상한으로 설명하지 않는다.

## 비용·한도와 모델 변경

무료 Gateway/Gemini 전환을 준비할 필요는 없다. 사용자가 제공한 OpenAI API 프로젝트의 실제 크레딧·결제 활성·모델 권한·rate limit을 확인한다. 무료 크레딧이 자동 제공된다고 가정하지 않으며 플랫폼 계정 구매·자동 충전·한도 상향은 대신 수행하지 않는다. 소량 사전점검과 사용자가 요청한 앱 호출은 해당 프로젝트의 사용량을 소비한다.

평가 전 baseline 호출량으로 남은 필수 평가·G5/G6·시연 예비량을 추정하고, 각 묶음의 token usage·실패/재시도를 집계한다. 관리 API 권한이 없는 일반 키로 정확한 계정 잔액을 조회할 수 있다고 가정하지 않는다. 사용량 대시보드/프로젝트 제한을 확인할 수 없으면 `unknown`과 로컬 집계 범위를 기록한다. 프로젝트 알림 예산을 확실한 hard stop이라고 가정하지 않는다.

429의 일시적 속도 제한은 제한 재시도, quota/credit 부족은 호출 중단·설정 확인으로 분리한다. 다른 제공자나 fixture로 자동 대체하지 않는다. 선택 실험부터 줄이고 필수 통과 기준·미실행을 숨기지 않는다. 모델 ID를 변경하면 해당 설정의 구조화 출력·자연어 최소 품질·두 역할 E2E·G5/G6 증거를 갱신한다.

## 공식 근거

2026-09-21 확인: [OpenAI quickstart](https://developers.openai.com/api/docs/quickstart), [GPT-5 Mini](https://developers.openai.com/api/docs/models/gpt-5-mini), [Structured Outputs](https://developers.openai.com/api/docs/guides/structured-outputs), [오류 코드](https://developers.openai.com/api/docs/guides/error-codes). 이번 문서의 모델 예시는 계정별 성공 증거가 아니며 키 입력 후 실제 실행으로 확인한다.

## 검사 결과 읽기

`CONFIGURED`는 설정 검사 통과이며 기본 출력은 `live=not_run`이다. `CONNECTED`는 `--live`의 실제 단일 호출 성공이다. 두 경우 모두 `ready_for_goal=false`로 전체 preflight와 구분한다. 종료코드는 0(설정 또는 연결 성공), 2(누락/형식 오류), 3(fixture에서 live 검사 금지), 4(연결/응답 실패)다.

이 검사기는 OpenAI 연결 준비용이므로 fixture여도 키/모델 누락을 MISSING으로 표시한다. 키 없는 fixture 앱/CI의 필수 통과 조건으로 사용하지 않는다. 정적 검사가 사용하는 dotenv 문법은 제한된 부분집합이며 변수 보간·쉘 실행은 지원하지 않는다.
