# M01 경영주 UI 독립 검증

- reviewer: `/root/research`; merchant 구현자: `/root`. 고객 구현 경험은 경영주 독립 검증 결과로 세지 않는다.
- consumed_context_hash: `e8d6eb6ffef8765544e3aeeeb9c27b1e98f0c7cb5131202712ec4d32d806ea99`
- 기준: card, CORE-05/06/07/10/11/17/24/25/26, D-43/44/45, ADR-002/003/004/005, docs21/26/27, wanna-gs-verify 및 wanna-gs-ux-audit.
- URL: `http://localhost:3440`; 독립 Chromium headless profile, viewport 1440×900 / 768×900 및 CSS zoom 200%.
- 소스: `/Users/gsr/Desktop/workspace/2026-ralphton-merchant`, branch codex/m01-merchant, base `04a2a3f274c0f0d0917801d7f625f2036ac32331` + 구현자의 미커밋 M01.
- 최종 판정: **독립 UI fixture 범위 PASS** — 1차 FAIL 3개 결함을 구현자가 수정했고 같은 반례·인접 정상 회귀를 모두 재실행했다. 실제 SQLite/IndexedDB/API/live-model 및 G4~G6는 **not_run**.

## 목적·자료·독립성

고객이 동의한 수요를 경영주가 10SKU 한 검토 화면에서 보고 한 번에 승인하며, 자연어로 이번 묶음/지속 정책을 구별하고 통제할 수 있어야 한다. 기존 상품범위·예산·상한과 오래된 응답 방지를 유지해야 한다. 모든 정상건을 거절해 안전하게 보이는 결과는 통과가 아니다.

조사 연결은 초기 연구의 경영주 반복 업무/불확실 수요 통제 필요와 ADR003의 10SKU workload다. `tests/merchant/fixture.ts`의 10상품·10고객·1점포·각2개·매입1000원/판매2000원은 독립 검증자가 작성한 **synthetic_expansion**이며 실제 GS 상품·실적·거래가 아니다. scoped snapshot만 주입한다. fixture reducer는 UI가 보낸 명령·예상버전·확인값과 화면 반영을 관측하는 장치다. 도메인 FIFO/금액/중복발주/권한/내구성의 정답 구현이나 실제 DB 증거로 쓰지 않는다. 외부 모델 호출0, holdout 접근0.

## 1차 소스 지문

| 파일 | SHA256 |
|---|---|
| MerchantView.tsx | 9ddaad8ab454457201bbc38f9773d4dd8ce0956867c8dc9d5d14423c623464d8 |
| model.ts | 641867ba22c50048601e744d66908b1b262544d3dbd67ce20c00800566262ca4 |
| merchant.module.css | 15c484517d97cd1fa46f775b5b212a8e9b54a1af9595b7d2a436e19bef16ff85 |
| domain.ts | 952c22bb73bb93218c6fcf573d8c7264a2c749560d809a8bb26c2f15eb968105 |
| assistant.ts | a482963843722dcd469d220ed41b391c3bc776eab5a79983adb8c1016b59815b |

## 실행 결과

`npm run typecheck` PASS. 기존 구현자의 `npx tsx --test tests/merchant/model.test.ts` 3/3을 별도 실행해 PASS를 확인했으나 새 독립 사례 수로 부풀리지 않았다. 독립 `browser-check.cjs` 1차12항목 중9 PASS/3 FAIL, pageerror0 포함. 독립 fixture 서버 session을 작업 공간에 보존한다.

