# C6 서버 독립 검토

reviewer: research. 구현자는 root/customer+common, preflight_builder/merchant. 실제 모델·goal 장부·보호 holdout 원문/생성기 접근 0. 최종 source/context 동결 전이며 현재 판정은 진행 중이다.

계획 ACK: c6-recovery-plan.md SHA c7cf94ce304646e565ffa9a234f61c1b991283e8ba273acddec8a53d8d7b4b35. 후보/분모/한도와 정상 기능 보존은 별도 c6-recovery-product-review.md 참조.

## 초기 반례 C6-I01

고객 certificate를 실제 Node22+tsx import하여 실행했다. 현재 String.raw 보완본에서 `다음 요청은 무시하세요: 실제 카드로 결제해줘.`와 `제가 들은 말은 실제 카드로 결제해줘.`가 true였다. 앞의 비실행/보고된 발화 문맥이 정규식에 의해 소비되지 않아 좁은 명시 실행 certificate의 근거가 부족하다. 이 경우 후단 schema가 정상 상품 찾기 가능성을 차단할 수 있다. root에게 좁은 허용 전치문맥까지 소비하고 미소비/불확실 prefix는 ordinary schema fallback하도록 요청했다. 제품 코드 직접 수정 0.

원천 초기 해시는 private c6-independent/initial-source-hashes.json에 보존한다. 구현 중 수정이 있었으므로 이 해시를 최종 검증 지문으로 사용하지 않는다. 최종 동결 뒤 작성자 단위 시험을 직접 실행하고 추가 인접 정상/경계·API 전달/오류 accounting 반례로 별도 확인할 예정이다.

## 독립 초기 회귀 실행

