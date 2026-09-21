# 원하GS — 확정 DB 스키마

추출일: 2026-09-21
기준: PostgreSQL, STEP-1~4 구현의 migration 001~003 및 마이그레이션 실행기
업무 테이블 8개 + 내부 관리 테이블 1개. STEP-4는 스키마 변경 없이 조회 기능만 추가했다.

이 문서는 소스에 정의된 스키마를 사람이 읽는 표로 추출한 것이다. 운영 DB 덤프가 아니며 STEP-5·6·9의 미확정 설계를 포함하지 않는다. 아래 SQL 파일명은 원 프로젝트의 근거 표시일 뿐, 전달본에 SQL 파일은 포함하지 않는다.

## 공통 규칙

- 아래에서 NULL 허용을 표시하지 않은 컬럼은 모두 NOT NULL이다. PK 컬럼도 필수다.
- UUID 기본키에는 DB 생성 기본값이 없다. 애플리케이션이나 고정 seed가 값을 지정한다.
- 시간 컬럼은 TIMESTAMPTZ, 문서와 화면의 표시 기준은 한국 시간이다.
- 모든 FK는 ON DELETE RESTRICT이며 연쇄 삭제하지 않는다. ON UPDATE는 별도 지정하지 않아 PostgreSQL 기본 NO ACTION이다.
- 상태는 ENUM이 아닌 TEXT + CHECK다. 필수 문자열 중 공백 금지 표시는 `btrim(컬럼) <> ''` 제약을 뜻한다.
- PK·UNIQUE에는 PostgreSQL이 고유 인덱스를 생성한다. 일반 FK 컬럼에 인덱스가 자동 생성되는 것은 아니다.

## 1. stores — 점포

| 컬럼 | 타입 | 제약·기본값 | 의미 |
| --- | --- | --- | --- |
| id | UUID | PK | 점포 식별자 |
| store_code | TEXT | UNIQUE, 공백 금지 | 점포 코드 |
| name | TEXT | 공백 금지 | 점포명 |
| created_at | TIMESTAMPTZ | DEFAULT now() | 생성 시각 |

## 2. products — 상품

| 컬럼 | 타입 | 제약·기본값 | 의미 |
| --- | --- | --- | --- |
| id | UUID | PK | 상품 식별자 |
| product_code | TEXT | UNIQUE, 공백 금지 | 상품 코드 |
| name | TEXT | 공백 금지 | 현재 상품명 |
| image_url | TEXT | NULL 허용 | 이미지 경로 |
| order_unit_quantity | INTEGER | CHECK > 0 | 최소 발주 수량 한 묶음 |
| created_at | TIMESTAMPTZ | DEFAULT now() | 생성 시각 |

## 3. customers — 고객

| 컬럼 | 타입 | 제약·기본값 | 의미 |
| --- | --- | --- | --- |
| id | UUID | PK | 고객 식별자 |
| display_name | TEXT | 공백 금지, 중복 허용 | 표시 닉네임 |
| created_at | TIMESTAMPTZ | DEFAULT now() | 생성 시각 |

현재는 가상 고객 데이터다. 로그인 계정, 전화번호, 인증 정보는 정의하지 않았다.

## 4. recruitment_rounds — 모집 회차

| 컬럼 | 타입 | 제약·기본값 | 의미 |
| --- | --- | --- | --- |
| id | UUID | PK | 회차 식별자 |
| store_id | UUID | FK → stores.id | 모집 점포 |
| product_id | UUID | FK → products.id | 모집 상품 |
| target_quantity | INTEGER | CHECK > 0 | 모집 시작 당시 목표 수량 |
| status | TEXT | DEFAULT recruiting, 아래 값만 허용 | 모집 상태 |
| deadline_at | TIMESTAMPTZ | CHECK deadline_at > created_at | 모집 기한 |
| created_at | TIMESTAMPTZ | DEFAULT now() | 모집 생성 시각 |
| updated_at | TIMESTAMPTZ | DEFAULT now(), UPDATE 트리거 | 마지막 수정 시각 |
| supply_available | BOOLEAN | DEFAULT true | 모의 공급 가능 여부, STEP-2 추가 |

