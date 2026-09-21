# 실행 조사 R20260921-v1

- 작업: P01 / 조사 담당 `/root/research`. 시작·확인·종료: 2026-09-21(KST).
- 상태: **초기 조사 초안 완료 / 독립 검토 대기**. 앱·전체 seed·자연어 평가 통과를 뜻하지 않는다.
- consumed_context_hash: `74bf125ebe9c8ed2f7933abb55b08c904400f3a7ba1319c395a2429c32c20679` (파일 SHA-256 재확인, ACK 전달).
- manifest: `CTX-20260921-BOOT-v1`, base SHA `3ef1ee3447ab3943527c4685949da4116bcf0566`.
- 적용: CORE-03/05/06/10/11/14/21/22/24/25/26, AC-30/31/32, D-40/44/45, ADR-001. 고객의 정상 요청과 보수적 발주·48시간 픽업을 유지한다.
- research_version: `R20260921-v1`; catalog/scenario/eval/seed: 아직 미생성. 아래 ID는 후보이며 실제 DB row가 아니다.
- 소유 파일은 이 문서뿐. PROGRESS/WORKPLAN 반영·독립 data reviewer/nl-evaluator 배정은 조정자에게 인계한다.

## 질문·범위·중단

1. 최신 상품과 한정/맛 변형에서 어떤 정확한 SKU 확인이 필요한가?
2. 고객의 탐색·재고 불일치·기다림, 경영주의 제한 공급·반복 문의 부담을 어떤 자료가 지지하는가?
3. 200개 독립 SKU와 실제 밀집 점포 8~12개를 출처·합성 구분을 유지해 확대할 수 있는가?
4. 고객/경영주 UX와 의미 family 평가에 어떤 정상·예외를 포함해야 하는가?

공식 상품 발표, 공공 점포 목록, W3C/지도 제공자 원문을 우선했다. 12개 본문 자료를 직접 열어 읽은 뒤 추가 반복 검색을 멈췄다. 공식 상품 발표가 전국 인기/현재 재고 증거는 아니다. 실제 사람 인터뷰·앱 내부 기능 실험은 수행하지 않았다. 시장 조사를 근거로 본부·레시피·사진·링크·실결제·외부 DB·다중 사용자 거래를 추가하지 않는다.

## 확인한 source records

모든 `checked_at`은 2026-09-21. 직접 인용 없이 필요한 사실만 아래 자체 문장으로 요약했다. 뉴스와이어는 원문에 **뉴스 제공 GS리테일**을 확인했으므로 기업 제공 자료이며 독립 언론조사로 세지 않는다. 동일 보도자료 재전송을 독립 근거로 합산하지 않았다.

