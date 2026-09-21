# D03 최종 데이터 독립 표본 검증

- reviewer: `/root/research`; 2026-09-21
- consumed_context_hash: `e8d6eb6ffef8765544e3aeeeb9c27b1e98f0c7cb5131202712ec4d32d806ea99`
- 판정: **PASS — 최종248 마스터·9점포 전달/무결성 및 제한된 원문 표본 범위**. 앱 전체 품질, 모든248 사실 전수검증, live 모델/브라우저 지도는 본 판정이 아님.
- 읽기 대상: root `data/seed/{products,stores,config}.json`, 연구 provenance, domain worktree `public/demo/{catalog.json,manifest.json,seed.sqlite}`. SQLite는 mode=ro로 읽었고 초기화 검사는 sql.js 메모리 사본에서 수행했다. 구현·원본 데이터 변경 없음.
- 독립성: 기존220 상품 및 점포 자료는 본 검토자가 생성하지 않아 독립 검증. 최근28은 본인이 작성했으므로 자체검사이며 독립 검증으로 세지 않는다. 최근28의 독립 표본은 method_auditor의 아래 별도 증거로 구분.

## 버전·전달·중복 실행 결과

최종 확인 manifest: schema-v2 / seed-248-v2 / catalog-248-v1 / ADR002+004+005.

- catalogHash `f2696abe92521e3ff8f9ab43cb36a1d297a6fd23d272e239605b49fab4343b1e`
- seedHash `4cb10e899c9706bb0a9278b458bd7b70d3c34bf28f649b62ffae0894794a2b45`
- 제품248, SKU248 고유, NFKC/문장부호·공백 정규화 brand+name+size248 고유. 점포9, ID9/주소9 고유. 단위/맛이 다른 동일 브랜드를 중복 SKU로 제거하지 않았다.
- root 마스터와 public catalog JSON 전체 동등성 PASS. compact JSON SHA256과 manifest catalogHash 일치. SQLite 파일 SHA256과 manifest seedHash 일치.
- 248개 name/category/brand/size/flavor/sourceOrigin 및 9개 점포 name/address/lat/lng/sourceOrigin을 SQLite row와 전수 대조 PASS. 마스터→배포 JSON→SQLite 전달 중 출처 metadata 손실 없음.
- SQLite `PRAGMA integrity_check=ok`, `foreign_key_check=[]`.
- 전 제품/점포 sourceIds/sourceUrls/researchCaseIds 존재. 기존220 trendConfidence는 모두 unverified. 크기 미확인 null과 2입/4입 패키지 단위가 최종 마스터에서 유지됨. 속성·별칭을 근거 없이 증식하지 않음.

검토 중 builder가 ADR005 schema-v2로 seed를 갱신했다. 위 마지막 hash에 대해 manifest/file 일치와 메모리 초기화를 다시 확인했으며 초기 schema-v1 hash를 최종 증거로 재사용하지 않았다.

## 기존220의 독립 원문 표본 8개

웹 원문을 실제 열람하고 동적 본문이 도구에서 누락되면 같은 공개 URL/공식 상품 선택기 응답을 별도 읽기 요청으로 확인했다. 단순 검색 결과 문구만으로 확인하지 않았다.

