# I01 고객·공통 AppShell 독립 브라우저 QA

- 검증자 method_auditor. 고객 구현 research, 공통 AppShell root/builder와 별개. 적용 wanna-gs-ux-audit 및 verify; CTX-APP-v5 hash `10701ed7619c86fe94cec16a31b6ac8b02a1afa9f2843ffdcce4ec446e952234` ACK,23원본 hash 일치 확인.
- URL `http://localhost:3217`, Next production build `bxh_JHrpTuQF-CXQSB0CW`, Chrome153.0.8010.50, 독립 fresh profile/context, 고객390×844/360×800. 이 로컬 build는 Git/Vercel 제출 검증이 아니다.
- seed248-v2/schema-v2, catalog `f2696abe92521e3ff8f9ab43cb36a1d297a6fd23d272e239605b49fab4343b1e`, ADR002/004/005. live `gpt-5-mini-2025-08-07`, baseline-v1; 실제 연구 RC03/04/07/08의 상품·점포 불확실성/오류회복과 synthetic QA 시나리오. 보호 holdout 미사용.
- 최종 I01 bounded 판정: **고객·공통 AppShell 실제 UI/SQLite G3/G4 범위 PASS. CQA-01/02 수정 후 독립 재검증 완료**. G4 전체완료/G5/G6/정식 NL 품질 PASS를 선언하지 않는다.

## 실제 정상 경로

`tests/integration/customer-browser.mjs --live`에서 실제 모델1회로 짜슐랭145g을 찾고 실제 UI/Worker/SQLite를 사용했다. 16,638 input +133 output=16,771tokens, 표시 추정비용 $0.0044255, model latency1887ms. API응답200, mode live와 providerCalled true 및 usage4필드를 agent_runs에 저장했다. 독립 QA 총 실제 모델호출1이며 아래 fixture는 추가 공급자 호출이 아니다.

1. 가시적 원하GS/‘원하지쓰’/고객/모의 표기,390px 가로넘침0, 예시 클릭의 자동전송0/기존입력복구, 사전 수요0.
2. 실제 정확 후보를 고객이 선택, 수량2/점포/단가3000원 총액 확인. 체크 전요청불가, 체크후수량변경시동의해제. 지도 타일 요청을 실패시켜 목록 fallback으로 동일 store_id 선택.
3. 요청 버튼을 한 탭에서 연타해도 SQLite purchase_requests1/quantity2/consent1. 추천·니즈만으로 요청을 만들지 않았고, 아직orders/reservations0.
4. 새로고침 뒤 동일요청 유지. 같은탭 경영주 전환→검토→묶음승인→공급확정→고객 예약확정. 자동모의결제성공, orders1, 아직 pickupDeadline null/픽업알림0. 고객 화면은 아직48시간 시작 전이라고 표시.
5. 입고 후 pickup_ready, 알림1, pickup_deadline - pickup_available=172800000ms. 고객·경영주 같은 저장본의 상태일치. refresh뒤 기한 불변, 경영주 모의수령→고객 수령완료.

중간 테스트가 실제 버튼 ‘요청 상세 보기’를 잘못된 ‘자세히 보기’로 찾는 harness 오류로 중단됐다. 제품 실패로 세지 않았고 원결과를 보존했다. 직전 저장된 confirmed SQLite snapshot을 fresh context에 복원하여 `--resume-confirmed`로 이후 사용자 경로를 계속했다. 재시작시 경영주 역할임을 놓친 두 번째 harness 초기화 오류도 수정했다. 실제 모델을 다시 부르거나 요청·발주를 새로 만들어 이전 실행을 숨기지 않았다. normal-result와 continuation-result를 함께 읽어야 전체 경로 증거가 된다.

## 독립 예외/저장 경계

`tests/integration/customer-boundaries.mjs`의 최초 보완 후11검사는 아래 기능에 PASS, console pageErrors0, 실제 모델0/HTTP fixture12였다. fixture 응답의 mode와0토큰은 합성으로 구분하며, 오류 경로의 providerCalled true/null usage는 주입한 오류 계약일 뿐 실제 공급자호출 증거가 아니다.