| ID / 종류 | 원문·발행/관찰 시점 | 직접 확인한 사실 / evidence_scope | 한계·confidence |
|---|---|---|---|
| S01 / official_product | [한정선 요거트 찹쌀떡](https://www.newswire.co.kr/newsRead.php?no=1041771), GS리테일, 2026-09-03; 행사 08-28 | 한정선·로로멜로 협업 냉동 요거트 찹쌀떡 출시. 두 행사장 총 400개 조기 소진 발표. `product_identity`, 한정된 `trend` | product high. 행사 소진은 기업 발표 medium; 전국 품절·현재 점포 재고 unverified. |
| S02 / official_product | [라라스윗 쫀득바](https://www.newswire.co.kr/newsRead.php?no=1041291), GS리테일, 2026-08-27; 5월 말~8월 | 메론·망고 2종, 8월 25일 그릭 복숭아 추가 출시. 기존 2종 누적 400만개는 업체 판매 집계. 스크류바/죠스바 젤리 변형도 별개 상품으로 언급. | product high; 기업 집계 범위 trend medium. 건강 적합성·모든 맛/규격의 속성 전이 금지. |
| S03 / official_product | [8월 이달의 도시락 혜자편](https://www.newswire.co.kr/newsRead.php?no=1039966), GS리테일, 2026-08-05 | 월별 한정 판매 시리즈와 8월 혜자편 구성 공개. `product_identity`, 판매 기간 구분 | 역사적 상품 사실 high. **9월 현재 발주 가능 근거 아님**. 시리즈 누계와 특정 SKU 판매량 구분. |
| S04 / official_product | [춘식이 꼬북칩 고구마탕후루맛](https://www.newswire.co.kr/newsRead.php?no=1039781), GS리테일, 2026-08-02; 출시 예정 08-06 | 춘식이·꼬북칩 협업 맛 변형, 꼬깔콘 마성옥수수맛·미쯔 블랙 요거트 언급. `product_identity`, 협업/맛 혼동 | product high(명칭). 용량 미확인. 브랜드/캐릭터만 같은 다른 SKU를 동일 상품으로 연결하지 않음. |
| S05 / official_product | [유어스로얄밀크티](https://www.newswire.co.kr/newsRead.php?no=1039749), GS리테일, 2026-07-31; 출시 07-29, 집계 1~6월 | 커피 중심 컵음료에서 밀크티 선택 공백을 분석해 PB 컵 밀크티 출시. 홍차 분말·우유 사용 공개. `product_identity`, 미충족 니즈 | product high. 상품군 성장 수치는 회사 집계 medium; 무카페인·저당·알레르기 안전 주장 근거 없음. |
| S06 / reporting | [민음사빵 탐색/재고 경험](https://www.mt.co.kr/amp/society/2026/09/08/2026090709475845306), 머니투데이, 2026-09-08; 8월 말~9월 초 | 여러 매장 탐색·앱 재고와 현장 차이 경험, 무작위 책갈피, 한 점주의 공급보다 많은 방문 문의가 보도됨. `user_need`, `stock`, `merchant_exception` | 특정 사례 관찰 medium; 전체 고객 대표성 low. 현재 공급/전국 재고/정확 SKU 규격 unverified. 개인 이름·인용·프로필은 dataset에 복제하지 않음. |
| S07 / official_product(기업 업무 발표) | [52g 현장 중심 AX](https://www.newswire.co.kr/newsRead.php?no=1007981), GS리테일, 2025-03-23; 협의체 03-19 | 흩어진 고객 의견 정리와 경영주 정보 전달 개선을 추진 과제로 공개. `merchant_need`, `unmet_need` | 과제 존재 high; 실제 경영주 시간 절감 효과·성과 수치 unverified. |
| S08 / reporting | [GS리테일 AI 활용](https://www.etnews.com/20250910000272), 전자신문, 2025-09-21 | FF 상품군 자동발주와 점포 운영 정보 제공 사례를 보도. `merchant_workflow` | 2025년 보도 medium. 현재 GS 내부 알고리즘/권한/API 근거가 아니며 우리 데모는 사용자 승인 정책과 유효 수요로 한정. |
| S09 / official_store(지자체 공개자료) | [광진구 2025.6 종량제 봉투 판매소](https://www.gwangjin.go.kr/editorUpload/files/000006/20250625153633250_WBFHJ02K.pdf), 광진구청, 문서 기준 2025-06 | GS25 점포명·도로명 주소를 다수 수록. 아래 10개 후보는 PDF pp.2~3에서 직접 확인. `store_identity`, `address` | 해당 시점 명칭/주소 high, 현재 영업 unverified. 좌표 없음. 전화번호/인적 정보 수집 제외. |
| S10 / official_technical | [WCAG 2.2 상태 메시지 이해](https://www.w3.org/WAI/WCAG22/Understanding/status-messages.html), W3C, 발행일 미표기/현행 열람 | 대기·검색 결과·진행·오류 등의 상태 변화는 포커스 이동 없이 보조기술이 인지하도록 표현. `UX`, `accessibility` | 기준 해석 high. 제품 접근성·사용성 통과는 실제 구현 QA 필요. |
| S11 / official_technical | [Nominatim 이용 정책](https://operations.osmfoundation.org/policies/nominatim/), OSMF, 발행일 미표기/현행 열람 | 최대 초당 1회, 식별 가능한 요청, 결과 캐시, autocomplete/체계적 POI 수집 금지. LLM 생성 범용 주소검색 서비스 금지 및 의식적 개발자 선택 요구. | 서비스 채택 결정 아님. 자동 geocoding 코드는 이번 조사에서 만들거나 실행하지 않음. |
| S12 / official_technical | [OSM raster tile 이용 정책](https://operations.osmfoundation.org/policies/tiles/), OSMF, 발행일 미표기/현행 열람 | 출처 표시·유효 referer·HTTP 캐시 준수, bulk/prefetch/offline 다운로드 금지, best-effort 제공. | 지도 제공자 최종 선택·연결 검증 미실행. CI 지도 전역 순회 금지, 목록 fallback 별도 QA. |

### 접근 실패·채택하지 않은 근거

- 구 GS25 [행사상품](https://gs25.gsretail.com/gscvs/ko/products/event-goods?uiel=Mobile), [우리동네GS 소개](https://gs25.gsretail.com/gscvs/ko/store-services/woodongs?uiel=Mobile), [매장찾기](https://gs25.gsretail.com/gscvs/ko/store-services/locations)를 실제 열면 brand/gs25로 이동하고 본문 추출은 1줄이었다. 검색 결과에는 과거 상품·기능이 남지만 현재 데이터 획득 증거로 채택하지 않는다. 후속 담당이 실제 브라우저로 공개 UI를 확인하거나 제조사/공공 대체 자료를 사용한다.
- 검색된 광고 패키지 점포 목록은 원문 열기 오류와 발행 주체 검증 부족으로 점포 seed 근거에서 제외했다.
- 공개자료를 읽은 사실과 snapshot/checksum 확보는 다르다. 전체 source 원문을 저장하지 않았으며 이 문서의 최종 SHA가 조사 산출물 checksum이다. 후속 seed에는 사용한 정규화 사실 입력의 checksum을 기록한다.

## 조사 사례와 목적 보존

| research_case_id | 필요·관찰 / source | 상품·trend 신뢰 / 미확인 | 설계 연결·금지 결과 |
|---|---|---|---|
| RC-01 | 최신 협업 냉동 디저트를 정확히 찾기 / S01,S02,S04 | 확인된 명칭 high; 식감/캐릭터만으로 단일 SKU 결정은 unverified | 이름·맛·형태 차이 표시, 모호하면 선택. 모든 모호 입력 거절·첫 후보 자동 확정 금지. |
| RC-02 | 이름을 몰라도 음료 특성으로 찾기 / S05 | 홍차·우유 포함 high; 무카페인/저당 unverified | 확인 속성만 사용. 필수 조건을 모르면 확인 필요 또는 적합 대안 없음. |
| RC-03 | 한정 상품의 과거 인기와 지금 요청 가능 구분 / S03,S06 | 과거 출시 high/medium, 현재 판매 unverified | 카탈로그 존재·재고 0·미취급·공급 제한·조건 없음·API 실패를 별개 표시. 모의 공급 가능은 simulated임을 표시. |
| RC-04 | 여러 매장 탐색·불확실한 대기 감소 / S06,S09 | 제한된 탐색 사례 medium; 일반 빈도 low | 한 점포를 고객이 명시 선택, 확보 전 예약/픽업으로 표현하지 않음. 전국 품절/입고 시각 창작 금지. |
| RC-05 | 상품과 무작위 동봉품 요구 구분 / S06 | 동봉품 무작위 보도 medium; 정확 빵 SKU/규격 추가 확인 | 불가능한 부가 조건은 보장하지 않고 원래 니즈 보존. 책갈피를 새 SKU로 만들지 않음. |
| RC-06 | 공급 제한 때 문의/예외를 묶어 파악 / S06,S07,S08 | 현장 문의 사례 medium, 생산성 개선 효과 unverified | 상품 묶음→고객별 수량/동의/상태 상세. 확약만 집계, 관심 합산·건별 승인 강요 금지. |
| RC-07 | 결과·로딩·실패를 놓치지 않고 다음 행동 찾기 / S10 | 기술 근거 high; 실제 사용성 미검증 | 상태 텍스트/role=status, 실패 입력 보존, 정상 검색 복구. 색/토스트만으로 동의·기한 전달 금지. |
| RC-08 | 점포 위치 선택과 외부 지도 실패 회복 / S09,S11,S12 | 역사적 주소 high, 좌표/영업 미검증 | 공개 위치와 모의 재고 분리. 지도·목록 동일 store_id, 목록 fallback. 추정 좌표를 실제값으로 꾸미지 않음. |

모든 사례 `review_status=draft`, `privacy_and_quote=자체 요약`; 인터뷰 인용·실사용자 프로필은 수집하지 않았다. 48시간·FIFO·고객 동의·보수적 자동발주는 조사에서 새로 정한 정책이 아니라 기존 CORE 계약이다.

## 초기 상품 후보와 200 SKU 확대 경로

아래는 **확인된 명칭 후보**다. 규격이 원문에 없으면 null/미확인으로 남긴다. 임의 100g/200ml를 붙여 실제 SKU라고 하지 않는다. 실제 GS 상품코드 대신 `DEMO-*` 내부 ID를 쓴다. 출처 가격을 읽었어도 데모 판매가·매입가·재고·공급 조건은 전부 `simulated`로 만든다.

| candidate ID | 확인 명칭 | origin / source | seed 판단 |
|---|---|---|---|
| CC-01 | 한정선 요거트 찹쌀떡 | reference_verified / S01 | 최근 출시, 디저트 형태/브랜드 식별 |
| CC-02 / 03 / 04 | 라라스윗 메론 쫀득바 / 망고 쫀득바 / 그릭 복숭아 쫀득바 | reference_verified / S02 | 실재하는 3개 맛 변형, 분리 SKU 후보 |
| CC-05 / 06 | 스크류바 젤리 골드키위&딸기 / 죠스바 젤리 먹은 포도&피치 | reference_verified / S02 | 동일 브랜드 원제품과 변형 구별 |
| CC-07 | 이달의 도시락 혜자편(2026년 8월) | reference_verified_historical / S03 | 9월 실제 판매 주장은 금지. 역사/공급 제한 사례 후보 |
| CC-08 / 09 / 10 | 춘식이 꼬북칩 고구마탕후루맛 / 꼬깔콘 마성옥수수맛 / 미쯔 블랙 요거트 | reference_verified / S04 | 캐릭터·과자 브랜드·요거트 카테고리 차이 |
| CC-11 | 유어스로얄밀크티 | reference_verified / S05 | 컵음료, 홍차/우유 기반 특징 탐색 |
| CC-12 | 민음사 협업 빵 4종군 | reference_reported / S06 | 상품군 후보만. 정확 4종명/규격 확보 전 4 SKU로 삽입 금지 |

D04A는 ADR-001대로 위 표의 일부와 명확히 표시한 합성 경계 데이터를 같은 importer 계약으로 준비할 수 있다. 전체 데이터 완료는 D04B/D05에서 별도 판정한다.

1. 위 최근 공식 상품과 제조사/GS 공개 UI 표본을 출발점으로 19번의 8개 카테고리 배분(25/25/25/30/25/30/20/20)을 채운다. 총 200개 이상 **정규화 명칭+맛+규격이 독립적인** SKU를 확보하고 단순 복제는 금지한다.
2. D04B 담당은 GS SPA 공개 상품 UI와 제조사 공식 상품 페이지를 기능별로 필요한 소량 열람한다. 자동 내부 API 탐색·대량 수집을 필수로 두지 않는다. 정확 브랜드/맛/규격을 확인하지 못하면 해당 필드 `unverified` 또는 전적으로 구별되는 `synthetic_product`로 표시한다.
3. 최근 관심/신상품 목표 20~30개 중 본 조사로 확보한 것은 11개 명칭 후보뿐이다. 나머지는 최신 기업 발표 원문에서 확인하거나 부족분을 `synthetic_scenario`로 표시한다. 합성값을 실제 최근 유행 20~30개 확보로 세지 않는다. 출시는 `launch_announcement`, 판매는 `vendor_sales_report`, 언론 경험은 `reported_observation`으로 분리한다.
4. 모든 row에 research_case_id/source_id/source_url/checked_at/field_origin/product_confidence/trend_confidence를 연결한다. 실재 상품명에 임의 변형을 붙여 reference_verified SKU를 늘리지 않는다.
5. 실제 점포×SKU 취급·가격·재고는 모의 희소 20~35% 기본안. 정상 시연 상품은 2곳 이상, 희소 품목은 1~3곳. 누락된 조건 row는 미취급의 증거로 쓰지 않는다. 비율 조정 시 PLAN-READY ADR 검토.
6. 합성 고객 약 20명과 점포별 합성 경영주를 매핑한다. 실제 점주 관계·실제 이용 기록은 주장하지 않는다. importer의 반복 안전성·FK·카테고리·중복·양수 가격 검사를 구현한 뒤 독립 검토한다.

## 실제 점포 10개 후보와 좌표 확보 경로

지역 제안: **서울 광진구 구의동**. 근접한 주거/역 주변 점포를 한 목록으로 비교할 수 있고 S09의 공식 공개 주소를 10곳 확보했다. 모두 S09 문서 pp.2~3, 행 139~164/201~206의 역사적 주소 근거이며, 현 영업/재고는 확인하지 않았다.

| 후보 ID | 점포명 | 공개 주소(서울특별시 광진구) |
|---|---|---|
| ST-01 | GS25 구의무학점 | 아차산로51길 86 |
| ST-02 | GS25 구의새한점 | 아차산로57길 41 |
| ST-03 | GS25 구의창원점 | 자양로30길 79 1층 |
| ST-04 | GS25 구의행복점 | 광나루로 532 1층 1호 |
| ST-05 | GS25 광진구의점 | 자양로18길 65 |
| ST-06 | GS25 구의미가로점 | 아차산로51길 41 |
| ST-07 | GS25 광진우체국점 | 강변역로 2 광진우체국 1층 |
| ST-08 | GS25 광진진넥스점 | 광나루로 604 진넥스 베르디엠 |
| ST-09 | GS25 구의바우점 | 아차산로65길 78 바우하우스 101호 |
| ST-10 | GS25 구의성진점 | 구의강변로 45 성진프라자 |

후속 데이터 담당은 (a) GS 공개 매장 UI 또는 최신 공공 데이터로 현재 명칭/주소 대조, (b) 공개 좌표가 있는 점포를 우선 선택, (c) 부족하면 허용된 소량 geocoding을 명시적으로 선택해 결과 캐시, (d) WGS84 범위/lat-lon 순서/주소 일치·정밀도를 독립 검증한다. 지도 공급자가 없다는 이유로 외부 DB·유료 지도 계정을 새 선행조건으로 만들지 않는다. 선택한 점포의 좌표 근거가 없으면 미검증으로 남기고 전체 점포 gate는 PASS하지 않는다.

**Nominatim은 자동 채택하지 않는다.** 현행 [이용 정책](https://operations.osmfoundation.org/policies/nominatim/)은 초당 1회 이하, 식별 가능한 요청, 단일 기기/스레드, 캐시, attribution을 요구하며 자동완성·체계적 POI 수집 및 LLM 플랫폼의 범용 지오코딩 제공을 금지한다. 특정 데모용 소량 좌표 획득도 담당자가 해당 정책을 검토·선택한 뒤 수행한다. 실제 좌표 대신 임의 근사값을 사용하면 synthetic으로 표시하며 최종 실제 위치 요구를 대체하지 않는다.

## 시나리오·eval family 연결

모든 발화는 `synthetic_expansion`, 공개 **dev/demo 전용**이다. status=`hypothetical_unverified`, scenario_version=`SC-R20260921-v1`; 아래는 실행 계획이며 실행된 테스트가 아니다. 역할은 DEMO-CUSTOMER-001 등과 선택 점포의 DEMO-MERCHANT 계정. 실제 초기 상태·가격·수량·예산·clock은 importer/domain factory로 주입한다.

| scenario / family / research | 합성 목표/발화와 UI 단계 | 허용·금지 및 DB/event/UI oracle | gate / eval family |
|---|---|---|---|
| SC-01 / SF-EXACT / RC-01 | “라라스윗 망고 쫀득바 찾고 있어요” → 찾기→후보 확인→수량·점포·동의→요청 | CC-03 존재 ID만, 취소 시 거래 0. 정상 exact 요청이 성공해야 함 | G1~G6 / EF-C-EXACT |
| SC-02 / SF-FLAVOR / RC-01 | “그 쫀득한 라라스윗 아이스크림” → 맛 후보 비교→고객 선택 | 후보 차이 표시, 임의 메론 선택 금지, 불필요 반복 질문 측정 | G1/G3/G4/G5 / EF-C-CLARIFY |
| SC-03 / SF-ATTRIBUTE / RC-02 | “커피 말고 홍차 들어간 컵 음료” → 검증 속성 후보 | CC-11 후보 가능. “무카페인” 추가 시 근거 없는 적합 주장 금지 | G1/G3/G5 / EF-C-CONSTRAINT |
| SC-04 / SF-STATE / RC-03,04 | 같은 SKU에 재고 0/공급 가능, 미취급, 조건 누락, API timeout 각각 주입 | state별 다른 안내. timeout을 니즈/품절로 저장하지 않음. 재고 0이어도 공급 가능 정상 요청 보존 | G1~G6 / EF-C-STATE |
| SC-05 / SF-SUBSTITUTE / RC-01,02 | 원상품 미확보에서 다른 맛 제안→거절→원요청 복귀→새 후보 확인 | 거절/노출만으로 원상품·동의·순번 불변. 대체 요청은 새 동의, 중복 수요/발주 0 | G1~G6 / EF-C-ALTERNATIVE |
| SC-06 / SF-EXTRA / RC-05 | “빵은 고를게요, 원하는 책갈피도 확정해 주세요” | 확인되지 않는 부가 조건 보장 금지. 상품 확인 흐름/미충족 원문 단서 보존 | G1/G3/G4/G5 / EF-C-UNSUPPORTED |
| SC-07 / SF-GROUP / RC-06 | “이번 묶음에서 아이스크림은 빼고 예산 안에서” → 변경안→한 번 승인→결과 요약→고객 상세 | 이번만 변경, 집계 수량=허용 고객 상세 합. 성공/보류 혼합 요약, 건별 모달 강요 0 | G1~G6 / EF-M-SCOPE |
| SC-08 / SF-POLICY / RC-06 | “앞으로도 예산 안에서 자동 발주” → 지속 정책 승인→실행→반복→해제 | 명시적 승인 전 저장 0. 유효 미확보 수요·예산·MOQ/공급 제한 준수. 승인 정책 정상 성공도 필수 | G1~G6 / EF-M-AUTO |
| SC-09 / SF-STALE / RC-06 | 승인안 생성 뒤 고객 취소/예산 감소/정책 해제, 같은 명령 2회 | 실행 직전 재검사, 새 수요에 과거 승인 재사용 금지, 주문 1회 이하 | G1/G2/G3/G5/G6 / EF-M-STALE |
| SC-10 / SF-PICKUP / RC-04,07 | 공급 확보→모의결제 실패/성공→입고→픽업 알림→48시간 직전/정각/직후 | 실패를 예약 성공으로 표현 금지. 알림 생성+48시간, 재전송 연장 금지, 입고 전 만료 금지 | G1~G6 / EF-LIFECYCLE |
| SC-11 / SF-RECOVERY / RC-07,08 | 검색 오류/지도 실패→입력 유지/목록 선택→재시도→정상 요청 | 오류 role/status, 브랜드 ‘원하지쓰’ 가시성, 360/390px 고객·1280px 경영주. 포커스/CTA 가림 없음 | G4/G5/G6 / EF-UX-RECOVERY |

각 테스트 case는 `RC → CC/ST → SC/SF → EF → eval_case_id`를 저장한다. 동일 상품/의도/상태의 표현·오타·번역은 하나의 split_group이다. 이 문서에 노출된 family 발화는 보호 holdout으로 쓰지 않는다. 독립 nl-evaluator가 새로운 상품/조건 조합의 family를 큐레이션하고 정답·정확 발화는 구현자/실험자에게 전달하지 않는다. taxonomy 공유는 가능하다. 점수 기준/분모/편의성 허용폭은 측정 전 ADR로 정하고 두 독립 검토를 받는다.

## 준비 판정과 인계

작성자 판정: **ready_with_hypotheses 제안, 독립 검토 전**. 고객 탐색/대기, 경영주 집계/제한 공급, 상품/트렌드, UX/지도의 초기 근거와 확대 경로를 확보했다. 현재 데이터셋 규모는 200개가 아니며 점포 좌표·전체 카탈로그·실험 split·브라우저 UX·API 연동은 미실행이다.

다음 담당/완료 조건:

- data reviewer: S01~09 원문/날짜/명칭·역사적 주소, 실제/합성 필드·규격 누락·희소 배분 검토. 자료가 stale이거나 지역 좌표 접근이 불가능하면 검증 가능한 다른 점포로 교체 기록.
- nl-evaluator: dev/validation/holdout family 독립성, 긍정 성공·모호·미식별·대체 거절·정책 범위·오류 분포 검토. 현재 split hash/분모 없음, 실행기 생성 시 고정.
- UX 담당: 26번 공식 앱/첨부 이미지를 실제로 열어 시각 매핑하고 S10 기반 로딩·결과·실패 동작 구현. 조사 문서는 실제 QA가 아님.
- domain 담당: 위 SC의 권한/동의/중복·FIFO·48시간 oracle을 기존 계약에 연결. 조사 자료로 정책을 몰래 변경하지 않음.
- coordinator: 독립 검토 결과와 자료 revision을 PROGRESS/WORKPLAN에 연결; D04A 기반 개발과 D04B 확장을 분리.

추가 검색은 특정 SKU의 규격/현행 여부 불명, 주소·좌표 불일치, eval 실패가 실제 단서 누락을 지시하거나 API/지도 정책이 바뀌었을 때 해당 출처만 갱신한다. 출처 문구 자체를 학습/평가 정답으로 하드코딩하지 않는다. 변경된 상품·scenario·split만 관련 테스트 증거를 stale 처리한다.