- 상태: `recruiting` 모집 중, `completed` 모집 목표 달성, `cancelled` 모집 취소, `expired` 모집 마감.
- `completed`는 발주·입고·수령 완료가 아니다. 마감 상태 값이 있다고 자동 마감 작업이 구현된 것은 아니다.
- 부분 고유 인덱스 `one_recruiting_round_per_product`: `(store_id, product_id) WHERE status = 'recruiting'`. 동일 점포·상품의 모집 중 회차는 최대 1개다.
- 일반 인덱스 `rounds_store`: `(store_id)`.
- `preserve_round` 트리거는 생성 후 store_id, product_id, target_quantity, created_at 변경을 막는다.
- `target_quantity`는 상품 발주 단위가 바뀌어도 유지되는 스냅샷이다. DB가 상품의 현재 발주 단위와 일치시켜 주는 것은 아니다.
- 데모 발주 기한은 모집 기한을 함께 사용한다. 실제 공급사 기한은 별도 정의가 필요하다.

## 5. customer_requests — 고객 요청

| 컬럼 | 타입 | 제약·기본값 | 의미 |
| --- | --- | --- | --- |
| id | UUID | PK | 요청 식별자 |
| round_id | UUID | FK → recruitment_rounds.id | 모집 회차 |
| customer_id | UUID | FK → customers.id | 신청 고객 |
| quantity | INTEGER | CHECK > 0 | 요청 수량 |
| status | TEXT | DEFAULT active, active/cancelled만 허용 | 현재 요청 상태 |
| created_at | TIMESTAMPTZ | DEFAULT now() | 최초 신청 시각 |
| updated_at | TIMESTAMPTZ | DEFAULT now(), UPDATE 트리거 | 마지막 수정 시각 |

- UNIQUE `(round_id, customer_id)`: 같은 고객은 같은 회차에서 하나의 행만 가진다.
- 일반 인덱스 `requests_customer`: `(customer_id)`.
- 취소 시 행과 수량을 남긴다. 재신청은 기존 행을 활성화한다. 개별 수정 이벤트 전체를 보관하는 테이블은 아니다.
- 인원은 active 행의 COUNT, 수량은 active.quantity의 SUM이다. 취소 요청은 집계에서 제외한다.

## 6. purchase_orders — 모의 발주 결과

| 컬럼 | 타입 | 제약·기본값 | 의미 |
| --- | --- | --- | --- |
| id | UUID | PK | 발주 식별자 |
| round_id | UUID | UNIQUE, FK → recruitment_rounds.id | 회차당 최대 한 건 |
| quantity | INTEGER | CHECK > 0 | 발주 당시 수량 |
| status | TEXT | accepted/rejected만 허용, 기본값 없음 | 접수 성공/실패 |
| reason | TEXT | NULL 허용, 아래 복합 CHECK | 실패 사유 |
| supplier_reference | TEXT | UNIQUE, NULL 허용, 아래 복합 CHECK | 모의 접수 참조번호 |
| created_at | TIMESTAMPTZ | DEFAULT now() | 결과 기록 시각 |
| order_mode | TEXT | DEFAULT manual, manual/auto만 허용 | 발주 당시 방식, STEP-3 추가 |

복합 CHECK:

- accepted: reason IS NULL AND supplier_reference IS NOT NULL.
- rejected: reason IS NOT NULL AND btrim(reason) <> '' AND supplier_reference IS NULL.
- supplier_reference는 성공 시 NULL이 아니어야 하지만 빈 문자열 금지 CHECK는 없다. UNIQUE 컬럼의 NULL은 여러 행에서 허용된다.
- round_id UNIQUE는 거절 결과에도 적용된다. 현재는 실패 회차 재발주를 지원하지 않는다.
- 기존 STEP-2 발주는 STEP-3 migration에서 manual로 채워졌다. 현재 설정을 바꿔도 이 값은 바뀌지 않는다.
- 실제 공급사 접수·결제·예약 테이블이 아니다. updated_at 및 DB 차원의 수정 금지 트리거는 없다.

## 7. store_product_order_settings — 현재 자동 발주 설정

| 컬럼 | 타입 | 제약·기본값 | 의미 |
| --- | --- | --- | --- |
| store_id | UUID | 복합 PK, FK → stores.id | 점포 |
| product_id | UUID | 복합 PK, FK → products.id | 상품 |
| auto_order | BOOLEAN | DEFAULT false | 자동 발주 여부 |
| updated_at | TIMESTAMPTZ | DEFAULT now(), UPDATE 트리거 | 마지막 설정 수정 |

PK는 `(store_id, product_id)`이며 별도 id는 없다. 회차가 아닌 점포·상품에 귀속되어 다음 회차에도 유지한다. 설정 행이 없으면 애플리케이션은 수동으로 해석한다.

## 8. order_setting_history — 설정 변경 이력

