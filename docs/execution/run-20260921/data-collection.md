# D01 공개 데이터 원본 수집 — 2026-09-21

작성자 preflight_builder. 범위는 공개 원본 조사·후보 정규화이며 DB/schema/seed/holdout을 작성하지 않았다. `context-app-v2.json` SHA-256 `1cc5b18da57bdfb492d3f2cf1e09aedb8357e72e0be951c680446583417134ef`와 ADR-002/003 적용을 ACK했다. 상품 식별→점포 선택→동의·확약→보수적 발주 목적을 보존하며 실제 GS 취급·재고·가격을 주장하지 않는다.

최종 후보 **414 SKU / 8개 분류 / 실제 위치 참고 9점포**. 425개 수집 후보에서 파트너 브랜드 미확인 9개와 공백 중복 2개를 제외했다. 자체 원본계약 검사 PASS이며 독립 검토 대기다. 원본 카탈로그 hash `0a148016ae38dd23d2dadf9e1757b8125e6e992eadc36caae493064aec6c1dd0`, 점포 hash `f421e2a650b432066b708b0afd3851d173f6e91fea3535b28541f0a0037d4c85`.

후속 context-app-v3 SHA `e8d6eb6ffef8765544e3aeeeb9c27b1e98f0c7cb5131202712ec4d32d806ea99`도 확인하고 ACK했다(정책 변경 없음).

## 출처와 수집 범위

