# E01 독립 평가 계약·taxonomy/scorer 계획

- owner: `/root/method_auditor` → nl-evaluator. 기능/prompt/search/candidate 구현자가 아니다.
- consumed_context_hash: `1cc5b18da57bdfb492d3f2cf1e09aedb8357e72e0be951c680446583417134ef`.
- 적용: ADR-003 adopted·실행 미검증, ADR-002, docs/21/23, CORE-03/05/17/21~23/25/26.
- 상태: taxonomy/scorer 계획. 정확 상품/점포/API 계약 전이므로 case 발화·정답·dataset 파일은 아직 만들지 않는다. baseline/candidate/holdout 호출0, 평가 PASS 주장 없음.
- 독립 검토: research가 taxonomy·분할 metadata·scorer 기대값을 검토한다. private holdout 정확 발화·정답은 읽지 않는다.

## 분포와 family 보호

다음 분포를 고정할 계획이다. case별 실제 조합을 만들 때 family 단위로 배정하고 ADR의 최대2개 오차가 필요하면 baseline 전에 metadata와 이유를 확정한다. 범주별 role/split 최소2개를 실제 validator로 강제한다.

| 고객 범주 | total | dev | validation | holdout |
|---|---:|---:|---:|---:|
| C01 정확명 | 45 | 27 | 9 | 9 |
| C02 검증 속성 조합 | 40 | 24 | 8 | 8 |
| C03 오타·별칭·자모·한영 | 40 | 24 | 8 | 8 |
| C04 모호·다후보 | 35 | 21 | 7 | 7 |
| C05 미등록·미확인 | 30 | 18 | 6 | 6 |
| C06 정정·후보/대체 거절 | 30 | 18 | 6 | 6 |
| C07 수량·점포 혼용 | 30 | 18 | 6 | 6 |
| C08 범위밖·긴입력·잡음 | 25 | 15 | 5 | 5 |
| C09 주입·가짜SKU·도구오용 | 25 | 15 | 5 | 5 |
| 합계 | 300 | 180 | 60 | 60 |

| 경영주 범주 | total | dev | validation | holdout |
|---|---:|---:|---:|---:|
| M01 포함·제외 | 15 | 9 | 3 | 3 |
| M02 예산·수량·조건 | 15 | 9 | 3 | 3 |
| M03 이번만·앞으로 scope | 15 | 9 | 3 | 3 |
| M04 이전복원·대명사 | 15 | 9 | 3 | 3 |
| M05 모호·충돌 | 15 | 9 | 3 | 3 |
| M06 stale | 15 | 9 | 3 | 3 |
| M07 권한·주입 | 10 | 6 | 2 | 2 |
| M08 긴·불완전입력 | 10 | 6 | 2 | 2 |
| M09 연속수정·중복 | 10 | 6 | 2 | 2 |
| 합계 | 120 | 72 | 24 | 24 |

같은 의도·상품/조건·상태 조합에서 파생한 표현/오타/번역은 하나의 split_group_id다. 넓은 범주 ID와 의미 family ID를 구분한다. research.md의 공개 발화 및 동등 family는 dev/demo에만 배정한다. taxonomy와 aggregate counts는 공개해도 되지만 private family를 복원할 수 있는 SKU+조건 조합 목록이나 query·oracle을 일반 보고서에 쓰지 않는다.

## 산출물·소유권

- 공개 평가 계약: evaluator 소유 `eval/taxonomy.json`, `eval/case.schema.json`, `eval/score-contract.md`, `eval/dev.jsonl`, `eval/validation.jsonl`(정확 경로는 E01 구현 계약에서 coordinator와 확정).
- 독립 검토용 metadata: split별 counts, 익명 group hash, dataset checksum, source/catalog/schema/prompt/model/config revision, overlap0 검사 결과. protected case 내용은 포함하지 않는다.
- 보호 데이터: evaluator 전용 `artifacts/private/run-20260921/eval/holdout.jsonl`. 현재 .gitignore의 artifacts/private/ 범위에 들어가며 생성 후 `git check-ignore`와 public/seed/bundle/import 유출 검사를 수행한다. 경로명만으로 보호 성공을 주장하지 않는다.
- root는 live transport/runner를 만들되 holdout 원문·정답을 열람하거나 stdout에 출력하지 않는다. evaluator가 protected path를 입력해 최종 freeze 후보를 실행하고 상세 결과는 private에 저장, 공개 결과에는 aggregate·hash·오류 종류만 남긴다.
- holdout을 읽은 evaluator는 후속 prompt/alias/search 후보를 직접 작성하지 않는다. 노출된 case를 회귀용으로 이동시키는 경우 새 독립 family와 접근 기록을 확보하며 원래 실패를 보존한다.

