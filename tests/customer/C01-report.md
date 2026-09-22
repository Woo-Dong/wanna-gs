# C01 고객 화면 자체 구현·검증

- owner: `/root/research`; 2026-09-21
- workspace: `/Users/gsr/Desktop/workspace/2026-ralphton-customer`, branch `codex/c01-customer`, assigned base `04a2a3f`
- consumed_context_hash: `e8d6eb6ffef8765544e3aeeeb9c27b1e98f0c7cb5131202712ec4d32d806ea99`
- status: **자체 UI 상태/fixture PASS, 독립 검토 및 실제 통합 not_run**
- 소유 변경: `src/components/customer/**`, `tests/customer/**`만. package/lock/공통 app/브랜치/commit은 조정자 소유이며 변경하지 않았다. 계약 타입은 소유자의 전파 지시에 따라 domain·assistant 최신본을 그대로 복사했다. `npm ci`로 기존 lock에 따라 의존성 설치.

## 구현 계약과 목적 보존

`CustomerView({snapshot,client,onSnapshot})`를 named export. 조정자가 제공한 domain-v1 DemoSnapshot/DemoClient 및 assistant 계약을 소비한다. 호출 경로는 `/api/product-assistant`, 거래는 `client.dispatch`이고 결과 snapshot 내구 저장 성공 receipt 후에만 완료를 표시한다. 고객의 명확한 정상 요청을 막아 안전 점수를 높이지 않으며, 존재 후보 확인→한 점포/수량/현재 모의 판매가격→기본 미체크 동의→요청을 구현했다.

- 원하GS/‘원하지쓰’ 가시 안내, 시안/블루·둥근 흰 카드·입력 예시·하단 탐색. 제외된 사진/마이크/본부/실제결제 기능 없음.
- session/generation/actor/roleEpoch/conversation/inputRevision/catalogHash/requestId 대조 후에만 모델 결과 적용. 입력 변경·새 대화·역할 변경 시 오래된 응답 배제. 검색/API 실패 시 입력 보존, 니즈/요청 자동 저장 없음.
- 후보/대체 차이·미확인 속성, 명시적 선택/거절. 원문·대화·추천 기록을 구매 확약과 분리하고 니즈 기록은 명시 행동으로만 저장. 전환 탐색 취소는 원요청 불변; 명시 새 동의 후 `request.replace` 원자 명령 사용.
- 수량/가격/점포/요청 revision이 달라지면 consent tuple 불일치로 체크 해제. 중복 클릭 중 dispatch 잠금. 통신 예외의 저장 결과 미확인은 같은 command ID·payload로 확인 가능.
- 요청 접수/발주/배정/모의결제 실패/예약/픽업/만료 구분. 7일 구매 동의 기한, 10분 실패결제 점유, 픽업 알림부터48시간을 서로 다른 라벨과 실제 snapshot clock으로 표시. request 취소·수량 변경·재동의·결제 cycle 재시도·알림 읽음 연결.
- verified store 좌표의 OSM 가시 타일 지도(선택 시 로드), attribution, 주소 목록 및 지도 실패 fallback. 실제 GPS 미수집, 첫 점포 위치를 명시 가상 시연 기준점으로 사용하고 직선거리 표시. 서버 재고·가격을 실제 GS 값이라고 주장하지 않는다.

모든 도메인 권한·금액·조건·FIFO·내구 저장 검사는 domain service의 최종 책임이며 FE의 사전 표시/검사만으로 이를 입증하지 않는다. 현재 도메인의 not_listed 차단과 docs27의 별도 공급가능 판정 간 차이를 조정자에게 전달했다. FE는 관측된 가격 조건으로 동의 정보를 표시하고 최종 domain 오류를 숨기지 않는다.

## 디자인 참고

직접 열람한 `docs/assets/wanna-gs-promo-mascot.png` SHA256 `ff1f572a8030fa5bdce6b98ab9d91d796dfbae80a62d4a229209f109a944b876`. docs26의 공식 앱 관찰 요약·고객 정보 위계와 시안/블루 기준을 소비했다. 포스터를 배경으로 사용하지 않았고 모든 정보·버튼을 실제 DOM으로 구현했다. 작은 자체 SVG 장식은 공식 캐릭터 원본으로 주장하지 않는다. 실제 상품 포장 이미지 대신 중립 카테고리 기호를 사용하며 필수 상품명·브랜드·미확인 용량은 텍스트로 노출한다.

## 실행 증거

- `npm run typecheck`: PASS, 마지막 수정 후 재실행.
- `npx tsx --test tests/customer/model.test.ts`: **5/5 PASS**, skip/error0. scope/envelope의 8개 변형, 단계 분리, 픽업 정각 만료, 결제 재시도/동의/cycle 한계, 조회오류·재고0 구분.
- 실제 Chromium headless 브라우저, viewport390x844/360x844, `browser-check.cjs`: **PASS**, pageerror0. 자체 fixture API/client이며 실제 모델·sql.js 거래는 사용하지 않음.
- 브라우저 checks: 브랜드발음, 예시 비제출, 명시 후보선택, 기본미체크, 수량변경 동의해제, 지도실패 목록fallback, sourceNeed 연결 요청1회, API실패 입력보존/니즈0, 입력수정 후 늦은 응답폐기, 360/390 가로넘침0, 대체전환 탐색거절 원요청 불변.
- 초기 브라우저 검사 스크립트가 점포 선택 전 아직 표시되지 않은 동의 체크박스를 조회해 timeout. 제품 실패가 아니라 fixture assertion 순서를 수정한 뒤 같은 시나리오를 재실행했고 통과했다.