- [오뚜기 공식 상품 분류](https://www.otoki.com/product/product_cat)에서 연결된 [오뚜기몰](https://www.otokimall.com/front/product/category/23)의 공개 상품목록을 사용했다. 6개 분류의 첫 페이지(페이지당 80, 사이트가 제공하는 40/60/80/100 선택 범위)만 조회했다. 공개 UI 스크립트가 사용하는 읽기 전용 POST `/front/product/product_list.ajax`로 실명·규격을 수집했다. 식품 동일 이름·규격의 다중팩은 한 후보로 정규화했다. 상품 상세 페이지 URL과 원문 상품명이 각 후보에 있다. 제조사 소유 몰이라는 사실은 개별 파트너 상품의 브랜드를 자동 증명하지 않으므로 식별된 파트너 상품은 제외했고, 나머지 오뚜기 umbrella brand도 `medium_catalog_owner_inference`로 표시했다.
- [빙그레 공식 상품목록](https://www.bing.co.kr/product/list)의 공개 UI가 표시하는 25개 상품군을 한정 조회했다. UI에 실제 나타난 family/product 식별자와 공식 공개 규격 selector만 사용한다. 개별 맛/용량의 존재를 확인한 경우만 독립 후보로 둔다. 이름만 임의로 바꾸어 SKU를 늘리지 않는다.
- 모든 후보의 `trend_confidence`는 `unverified`다. 상품목록 게재는 인기·신상품·품절 증거가 아니다. 최근 20~30개 관심상품 요구는 별도 날짜 있는 보도자료 연결이 아직 필요하다.
- [전국 편의점 지도 GS25군자](https://sav.purpleo.kr/article/39204)와 이 페이지가 직접 연결한 인근 GS25 페이지의 공개 JSON-LD를 소량 조회했다. 사이트가 표시한 소상공인시장진흥공단 상가정보를 재게시한 2차 자료다. 점포명·도로명주소·지번·좌표·원본 상가업소번호·페이지 갱신일을 기록했다. 원 공공데이터 전체 파일을 내려받거나 키를 요구하는 서비스를 사용하지 않았다.

`data/research/sources-metadata.json`과 `stores-sources-metadata.json`에 정확한 URL·POST 매개변수·확인일·응답 SHA-256이 있다. 원문 전체와 상품 이미지는 저장소/배포물에 넣지 않았다. 일시 캐시는 `/tmp/wanna-gs-data-20260921`에 있고 인증정보가 없다. 요청은 순차·1.05초 간격·캐시 재사용으로 제한했다. 공개 식별 사실의 최소량만 정규화했으며 사이트의 콘텐츠 전체에 대한 재배포 권한을 주장하지 않는다.

## 제외·접근 제한

GS25 공식 브랜드 페이지는 차단 응답이어서 우회하지 않았다. 별도 편의점 상품 집계 사이트는 2026년 9월 GS 목록 1,855건을 표시했지만 약관의 무단 대량수집 금지를 확인해 자료원에서 제외했다. 보호 API·계정·토큰·우회 프록시는 사용하지 않았다. 상품의 모든 실제 가격은 결과에서 제외했다.

## 실제 위치 선택

최초 연구의 구의동 공공 PDF는 주소만 확인되어 좌표를 추정하지 않았다. docs/19가 허용하는 ‘다른 검증 가능한 점포 선택’에 따라 약 0.8km 범위 군자동·화양동·인접 송정동의 공개 좌표 보유 점포 9곳으로 바꿨다. 동일 주소 중복 자료 2건은 제외했다. 같은 `지에스25화양` 상호 2건은 주소와 좌표가 서로 달라 각각 유지했다. 점포 ID로 구분하고 목록에 도로명주소를 반드시 표시한다.

이는 위치 참고 후보이며 현재 영업 중·공식 제휴·해당 상품 취급을 확인했다는 뜻이 아니다. 자료 페이지 갱신일은 2025-04-27이고 확인일은 2026-09-21이다. 좌표는 공개 자료의 수치를 보존했으며 현장 측량 정확도를 주장하지 않는다. 가상 고객·경영주 및 availability/가격/재고/결제는 후속 seed에서 별도 simulated로 작성해야 한다.

## 필드·정규화 계약

`catalog-candidates.json`: `sku`(DEMO 내부ID), `name`, umbrella `brand`, `category`, `size`, `flavor`(직접 이름에서 관찰되거나 null), `aliases`(빈 배열), `attributes.observed_name_terms`, `origin`, `source_id/source_url`, `raw_name`, `field_origin`, 상품·유행 신뢰도와 버전. `attributes`는 상품명에 실제 나타난 단어만 제공하며 알레르기·영양 적합성·인증·비건 여부로 확대 해석하면 안 된다. `flavor:null`은 미확인이다.

`stores-candidates.json`: `store_id`, `name`, `brand`, 도로명/지번주소, `lat/lng`, `source_id/source_url`, 공공 원본 record ID, 페이지 발행/갱신일, 확인일, 위치 신뢰도, `current_operating_status:unverified`. 원문 공개 상호를 임의 지점명으로 고치지 않았다.

`collect-public.py`, `collect-stores.py`는 읽기 전용 출처 수집기이고 `normalize-candidates.py`는 명백한 공백 중복·파트너 브랜드·카테고리 정리다. 원문 최초 상품명이 `raw_name`에 남는다. 최종 seed의 200 SKU 선택·카테고리 재배분·합성 상품 보완은 이 후보를 검토한 후 단일 schema/seed 작성자가 수행한다. 실제 상품 후보와 합성 도시락/김밥 등 확장은 origin을 섞지 않아야 한다.

## 검증 및 남은 게이트

원본 후보 수/카테고리/중복/출처 일치/좌표 범위에 대한 실행 결과는 `validation-summary.json`에 있다. 이는 DATA 사전작업이며 독립 data review, seed dry-run/rollback, sqlite 무결성, 앱 검색/점포 선택, 전체 eval 완료를 의미하지 않는다. 담당자 독립 표본검토가 뒤따른다.

공개 seed·catalog·클라이언트 자산에 보호 holdout 발화·정답·oracle·private fixture를 넣지 않는다. 이 작업자는 보호 holdout을 열거나 작성하지 않았고 상품 별칭도 아직 생성하지 않았다. 평가 담당자는 공개 마스터를 별도로 바인딩하되 같은 의미/상품/상태 family를 split 사이에 복제하지 않는다.

## 재현 명령

Python 3 + beautifulsoup4 환경에서 프로젝트 root 기준:

```sh
python3 data/research/collect-public.py
python3 data/research/collect-stores.py
python3 data/research/normalize-candidates.py
python3 data/research/validate-candidates.py
```

전체 재수집은 원본 갱신에 따라 새 후보 버전으로 취급한다. 현재 검증만 재실행하려면 마지막 명령만 사용한다. seed/앱 dependency나 lockfile은 변경하지 않았다.
