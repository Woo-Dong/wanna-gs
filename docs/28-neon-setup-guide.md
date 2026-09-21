# Neon 계정 이후 연결 가이드

기준일: 2026-09-21. 사용자가 **Neon 계정 생성 완료**를 알렸고 아래 대상을 포함한 후속 안내를 제공했다. 이 문서는 안내를 기존 아키텍처에 맞춰 정리한 것이며 명령을 실행한 결과가 아니다.

| 항목 | 현재 확인 수준 |
|---|---|
| 계정 생성 | 사용자 완료 보고 |
| 프로젝트 ID | 사용자 제공 `green-unit-60810095` |
| 브랜치 이름 | 사용자 제공 안내의 `production`; 실제 존재·ID·역할 미검증 |
| CLI/MCP 인증·프로젝트 접근 | 미검증 |
| 개발/test/Preview 격리·DB URL | 미검증 |
| 로컬/배포 DB 왕복·migration·seed | 미실행 |

프로젝트 ID는 접속 비밀번호가 아니다. DB 연결 문자열·API 키·OAuth 자격증명은 문서나 채팅에 저장하지 않는다. 프로젝트가 이미 있으므로 새 계정을 만들거나 프로젝트를 중복 생성하는 것부터 시작하지 않는다.

## 이 프로젝트에서 사용할 범위

- **Vercel:** Next.js FE·BE와 제출 URL.
- **Neon:** PostgreSQL 및 필요한 DB 관리 경로.
- **Vercel AI Gateway / Gemini 직접 호출:** 기존 D-31의 앱 LLM 경로.
- **Neon CLI/MCP/skills:** 개발 도구의 선택지. DB 연결 자체나 앱 런타임의 필수 의존성으로 모두 설치할 필요는 없다.