| 상품 | 직접 출처 | 확인한 필드·한계 |
|---|---|---|
| 오뚜기밥210g | [오뚜기몰3043](https://www.otokimall.com/front/product/3043) | 공식36개 묶음명의 개당210g. 카탈로그는 모의1단위로 정규화했고 묶음 가격을 복사하지 않음. |
| 진라면 매운맛120g | [오뚜기몰503](https://www.otokimall.com/front/product/503) | 공식120GX5명칭의 제품·맛·개당중량 일치. |
| 옛날 쌀떡국(용기)166.6g | [오뚜기몰841](https://www.otokimall.com/front/product/841) | 명칭·소수중량 일치. 웹 캐시 시점이 오래된 사실을 현재 판매 근거로 확대하지 않음. |
| 스위트앤젤 밀감90g | [오뚜기몰3150](https://www.otokimall.com/front/product/3150) | 공개 상품 본문 명칭·90G 일치. |
| 꼬리까지 가득 찬 팥붕어빵480g | [오뚜기몰2452](https://www.otokimall.com/front/product/2452) | 공개 상품 본문480G 일치. 개별 붕어빵 한 개가480g이라는 주장 아님. |
| 꽃게랑 오리지널70g | [빙그레76](https://www.bing.co.kr/product/detail?PDT=76) | 공식 맛 선택기 오리지널 및 공개 get_volume_list(prod_idx212)의70g 일치. |
| 바나나맛우유240ml | [빙그레123](https://www.bing.co.kr/product/detail?PDT=123) | 공식명칭 및 공개 get_volume_list(prod_idx410)의240ml 일치. |
| 검은깨 콩맛190ml | [빙그레247](https://www.bing.co.kr/product/detail?PDT=247) | 공식 제품명 검은깨 콩맛 및 get_volume_list(prod_idx1092)의190ml 일치. web 도구 접근 오류 후 동일 공개 페이지 GET/공식 선택기 읽기로 검증. |

기존220은 오뚜기133·빙그레87로 출처 제조사 편중이 있다. 8개 기존 대분류와 최근 편의점 상품을 합쳐17개 연구 분류가 존재한다. 분류는 research_classification이며 제조사 공인 taxonomy나 시장 대표 표본이라고 주장하지 않는다. 기존 `샌드위치·버거·빵`과 최근 `샌드위치`처럼 의미가 인접한 분류가 있으므로 자연어 제외 조건의 SKU 집합 정확성은 N01/E01에서 별도 검증해야 한다. 이 자료만으로 “샌드위치는 빼고” 동작을 통과시키지 않는다.

## 점포 독립 표본 2곳 / 구조9곳

전9점포 좌표가 정상 숫자이고 서울 지역 범위 안이며 주소·ID가 고유하다. 아래2곳은 출처의 공개 JSON-LD Place/GeoCoordinates/도로명주소를 직접 대조했다.

- [GS25군자](https://sav.purpleo.kr/article/39204): 서울특별시 광진구 동일로34길17, lat37.5499659981206/lng127.069573880996 일치.
- [GS25S어린이대공원역점](https://sav.purpleo.kr/article/36859): 서울특별시 광진구 능동로210, lat37.5478726441874/lng127.074551058147 일치.

출처는 공공 상권자료 재배포 사이트이며 GS 공식 실시간 점포 API가 아니다. 공개 보고 좌표의 일치만 확인했고 현장 측량·현재 영업·실제 재고·서비스 가입은 검증하지 않았다. `public_data_redistributor`, `reported_public_coordinates_not_field_surveyed`, `operatingStatus=unverified` 표시가 유지된다. 좌표를 생성하거나 범용 geocoding/POI 수집을 하지 않았다.

## 최근28 자체검사와 별도 독립 표본

본인이 작성한 원본 recent-products.json28건은 자체확인 대상으로 최종 필드 전달을 대조했다. 신규 SKU 자체 생성·근거 없는 인기 증식은 하지 않았다. GS리테일 직접 보도자료9개의 상품명/보도일/명시 출시일, 미확인 size=null, 실제 GS 현재 취급/가격 미확인, 과거 판매량의 기간/범위를 구분한다.

method_auditor의 [R02 독립 표본 기록](eval-evidence.md)은 3개 직접 원문/6개 상품에 대해 PASS다: 마들렌모양 버터모찌(2입), 스마일 루씨허버터떡4입, 이달의도시락7월복날편, 훈제오리&장어, 더큰오리매콤양념구이, 라라스윗그릭복숭아쫀득바. 해당 검토는 팩 개수/부분중량/과거 출시·현재 취급 미확인/기존 시리즈 실적의 신상품 전가 금지를 대조했다. 본 보고서가 이를 자체 독립 전수검증으로 재분류하지 않는다.

## 합성/모의 데이터 분리 실행

배포 seed.sqlite에는 고정 상품248·점포9만 있고 actors/conditions/거래는0이었다. 실제 sql.js로 해당 파일의 메모리 사본을 열고 DomainEngine 초기화를 독립 실행한 결과:

- 상품248·점포9 유지, 합성 고객30명·점포별 합성 경영주9명.
- 희소 점포 조건578개, snapshot 모든 condition.simulated=true.
- 초기 요청0·주문0, 모든 자동발주 정책off, FK위반0.
- `DEMO-CUSTOMER-*`/`시연 고객`, `시연 경영주`로 실제 인물 관계·구매 이력을 만들지 않음.
- 가격·재고·capacity는 seed 계산의 모의값이며 출처 웹의 가격을 도입하지 않음. 마스터 사실과 session별 거래를 별도 테이블로 유지.

이 검사는 Node에서 실제 sql.js/WASM+SQLite 초기화를 실행했지만 브라우저 IndexedDB 재개·지도 네트워크·고객/경영주 거래 시나리오를 실행한 증거는 아니다. 다양한 정상/제한/미식별 거래는 domain factory 시나리오 및 상위 통합에서 별도로 확인해야 한다. data 파일 일치만으로 최종 G3~G6나2400호출 예산을 승인하지 않는다.