- HTTP timeout: 입력보존, usage null/lookup_error 기록, 니즈/확약0, 바로정상 fixture 재시도회복. 저장완료를 기다리지 않은 초기읽기 때문에 agent_runs0을 관측한 harness는 명시적 durable-row polling으로 수정했다. Worker 응답success와 이후SQL저장 모두확인했고 로그0을제품PASS로 숨기지 않았다.
- 실제 이전 질문 history와 clarificationCount 전달, 추가질문2회후3번째거절/거래0.
- 미식별 결과는 점포를 명시하여 니즈만1저장, 요청/발주0.
- 허구SKU응답 후보선택차단/수요0, 정상 fixture 재시도 성공.
- 늦은 응답: 입력revision 또는역할변경 후 후보/로그/거래 생성0.
- 기존 요청에서대체탐색→후보거절→전환취소: 원요청·동의row 완전동일.
- 실제 SQLite 모의결제최초+고객재시도실패→review_required/풀해제→새조건·새동의명시→동일풀정상결제. 결제기록3, 새cycle2, consent2, orders1유지.
- 다른 합성고객은 내요청빈상태,원고객SQL요청1유지. 한PC로컬role분리이며실제로그인보안주장아님.
- 손상snapshot3bytes를주입후자동덮어쓰기없이복구안내. 체크전초기화불가/명시체크후generation+1/요청0.
- 실제Worker의IndexedDB write transaction을1회abort: PERSISTENCE_FAILED, 요청/니즈0유지→같은화면정상재시도1접수→refresh보존. DOM모의저장이나fixtureSQLite가아니다.
- 저장된입고상태에서UI clock을픽업마감으로이동: 고객수령기한종료,DBpickup_expired/원마감불변. 경영주명시reset후generation+1/내역0/refresh유지.

## 발견한 제품 결함 및 수정 요청

### CQA-01 후보 정정의 대화 맥락 누락

실제 UI에서 두 후보를 보여준 뒤 ‘두 번째 말고 첫 번째를 보여줘’를 입력했다. 다음HTTP request.history의assistant content는 reason문장 하나뿐이었고 두 후보SKU·순서·차이가 없었다. CustomerView setHistory가 `value.question || value.reason`만 저장하는 것이 원인이다. E02평가기의실제응답JSON history와앱입력이달라질수도있다. 전체검증된result를JSON으로보존하고연속정정/추가질문정상흐름을재검증하도록구현자에게전달했다. 실제 모델로오류율을추정한것은아니며모델이받을필수후보문맥의직접누락반례다.

### CQA-02 확대 글자에서 하단 메뉴 겹침

html font-size만2배로바꾸는초기검사는px스타일을충분히확대하지않으므로확대PASS근거로채택하지않았다. 각현재DOM의computed font-size/line-height를2배로주입해360px에서실제이미지와DOMRange를검사했다. nav icon span의height28px고정때문에확대icon본문이아래라벨과겹쳤다. 문서가로넘침0만으로통과시킬수없는결함이다. 고정높이를글자상대값/auto로바꿔수정후재검증한다. 이주입은200%텍스트확대시뮬레이션이며실제인간사용성실험이나전브라우저접근성인증이아니다.

두반례는fresh profiles의추가독립실행에서FAIL을재현했다. `before-fix-boundaries-retest.json`, `before-fix-followup-history.json`, `before-fix-text200-spacing.json`, `before-fix-text200.png`를별도보존했다. 정상기능을삭제하거나질문/정정기준을낮추는수정은허용하지않는다.

## 증거·한계

private `artifacts/private/run-20260921/customer-qa/`의 result JSON,SQLite원본,상태row,event,usage,스크린샷을보존한다. 소스지문전체는source-before-fix.json. 주요구현지문:
- CustomerView `3a3d388341186ebbd65fb420aa581ba1cdfd836787b874f26f907b913799985a`
- AppShell `116404f640343e106dd954bc8aa470a569d2abe529c833dcdd339f7588db52fb`
- engine `b9ea21cd344c7467cf6d34fb7fa3abfb21a02c9cbcf3bb46d977cf7ed684cff4`