스크린샷 직접 열람: `.browser-build/home-390.png`, `consent-390.png`. 추가 `home-360.png`, `candidates-390.png`, `request-390.png`, `result.json` 보존. 산출물/번들 디렉터리는 로컬 작업공간에 남기고 git에서는 제외한다. 3439 fixture HTTP 서버를 실행 중으로 남겼다.

재현:

```sh
node_modules/.bin/esbuild tests/customer/browser-fixture.tsx --bundle --outfile=tests/customer/.browser-build/fixture.js --loader:.css=local-css
# .browser-build/index.html은 fixture.js/fixture.css 및 root div를 사용한다.
python3 -m http.server 3439 --directory tests/customer/.browser-build
# 설치된 Playwright 모듈 및 Chromium 경로를 환경별 지정
PLAYWRIGHT_MODULE=/path/to/playwright CHROMIUM_EXECUTABLE=/path/to/chromium node tests/customer/browser-check.cjs
```

## 남은 독립/통합 검사

실제 SQLite·IndexedDB 저장실패/복원·역할전환/reset, 실제 서버 모델 응답·429/timeout, 실제 domain 모든 mutation(재동의·결제실패·전환·48시간경계)와 DOM 정합성,200%확대·키보드/focus 상세·편의성 측정은 not_run이다. 상위 app 통합·독립 고객QA는 조정자와 method_auditor가 수행한다. 앱 G3~G6 또는 릴리스 완료를 선언하지 않는다.

## 호출 기록 계약 후속 확인

2026-09-21 domain의 `agent.record.usage nullable/providerCalled` 및 서버 `error.attempt` 계약을 소유자 지시대로 소비했다. 모든 scope·대화·입력 revision·catalog 일치 검사 후 성공 및 서버가 명시한 실패 시도를 기록한다. 실패의 사용량 미상은 `null`; 네트워크 자체 실패처럼 시도 여부를 알 수 없는 경우 `0` 또는 `providerCalled:false`를 꾸며내지 않는다. 니즈/요청 저장과 구분하며 성공 기록 receipt 이후 후보를 표시한다.

수정 후 `npm run typecheck` PASS, 자체 모델 상태 5/5 PASS, 실제 Chromium fixture 브라우저 14개 검사 PASS·pageerror0. 기존 정상 요청·동의·입력 보존 검사를 유지하고, fixture 정상은 providerCalled false 및 알려진 0 usage, 서버 시도정보를 가진 timeout fixture는 providerCalled true 및 usage null/lookup_error만 기록하며 니즈·요청 0임을 추가 확인했다. 이 실패는 서버 응답 모사이며 실제 공급자 호출 또는 실제 SQLite 저장 검증으로 세지 않는다.

## CQA-01/02 소유자 복구 — 2026-09-21

독립 고객 QA가 찾은 후보 후속참조 정보 누락과 200% 텍스트 nav 겹침을 최소 변경했다. 모델 history의 assistant에는 검증한 `CustomerInterpretation` 전체 JSON을 저장해 실제 후보 순서·SKU·차이·미확인 조건을 다음 API에 보낸다. 별도 displayHistory는 기존 user 원문/assistant 질문·설명을 유지하며 `need.record.dialogue`에만 사용한다. 새 대화·scope 변경 때 두 이력을 함께 비운다. 최초 originalText, 명시 저장/동의, 수요 자동 합산 금지 동작은 유지한다. nav 아이콘의 고정 height28px를 글자 상대 min-height1.22em/line-height1.2로 바꿨다.

자체 검사: typecheck PASS, 상태단위5/5 PASS, 기존 정상 흐름을 포함한 브라우저 fixture16개 PASS. 실제 2후보 표시→“두 번째 말고 첫 번째 상품을 보여줘” 후속 요청의 JSON history에서 IDs p0/p1·순서·차이·미확인 조건이 일치함을 검사했다. 이어 요청 제출 후 니즈의 originalText가 최초 입력이고 dialogue가 두 user 원문+두 assistant 설명문으로 유지되며 JSON이 섞이지 않음을 확인했다.

추가 `tests/customer/accessibility-check.cjs`: 360px에서 현재 DOM computed font/line-height200% 주입, 3개 nav 버튼 각각 icon text bottom742.69 <= label top749.80, label bottom782.80 <= button bottom792.00 PASS. 확대 후 메뉴 전환·다시 입력 PASS, 가로 넘침0. `nav-text200.png` 직접 열람, `text200-result.json`과 전체 screenshot 보존. 실제 인간 접근성/전브라우저 인증이 아니라 명시한 텍스트 확대 반례의 자체회귀다. 모델 실호출0, 실제SQLite 독립delta는 root 통합 후 method_auditor가 수행한다.
