# D02 독립 도메인·실제 Worker/IndexedDB 검토

- 검증자 method_auditor, 구현자 preflight_builder와 별개. wanna-gs-verify, ADR002/004, CORE동의/수량/FIFO/보수적발주/48시간, docs29 계약.
- worktree `/Users/gsr/Desktop/workspace/2026-ralphton-domain`, root source를 수정하지 않았다. consumed_context APP-v4 `0788c0e5ed96f22adc527f3cd30dc4830a5e43138cd5da992a734e0b06559997` ACK.
- 최종 bounded 판정: **D02 G1/SQL·Worker·IndexedDB G2 및 ADR005 delta PASS**. 아래 최초 반례와 복구 기록을 보존한다. 제품 UI/G4/live 모델 연결은 이 보고서에서 not_run.

## 실행한 검사

1. Node22 `scripts/build-seed.mjs` 실행248상품/9점포, catalog hash `f2696abe92521e3ff8f9ab43cb36a1d297a6fd23d272e239605b49fab4343b1e`, seed hash `4bf227886af5a618558df8cad916ce2239aaf16a1299b4acc9db5d90044a0429`. `tests/domain/domain.test.mts` 독립재실행24/24 PASS, tsc PASS. 이후작성자공급종료25번째test는추가되었으므로후속반영을분리한다.
2. 기존24에는13명/MOQ6→12발주+1미발주, whole FIFO 복수소스합산, 취소된이미발주coverage보존/부족분supplier capacity자동복원금지,가격변경·동의7일·결제실패10분2회·48시간정각·원승인일예산·자동정책정상/해제·같은명령재전송·다른역할/점포상세거절이포함된다. 특히취급not_listed/재고0과공급available을분리해정상접수→결제예약되는기존회귀를확인했다.
3. 별도 실제Chrome153.0.8010.50를 사용해 실제src/db/worker.ts를esbuildbrowserbundle로만변환한전용하네스에서다음8검사를실행했다. 모델fixture도호출하지않았으며liveCalls0이다.
   - Worker에서sql.js/WASM/seed248·점포9초기화.
   - 요청수량2 저장후 실제IndexedDB snapshot.bytes를꺼내별도sql.js SQL SELECT quantity=2와integrity_check=ok 확인.
   - 브라우저새로고침후동일requestId복원.
   - 같은탭customer→merchant역할전환후동일요청확인.
   - faultworker의IDBDatabase.transaction에1회abort를주입: 실제IndexedDB write transaction 실패→PERSISTENCE_FAILED. SQLproposals0과이전snapshotbytes완전동일 확인.
   - 바로동일정상검토재시도시proposal1개생성/저장성공.
   - merchantreset generation+1,요청0,이전scope STALE_GENERATION,새로고침후초기화상태유지.
   - 저장된sqlitebytes를3byte손상으로교체: SNAPSHOT_CORRUPT,손상3byte자동덮어쓰기없음. explicit false복구거절/true복구성공.
   pageErrors0. 증거 private/run-20260921/d02-browser.json·d02-worker-independent.png·d02-browser.mjs 및전용하네스보존. fault주입wrapper는실제Worker소스에저장실패를발생시키기위한테스트계층이며제품코드를수정한것이아니다.

## 독립 SQL 반례 — 수정 요청

private d02-counterexamples.ts는실제DomainEngine+sql.js에공개명령을보냈다.

- **D02-01**: 정상request2개후reconsent `{accepted:true,termsVersion:''}`를보내면새consent.version2,빈termsVersion,status=valid로저장된다. 최초create의빈약관거절과불일치다. 수량변경/재동의의명시동의문서버전도검증해야한다.
- **D02-02**: proposal.revise `{scope:'once',excludeSkus:['NONEXISTENT']}` 통과,기존실제상품line1은그대로실행가능하다. 알수없는상품/분류제약을침묵무시하지않고명령전체거절해야한다.
- **D02-03**: proposal.revise `{scope:'once',budgetLimitKrw:0}`(정식필드는budgetCapKrw)도통과하고2000원발주안유지. TypeScript타입은WorkerJSON런타임검증이아니다. 허용키/값검증과N01→도메인명시adapter가필요하다. 잘못된예산필드가조용히없어진상태에서승인가능안을만들면사용자명시제약을잃는다.

