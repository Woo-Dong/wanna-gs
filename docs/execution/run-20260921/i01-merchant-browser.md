# I01 경영주 실제 브라우저·SQLite 독립 검증

- 판정: **실행한 경영주 I01 범위 PASS**. 정상 실제 모델 2회와 같은 소스의 실제 SQL/IDB 브라우저 회귀12/12 PASS. 전체 자연어 품질·고객 독립QA·Preview/G5/G6 완료를 의미하지 않는다.
- reviewer `/root/research`, merchant 구현자 `/root`. 고객 화면은 본 검토자의 구현이므로 고객 독립 QA로 세지 않았다.
- consumed_context_hash: `10701ed7619c86fe94cec16a31b6ac8b02a1afa9f2843ffdcce4ec446e952234` (APP-v5 원본 ACK).
- 기준: card/CORE-05~11·17·24~26, D43/44/45, ADR002~005, docs21/26/27/29, wanna-gs-ux-audit·verify.
- URL `http://localhost:3217`; 실제 Next production build `bxh_JHrpTuQF-CXQSB0CW`, Chromium headless 독립 profile/context, 한 탭. main/Preview/Production 외부 변경 없음.
- 최종 SQL 회귀 run `e96835c6-a4e6-474b-ab52-56aa0b5e8bf7`; 수정후 live run `5e095d03-1574-4a11-aba0-a71596342091`. 두 run의 제품 소스 hash 동일, 실행 중 build ID 불변.

## 목적 보존과 준비 경계

10개 SKU의 고객 동의 수요를 경영주가 한 검토 화면에서 보고 한 번에 승인하며, 자연어 수정/되돌리기와 통제 가능한 자동발주를 유지하는지를 검증했다. 정상 성공을 모두 차단하는 방식으로 안전 기준을 통과시키지 않았다.

`tests/integration/merchant-seed.mjs`는 실제248상품/9점포 seed SQLite를 메모리에서 열고 합성 유효고객 요청만 준비한다. batch는10SKU 각2개, single은1SKU2개, shortage는1SKU3개다. 시연가격/수요는 합성이다. 준비 단계에 merchant review/approve/supply/payment/receipt는 실행하지 않는다. 버전이 일치하는 SQLite bytes를 빈 독립 profile의 IDB에1회 주입한 후 모든 평가 행동은 실제 DOM 클릭·입력으로 진행했다. 별도 최소발주 사례는 앱의 공개 시연 도구 UI로 준비했다. 보호 holdout 접근0.

저장은 실제 `wanna-gs-demo-v1` / `snapshots` / `current`의 `Uint8Array`를 읽어 로컬 sql.js로 조회했다. 각 checkpoint의 SQLite 파일, bytes SHA256, session/generation/actor/roleEpoch/revision, 요청/동의/발주/ledger/예약/알림/events/agent_runs/proposals를 보존했다. 모든 읽기 checkpoint의 `integrity_check=ok`, FK위반0. 감사용 과거 generation은 지우지 않고 **현재 generation의 행**을 UI와 대조한다.

## 실행 증거

| 경로 | 실제 관측과 SQL 대조 |
|---|---|
| 10SKU 집계→고객 상세 | 10행/20개, 초안매입합계27,700원. 한 고객행의 수량2/판매가/동의시각·7일만료/접수순번·발주연결·배정·결제·예약·픽업 라벨, readonly 입력/버튼0. 검토 단계 orders0. |
| 점포 역할 전환 | 실제 상단 선택 UI로 타점포 이동→수요행/원점포고객상세0, 복귀→10행. 한 탭 actor/roleEpoch 전환; DB 공유 다중사용자 시험 아님. |
| 실제 자연어 수정/undo | “이번 묶음은 예산 5만원 안에서만 발주하도록 수정해줘”→명시 반영→proposal budgetCapKrw50000. “방금 변경을 취소하고 이전 검토안으로 되돌려줘”→명시 반영→원래 제약 복원. 이때orders0. 수정후 실제 agent_runs2 및 providerCalledtrue/토큰/비용 저장. |
| 한 묶음 승인·연타·새로고침 | 검토1화면+승인1회; 빠른연타에도 order1/lines10/orderedQty합계20. 실제 ledger 합계=매입가×발주량=27,700원. 승인직후예약0. 새로고침후같은actor/generation/order1 복원, 변화없는 재검토는새발주안0/승인disabled. |
| 공급→모의결제→입고→수령 | 공급확정후 reservation confirmed/픽업기한null/픽업알림0. 입고후 pickup_ready/알림1/정확한 deadline-start172800000ms. 실제 예약번호 입력 수령→collected/collected_at 및 reservation.collected event. |
| 부족 공급 | 3개 요청에2개확보→예약0/요청3보존/confirmedQty2. 다시검토는 풀2개coverage를 뺀 잔여1개만 제안, 기존주문1불변. |
| 자동정책 | 초기off/미체크, 명시 체크·cap2 동의후 policy order1/orderedQty2. 건별승인0. 변화없는검토2회 추가후 order1/알림수불변/수동승인disabled. |
| HTTP timeout 주입 | **HTTP fixture** 503, 입력보존/추가주문0, agent.record lookup_error/providerCalledtrue/usage null 저장. 실제공급자 timeout을 발생시킨 것이 아니다. |
| 기록 거절 | **HTTP fixture**에서 totalTokens≠input+output을 주입해 실제domain 기록검증거절. 입력보존/변경안버튼0/agent_runs증가0/orders0/기존proposal불변. 실제IDB quota 실패가 아니라 domain command 거절이다. |
| 픽업마감·초기화 | 시연도구datetime UI로 deadline−10초 이동→pickup_ready, deadline 지정→pickup_expired. 실제처리 event는 deadline+1161ms였으므로 브라우저에서 수학적 정각1ms를 재현했다고 주장하지 않는다. deadline불변/수령거절/collected_atnull. 명시초기화→generation1→2/현재요청·주문0, 새로고침후유지. |
| 최소발주 미달 | 시연도구UI로 minimum 시나리오준비→요청1개보존/최소6개/주문0/보류이유·다음행동/승인disabled. |
| 브랜드·반응형 | 실제shell 가시‘원하지쓰’/점포·경영주역할/모의안내. 1440×900·768×900·CSSzoom200%에서document가로넘침0/정책checkboxfocus. screenshot직접열람. nativebrowserzoom·OS텍스트확대 전수검사는아님. |

