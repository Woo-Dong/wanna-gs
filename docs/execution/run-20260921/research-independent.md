# R20260921-v1 독립 초기 조사 검토 및 WP-R05 기술 brief

- 검토자: `/root/preflight_builder` (연구 작성자 `/root/research`와 다름). 검토일: 2026-09-21 KST.
- 대상: `research.md`, SHA-256 `a1ab2edf8e4cd796039760c9c62fbae05ceaad268fbfa930761d36f292d5ecde`.
- consumed_context_hash: `74bf125ebe9c8ed2f7933abb55b08c904400f3a7ba1319c395a2429c32c20679`; `CTX-20260921-BOOT-v1`.
- 기준: card.md, CORE-03/08/13/14/17/21/22/23/24/25/26, DECISION_INDEX의 ADR-001, D-44/45, docs/19·21·24·29. 적용 스킬: wanna-gs-research; OpenAI 항목은 OpenAI Docs.
- 범위: 대표 원문 3개 직접 열람, 주장·날짜·출처 범위, 초기 시나리오와 데이터 확대 계획 및 기술 계약. 전수 200 SKU·좌표 검증, 제품 테스트, 비용/계정 권한 검증은 이 검토 대상이 아니다.

## 판정

**초기 조사 `ready_with_hypotheses`에 동의한다. 초기 기반 개발을 막는 출처 왜곡이나 범위 확장은 발견하지 않았다.** 200개 전체 데이터 준비나 SEED-READY/PLAN-READY 전체 통과를 뜻하지 않는다. 상품·실제 점포·고객/경영주 업무·오류 회복을 이어갈 초기 근거와 명시적인 미검증 목록이 있다. 아래 후속 조건은 전체 seed/eval 구현 때 실제 검사해야 한다.

검토자는 별도 사전점검 scaffold 작성자이므로 이 문서의 기술 brief는 scaffold의 독립 코드 승인으로 사용할 수 없다. 기술 source 검토와 연구 작성자의 주장을 독립 점검하는 역할만 수행했다.

## 대표 공식 원문 재확인

