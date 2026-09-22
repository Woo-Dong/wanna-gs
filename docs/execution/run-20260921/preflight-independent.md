# preflight 독립 코드·로컬 실행 검토

- 검증자: `/root/method_auditor`. app/api/model-probe/route.ts 작성자는 coordinator, 나머지 scaffold 작성자는 preflight_builder이며 검증자는 어느 코드도 작성·수정하지 않았다.
- 대상: `/Users/gsr/Desktop/workspace/2026-ralphton-preflight-20260921`.
- source SHA: `dc81df9005170cde0f48862fac302ae97b7fd202`. 실행 후 `git status --short` 출력 없음.
- consumed_context_hash: `74bf125ebe9c8ed2f7933abb55b08c904400f3a7ba1319c395a2429c32c20679`; scaffold PREFLIGHT.md와 동일.
- 시간: 2026-09-21, 마지막 hash/상태 관측 `2026-09-21T08:39:06Z`.
- 환경: Node 22 LTS `/opt/homebrew/opt/node@22/bin`, Chrome `153.0.8010.50`, Playwright npm exec cache, 한 ephemeral browser context, `http://localhost:3101`.
- 목적: CORE-08/13/17/19, D-44의 실제 브라우저 SQLite 저장·복원·역할 전환 경로를 제품 구현 전에 확인한다. 메모 probe이며 상품/동의/발주/예약 기능은 없다.
- 변경 소유: 이 보고서만. npm exec는 캐시를 사용했으며 package/lockfile 변경 없음. tests/build는 생성 대상 seed/WASM 및 .next를 재생성했고 tracked 파일 변경 없음.

## 판정

**P03의 로컬 scaffold/type/build 및 P06 실제 sql.js 검사 PASS. 로컬 브라우저 저장·오류 복구 검사 PASS.** 배포된 Preview의 P05/P07, 실제 모델 P08, 실제 모델→브라우저 저장의 P09는 이 검증자의 실행으로는 `not_run`이다. 독립 로컬 성공을 remote CI·Preview·live·제품 G1~G6 성공으로 재사용하지 않는다.

## 독립 실행 결과

작성자 결과를 받아 적는 대신 별도 shell로 다음 명령을 실행했다.

```text
PATH=/opt/homebrew/opt/node@22/bin:$PATH npm test
PATH=/opt/homebrew/opt/node@22/bin:$PATH npm run typecheck
PATH=/opt/homebrew/opt/node@22/bin:$PATH npm run build
```

- SQL 테스트: 8 실행, 8 PASS, 0 FAIL, 0 skip, 0 cancel, exit 0. 실제 sql.js seed insert/export/import, reopen FK, 실패 SQL transaction rollback, persist 실패 복원과 정상 재시도, 최초 저장 실패 쓰기 차단, reset generation과 늦은 명령 거절, 실패 reset 보존, idempotency/충돌, 손상 snapshot 거절·복구를 확인했다.
- typecheck: exit 0.
- production build: Next.js 16.3.5 webpack compile/type/static generation 성공, exit 0. `/api/model-probe`는 dynamic, health는 static임을 확인했다.
- HTTP health: 200, scope `preflight-only`, schema `probe-v1`, seed `20260921-v1`, database `browser-sql.js`, model `not-checked`.
- 무토큰 POST `/api/model-probe`: 401 `UNAUTHORIZED`. 실제 모델은 호출하지 않았다.

원본 shell 결과는 이 task의 exec 출력에 남는다(SQL/type session 67447, build session 11679). Playwright는 아래 기대값을 코드와 독립적으로 도출한 assert 기반 inline runner로 실행했다. 대상 앱 파일을 수정하거나 앱 상태를 성공으로 덮어쓰지 않았다.

## 실제 브라우저 + IndexedDB 바이트 대조

Playwright `chromium.launch({channel:'chrome',headless:true})`로 별도 context를 만들었다. DOM 행동은 label/button/heading으로 수행했고, IndexedDB `wanna-gs-preflight-20260921`의 `snapshots/current` 바이트를 읽어 SHA-256을 비교했다. UI count만으로 PASS를 부여하지 않았다.

| 순서 | 관측·독립 기대값 | 결과 |
|---|---|---|
| 최초 진입 | 메모0, FK 켜짐, 실제 SQLite format 3 header, 28,672 bytes | PASS |
| 고객 메모 저장 | count1, seed와 다른 SQLite snapshot hash | PASS |
| 경영주 역할 전환 | 경영주 화면에서 같은 고객 메모 표시 | PASS |
| 새로고침 | count1, 저장 전후 snapshot hash 정확히 같음 | PASS |
| 다음 저장 실패 시험 | 실제 IndexedDB readwrite transaction abort, STORAGE_FAILED_TEST, count1, 기존 snapshot hash 정확히 같음 | PASS |
| 일반 재시도 | count2, snapshot hash 변경 | PASS |
| 명시 reset | count0, generation 0→1, SQLite bytes가 seed hash와 같음 | PASS |
| reset 후 새로고침 | count0, generation1 유지 | PASS |
| 잘못된 접근 토큰으로 모델 입력 | UNAUTHORIZED 표시, count0, SQLite bytes 불변, 실제 모델 호출 없음 | PASS |