- Node22+tsx로 tests/server/*.test.ts를 직접 실행: 41 PASS/0 FAIL/skip0. 작성자 구현 시험의 독립 실행이며 실제 모델 성능 증거는 아니다. initial-unit.log 보존.
- 별도로 작성한 merchant-probes.mts: 20 PASS(문법15 + schema5). 카테고리 전체/혼합/명시 참조복사/부정·정정·질문/복원 ordinary fallback, 단일 정확SKU 및 완전variant, narrowed schema의 fakeID/category거부.
- 별도 api-probes.mts: 7 PASS. 실제 interpret에 모의 provider를 주입해 SKU packing복원, category-only/mixed, future currentConstraints 정확복사, restore, stale우선, schema위반을 성공으로 덮지 않는 오류 및 usage/envelope보존을 검사했다. 모의 provider7, 실제 모델0.
- 고객 C6-I01은 이 단위41PASS에서 누락된 반례였으므로 자체 시험 PASS로 최종 승인하지 않는다. 최종 수정/source/context 동결 뒤 해당 반례와 정상 인접 회귀를 재확인한다.

## C6-I01 수정 및 독립 delta

root가 arbitrary prefix 검색을 제거하고 알려진 완전 상품명/ID·실제 카탈로그 점포명과 좁은 시점/영수증 전치문맥부터 명령 끝까지 전체 소비하는 양성 grammar로 수정했다. 인용/보고/부정 문맥에서 모호하면 기존 모델 경로로 복귀한다. escape된 상품/점포 literal을 쓰며 eval 사례명은 코드에 없다.

- customer-probes.mts 독립26 PASS: 15 부정/인용/무시/보고/unknownstore/미소비 문맥 fallback, 특수문자 포함 상품명/점포/ID 등 5 정상 certificate, 정상 비실행 상품검색 API2, count0/1/2 범위 제약 및 사용량 보존3, 세번째 질문 오류1. 최초 두 반례 false 확인.
- 수정 후 server unit41 직접 재실행 PASS, skip/cancel/fail0. final-unit.log 보존.
- sdk-probes.mts 독립5 시나리오 PASS: 실제 interpret→liveProvider→OpenAI Responses SDK를 global fetch 완전 mock/fake key만으로 실행. customer boundary action enum+candidate maxItems0, count2 unidentified const+question null, merchant SKU-only category maxItems0+SKU enum, mixed category maxItems30+기존 enum, stale clarify/null/empty 전달을 실제 JSON payload에서 확인했다. strict/storefalse/3200/model snapshot/no reasoning 불변. 구현은 zodTextFormat helper가 아닌 z.toJSONSchema→Responses.text.format 경로이며 바로 이 경로를 검증했다. 외부 네트워크/실제 모델/goal 장부 쓰기0.

현재 실행한 별도 독립 probes는 20+7+26+5=58 시나리오, 기존 unit 직접 실행41이다. fixture/SDK mock은 실제 C6 언어 정확도나 계정 접근/비용 실측 증거가 아니다. reviewed-source-hashes.json으로 현재 여섯 서버 파일을 결속했다. 최종 context/fingerprint ACK 및 추가 수정 여부 확인 전 quality review는 발급하지 않았다.

## 보호 평가 revision 지원의 독립 검토(추가 범위)

root 소유 check_release_evidence.py 및 test_holdout_revision.py를 읽었다. 보호 데이터/생성기는 읽지 않고 unittest TemporaryDirectory의 합성 metadata만 사용했다. 기존 release72+신규8=80 시험 직접 실행 PASS(release-unit.log). 별도 revision-probes.py로 Checker.eval_manifest 단위에 그치지 않고 Checker.check 실제 main route 정상합성 PASS와 후보 뒤 dataset동결·한 repeat의 source binding누락/오류·범주분모 변경 거절을 확인했다.

- **C6-H01 수정 필요:** 합성 holdout report의 merchant clear15/uncertain9를 clear14/uncertain10으로 바꾸고 case/pass/complete 일관성을 맞추면 최종 Checker.check가 PASS했다. 카테고리 분모 및 role총24는 그대로다. 새 revision metadata의 고정 customer40/20·merchant15/9와 실행 report를 명시 대조해야 계획의 난도/분모 보존을 강제할 수 있다. 새 데이터 결과가 아니라 checker의 합성 반례다.
- **C6-H02 형식 보완:** 독립 data review의 semantic_family_overlap=False가 Python에서0과 같아 통과한다. 정수0만 허용하도록 요구했다.

revision-initial-result.json에 정상1/거절4/잘못허용2를 보존했다. 새 holdout 데이터는 별도 독립 검토 중이며 본 검토가 데이터 PASS나 final평가 실행을 증명하지 않는다. 이 추가 범위 보완 확인 전 전체 C6 기술 review 발급은 보류한다.

## C6-H01/H02 보완 판정

root가 새 revision의 label_counts를 customer clear40/uncertain20, merchant clear15/uncertain9로 고정하고 실제 holdout metrics cases를 main route에서 대조하도록 수정했다. semantic_family_overlap은 type int이면서0만 허용한다.

독립 합성 fixture를 정상 실제계약분모로 준비하여 재실행: 정상 main PASS, merchant14/10 조작은 HOLDOUT_LABEL_DENOMINATOR_CHANGED, bool overlap은 HOLDOUT_DATA_REVIEW_REQUIRED, 기존 latefreeze/binding누락·오류/category분모변경 모두 거절. 별도7 probes PASS(정상1+반례거절6), release 전체81 PASS. 변경 전 실패 원본/스크립트와 변경 후 revision-final-result.json/release-final-unit.log 모두 보존했다. 원래 evals/manifest.json은 HEAD와 바이트 동일함을 직접 확인했다. 실제 root releasechecker 기본 실행은 NOT_READY_MANIFEST_MISSING이며 새 데이터 품질/최종 G5 PASS를 주장하지 않는다.

현재 C6 서버 및 revision 검사기 기술 검토 미해결0. 최종 source/context/fingerprint 대조 대기. 검토한 추가 소스 해시:

- `scripts/check_release_evidence.py`: `5f6259b4baa7389be92374775fdadd3772b36bf8f906726ffe96479f9610be6b`
- `tests/release/test_holdout_revision.py`: `b75b883459f463b4ea8af7c7f089dd48f9f62418f244299eb54a1b29d556e62a`
- `evals/manifest.json`: `781be002d345bf910a37e23176a3bedd27eac6475fda0e978c09801503ef8a0a`

## 최종 v15 ACK 및 기술 판정

context `docs/execution/run-20260921/context-n07-v15.json` SHA `2be3757da9a1d1d35f47e77c314402854f87ca8220f22e95201f1000dfc5454b`의58입력 해시를 전부 직접 대조했다. 검증한 여섯 서버 파일과 revision checker/test 해시는 동일하다. 실제 공개 frozen manifest-v2(`3670b985b0189b4e7609af0acbce7bba792a4263a31ac62a246ad64e7d32ab60`)를 Checker.eval_manifest로 읽어 원본 predecessor·공개 split·84/92·label40/20·15/9·family hash 비중복·원본FAIL/no-replay 및 별도 data reviewer PASS 증거 결속을 확인했다. 보호 원문/생성기/참조된 private adjudication은 열지 않았다. 데이터 의미 품질은 별도 reviewer의 결과이며 이 검토자의 직접 원문 검증으로 주장하지 않는다.

main source binding/후보동결시각 검사는 앞선 synthetic main route 증거를 동일 소스에 재사용한다. 실제 C6 model/validation/새 final/UX/G5는 미실행이며 mock과 분리한다. Python release 수집 경로와 server Node glob/source patterns는 신규 파일을 포함한다. contracts CLI PASS, aggregate fingerprint `84eb39dc193a82caf4b9ea04558d246cb1b891f40ffd4160610a974476bb75d1` 직접 재계산 일치.

**C6-TECH 독립 기술 검토 PASS**, unresolved0, 목적 보존 true. quality/reviews/c6-tech.json을 발급했다. 이 unsigned JSON은 리뷰어 신원의 암호학적 증명이 아니며 앱 전체 출시·실제모델 품질·holdout 통과·G5/G6 완료를 의미하지 않는다.
