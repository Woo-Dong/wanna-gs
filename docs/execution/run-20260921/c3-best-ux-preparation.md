# C3 best UX 24회 실행 준비 — 읽기 전용

2026-09-21, preflight_builder. **실행 승인 파일이 아닌 준비 기록**이다. 모델 호출 0, 브라우저 실행 0, ledger 쓰기 0, 앱/계측기/CI 변경 0. C3 dev/validation 합격 여부는 이 조사에서 판정하지 않는다. CORE-13/17/21/23/25와 ADR-003/006을 유지한다.

## 판정

현재 계측기 그대로 remote Preview에서는 실행 불가다. `run.mts:9`가 localhost/127.0.0.1만 허용하며 `live.mts`에는 Vercel bypass 주입 기능이 없다. 조정자 지시에 따라 계측기를 변경하지 않는다. **동일 C3 소스로 만든 로컬 production build + 명시적 서버 환경 + 별도 포트**는 기존 실행기 계약에 맞는 경로다. 이는 로컬 best 절대 기준 측정이며 Preview/G6 또는 두 역할 독립 live QA의 대체 증거가 아니다.

B0 원본과 ADR-006 재측정은 모두 incomplete다. 추가 B0 실행 권한은 없다. best 24/24가 성공해도 baseline 대비 회귀 비교는 NOT_READY이며, 두 실패 원본의 행을 섞어 완성된 baseline을 만들지 않는다.

## 확인한 C3 대상과 소스

- Preview 기록: `dpl_EK3hT5PniMZihubk9Z3csF7VUxGx`, `https://wanna-krv43ok6h-beatrain-4635s-projects.vercel.app`, READY, branch `codex/n04-model-candidate`, SHA `55f92fe107694d0e570135362321d35d47131343`. 기존 private proof JSON을 읽었으며 새 네트워크 조회는 하지 않았다.
- `n04-c3-config.json`의 source_files 28개와 현재 root 파일의 SHA256를 직접 대조: **28/28 일치**. 이 선언 집합은 full runtime inventory와 별개다. 실행 전 G5 runtime 전체 집합과 후보 binding도 별도로 동결해야 한다.
- 해당 config: model `gpt-4.1-mini-2025-04-14`, prompt `packed-refs-v4`, catalog hash `f2696abe92521e3ff8f9ab43cb36a1d297a6fd23d272e239605b49fab4343b1e`.
- root `.next/BUILD_ID` 읽기값: `MPD63_Lk7ojfotRHD1cWx`. 조정자는 C3 소스로 방금 build했다고 보고했다. BUILD_ID 자체는 source attestation이 아니므로 빌드 명령·동결 소스·프로세스 시작을 함께 기록해야 한다.
- 기존 localhost:3217 / session19063은 B0 서버라는 조정자 인계다. 현재 디스크 `.next`가 C3라고 해서 이미 실행 중인 B0 프로세스를 C3라고 판단하지 않는다. 그 포트를 재사용하지 않는다.

## 계측기와 SQL 증거 확인

현재 5파일 SHA가 B0 원본과 복구 결과 양쪽의 harnessHashes와 일치한다.

| 파일 | SHA256 |
|---|---|
| run.mts | 1242a81bcc40b99b80b5fa4727e5c0f0ee0a899ab80f9d304349c80a01d8b825 |
| seed.mts | a62dde6e62b70f47f870d42b9d4ced35477cfe0bc760a248582e8144adb9ee9e |
| metrics.mjs | a73ee753ad73804241f64d8315758af736adf03c27a384be752e1189dad4ec54 |
| live.mts | a5b201b949b6d2405e4819fff65a3d54065a9b3a30949ec4a61814b347be9221 |
| budget_bridge.py | 875f22a63091c6a406891b3e55549afd5dc1eff1b61b9f79baf5a505f253fe7b |

seed SQLite hash는 `4cb10e899c9706bb0a9278b458bd7b70d3c34bf28f649b62ffae0894794a2b45`, 두 B0 원본 workloadHash는 `613bbb701a155913f02f2de4bf6f45fef793b1d3fa5e61cd5a5211a25e32d71d`다. 같은 계측기·seed·선택상품·clock을 보존한 실행에서 재계산값을 대조한다. 결과의 hash를 수동 대입하지 않는다.