이 실행에서 pageerror는 0이었다. 실제 서버 live 응답을 대체하는 mocked 성공 응답은 사용하지 않았다.

관측 fingerprint:

```text
seed/reset SQLite sha256
6b1b713977bc0dfddaa08a63a0dad756249e8f4b267bb0565e3e2f6f952a2f7e
첫 고객 메모 저장 SQLite sha256
92c0a1e5e7c368ec1f1502bbd1935d8f5ebd872bd9a99948b528e9ec1219f591
browser=153.0.8010.50
seed generation=0, reset generation=1
pageErrors=[]
```

추가로 별도 browser context에서 snapshot bytes를 `[1,2,3]`으로 손상시킨 후 새로고침했다. 앱은 명시 오류와 쓰기 차단을 표시했고 자동 덮어쓰지 않았다. 사용자의 명시 초기화 후 정상 메모 추가가 다시 성공했다. 이 오류 복구 검사는 exit 0/PASS이며 다른 context나 사용자 시연 DB는 건드리지 않았다. browser context를 닫아 테스트 전용 상태를 폐기했다.

브라우저 원본 결과는 exec session 97584(정상/실패/재시도), 84164(손상 복구)에 있다. 재현 도구 경로는 `/Users/gsr/.npm/_npx/e41f203b7505f1fb/node_modules/playwright/index.mjs`다. 별도 다운로드 중인 Playwright bundled Chromium은 이 결과에 사용하지 않았다.

## 코드 검토

읽은 대상: PREFLIGHT.md, package.json, app/page.tsx, app/api/health/route.ts, app/api/model-probe/route.ts, public/probe/core.mjs·worker.js, scripts/build-seed.mjs, tests/sqlite.test.mjs, .github/workflows/preflight.yml.

- 실제 SQL은 Worker에서 실행하고 server route는 OpenAI 모델만 호출한다. 임의 SQL/URL/model/token 수를 외부 입력으로 실행하는 경로가 없다.
- add는 SQL commit 뒤 export/persist 성공을 기다리고, 실패하면 마지막 내구 snapshot을 다시 연다. reopen/export 후 FK 활성화를 수행한다. reset은 저장 성공 뒤 generation을 갱신한다.
- 단일 Worker queue가 명령을 직렬화하며 core는 중복 ID 동일 payload와 ID_CONFLICT를 구분한다. UI 모델 응답에는 request 번호와 generation 검사가 있다.
- seed SHA-256을 manifest와 대조하고 schema/seed/integrity/FK를 검사한다. 상품 seed가 아니라 메모 시험용 seed다.
- 모델 route는 timing-safe access token 비교, 서버 전용 환경변수, 고정 모델/토큰, 무재시도·45초 제한, 구조화 출력·status 검사, instance당 6회 제한, cache no-store를 사용한다. instance limit은 계정 전체 사용량/분산 비용 한도가 아니며 UI도 그 제한을 명시한다.
- CI는 지정 preflight branch에만 반응하며 contents read 권한으로 npm ci/check를 실행한다. 실제 원격 CI 실행과 PR merge 결과는 여기서 검증하지 않았다.

이 범위에서 로컬 preflight를 막는 코드 결함을 발견하지 않았다. 다만 route text 입력은 길이만 검사하므로 공백-only 직접 API 요청도 권한이 있으면 호출에 들어갈 수 있다. UI는 trim으로 막고 token을 가진 소량 probe 경로라 이번 저장/복원 증거를 무효화할 결함은 아니지만, coordinator가 P08 invalid-input 검증에서 trim 기반 INVALID_INPUT을 기대한다면 명세/구현을 맞춰야 한다. 제품 입력 검증의 기준으로 이 단순 probe를 그대로 재사용하지 않는다.

## source fingerprint

```text
app/page.tsx ba42d4f6fb524034f21c2cde9fc500604f803c956322ab8505c7b9caa242b4c6
app/api/model-probe/route.ts 1a7157e5be6e522a3e0208b79d69eaae90da6ba0aba7e985f68b57d2ee0a0320
public/probe/core.mjs 953767e7d781a968446265fd6cf2c6e2adcf7b6b9a77dea1df96b487f493ffff
public/probe/worker.js d9a77c60e850acfa99261923aca3a1ec93c476f132810d4e0a69d4c2ad2b73d1
tests/sqlite.test.mjs 650a4797fc5f1c99760f3933f016ab0546909eb10bf01a96b6b7d390ad2370cf
.github/workflows/preflight.yml ac20694a74d887a7bf7eaad2af44cac5b36fff0aa49afeace655c6636ca4901e
```

## 남은 검사