| 시나리오 | 결과·관측 |
|---|---|
| 10SKU 수요→검토 갱신→한 묶음 승인 | PASS. 한 경영주 화면의10행, 합계20개/2만원, 고객별승인0, 최종승인1. review1→approve1 및 expectedProposalVersion2/confirmedtrue/currentactor 확인. 세로 스크롤은 필요하며 한 viewport에10행이 전부 보인다는 뜻은 아니다. |
| 고객 요청 상세 | PASS. 선택 SKU 고객2개/행합계 일치, 가격·동의시간·순번·발주·배정·결제·예약·픽업시간 표시, 상세내 변경 버튼/input0, dispatch0. |
| 자연어 이번 변경→undo | PASS. 모델 응답은 agent.record만, 명시 반영 후 revise1, 다시 명시 반영 후 undo1. 발주승인0, 기존 proposal로 복원. |
| 기본정책·NL 지속정책·cap | PASS. 최초 자동off/동의미체크/승인disabled, NL초안은 거래없음, 검토당상한과 일일누적아님 명시, 예산변경은 동의해제, 최종체크 후 예산60000/cap3/confirmedtrue 정책명령1. |
| 공급→입고→픽업→수령 | PASS(fixture). 승인 직후 공급확인중, 확정후 입고대기, 입고후 픽업가능, 픽업시작+48h 데이터/화면경로 확인, 예약번호입력 수령명령1. 실제 allocation/clock 경계는 이 검사가 증명하지 않는다. |
| 미충족 니즈 | PASS. 관심은 구매확약과 분리, 니즈조회 dispatch0/유효수요20 불변. |
| 모델 timeout | PASS. 입력보존, agent.record lookup_error/providerCalledtrue/usage null, 거래명령0. 실제provider 실패가 아니라 서버응답 모사. |
| 768/1440/200%·키보드 | PASS(한정). document 가로넘침0, 표는 컨테이너내 overflow 허용, 정책checkbox focus 가능. CSSzoom2와1440viewport이며 OS/native browser zoom 검사가 아님. 스크린샷 직접 열람. |

## 재현 결함 — 조정자에 전달, UI 직접 수정 없음

### M01-F01 — 호출 중 catalog 변경 후 이전 응답 기록·표시 (차단)

`scenario='slow'`에서 “이번에는 5만원” 제출 직후 snapshot.versions.catalogHash를 A→B로 교체한다. 550ms 뒤 이전 카탈로그 응답의 agent.record1 및 적용버튼이 남는다. 요청 captured와 응답끼리는 비교하지만 현재 snapshot 카탈로그를 검사하지 않는다. 현재 catalog 및 모든 scope/대화/입력 버전이 맞을 때만 기록·표시해야 한다.

### M01-F02 — 지속정책 예산 변경이 기존 categoryScope 해제 (차단)

기존 정책을 enabledtrue/categoryScope=['빵']으로 준비하고 “앞으로 5만원”→정책 확인 화면으로 이동한다. 음료 제외 checkbox가 false가 된다. `applyAnswer`가 기존 skuScope만 보존하고 categoryScope 제한을 제외 집합에 합치지 않는다. 기존 제외 조건을 임의로 제거하지 말고, 명시한 예산 변경만 반영해야 한다. SKU 범위·cap 보존도 인접 회귀로 확인한다.

### M01-F03 — 같은 actor의 새 roleEpoch에 이전 정책 제안 잔류 (차단)

“앞으로 5만원” 제안을 받은 뒤 같은 actor의 roleEpoch를+2로 변경한다(역할 이동후 복귀에 대응하는 단독 fixture 교체). 기존 정책 확인 버튼이 남아 새 scope에서 과거 대화 제안을 옮길 수 있다. effect reset이 actor/generation에만 묶인다. 세션/역할 epoch/catalog 교체 시 제안·대화와 미저장 동의를 무효화해야 한다. 실제 상위 shell의 mount/unmount 동작은 통합 후 별도 검사한다.

## 증거·재현

소유 test: `tests/merchant/{fixture.ts,browser-fixture.tsx,browser-check.cjs}`. `.browser-build/initial-result.json`은 1차를 보존하고 `result.json`은 최신 실행이다. `demand-1440.png`, `layout-768-1.png`, `layout-1440-2.png`, `fail-8.png`~`fail-10.png` 보존. 지표는 DOM assertion+명령기록을 함께 관측한 결과이며 screenshot 단독PASS가 아니다.