초기/픽업/확대이미지를직접열어브랜드·상태·위계를확인했다. 실제동의후원수요·가격·입고기한을보존하고서버키가UI에나타나지않았으며실결제/외부DB를추가하지않았다. 전체UX48workload반복·편의성수치비교·420NL최소품질·최종Vercel은이검사에포함하지않는다. 실제지도정상타일연결은이번실행에서장애fallback만검증했으므로별도원격검사가필요하다. 모델예외/모호/대체는명시HTTPfixture경계이며live상품품질을대신하지않는다.


## CQA-01/02 수정 후 최종 독립 delta PASS

새build **Ob3v4bKR3BUZlzGBamRYO**, 동일localhost3217에서fresh context로검증했다. CustomerView `50044eaad848a3dc58defcf08df3cc74947096948a4a456d19a909f9d19b2705`, CSS `0d96bbda324205116a46a738924d5f01ecede6be2f619662a7dc573b0a0d9dc5`. 두실행의BUILD_ID시작/종료불변과서로동일을확인했다.

- 정상5단계를이번에는중단없이처음부터끝까지재실행 **5/5 PASS**. 실제live1추가, 16,630input+147output=16,777tokens, $0.0044515,3079ms. 이고객QA전후총실제2회/33,548tokens/$0.008877추정이며기존1회실패검사기기록도유지한다.
- 수정반례를포함한경계 **12/12 PASS**, 실제모델0/명시HTTPfixture14, pageErrors0. 고객자체unit5개도비구현자가재실행5PASS/skip0.
- CQA-01: 두후보후후속request.history의assistant가검증된result전체JSON으로전달되어각SKU/순서/차이/unknownConditions를유지했다. 추가질문JSON.question/count/2회한도도PASS. 별도실제SQLite need.dialogue에는원래user문장과사람이읽는assistant설명만남고confirmationRequired등내부JSON을표시하지않음을검증했다. 역할·새대화reset검토와기존늦은응답차단이유지된다.
- CQA-02: 같은200%computedfont/lineheight주입으로3메뉴모두icon bottom742.69 < label top749.80을확인했고실제스크린샷도직접열어겹침해소를확인했다. 이전26px겹침을단순가로폭assert로덮지않았다. 기본390px 및360px수요/역할전환조작도정상이다.
- 결제2회실패→재동의·풀보존, actualIndexedDBabort→정상재시도, 손상snapshot명시복구, 48h정각만료·reset·refresh를동일새build에서다시통과했다. 이전domain/동의/정상기능을삭제한복구가아니다.

수정전증거전체는private/customer-qa/pre-delta와before-fix-*로보존했다. 현재normal-result.json/boundaries-result.json은새build의실행이며정식NL평가가아니다. 운영G4checkpoint의두미완료는이delta로해소했다. 고객/AppShell의해당I01독립review작성은가능하지만정식NL최소/48회UX비교/최종VercelG5/G6는여전히별도필수미완료다.


## CSS 마지막 공백만 제거한 의미 불변 delta

독립적으로 git staged-index의customer.module.css와worktree실제bytes를비교했다. 마지막줄바꿈직전ASCII공백1byte만제거됐고다른byte는완전히동일하다. oldCSS `0d96bbda324205116a46a738924d5f01ecede6be2f619662a7dc573b0a0d9dc5` → newCSS `2a550c25c4e998baca0346b212e473eb1f2b61b4b2c77ff406a27d467a73cbca`. 현재소스집합에서이CSS만indexbytes로치환해계산한전체지문은기존8d94bcb2…와정확일치하므로다른게이트소스변경이함께숨지않았음을확인했다. 현재전체지문 `6ab487de4e1e7bc69cc3b1805ed01e35a897c30787351d5f737811a3734a92f3`로3독립review를갱신했다. CSS구문/선택자/값/렌더링의미가변하지않아앞선실제브라우저/SQL증거를유지하며재실행0/추가모델호출0이다. private i01-whitespace-delta.json에비교증거보존.