수정검증은원래정상수량/유효제약/정상재동의회복과함께실행해야하며모든변경을거절하는방식은인정하지않는다. 별도통합주의: N01 maxQuantity의policy scope는현재PolicyView에대응필드가없다. 임의로조건을버리지않고계약을정하거나지원범위를명시해야한다.

## 한계

이검증은실제Worker·IndexedDB·SQLite G2경계이며제품화면이아니다. BrowserDemoClient의Next.js번들/실제고객UI·경영주UI/실제모델·지도·브랜드/최종제출Vercel은후속G3~G6이다. 단일탭만검증했고다중기기동시성/실제로그인보안을주장하지않는다. 테스트용원본·로그·작업공간을유지한다.

## 검토 소스지문
- `src/domain/engine.ts`: `dc934949eeaba9046e56e52c0e7bec3619bc6588837fbf32f63da8816510a5fe`
- `src/db/runtime.ts`: `b567984ecef5504f6d091c30ab518dffbef767e69e06c4c8ee8d7f7ae1ecf631`
- `src/db/worker.ts`: `bd77f036336dcb6aa54ef7512ef6b6b10b031a9b64b058e04b62de3a062cbc3a`
- `src/db/client.ts`: `e95f598ec94cb5e5a8fceb4a73b08f1f775b6f03cea96eee1f03e2fdb56d9810`
- `data/schema/001.sql`: `fb3f47775e9745d1dfeac3586af423c1d6f8427fb81704c53935a3a5be21b5b0`
- `scripts/build-seed.mjs`: `26aa7c8d6c24b791f20306c6f4546c3264a629f4a5d88c1b13fe10b28dabd1b6`
- `src/contracts/domain.ts`: `be4ce230606b5b2b78d9b6f3dafc8fc5700e7f70c277d7228e98206643738743`

## 독립 인접 정상 회귀

private d02-adjacent.ts를실제sql.js에서추가실행PASS:결제2회실패후pool2개해제→valid terms-v2로재동의→동일pool로결제성공/paymentCycle2,orders1개유지/payments3건. 입고알림생성후정확48시간-1ms수령성공,pickup알림1건이다. 정상재동의가다시발주하거나공급을중복소비하지않음을확인했다. 이경로는실패2회를숨기지않고새cycle로정상복귀하는ADR002계약을검증한다. 전용localhost3135하네스서버는검증후종료했고파일/스크립트/스크린샷/로그는보존했다.

## 2차 D02-01~03 복구 검증

engine hash `bd6ea7ca138c9a44c8c7ce7336146f261161a64c6f20ee178e8bddd20cc2cd6b`에서독립동일반례재실행:빈약관재동의CONSENT_REQUIRED,unknown제외SKU와잘못된예산필드INVALID_INPUT으로모두거절됐다. 유효재동의정상복귀/공급풀보존/단일발주/48시간-1ms수령의5독립인접assert도PASS,작성자확장tests/domain27개를별도로재실행27PASS/skip0다. **D02-01~03 해소, 기존D02범위G1+SQL/runtime G2 bounded PASS**다.

Worker/IndexedDB 소스는그대로여서앞선실제브라우저8검사의해당저장경계증거가유효하다. 다만새engine validation을포함한최종제품bundle/브라우저전체검증을완료했다고표현하지않는다. 새ADR005 지속정책수량상한은별도채택/구현중이며그필드·명령당한번자동발주·snapshot버전변경은이PASS에포함되지않는다.


## ADR005 최종 delta 독립 검증

2026-09-21 engine `fd9b4f92b05b7e88c7d975f4f10cf77c739f713b1c22414b8da7eb2c1cb38297`를 root 및 domain 작업공간에서 동일하게 확인했다. seed schema-v2/seed-248-v2 SHA `4cb10e899c9706bb0a9278b458bd7b70d3c34bf28f649b62ffae0894794a2b45`; catalog248 hash는 변경 없다. ADR005 adopted 원문과 실행 계약을 대조했다.