| 컬럼 | 타입 | 제약·기본값 | 의미 |
| --- | --- | --- | --- |
| id | UUID | PK | 이력 식별자 |
| store_id | UUID | 복합 FK 구성 | 변경 점포 |
| product_id | UUID | 복합 FK 구성 | 변경 상품 |
| previous_auto | BOOLEAN | 아래 CHECK | 변경 전 값 |
| next_auto | BOOLEAN | CHECK previous_auto <> next_auto | 변경 후 값 |
| changed_at | TIMESTAMPTZ | DEFAULT now() | 변경 기록 시각 |

- 복합 FK `(store_id, product_id)` → store_product_order_settings의 동일 복합 PK.
- 일반 인덱스 `setting_history_product`: `(store_id, product_id, changed_at)`.
- 동일 값 재저장은 애플리케이션에서 이력 추가를 생략한다. 이력과 실제 설정의 일치까지 CHECK가 보장하는 것은 아니다.
- 변경자 ID와 모집 회차 ID는 없다. 이력은 상품별 기록이며 특정 회차의 행위로 간주하지 않는다.
- 앱은 INSERT만 하지만 DB 관리자 UPDATE/DELETE를 막는 제약은 없다.

## 9. schema_migrations — 내부 스키마 적용 기록

| 컬럼 | 타입 | 제약·기본값 | 의미 |
| --- | --- | --- | --- |
| name | TEXT | PK | 적용한 SQL 파일명 |
| checksum | TEXT | NOT NULL, 형식 CHECK 없음 | 실행기가 계산한 SHA-256 |
| applied_at | TIMESTAMPTZ | DEFAULT now() | 적용 기록 시각 |

`scripts/database.ts`가 생성하는 관리 테이블이다. 업무 migration SQL 001~003만 실행하면 이 테이블이나 체크섬 기록은 생성되지 않는다. 실행기는 이미 적용한 파일의 내용이 바뀌면 거절하며, seed 초기화에서도 이 테이블은 보존한다.

## 트리거·함수

| 함수 / 트리거 | 대상·동작 |
| --- | --- |
| touch_updated_at() | NEW.updated_at = clock_timestamp() |
| touch_round | recruitment_rounds의 BEFORE UPDATE에서 위 함수 실행 |
| touch_request | customer_requests의 BEFORE UPDATE에서 위 함수 실행 |
| touch_order_setting | store_product_order_settings의 BEFORE UPDATE에서 위 함수 실행 |
| preserve_round_terms() / preserve_round | 모집 회차의 목표·점포·상품·생성 시각 변경 시 예외 발생 |

## 테이블 관계

- 점포 1 : N 모집 회차, 상품 1 : N 모집 회차.
- 모집 회차 1 : N 고객 요청, 고객 1 : N 고객 요청. 회차·고객 조합은 고유하다.
- 모집 회차 1 : 0..1 모의 발주 결과.
- 점포·상품 조합 1 : 0..1 현재 설정, 현재 설정 1 : N 설정 변경 이력.

## 단계별 확정 내역

| 단계 | 변경 | 근거 |
| --- | --- | --- |
| STEP-1 | stores, products, customers, recruitment_rounds, customer_requests 추가. 인덱스·트리거 포함 | 001_step1.sql |
| STEP-2 | supply_available 추가, purchase_orders 추가 | 002_step2.sql |
| STEP-3 | 설정·변경 이력 테이블, order_mode 추가 | 003_step3.sql |
| STEP-4 | 스키마 변경 없음. 기존 테이블로 이력·상세 조회 | 조회 구현 및 step4.sql 예시 |
| STEP-5·6·9 | 데이터 필요 사항만 초안. 테이블·컬럼·제약 미확정 | 요구사항 문서 |
| STEP-7 | 고객 픽업 단계 제외 | 최신 범위 합의 |

## DB 제약과 애플리케이션 규칙 구분

목표 초과 차단, 마감 검사, 목표 도달 상태 전환, 자동 발주 실행, 설정 변경 시 이력 INSERT는 애플리케이션의 트랜잭션 로직이다. DB에 직접 INSERT한다고 이 동작이 모두 실행되지 않는다. 동일 점포의 쓰기는 점포 행을 먼저 잠그고 회차 행을 잠그는 순서를 따른다.

다음은 현재 확정 스키마에 없다: 입고 이벤트, 고객별 확보·안내 상태, 대기 동의, 정확한 모집 완료/취소 시각, 픽업·결제·운영 인증. 기존 updated_at이나 발주 accepted를 이 정보의 대용으로 사용하지 않는다.

## 전달 범위

확정 스키마 MD만 전달하며 SQL·seed·샘플 데이터는 포함하지 않는다. 실행 중인 DB의 실제 행, 접속 문자열, 환경파일, 고객 개인정보, node_modules도 포함하지 않는다. 새 스키마 적용이나 DB 변경은 이번 추출 작업에서 수행하지 않았다.