```sh
node_modules/.bin/esbuild tests/merchant/browser-fixture.tsx --bundle --outfile=tests/merchant/.browser-build/fixture.js --loader:.css=local-css
cp tests/merchant/browser-index.html tests/merchant/.browser-build/index.html
python3 -m http.server 3440 --directory tests/merchant/.browser-build
PLAYWRIGHT_MODULE=/path/to/playwright CHROMIUM_EXECUTABLE=/path/to/chromium node tests/merchant/browser-check.cjs
```

## 남은 경계

실제브라우저SQLite·IndexedDB저장실패/복원·reset/역할전환, live모델 해석품질·최종카탈로그248, 실제 FIFO/미확보coverage/예산·공급capacity·자동정책정상/수동복구, 픽업48h직전/정각/직후, 전체 shell 브랜드발음/직접진입, 200%nativezoom/확대텍스트 전수·스크린리더·대비 및 ADR003 8workloads×3 baseline/best 편의성 시간 측정은 not_run. 본 fixture는 앱/독립QA 최종완료 또는 제출판정이 아니다.

## 수정 후 독립 재검증 — 최종

- final run_id: `ef438f3d-7737-423e-9a0e-2613e7d6faa1`, checked_at: `2026-09-21T09:31:34.897Z`.
- `MerchantView.tsx` SHA256: `9a52b629e97dc0f5f1461df859aa77b458cdae80aa0a8bd52082fb1c739727f6`; 나머지 위 소스/계약 hash 동일. `.browser-build/result.json`에 전체 파일별 hash·17개 결과를 저장했다.
- **17/17 PASS, skip0, pageerror0**. 16개 독립 UI 시나리오와 pageerror 검사1이며 자연어 eval case 수로 세지 않는다. typecheck 및 기존 model3/3도 수정후 별도로 PASS.
- F01: 현재 snapshot과 captured 비교에 catalogHash 포함. 변경중 응답 agent.record0/적용버튼0 확인.
- F02: 기존 categoryScope의 제외상품도 유지. `categoryScope=['빵'] + skuScope=['p0','p6'] + cap2`에서 “앞으로5만원”만 바꿔 최종 policy.update의 skuScope가 `['p0']`, cap2, 예산50000임을 관측했다.
- F03: reset 의존성 sessionId/actor/roleEpoch/generation/catalog 완전 반영, answerProposal·policyConsent 무효화. 이전 제안버튼0 및 이미 체크한 정책동의 false 재확인. 수정전 이 체크는 true로 남는 인접 반례도 추가 재현했으며 `pre-fix-expanded-result.json`에 보존했다.
- 정상/인접: 기존 10SKU 단일승인, once 수정/undo, NL정책명시동의/상한, readonly 고객상세, 공급/입고/픽업/수령, 니즈분리, 실패입력보존 유지. 추가로 입력변경후 늦은 응답차단, stale proposal 버전 revise0, 빠른 승인연타 dispatch1을 확인했다.
- 경영주 수요 화면과 정책 화면 각각1440/768/CSS200%에서 document 가로넘침0. `demand-1440.png`, `layout-1440-2.png`, `policy-768-1.png`를 직접 열어 금액·수량·CTA·설명이 가려지지 않는지 검토했다. 배경 시안/블루·흰 카드와 읽을 수 있는 DOM 정보 위계는 docs26 참고와 일치한다. 공통 원하GS 브랜드/발음은 이 단독 fixture가 대신 구현하지 않으며 실제 shell 검사에 남긴다.

검증 스크립트는 FAIL 결과가 하나라도 있으면 exit1로 종료하며 각 결과와 소스 지문을 저장한다. HTML 시작파일도 `tests/merchant/browser-index.html`로 남겨 무시된 산출물을 재생성할 수 있다. 검토자는 UI·공통파일을 직접 수정하지 않았고 소유 tests와 이 보고서만 작성했다. 수정과 재검증은 경영주 정상 성공/업무 감소 목적을 보존하며 기준 완화나 필수 여정 삭제가 없다.