- 작성자가 추가한 전체 SQL tests를 비구현자가 재실행: **34/34 PASS, skip/todo/cancel 0**. 원래 수량/FIFO/동의/48시간 정상 경로와 새 cap/MOQ/null/보존/저장 실패를 함께 확인했다.
- 별도 독립 `d02-cap-independent.ts` 실제 SQL 경계 9개 PASS: 수요 없는 정책 활성화0 → 새 요청10에서 정확3 → auto 명령에서3 → 같은 명령 replay0 → 공급확정/입고/clock 추가발주0 → 새 merchant.review3 → 잔량1 → 후속 검토3회 추가0. 원요청10·capacity60→50·상한3을 보존하고 invariant를 통과했다. 과거 직접auto+reconcile 중복 경로는 제거됐고 merchant.review도 자동검토 한 번 뒤 제안만 생성한다.
- 독립 인접 정상 `d02-adjacent.ts`의 결제2회 실패→풀 해제→정상 재동의→동일 풀 결제/단일 발주/48시간-1ms 수령/알림1개를 최신 소스로 재실행 PASS했다.
- 최신 Worker를 다시 bundle하여 실제 Chrome/IndexedDB 8검사를 **전부 재실행 PASS**, pageErrors0. seed248/점포9, SQLite SELECT/integrity, refresh, 역할 변경, 실제 IDB abort 시 rollback 및 정상 재시도, reset/generation, 손상 snapshot의 명시 복구를 확인했다. 증거 `artifacts/private/run-20260921/d02-browser-v2.json`, `d02-worker-independent-v2.png`; 모델 호출0. 이전 증거는 덮어쓰지 않았다.

타입 검사 범위 정정: 최초 domain 작업공간 기본 tsconfig의 include는 app 중심이어서 당시 tsc PASS만으로 src/domain 및 .mts 전체 타입 검증을 주장할 수 없었다. 통합에서 line(id)의 반환 추론 오류가 발견되어 작성자가 `:Row` 주석을 추가했다. 독립 검증은 별도 `d02-fulltype.json`에서 **domain src/**/*.ts와 tests/domain/**/*.mts를 명시 포함**, Node22/TypeScript noEmit을 실행해 PASS했다. 런타임 변경과 타입 범위 정정을 구분한다.

목적 보존: 상한은 외부 검토 이벤트당 SKU 단위이며 일일 총량으로 바꾸지 않았다. 수요를 없애거나 MOQ 이상으로 억지 보충하지 않았고, policy null/해제 보존·버전·명시 확인·원자적 저장 복구를 유지한다. 이 결과는 독립 domain/실제 저장 G2 범위의 PASS이며, AppShell/고객·경영주 화면 및 live 최종 UX는 별도 단계다.


## live usage 계약 좁은 후속 delta

실제 UI 호출에서 N01 usage의 estimatedCostUsd 필드를 도메인이 알 수 없는 키로 거절하는 통합 오류가 발견됐다(root/research 관측). 작성자가 optional number|null 계약을 보완한 engine `b9ea21cd344c7467cf6d34fb7fa3abfb21a02c9cbcf3bb46d977cf7ed684cff4`, contract `fc06aec7bf7b089ebfbf379ad7daf1df9b003f907413aea38818beae8183bd4a`를 독립 검토했다. 도메인36/36 및 명시 전체타입 검사 재실행 PASS. 별도 d02-usage-independent.ts는 실제 N01 사용량 4필드 형태를 SQL에 저장·재전송중복0·음수비용rollback·unknown null·실패후정상 저장·수요오염0을 검증해6경계 PASS였다. 과거 실패를 지우지 않았고 비용을 모르면0으로 바꾸지 않았다. seed/schema/catalog 및 수량 정책은 변경 없다. UI에서 후보가 실제 표시되는 정상 회귀는 I01 고객/경영주 독립 브라우저 보고서에서 이어 검증한다.