최종 회귀12/12 PASS, pageerror0, required skip0. SQL 검사는 실제 DB이고 마지막 회귀의 모델 해석만 HTTPfixture다. live 성공은 별도 run의 실제 모델 증거를 연결하며 fixture 응답을 live 호출로 세지 않는다.

## 발견·수정·재검증

I01-MF01: 첫 live2회 모델 응답/수정/undo는 성공했지만 agent_runs0. 서버 ModelUsage의 estimatedCostUsd를 UI가 전달하는 반면 domain은 정확3토큰키만 허용하여 기록이 거절됐다. MerchantView는 기록실패를 무시하고 변경안을 보여주었다. root도 별도고객경로에서 발견했다. builder가 nullable 비용 필드를 검증·보존하도록 계약/도메인을 수정하고 root가 기록 성공후에만 변경안 표시하도록 수정했다. 수정후 동일live2회로 비용 포함 agent_runs2, 인접 기록거절→입력보존/변경안0과 정상승인 경로를 확인했다. 검토자는 제품코드를 수정하지 않았다.

하네스 보정은 제품수정과 구별한다: 초기 about:blank에서의 IDB 접근오류를 origin guard로 제거; reset후보존되는 과거generation을 활성거래로세지않도록조회조건보정; 실패메시지렌더직후비동기기록완료를기다림; 숨은시나리오 option과 실제‘픽업 기한 종료’ span의 동명locator를 merchant영역으로한정. 마지막 오류는 수정후live run의 유일한실패였으며 동일소스 fixture회귀로 완료했다. 원본실패결과는삭제하지않았다.

## 모델 사용량

총 **실제 모델4회**(최초실패조사2+수정후2), 추가재시도0. 모두 `gpt-5-mini-2025-08-07`, prompt baseline-v1. 최초2회는HTTP200이지만앱로그실패라완료로세지않는다.

- 최초2회: 34,577tokens, 로컬추정비용$0.00902225, 지연2557/1658ms.
- 수정후2회: 34,546tokens, 로컬추정비용$0.008997, 지연1813/2323ms.
- 합계69,123tokens, 추정$0.01801925. 공급자잔액·실제청구확정값이아님. fixture의 providerCalledtrue는 실패계약 검증용 응답 모사이며 추가실호출에합산하지않는다.

## 최종 소스 지문

| 파일 | SHA256 |
|---|---|
| MerchantView.tsx | 1352bf1ea64bd0f30e5c3acc6352e89a538069427b52c471517544694ac1153f |
| AppShell.tsx | 116404f640343e106dd954bc8aa470a569d2abe529c833dcdd339f7588db52fb |
| DemoControls.tsx | 77ed26af08614b64720a44a1a581095c9f3fc430fb0f79b9283294f1ac832c43 |
| runtime.ts | b567984ecef5504f6d091c30ab518dffbef767e69e06c4c8ee8d7f7ae1ecf631 |
| client.ts | e95f598ec94cb5e5a8fceb4a73b08f1f775b6f03cea96eee1f03e2fdb56d9810 |
| worker.ts | bd77f036336dcb6aa54ef7512ef6b6b10b031a9b64b058e04b62de3a062cbc3a |
| engine.ts | b9ea21cd344c7467cf6d34fb7fa3abfb21a02c9cbcf3bb46d977cf7ed684cff4 |
| seed.sqlite | 4cb10e899c9706bb0a9278b458bd7b70d3c34bf28f649b62ffae0894794a2b45 |

schema-v2/seed-248-v2/cataloghash `f2696abe92521e3ff8f9ab43cb36a1d297a6fd23d272e239605b49fab4343b1e`. 커밋 후 동일 바이트 여부는 조정자가 이 해시와 대조한다.

## 재현과 보존

검사 `tests/integration/merchant-{seed,browser}.mjs`. 기본실행은HTTPfixture이며 `--live`는2회실호출하므로이번권한상한소진뒤추가실행하지않는다. Playwright/Chromium경로를환경변수로설정해 `npx tsx tests/integration/merchant-browser.mjs` 실행. DB내용/스크린샷/네트워크메타데이터는 `artifacts/raw/i01-merchant/` 보존; 최초는 `initial-live/`, 수정후live는 `corrected-live/`, 최신은 `result-fixture.json`. 키/Authorization내용은기록하지않았다.

## 한계·후속

독립고객QA, 실제IDB저장용량/디스크실패, 보호평가셋전체live, ADR003 workload8종×3 baseline/best 시간측정, Preview·최종Vercel/G5/G6는본보고서의PASS대상이아니다. 48h 정확정각은domain독립테스트증거와합쳐판정해야한다. 경영주상세의 `awaiting_order_review` 원문코드노출은 비차단카피개선으로root에전달했다. 화면의핵심한글상태·다음행동은제공되지만최종카피검토에서정리할필요가있다.