각 run은 로컬 DomainEngine으로 **준비에 한해** 합성 시나리오를 만들고 새 브라우저 context의 IndexedDB에 SQLite envelope를 넣는다. 준비 engine/contract와 app-root 파일 hash를 먼저 확인한다. 평가 경로는 실제 UI activation이며 실제 Worker/sql.js가 거래를 처리한다. 화면 저장 성공 뒤 IndexedDB bytes를 다시 sql.js로 열어 integrity/FK, 요청 SKU·수량·동의 가격/버전/만료, 발주/line/중복 알림을 검증하고 durableHash를 기록한다. 이것은 한 탭 실제 SQLite 검증이며 서버 거래 DB나 다중 사용자 검증이 아니다.

clock은 페이지 및 계측 Worker의 Date.now를 `2026-09-21T03:00:00Z`로 고정하고 첫 snapshot에서 동일함을 assert한다. performance/timer와 서버 모델 시간은 실제 경과시간이다. 화면/의사결정/질문 수와 모델 HTTP 대기, 예산 bridge 시간은 분리 기록한다. 8종 × 반복 1/2/3 고정 분모, 중복·누락 검사는 그대로 유지한다.

정상 경로의 모델 호출은 clear 3종×3 = 9, ambiguous 2turn×3 = 6, auto 1turn×3 = 3으로 합계 18이다. 재동의/10SKU 묶음/예외 묶음은 SQL·UI 흐름으로 모델을 호출하지 않는다. 따라서 이 측정의 경영주 workload 성공만으로 **경영주 live 자연어 API** QA를 완료했다고 표현하지 않는다.

## 실행 전 동결과 로컬 시작안

1. 조정자가 C3 선택 조건과 실행 예산을 확인하고 best run_id 하나·출력 폴더 하나를 승인한다. 다른 NL/QA 모델 호출과 직렬 실행한다.
2. 전체 app runtime inventory, 후보 source28, 서버 model profile/prompts/catalog, seed/schema/WASM, 계측기5파일, budget runner 및 bridge, npm lockfile, build 로그/BUILD_ID를 동결한다. `run.mts`의 sourceFiles는 15개 UI/domain 계약만 기록하므로 서버와 runtime 전체 source 증거는 별도 실행 보고서가 필요하다.
3. root production build가 동결 후보와 연결됐음을 확인한다. 별도 빈 포트를 조정자가 선택하고 동일 디렉터리에서 새 Next production process를 시작한다. 아래 `<fresh-port>`는 실제 승인값을 넣는 계획 표기이며 여기서는 실행하지 않았다.

```sh
PATH=/opt/homebrew/opt/node@22/bin:/Users/gsr/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin:$PATH \
OPENAI_MODEL=gpt-4.1-mini-2025-04-14 LLM_MODE=live \
npm run start -- --hostname 127.0.0.1 --port '<fresh-port>'
```

기존 root `.env.local`의 서버 API key를 사용하고 값을 출력·복사하지 않는다. 셸의 model/mode를 명시하고 기존 파일을 수정하지 않는다. key 로딩과 실제 응답 model은 실행 담당자가 확인해야 하며, 값 존재만으로 실제 호출 성공을 선언하지 않는다. 서버 PID/세션/포트/시작시각과 build/source를 함께 남긴다. 프로세스 생존 동안 같은 `.next`를 rebuild하지 않는다. 준비 상태 확인 GET에는 모델 호출을 넣지 않는다.

4. 동일 root를 app-root로 사용하고 UI origin을 config와 정확히 일치시킨다. 로컬 경로에는 bypass가 필요 없다. 실제 원격 Preview의 same-origin bypass는 별도 역할 QA 기구가 담당하며 현 UX 실행기를 임의로 확장하지 않는다.

```sh
# 조정자가 경로와 권한을 확정한 뒤 실행할 템플릿; 현재 미실행
PLAYWRIGHT_MODULE='<existing-absolute-playwright-module>' \
CHROMIUM_EXECUTABLE='/Applications/Google Chrome.app/Contents/MacOS/Google Chrome' \
node --import tsx tests/ux-benchmark/run.mts \
  --app-root /Users/gsr/Desktop/workspace/2026-ralphton \
  --url 'http://127.0.0.1:<fresh-port>' \
  --live --budget-config '<approved-private-config-path>' \
  --output '<new-private-output-directory>'
```