Neon의 `aiGateway`는 Vercel AI Gateway와 다른 서비스다. 공식 플랜 자료는 Neon AI Gateway를 유료 플랜 대상으로 안내하므로 이번 무료 우선 기준선에는 활성화하지 않는다. Neon 계정 생성은 앱 LLM 인증이나 크레딧 준비 완료를 뜻하지 않는다. [Neon 공식 플랜 문서 원문](https://github.com/neondatabase/website/blob/main/content/docs/introduction/plans.md).

## 전달받은 일곱 단계의 적용 판단

| 원 안내 | 원하GS에 적용할 방법 |
|---|---|
| 1. CLI 설치·로그인 | 사용할 관리 경로가 CLI일 때 준비. 공식 안내의 `neon auth`를 기준으로 하고 `login` 별칭은 설치 버전 도움말 확인 |
| 2. `neon skills -y` | 선택. 필요한 Neon/Postgres 지침만 설치하고 기존 프로젝트 지침과 변경 파일 확인 |
| 3. `neon mcp -y` | 선택. 대상 에이전트·설정 위치·인증 범위를 먼저 지정. 이미 연결된 관리 도구가 있으면 중복 설치하지 않음 |
| 4. production link | 제공받은 프로젝트/브랜치 확인에 활용. 개발·파괴적 테스트의 기본 DB로 사용하지 않음 |
| 5. `neon config init` | Neon 서비스의 설정 코드가 필요한 경우만 수행. PostgreSQL 접속만을 위한 필수 단계가 아님 |
| 6. `neon.ts` | `preview`의 서비스 키는 현 공식 패키지에서 deprecated 안내. 주석 처리된 aiGateway는 활성화 지시가 아님 |
| 7. `neon deploy` | Neon 구성 적용. Vercel 배포·업무 테이블 migration·seed·E2E 완료와 별개. 이번 DB 전용 경로에서 기본 실행하지 않음 |

명령/옵션은 실행 시 설치 버전 도움말과 대조한다. 일부 Neon docs 경로는 조회 도구가 Markdown 응답을 처리하지 못해, 아래 공식 CLI·설정 패키지 원문과 공식 블로그로 보완했다. [CLI 변경 안내](https://neon.com/blog/just-landed-in-the-neon-cli), [설정 패키지](https://raw.githubusercontent.com/neondatabase/neon-pkgs/main/packages/config/README.md).

## 1. 계정과 프로젝트 접근 확인

현재 clone/worktree 루트에서 진행한다. 아래는 **설정할 때 사용할 예시이며 이번에 실행하지 않았다.**

```bash
git rev-parse --show-toplevel
node --version
npm i -g neon@latest
neon --version
neon auth
neon link --help
```

공식 CLI는 Node 20.19 이상, skills 명령은 22.20 이상을 요구한다고 안내한다. 사용할 앱·도구 전체를 지원하는 Node 버전을 준비하고 실제 CLI 버전을 기록한다. 초기 설치 뒤 매 goal 반복마다 latest로 갱신하지 않는다. `neon auth`는 브라우저에서 사용자 인증을 거치는 사전 준비 단계다. [공식 CLI 원문](https://raw.githubusercontent.com/neondatabase/neon-pkgs/main/packages/cli/README.md).

인증 후 제공받은 프로젝트를 조회해 소유 조직·접근 권한·리전·플랜·브랜치 이름/ID를 확인한다. 이름이 다르거나 권한이 없으면 비슷한 다른 프로젝트를 선택하거나 `production` 브랜치를 새로 만들어 맞추지 않는다. 실제 확인 결과를 P00/P06에 기록한다.

## 2. Production 확인과 개발 연결을 구분

원 안내의 연결 대상은 다음과 같다. 환경변수를 바로 가져오지 않도록 옵션을 보완했다.

```bash
neon link --project-id green-unit-60810095 --branch production --no-env-pull -y
```

이 명령도 로컬 연결 포인터를 production으로 바꾸므로, 실행했다면 이후 명령의 대상이 무엇인지 다시 확인한다. 프로젝트에 연결했다는 사실을 테스트 DB 격리 완료로 표시하지 않는다. 이후 개발용 연결은 실제로 확보한 브랜치를 대상으로 한다.

```bash
# 실제 존재·권한·용도를 확인한 값으로 교체한다.
neon link --project-id green-unit-60810095 --branch '<검증한 개발 브랜치 이름 또는 ID>' --no-env-pull -y
```

독립 DB branch 또는 동등하게 격리한 schema/DB를 08/18번에 따라 마련한다. 무료 한도·현 자원 수를 확인하고 브랜치 수를 무제한 늘리거나 유료 전환하지 않는다. Production과 같은 자원 안의 schema를 쓰는 경우에는 전용 role·search_path·migration/reset 범위를 검증해야 격리로 인정한다.

CLI의 `.neon`은 로컬 포인터이며 상위 디렉터리의 설정도 탐색한다. `link`는 브랜치를 지정하면 기본적으로 환경변수를 가져올 수 있다. 새 clone/worktree에서 이전 디렉터리의 대상이나 DB URL을 상속했다고 가정하지 않는다. `.neon`과 `.env*`는 비공개 로컬 설정으로 관리한다. [공식 branch/env 안내](https://neon.com/blog/branch-first-dev-loop).

각 환경의 실제 연결 대상은 다음처럼 기록한다. 비밀 URL 대신 프로젝트/브랜치 ID·DB/schema·role 식별자와 검사 시각을 남긴다.

| 실행 환경 | 연결 목적 | 통과 조건 |
|---|---|---|
| 로컬 개발 | 개발 데이터·migration/seed | 제출 자원과 격리, 현재 작업 대상 확인 |
| CI/test | 재현·동시성·rollback 검사 | 허용된 테스트 범위만 쓰기/정리 |
| Vercel Preview | 두 역할 E2E | Preview 전용 연결, 제출 데이터 reset 불가 |
| Vercel Production | 최종 데모 | G5/G6의 배포·schema·seed와 연결 |

이 표는 브랜치 네 개를 반드시 생성하라는 뜻이 아니다. 동등한 격리 방법과 무료 범위 안에서 실제 구조를 기록한다.

## 3. DB 연결 문자열 주입

Neon Console 또는 검증한 CLI 경로로 선택 DB의 연결 정보를 얻어 로컬 비밀 파일과 Vercel의 해당 환경에 넣는다. `DATABASE_URL`은 서버 전용이다. 클라이언트 번들·로그·스크린샷·리뷰 diff에 노출하지 않는다. CLI 관리 인증과 PostgreSQL 접속 인증은 별개로 검사한다.

앱용 pooled URL과 migration 도구가 요구하는 직접 연결을 구분한다. `DATABASE_URL_UNPOOLED`를 쓰는 도구를 택하면 이름 매핑을 명시하고, CI용 `DATABASE_URL_TEST`도 필요에 따라 별도 설정한다. 현재 driver/migration 도구의 잠금·트랜잭션 동작을 실제 시험한다. URL이 존재하거나 단순 SELECT가 성공했다는 이유만으로 이 검증을 생략하지 않는다.

로컬 `.env`가 Vercel이나 GitHub Actions에 자동 전달되지는 않는다. Neon/Vercel 연동을 이용하는 경우도 실제 Preview/Production별 연결을 확인한다. 배포 서버가 DB를 읽고 쓰는 P07까지 끝나야 서버 연결 성공이다.

## 4. 선택: Neon skills와 MCP

기존 도구만으로 DB 작업을 할 수 있으면 추가 설치 없이 진행할 수 있다. 선택해 설치할 경우 Codex·Neon/Postgres에 범위를 맞춘 예시:

```bash
neon skills -s neon -s neon-postgres --agent codex -y
neon mcp --project --agent codex --oauth --project-id green-unit-60810095
```

명시적인 MCP 옵션은 무인 기본값의 전역 설치·API 키 생성과 구분하기 위한 것이다. OAuth 최초 연결은 사용자가 준비 단계에서 완료한다. MCP 연결 후 해당 에이전트 세션에 실제 도구가 보이고 프로젝트를 조회할 수 있는지 확인한다. 설치 파일이 있다는 사실만으로 무인 접근 성공을 판정하지 않는다.

공식 안내에 따르면 단순 `neon mcp -y`는 전역 설정과 키 재사용/생성을 선택할 수 있다. 새 키의 프로젝트 범위와 기존 인증의 권한은 같다고 가정하지 않는다. 기존 연결·비밀값을 출력하지 않고 설정 범위를 확인한다. [Neon 공식 CLI 배포 문서](https://www.npmjs.com/package/neon).

설치된 외부 skill은 DB 작업의 참고이며 card/CORE·현재 권한·비용·릴리스 규칙을 바꾸지 않는다. 설정·skill 설치가 만든 파일 목록과 Git diff를 확인하고 인증값은 커밋하지 않는다. MCP는 개발 에이전트용이며 공개 앱의 상품 검색이 이를 직접 호출하는 설계로 바꾸지 않는다.

## 5. 선택: neon.ts와 Neon 구성 적용

현재 기준선에서는 Neon Auth·Data API·Functions·Object Storage·Neon AI Gateway를 추가할 필요가 없다. 따라서 `neon config init`과 `neon deploy`를 기본 준비 체크에서 생략해도 된다. 이 명령의 부재를 preflight 실패로 판단하지 않는다.

추후 구성 코드가 필요해질 때만 init의 서비스 선택과 package/lockfile 변경을 검토한다. 새 추가 서비스를 선언하지 않는 개념 예시는 다음과 같다. 이번에는 파일을 만들지 않았다.

```ts
import { defineConfig } from "@neon/config/v1";

export default defineConfig({});
```

빈 구성은 기존 원격 서비스를 전부 끈다는 의미가 아니다. 기존 `neon.ts`가 있으면 덮어쓰지 않고 현재 정의와 대상 branch를 읽는다. `preview`라는 키를 Vercel Preview 환경 분리 장치로 해석하지 않는다. 현재 패키지에서는 서비스 선언을 최상위에 두며 기존 preview 키를 deprecated로 안내한다. [공식 구성 계약](https://raw.githubusercontent.com/neondatabase/neon-pkgs/main/packages/config/README.md).

원격 구성을 변경할 필요가 생기면 정확한 프로젝트/branch를 고정해 status와 plan을 확인한 뒤, 기존 승인 범위의 필요한 변경만 apply/deploy한다. `neon deploy`는 `neon config apply`의 별칭이다. 무조건 실행하는 초기화 단계로 두지 않는다. 업무 테이블 migration/seed는 별도 저장소 코드로 관리하며 앱 배포는 계속 16번 Vercel 흐름을 따른다. [공식 CLI 구성 명령](https://raw.githubusercontent.com/neondatabase/neon-pkgs/main/packages/cli/README.md).

## preflight에 남길 결과

- 계정 완료 보고 / 인증 실제 관측 / 프로젝트·branch 확인을 구분한다.
- P00: CLI/connector/MCP 중 실제 관리 경로, 버전·권한·로컬 설정 위치 확인.
- P06: 격리 DB의 migration·write/read·rollback·경합 검사와 정리 증거.
- P07: 실제 Vercel Preview 서버의 DB 왕복, 서버 비밀값 미노출.
- 플랜·리전·한도·기존 데이터·분리 방식·현재 target ID를 기록한다.
- 미실행은 not_run/PARTIAL, 실제 필수 접근 차단은 BLOCKED로 보고한다. READY는 18번 전체 조건에 따른다.

이번에는 계정 완료 사실과 공식 안내 검토만 반영했다. 로그인·skills/MCP 설치·link·config 생성·deploy·DB 변경은 실행하지 않았다.