coordinator가 실제 PR/CI/source SHA·Preview URL/ID를 연결하고 local/Preview live 모델 최소 호출을 확인해야 한다. Preview 한 탭 저장·복원 및 모델→SQLite P09의 브라우저 동작도 해당 exact deployment에서 실행해야 한다. 이 보고서는 그 결과 없이 전체 preflight READY를 부여하지 않는다. 제품 자동발주·동의·FIFO·48시간·200개 상품·두 역할 UX QA와 G1~G6는 이 scaffold 범위 밖이며 모두 별도 구현·검증 작업으로 남는다.

## 후속 독립 Preview P07/P09 — PASS

이 절은 위 로컬 검사 이후 추가 실행한 결과다. 이전 절의 Preview/live `not_run`은 그 시점의 상태이며 아래 대상에 한해 갱신한다. coordinator가 알려준 배포 target=null/READY 및 source 메타데이터를 입력으로 받았고, 이 검증자는 정확한 URL의 health와 실제 브라우저/모델/SQLite 행동을 실행했다.

- 대상 URL: https://wanna-xcymomq9m-beatrain-4635s-projects.vercel.app
- deployment: `dpl_HjgwxK7oQCwRuoG48SUZF7XE9h3t`; 연결된 source `dc81df9005170cde0f48862fac302ae97b7fd202`.
- health: 보호 bypass로 200 및 기존 preflight-only/schema/seed 응답 확인.
- browser: Chrome 153.0.8010.50, 별도 ephemeral context, pageerror 0.
- 접근 보호: 파일에서 읽은 bypass를 정확한 Preview origin의 request header에만 주입. 외부 origin에는 전달하지 않음. token·bypass 값·trace·request header를 출력하거나 증거 파일에 저장하지 않음.
- 모델 호출: coordinator의 명시 요청으로 실제 live 1회만 실행. 무권한 오류 요청 1회는 API 호출 전 401.

P07: 실제 Preview에서 고객 메모 저장→경영주 전환→새로고침 바이트 동일→실제 IDB abort와 기존 바이트 동일→정상 재시도→reset seed bytes와 generation1→새로고침 유지 모두 PASS. 최초/초기화 SQLite SHA-256은 `6b1b713977bc0dfddaa08a63a0dad756249e8f4b267bb0565e3e2f6f952a2f7e`다.

P09: password 필드에 메모리로 접근 토큰을 입력하고 “원하지쓰 연결을 확인해주세요.”를 실제 서버 모델에 보냈다. HTTP200, mode=live, ok=true 응답 뒤 화면 메모1 및 IndexedDB snapshot을 확인했다. 그 snapshot bytes를 별도 Node sql.js reader로 열어 `SELECT body FROM notes` 결과가 실제 model response.message와 정확히 같음을 assert했다. 새로고침 후 동일 snapshot hash와 count1을 확인하고 접근 토큰 입력은 빈 값임을 확인했다. 이어 잘못된 token 오류 입력은 401/UNAUTHORIZED로 표시되며 count1·snapshot hash가 유지됐다.

```text
returned model: gpt-5-mini-2025-08-07
live calls: 1
input tokens: 87
output tokens: 42
total tokens: 129
reasoning tokens: 0
model SQLite snapshot SHA-256:
70e2982191b0316c8e85ea416b6affae2adb1ddfa801d130ca5039574f57cfed
pageErrors: []
result: PASS
```

원본 결과는 exec session 38860에 남는다. 증거 스크린샷은 `artifacts/private/run-20260921/preflight-preview-independent.png`에 저장하고 시각 검토했다. 저장 전에 token 필드를 비웠으며 추가 mask도 적용했다. 실제 모델 확인문, 메모1, generation1, FK 켜짐을 볼 수 있다. 응답 확인과 저장 완료를 별도 상태로 표시한다. 제품 고객/경영주 E2E 또는 G4/G6 증거는 아니다.

첫 배포의 Production 오분류·삭제 및 최종 Preview target 판별은 coordinator의 remote ledger 검증 범위다. 이 독립 결과만으로 그 사건이 없었다고 하거나 P11/Production 불변 전체를 PASS 처리하지 않는다. 목표 READY 집계에는 원격 PR/CI·최종 resource ledger·cleanup/보존 영향 검토가 여전히 필요하다.

후속 config 검토: `git show 9e0f12f4eaf6bd7813cd2514e3422bea6f8764b5`에서 변경은 vercel.json 1개 추가(`git.deploymentEnabled:false`)뿐임을 확인했고, dc81df9 대비 app/public/scripts/tests/package/lock/workflow diff는 비어 있었다. 기존 Preview의 runtime 증거는 동일 코드 증거로 유지할 수 있지만 이를 새 head 배포/source 증거로 바꾸지는 않는다. 새 head CI·임시 base merge와 자동 배포 차단의 실제 remote 효과는 coordinator의 후속 P04/ledger 확인 대상이다.