| 대상 | 실제 열람·대조 | 판정과 한계 |
|---|---|---|
| S01 [GS리테일 제공 한정선 발표](https://www.newswire.co.kr/newsRead.php?no=1041771) | 제공자가 GS리테일이며 발행은 2026-09-03 10:47. 8월 28일 두 장소의 합계 400개 행사, 요거트 찹쌀떡 냉동 상품 발표를 확인했다. | 조사와 일치. 행사일과 발표일을 구분했고 소진 발표를 전국 수요·현재 재고로 확대하지 않았다. 기업 제공 발표이지 독립 인터뷰가 아니다. |
| S02 [GS리테일 제공 라라스윗 발표](https://www.newswire.co.kr/newsRead.php?no=1041291) | 발행 2026-08-27 14:29. 메론·망고와 8월 25일 추가 맛의 명칭, 기존 두 맛의 누적 판매 집계 범위를 대조했다. | 조사와 일치. 기존 두 맛의 집계를 신규 맛 전체로 확대하지 않았다. 맛별 속성은 개별 근거가 필요하다. 확인 명칭 후보를 규격 확정 SKU와 구분한 것도 적절하다. |
| S09 [광진구 공개 판매소 PDF](https://www.gwangjin.go.kr/editorUpload/files/000006/20250625153633250_WBFHJ02K.pdf) | PDF 2~3쪽에서 ST-01~10의 점포명과 주소를 모두 대조했다. 예: 구의무학점·아차산로51길 86, 광진우체국점·강변역로 2. | 역사적 명칭/주소 후보로 일치. 좌표·현재 영업·상품 취급 근거는 없다. 표기의 GS25/지에스(GS)25 정규화는 원문 이름을 별도 보관하는 조건으로 타당하다. 전화번호는 dataset에 옮길 필요 없다. |

원문은 웹 도구로 열어 읽었다. 별도 원문 파일 보관·PDF screenshot 교차검사·현장 확인은 수행하지 않았다. S01/S02와 PDF 외 나머지 S03~08은 이번 bounded 검토에서 재열람하지 않았으므로 전수 출처 승인으로 확장하지 않는다. PDF의 문서 기준 시점은 조사에서 밝힌 2025-06으로 소비하며, URL의 업로드 시각만으로 현재 운영을 추정하지 않는다.

## 목적 보존·확대·평가 분리

- **정상 사례:** SC-01 exact 요청, SC-04 재고 0이지만 공급 가능한 요청, SC-08 승인 정책의 정상 실행을 성공 oracle로 둔다. 모두 거절하거나 영구 보류하는 구현이 안전 성공으로 분류되지 않는다.
- **예외·인접 기능:** SC-05 대체 거절 후 원요청 보존, SC-07 상품 묶음과 고객 상세 수량 대조, SC-09 stale/중복, SC-10 결제·입고·정확한 48시간 구분, SC-11 입력 보존·지도 목록 회복이 기존 CORE 목적을 지킨다. 이것은 테스트 설계이며 실행 결과가 아니다.
- **200 SKU 확대:** 8개 카테고리의 합계 200 및 독립 맛·규격, 출처별 field_origin, 합성 거래값, 희소 점포 availability, 합성 계정을 계획했다. 현재 11개 명칭 후보를 200개 준비로 세지 않았다. D04A를 같은 importer의 최소 seed로 먼저 만들고 D04B/D05에서 전체 데이터로 바꾸는 ADR-001과 일치한다.
- **최근 상품:** 20~30개 목표 미달을 명시했다. 실제 출시 후보와 synthetic_scenario를 각각 계수해야 하며 합성 부족분으로 확인된 최근 상품 목표를 채웠다고 보고하면 실패다. 역사적 상품·현재 취급·실제 인기의 세 라벨도 별도 유지한다.
- **실제 점포:** 10개 주소 후보와 좌표 확보·정밀도·WGS84 검증 후속 작업이 현실적이다. 현재 근거를 주소 수준으로 제한하고, 좌표가 막히면 근거 있는 대체 점포를 택할 수 있어 제품 기반 작업과 불필요한 순환이 없다.
- **family:** 공개 SC 문장과 동일 의도/상품/상태의 오타·번역·패러프레이즈를 dev/demo에 두고, 독립 평가자가 새 family를 구성하는 방향이 docs/21과 일치한다. taxonomy 공유는 허용하지만 공개 family를 일부 단어만 바꿔 holdout으로 세면 실패다. 현재 split_group_id 목록·hash·분모가 없다는 점은 초기 단계의 알려진 후속 항목이다.

다음 seed/eval gate에서 필요한 확인은 다음과 같다. 조사가 이미 완료했다고 한 항목의 수정 요구가 아니라 이후 산출물의 검사 조건이다.

1. normalized SKU unique key, field-level origin, source ID/날짜/checksum, 최소/전체 seed revision을 실제 파일로 고정한다. reference_verified 이름에 임의 맛·규격을 붙여 복제하지 않는다.
2. 공개 `seed.sqlite`·`catalog.json`·client import에는 제품에 필요한 카탈로그와 합성 시연 상태만 포함한다. **보호 holdout의 질의·정답·상세 oracle은 public 디렉터리·브라우저 bundle·alias·few-shot·배포 asset에서 제외한다.** 비공개 evaluator 전용 저장 경로와 노출 기록을 둔다. 경로 이름에 holdout이라고 쓰는 것만으로 보호했다고 판정하지 않는다.
3. evaluator가 split_group_id의 교집합 0, family의 의미 중복, 공개 예시 누출, 범주별 분모를 확인한다. bundle/seed table 검사와 import 의존 검사도 GATE-BOOTSTRAP에 연결한다. 카탈로그 공개 자체는 정답 유출과 구분한다.
4. 현재 주소/좌표 출처·정밀도, 지도 marker와 목록 store_id, 모의 취급 라벨을 전체 seed 전환 때 검증한다. 민간 지도나 유료 geocoder를 새 필수 서비스로 추가하지 않는다.

## WP-R05 기술 brief

2026-09-21에 아래 공식 문서 본문을 열었다. 이는 해당 API의 근거이며 실제 앱 통과나 모든 최신 버전의 상호 호환을 보장하지 않는다. 아래 적용은 D-44/45 안의 기술 제안이고 제품 정책 변경이 아니다.

| 영역·공식 근거 | 확인한 내용 | 구현 선택과 검사 |
|---|---|---|
| [Next 설치](https://nextjs.org/docs/app/getting-started/installation), [환경변수](https://nextjs.org/docs/app/guides/environment-variables) | 최소 Node 요구는 20.9. `NEXT_PUBLIC_`는 브라우저 bundle로 빌드 시 인라인되고 일반 환경변수는 서버 전용이다. | 기존 Node 22 기반과 exact dependency/lockfile을 local·CI·Vercel에 맞춘다. OpenAI 키는 서버 route만 읽고 public 변수·응답·로그에 전달하지 않는다. clean `npm ci`, typecheck, production build와 배포 revision을 검증한다. |
| [sql.js Database](https://sql.js.org/documentation/Database.html), [SQLite foreign keys](https://sqlite.org/foreignkeys.html) | export는 Uint8Array를 반환하며 DB를 닫고 다시 열어 pragma가 기본값으로 돌아간다. SQLite FK는 연결별 활성화가 필요하다. | SQL을 단일 Worker/연결 큐로 직렬화한다. 최초 open뿐 아니라 **export 후에도** foreign_keys=ON을 재설정·조회한다. 실제 SQL 제약/rollback, export/import 후 FK 위반 실패, bind parameter 사용을 검사한다. |
| [IndexedDB complete](https://developer.mozilla.org/en-US/docs/Web/API/IDBTransaction/complete_event), [abort](https://developer.mozilla.org/en-US/docs/Web/API/IDBTransaction/abort) | complete는 트랜잭션 commit 이후 발생한다. abort는 그 transaction의 변경을 되돌린다. Worker에서도 사용 가능하다. | request 성공만으로 저장 완료를 표시하지 않는다. bytes/schema/seed/generation을 한 readwrite transaction에 넣고 complete 후 성공. abort/quota/open 오류는 마지막 성공 SQLite bytes 복원과 쓰기 준비 상태로 처리한다. 초기 저장 실패·손상·버전 불일치·reset 저장 실패를 별도로 검사한다. |
| [OpenAI Structured Outputs](https://developers.openai.com/api/docs/guides/structured-outputs) | Responses의 text.format/json_schema·strict 형식, incomplete 상태와 refusal 처리 경로를 제공한다. 구조 형식 보장과 업무상 올바른 값은 별개다. | 서버 OpenAI 단일 경로를 유지한다. bounded input/output/timeout와 사용량을 기록하고 완료 여부·스키마·존재 SKU·catalog revision을 검사한다. 브라우저 서비스가 generation·최신 수요/예산·동의를 재검증한 뒤 SQL 적용한다. 오류를 fixture 성공이나 미등록 상품으로 바꾸지 않는다. 모델 변경·계정 권한은 실제 호출로 별도 확인한다. |
| [Playwright Best Practices](https://playwright.dev/docs/best-practices) | 사용자에게 보이는 동작, 독립된 테스트 환경, role/label locator와 자동 대기·재시도 assertion을 권장한다. | 고객/경영주 QA 담당을 분리하고 각자 한 context/탭에서 역할을 전환한다. 클릭·새로고침·reset·오류 회복은 실제 화면을 통과하고 SQLite 관측은 보조 증거로 쓴다. 외부 지도 실패는 fixture로 격리하되 실제 지도·live 모델 검증을 대체하지 않는다. 보호 Preview의 토큰은 해당 origin으로만 전송하고 trace에 비밀 입력을 남기지 않는다. |

기술 문서 접근 한계: 한국어 OpenAI structured outputs 페이지 열기에서 일시 오류가 났고, 동일 공식 영문 페이지를 열어 본문과 incomplete/refusal 예제를 확인했다. 외부 서비스를 새로 가입하거나 비용 한도를 변경하지 않았다. 기술 선택 구현과 실패 회귀는 후속 소유자·독립 검증자가 실제 코드에 대해 판정한다.

## 종료·인계

초기 연구 검토는 이 범위에서 종료한다. 조정자는 대상 research hash와 이 결과를 PROGRESS/WORKPLAN에 연결하고, data reviewer는 D04B/D05의 실제 row·좌표·provenance, nl-evaluator는 보호 split/분모, GATE-BOOTSTRAP 담당은 공개 asset 제외 검사를 책임진다. 연구 hash나 실제 API 계약이 바뀌면 영향받은 검토 항목만 다시 확인한다. 이 작업은 위 문서만 작성했으며 research 원본·스키마·scaffold·PROGRESS는 수정하지 않았다.