## case 및 결과 계약

case는 id/role/category/family/split, evidence_backed 또는 synthetic_expansion origin, research/scenario 참조, catalog/state snapshot hash, 입력 turn 목록, max_model_turns, 사전 label(clear/ambiguous/unidentified/out_of_scope), 허용 행동·정답 SKU 집합 또는 명령 필드, 금지 행동, 판정 근거를 갖는다. provider나 앱이 출력한 label로 정답 분모를 바꾸지 않는다.

실행 결과는 case와 별도 레코드이며 후보/version/context hash, 각 attempt의 provider_called/transport status/latency/usage, schema_valid, 응답 candidate/intent/fields, 실제 domain effect 및 command/state snapshot을 기록한다. 모델의 잘못된 제안과 domain의 안전 차단은 각각 점수화한다. transaction 불변식은 DB/event 검사로 평가하며 LLM judge 찬성만으로 통과하지 않는다.

scorer는 다음을 결정적으로 판정한다.

1. 누락/중복 case·잘못된 split/revision·response/schema 실패·unknown SKU를 검출한다. 모든 실패/attempt를 보존하고 transport 성공 subset과 전체 case 분모를 함께 낸다.
2. 고객 명확 case는 정답 SKU 후보 포함 AND 잘못된 확정 유도 없음 AND 고객 확인 경로 유지여야 성공이다. 적절한 후보가 있어도 전부 거절/불필요 질문으로 정상 경로를 막으면 실패다.
3. 모호·미식별은 허용된 확인/미식별 행동을 판정하고 없는 SKU를 만들거나 네트워크 오류를 니즈로 저장하면 실패다. 정정/대체 거절 후 원요청·동의 불변도 별도 도메인 회귀로 확인한다.
4. 경영주 명확 case는 intent/scope와 명시된 모든 포함·제외·예산·수량 필드가 oracle과 같아야 성공이다. 일부 필드 평균으로 한 case를 부분 성공 처리하지 않는다. 모호한 명령의 미실행과 명시 확인도 허용 행동 계약으로 채점한다.
5. mandatory 항목과 필수 정상 시나리오, role/split composite, 범주별/최악 범주, latency P50/P95, 불필요 질문/과잉거절 및 attempt/token 수를 따로 보고한다. mandatory1건을 평균 개선으로 상쇄하지 않는다.

API 응답과 상태 필드의 최종 이름이 정해지면 evaluator가 adapter 계약을 root와 확인한다. 정답을 구현 출력에 맞춰 바꾸지 않는다. 애매한 자연어의 허용 행동은 baseline 전에 독립 metadata 검토로 고정하며 실제 응답을 보고 정답을 넓히지 않는다.

## 실행 순서·예산

baseline은 dev252+validation84=336case, holdout은 실행하지 않는다. 선택 후보의 dev선별→해당 role validation→독립 채택→best validation 추가1회를 실행한다. 각 validation 반복이 출시 최소/mandatory 기준을 개별 충족해야 한다. code/model/prompt/search/seed/config를 freeze한 뒤 evaluator가 holdout84를 처음 실행한다. 200SKU 정확명/ID 전수 검사는 별도 결정적 검사다.

모든 case의 max_model_turns와 최대 transport attempt3을 사용해 stage별 최악 호출을 계산하고, 이미 사용한 outbound calls와 남은 best/holdout/UX/G5/G6 reserve를 먼저 차감한다. 앱 API의 권한오류와 provider outbound calls를 혼동하지 않는다. UX workload8종×3회×2버전=48실행 자체도 모델 turn 수에 반영하므로 명목40case 여유에 의존하지 않는다. $15 추정이 unknown이면 실제 공급자 hard cap으로 간주하지 않는다. 선택실험 중단은 필수 검증 면제가 아니다.

## 다음 행동

연구 담당에게 위 taxonomy/metadata/scorer 계획 독립 검토를 요청한다. data/dba가 최소 catalog field contract와 실제 SKU/source를 넘기면 공개 dev/validation family부터 생성한다. holdout은 별도 evaluator 작업으로 준비하되 정확 내용은 기능구현자에게 보내지 않는다. fixture scorer 반례(0case/누락/잘못된 분모/schema오류/가짜SKU/partial-field/같은family교차/mandatory위반)를 구현해 통과 여부를 확인한 뒤 실제 모델 baseline을 시작한다.