앞 명령과 같은 Node22/Python runtime PATH를 적용한다. 실제 응답이 그대로 UI로 전달되고 `budget_bridge`가 model/prompt/catalog/known usage를 검사한다. 첫 유료 검증을 별도로 추가하면 18회 외의 승인·장부가 필요하므로, 무승인 smoke를 끼워 넣지 않는다.

## 최소 config 및 예산 계산

아래는 실행용 JSON 파일이 아닌 **필드 계약**이다. `approved`는 여기서 발급하지 않는다.

| 필드 | 확정할 값 |
|---|---|
| approved | 조정자만 true로 승인 |
| run_id | 한 번만 사용할 새 ID; 과거 run/claim 재사용 금지 |
| stage | best |
| prior_call_reserve | 50 |
| authorized_calls | 정상 고정경로 18; 자동 재시도 0 |
| origin | http://127.0.0.1:승인한새포트, path/query/trailing slash 없음 |
| model | gpt-4.1-mini-2025-04-14 |
| prompt_version | packed-refs-v4, 실행 직전 고정 후보와 재대조 |
| catalog_hash | f2696abe92521e3ff8f9ab43cb36a1d297a6fd23d272e239605b49fab4343b1e |
| mandatory_reserve | 이 UX 이후 **남아 있는** 필수 단계별 호출수. 빈 object는 거절되므로 필요시 명시적 0 항목 유지 |
| mandatory_cost_reserve_usd | 위 후속 필수 단계의 최신 보수 비용 예약. 현재 UX 18회는 bridge가 별도 예약하므로 중복 합산하지 않음 |

장부는 app-root `artifacts/private/run-20260921/nl-budget.json` 단일 파일이며 bridge는 기존 Budget을 prior50으로 호출한다. `begin`이 run claim을 쓰므로 단순 준비 확인에도 실행하지 않는다. 매 outbound 전 reserve, 완료 후 finish, provider/usage 불명 또는 HTTP/model 오류면 stop; pending 불명확 상태에서 재전송하지 않는다.

호출 직전 장부 상한을 U, 비용 상한을 C, 후속 필수 호출수를 R, 후속 비용 예약을 F라 하면 첫 호출 조건은 `U + 18 + R <= 2400`, `C + 18×$0.05 + F < $15`다. 현재 UX 잔여 authorized calls를 bridge가 각각 $0.05로 예약한다. 18×$0.0105로 줄여 계산하는 코드는 아니다. 계정 hard cap 보장도 아니다.

읽기 시점 장부는 U=535, C=$4.7035897, pending0, prior50였다. C3 config에는 후속 예약 552+276+72+60=960, 비용 $10.08(호출당 $0.0105)이 있었다. 이는 C2의 이전 960×$0.009=$8.64와 구분한다. 이 값을 그대로 복사하면 현재 UX 중복 예약으로 비용 검사에서 막힐 수 있다. 예를 들어 **아직 완료한 필수 단계가 없다는 보수적 가정**에서 기존 UX72를 지금18로 대체하고 나머지888×$0.0105=$9.324를 F로 남기면 당시 비용 합은 $14.9275897, 호출 합은1441이다. 이는 그 순간 조건부 산술 예시이며 이후 validation/holdout 진행과 장부 변화에 따라 다시 계산해야 한다. 남은 필수 작업을 근거 없이 제거해 통과시키지 않는다.

## 완료 보고와 남는 제한

실행자는 원본 result.json/행별 실패·미실행/usage/스크린샷/budget-final/서버 로그를 보존하고 24개 denominator, 18개 정상경로 예상 대비 실제 outbound/provider/unknown을 분리한다. 불완료면 새 run ID를 만들어 자동 재실행하지 않는다. 별도 승인 없는 fallback/fixture 전환도 없다.

실행 뒤 7개 이하 고객 결정, 질문 최대2, 경영주 검토1화면·승인1회, auto 건별승인0·중복0, 실제SQL correctness를 raw에서 판정한다. `metrics.summarize`의 complete는 성공 행 분모 확인이며 모든 절대 기준을 홀로 증명하지 않으므로 독립 raw 검토를 병행한다. baseline 비교는 기존 incomplete와 동일하게 NOT_READY다. 최종 두 역할 Preview QA·정책 검토·G5/G6 및 제출 접근은 별도 완료해야 한다.
