# C11-NEED 니즈 근거 보존 최소 수리 — 자체 검증

작성자 research. 고객 UI 원작성자 및 이 수리 작성자이므로 **발견자 재현/자체 검증이며 독립 고객 QA가 아니다.** C11 고객 prompt 실험과 별도 수리다. 실제 모델·HTTP·브라우저·goal 장부·보호 원문 접근 0.

## 원래 누락과 근거

CORE25는 분석 가능한 니즈 기록을 요구하며, docs07의 니즈 의미 계약 131·134행 및 docs27:47은 정제 단서·근거·불확실성 보존과 모델 추정/사용자 확인 구분을 구체화한다. 별도 JSON column이나 새 schema를 강제하는 요구는 아니다.

기존 `saveNeed`는 `extractedClues=[]`를 고정하고, 저장용 대화는 질문 또는 reason만 보존했다. 정상 confirm 응답의 sharedEvidence/unknownConditions를 reason이 반복하지 않으면 그 두 정보가 사라졌다. 조정자가 허용한 최소 재현은 root의 `artifacts/private/run-20260921/c11-product-policy/need-roundtrip.mts`다. 실제 UI 함수 본문 추출→실제 sql.js dispatch→export/import→경영주 snapshot에서 누락을 확인했다. 같은 정보를 reason에 반복한 인접 경우는 텍스트가 보존됐다. 따라서 원문/모든 니즈가 소실된다는 주장이 아니라 특정 필수 근거의 보존을 reason 요약에 의존하던 결함이다. 최초 FAIL 상태와 보고서는 그대로 보존한다.

## 변경과 목적 보존

기존 `customer/model.ts`에 순수 `needCandidateClues`를 추가하고 `CustomerView.saveNeed`의 extractedClues 값에 연결했다. 각 후보 SKU·kind에 대해 `모델 해석 (사용자 확정 아님)` 라벨 및 모델이 제시한 관측 단서, 요청과의 차이, 미확인 조건을 기존 string[]에 넣는다. 후보별 소속과 exact/confirm/alternative 구분을 남기되 고객의 원문이나 동의로 승격하지 않는다. 후보가 없으면 기존처럼 []이며 없는 사실을 만들지 않는다.

원문·사람용 대화·reason·sourceRefs·추천 노출/선택/거절·후속 요청 연결은 기존대로다. 추천 기록은 요청/발주 수량을 만들지 않는다. 새 UI 조작·필드·DB schema·도메인 정책·프롬프트·모델 호출은 추가하지 않았다. 경영주 기존 니즈 카드가 저장 단서를 표시하므로 보존 내용은 기존 경로에서 조회된다.

## 실행한 검사

- 고객 기존5 + 신규2 = **7/7 PASS**, `tsc --noEmit` PASS, diff whitespace 검사 PASS.
- 순수 함수 정상: 후보 없는 미식별, exact, confirm의 미확인 조건, alternative의 차이를 SKU/종류별로 보존하며 입력 불변. 빈 조건에 가짜 미확인 문장을 만들지 않음.
- 실제 현재 `saveNeed` 함수 본문을 실행하여 sourceRefs·원문·사람대화·reason·추천 거절을 실제 sql.js에 저장하고 export/import했다. 복원한 경영주 snapshot에 SKU별 근거·차이·미확인 라벨이 그대로 있고 원문/대화/sourceRefs도 같았다. SQL integrity_check=ok, 요청0/수요0/주문0, 추천3건(노출2+거절1), followup_request_id=null을 확인했다.
- 이 테스트의 scope 검사는 정상 stub이며 저장 변환·실제 SQL 복원 범위만 검증했다. 실제 브라우저/IndexedDB 새로고침 또는 독립 고객 QA라고 부르지 않는다. 기존 freshness·결제 재시도·48시간 표시 등 고객 단위 검사는 함께 실행됐다.

증거는 격리 worktree `artifacts/private/c11-need-self/{customer-tests.log,typecheck.log,source-hashes.json}`에 보존했다. 독립 소비자 검토와 root 통합/현재 source 브라우저 QA가 남았다. 이 기술 수리로 C10 보호 실패나 C11 자연어 품질, G5/G6를 통과 처리하지 않는다.

## 동결 소스

- `src/components/customer/model.ts`: `bd47f698bc0ef67744f9bf6bc914dfb25cfad5f927159269bf0f8b7afabb900c`
- `src/components/customer/CustomerView.tsx`: `748fa2ed58fe354996a07e7eb5882e37dd0313b3c7c097ec1ae59d13cdc6b80e`
- `tests/customer/need-recording.test.ts`: `bdcd17991744f7c41068d214500aa52aa0db522050e7868b05a739ad0c05a543`

기존 기준 context v20의 76 입력 ACK와 C11 작업 계약은 C11 고객 자체보고에 있다. 이 추가 수리의 최종 root context/hash와 독립 review는 조정자가 따로 결속한다.
