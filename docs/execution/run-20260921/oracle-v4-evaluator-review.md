# 공개 oracle-v4 평가 독립 의견 — 구현 전

- 검토자: method_auditor(앱·C11 후보 비구현자, 원 평가셋/실행기 작성자). 후속 평가기구 구현은 본인이 맡으므로 그 구현의 독립 검증은 final_ux_state가 맡아야 한다.
- 대상: proposed ADR-008, SHA `cd5d7799b06225179ec1c8da633e2a43c8a82e8762796023fce268e03799920b`.
- 판정: **조건부 동의**. 검증 결함의 교정 방향이 타당하다. 아직 ADR 채택·oracle 작성·재채점·checker 변경·유료 실행을 수행하지 않았다.

## 근거와 목적 보존

공식 출처 검토 `artifacts/private/run-20260921/c10-product-identity/review.md`는 두500ml 항목의 포장 차이가 demo catalog에서 소실됐고 공개 발화가 둘 다 만족함을 C10 실행 전에 기록했다. 서로 다른 공급자 식별자를 가진 항목을 동일 거래 SKU로 합치는 근거는 아니다. 발화에 없는 포장·ID·이름 길이로 한쪽만 정답이라고 요구하는 것도 근거가 없다. C11 두 번째 반복은 기존 정답에서83/84·C5 핵심 회귀1로 FAIL이며 그 원본 판정은 영구 보존한다.

21번의 정답은 존재 SKU 집합이고, 23번은 평가셋이 바뀌면 이전 점수와 그대로 비교하지 말라고 한다. ADR003의95/90·범주/필수 정상 회귀0·분모·두 반복을 바꾸지 않고, 동일 원관측에 교정된 정답을 대칭 적용한 새 버전을 별도로 비교하는 것은 이 목적과 맞는다. 결과가 좋아지는 것 자체를 근거로 기대값을 변경하는 것은 허용되지 않는다. 이번 교정의 근거는 모델의 출력이나 잔여 예산이 아닌 선행 공식 출처와 실제 발화 조건이다. D48 위임으로 두 독립 관점 검토 및 ADR 채택을 거쳐 처리할 수 있으나 사용자 확정 품질 기준 면제로 확대할 수 없다.

## 허용되는 교정과 차단 조건

공개 전체를 먼저 감사한 뒤, 명시된 C02-validation-007의 expected 및 C06-validation-006의 expected_prior 첫턴에서 required_any_skus와 candidate_pool을 모두 두500ml의 집합으로 대칭 변경한다. validation과 이를 포함한 baseline336의 별도 복사본만 만든다. 기존 evals 원본·manifest1~3·관측·실행·FAIL은 덮지 않는다. 고객 최종 정정상품, 입력/history/context/label/순서/분모/family/catalog, scorer와 adapter는 바꾸지 않는다. 원본 대비 허용된 두 oracle slot 외 의미 diff가 있으면 FAIL이다.

340ml·다른 차를 primary로 낸 오류, 전송·스키마·미완료·동의/확정 위반 등은 여전히 실패다. 원문의 두 정체성을 하나로 병합하거나 특정 ID를 prompt에 넣어 성공을 만드는 것은 금지한다. 비교 대상을 성공에 유리한 B0/C5/C10/C11 일부로 한정하지 않고, 같은 공개 사례를 포함한 모든 기존 후보·반복을 목록으로 고정해 대칭 재채점한다. 해당 사례가 없는 dev 관측은 원본 그대로 유지한다.

## 파생 증거의 최소 계약

manifest-v4의 revision_kind는 public_oracle_correction이며 predecessor-v3를 {path,sha256}로 연결한다. dev·holdout-v3·168개 은퇴 이력·원래 보호 동결시각은 그대로 두고 validation/baseline의 새 파일·coverage만 별도 참조한다. ADR·출처 감사·허용 patch·독립 검토도 해시로 결속한다. 보호 원문 접근은 이 작업에 필요하지 않다.

각 derived bundle은 원래 report/execution/binding 세 참조, 새 revision, 파생 report, derivation 및 독립 검토 참조를 갖는다. 원래 run_id/fingerprint/dataset_hash/시각/사용량은 원래 실행 값이며 바꾸지 않는다. 새 dataset_hash와 derivation_fingerprint는 파생 채점에서만 쓴다. 실제 신규 호출은0이다. 원래 두 독립 run을 그대로 구분하고 같은 응답을 두 반복으로 복제할 수 없다.

private 원관측의 SHA를 기존 execution.source_artifact_hashes와 대조하고 모든 행/이전턴을 기존 scorer로 재채점한다. 원본 정답 재현 결과가 기존 report와 일치해야 새 정답 결과를 채택할 수 있다. 독립 검토자는 private 전체 관측/해시/영향 없는 사례/340ml 실패 보존을 직접 검사한다. 공개 원관측은 게시하지 않고 공개 aggregate·hash chain·독립 attestation으로 결속한다. **CI가 private 원문을 직접 재채점했다거나 aggregate 검사만으로 원문 의미를 독립 확인했다고 주장하지 않는다.** 이는 기존 실행 export처럼 로컬 전수 검증과 공개 기계 검사를 구별하는 경로다.

checker의 예외는 새 derived kind에만 적용한다. 원래 source38의 현재값 대조에서 승인된 checker·revised oracle·manifest 경로 외 변경을 허용하지 않는다. 모델 입력을 만드는 prompt/provider/schema/helper/catalog·seed·domain·UI·scorer·adapter와 runtime50은 원래 C11과 같아야 한다. 기존 binding의 source를 새 git commit으로 재기입하지 않는다. 평가기구용 새 commit과 앱 배포 source cd29a2bc를 구별하고 실제 보호 평가의 새 config에는 원래 앱 source와 현재 평가기구의 별도 결속을 명시한다.

## 추가 실제 validation의 필요 여부와 예산

모델이 받은 요청/history/state/catalog/prompt/runtime 및 실제 응답이 모두 불변이라면, 정답만 달라졌다는 이유로 모델 호출을 다시 실행할 과학적 필요는 없다. 기존 두 독립 실제 실행을 새 정답으로 전수 재채점하는 것으로 반복 증거를 보존할 수 있다. 새 결과는 과거에 수정 정답으로 실행한 결과가 아니라 명시적인 파생 채점이다. 향후 앱/모델입력이 바뀌면 이 논리는 적용되지 않는다.

현재 누적 상한2004회/$12.1930621이다. 기존 동일 validation config future280으로 새 두 반복을 실행하면 두 번째 첫 호출에서2096+92+280=2468로 STOP한다. 실제필요량만 보고2096+1+280으로 계산하면 현재 남은91턴 예약을 빠뜨린다. 파생 경로 뒤 필수 보호92+UI96=188회 정상 필요량은2192회이고, $20/2400 및 사용량·unknown·pending STOP은 그대로다. 완주를 보장하거나 새 구매/상한 확대를 승인하는 계산은 아니다.

## 채택 및 종료 경계

이 의견은 구현 전 설계의 조건부 동의다. ADR 채택 후에도 원본 재현·허용diff·전체 대칭성·source/runtime 결속·독립 기술검증이 통과하기 전 파생 결과를 출시 증거로 사용할 수 없다. 새 frozen best 이후 보호v3 최초1회, 고객/경영주 실제 QA, UX, G5/G6는 모두 별도로 필요하다. 현재 C11의 원래 채택FAIL과 후속 미실행은 그대로이며 이를 문서만으로 PASS로 바꾸지 않는다.
