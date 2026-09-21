# E01 독립 평가 장치 검토

- reviewer: `/root/research`; 작성자 `/root/method_auditor`와 독립
- reviewed_at: 2026-09-21
- status: **FAIL — 아래 반례 수정 후 재검토 필요**
- consumed_context_hash: `e8d6eb6ffef8765544e3aeeeb9c27b1e98f0c7cb5131202712ec4d32d806ea99`
- 기준: CORE-17/18/21/22/23/25, adopted ADR-003. 적용 스킬: wanna-gs-verify.
- 범위: 공개 taxonomy/schema/adapter/scorer/self-tests만. 실제 모델 호출, 제품 G3~G6, protected holdout 내용/정답 검토는 **not_run**. private 디렉터리 및 holdout 본문은 열지 않았다.
- 목적 보존: 정확한 정상 요청은 통과하고 모호/거절/정정 대화 및 모든 명시 조건은 별도로 평가한다. 누락·실패를 성공으로 바꾸거나 쉬운 사례만 남겨 합격시키지 않는다.

## 확인된 정상 동작

독립 실행 `python3 -m unittest discover -s evals/tests -v` 결과 **27/27 PASS**, skip/error 0. 구현자의 실행 결과를 인용한 것이 아닌 검토자의 재실행이다. 공개 taxonomy 산술은 고객 dev180/validation60/holdout60, 경영주72/24/24, 합계420으로 일치하고 각 role/split/category 최소2를 만족한다. 카탈로그/데이터 hash 불일치, 최종 관측 누락, fixture를 live로 투입, 허구 SKU, 잘못된 primary 후보와 정답 동시 반환(oracle pool이 있을 때), 경영주 전체 명시 조건 및 타입 불일치, domain violation, validation 한 회차 실패를 차단하는 정상 장치는 확인했다.

실제 family 배정 manifest/hashes와 420개 데이터셋은 검토 당시 생성 대기 상태이므로 **분할 독립성 및 정답 품질을 승인하지 않는다**. taxonomy 숫자와 실제 데이터 분포는 별개다. R02 공개 데모 발화/패러프레이즈 family는 dev에만 두도록 evaluator에게 전달했다.

## 실행으로 재현한 반례

공개 `evals/tests/test_scorer.py`의 `case()/obs()/CAT`를 import한 별도 Python 프로세스에서 아래 변형을 실행했다. 가상의 세 SKU만 사용했으며 모델/holdout 호출은 없었다.

| ID | 위치·재현 조건 | 실제 결과 | 요구되는 수정 |
|---|---|---|---|
| EV-01 | scorer.py 140–147: user turn을 2개로 늘리고 max_model_turns=2, prior_responses=[{}], 마지막 응답만 정답 | nl_minimum_pass=true, incomplete=0 | 이전 각 turn의 식별자·transport·schema·정답/필수위반 관측이 있어야 한다. 빈 객체/이전 오류를 최종 성공이 덮지 않게 하며 실제 다회 대화의 turn별 oracle 또는 명시적 평가 기준을 둔다. |
| EV-02 | live observation의 transport=ok, attempts에는 provider_called=true/status=timeout 한 건만 존재 | live_evidence=true 및 nl_minimum_pass=true | 완료 응답에는 해당 turn의 성공한 실제 provider attempt가 필요하다. 실패 후 성공 retry는 허용하되 timeout/401만 있는 모순 관측은 차단. turn/retry 연결 및 최대3/401·403·quota 재시도금지 계약은 runner와 함께 검증. |
| EV-03 | config-a/config-b 각각 유효하게 evaluate한 reports에 repeat_ready 호출 | true. 같은 report를 두 인자로 재사용해도 true | report에 모델/설정 fingerprint와 실행 고유 ID를 보존. 두 repeat는 같은 best 설정·같은 dataset, 서로 다른 실제 실행이어야 한다. 현재 설정 fingerprint가 report에서 사라져 모델/프롬프트가 바뀌어도 통과한다. |
| EV-04 | clear oracle에서 optional candidate_pool만 제거하고 response primary=[sku-b,sku-a] | nl_minimum_pass=true, fatal_errors=[] | 명확 고객 oracle은 허용 primary 집합을 필수로 가지거나 required 집합을 안전한 기본 pool로 사용. 정답 포함만으로 틀린 known SKU의 primary/확신 제시를 성공 처리하지 않는다. 정상 exact와 명시적 alternative 허용은 유지. |
| EV-05 | 검증용 1개 case와 그 자체 hash만 제공 | nl_minimum_pass=true; 같은 데이터의 require_full 검사=false | 부분 metric과 release-ready 판정을 명확히 분리. 실제 baseline336/validation84/holdout84 각각의 고정 manifest hash·범주/label 분모·family metadata를 실행기에서 강제해야 한다. 각 평가에 전체420 본문을 읽으라는 요청이 아니다. CLI가 받은 subset hash만으로 필수 coverage를 보장하지 못한다. |

EV-01~04는 현재 코드에 대한 필수 수정 요청이다. EV-05는 dataset/runner 통합 전에 닫아야 하는 완료 경계이며, 아직 없는 데이터셋의 결함을 추정한 것은 아니다. 스코어가 자기 보고된 boolean을 받는 사실만으로 실제 live의 인증성을 보장한다고 주장할 수 없으며, runner 원시 관측과 report 연결이 필요하다.

adapter의 confirmation_required=True는 UI 확인 단계를 구현하거나 검증한 것이 아니다. README가 이를 명시한 점은 적절하다. raw 모델의 자유문장 확신/실제 UI 선택유도는 구조화 ID 채점 외에 G5 브라우저 QA가 필요하다. 이 관측만으로 UI 결함을 단정하지 않는다.

## 재검토 조건

위 반례가 fail-closed로 바뀌고 원래 정상 exact/alternative/merchant/retry 성공이 유지되는 독립 재실행. 생성된 공개 metadata의 실제 role/split/category 수, 가족간 중복 검사 및 catalog binding hashes 확인. holdout 본문은 계속 평가자 전용이며 검토자는 읽지 않는다. 실제 baseline/두 validation repeat/최종 holdout은 별도 실행 증거가 생길 때만 판정한다.

## 검토 대상 fingerprint

| 파일 | SHA256 |
|---|---|
| evals/README.md | 617f9bd99bb58c4ec787d0f1bef0ee4f6d76322846dc0c4e1a7fdd2de56d600a |
| evals/taxonomy.json | dc5314cc20c095e933da4c31dfe0916e8af184bdf5b2a4051c350c4a1136a706 |
| evals/case.schema.json | d4ecc4ba463dab96c3ee820acfaa4b76c467eb838e93ca44a6822a77d325ec1d |
| evals/scorer.py | 814b6933ba8fbb22030179638588986177fcbcdcd67f39eea0ed002378fc3175 |
| evals/adapter.py | 68f1158551e094a8f6494aed525ed35aaafda4ba8cd6166ce099c63a0c30e690 |
| evals/tests/test_scorer.py | 654c49c9d42a4de2fdb1aae8e4a47861f4e9aa640dbc4de1703ce28580867866 |

구현 수정 없음. 이번 변경 소유는 본 보고서뿐이다. 수정 요청은 evaluator/coordinator에 전달했다.

## 2차 — 기존 반례 보완 및 인접 정상 회귀

수정 후 독립 재실행 self-tests **31/31 PASS**. EV-01 빈 prior 관측, EV-02 timeout-only live, EV-03 다른 설정/동일 실행 재사용, EV-04 pool 누락, EV-05 부분 metric의 stage_ready 분리가 모두 기대대로 차단됨을 별도 프로세스에서 재현했다. 전체 dataset metadata는 여전히 별도 검토 대상이다.

다만 EV-01 수정의 인접 정상 회귀가 발견되어 아직 FAIL을 유지한다. 최종 label=clear인 두 turn 대화에서 첫 모호 발화의 expected_prior.allowed_actions=[clarify], 실제 prior는 정상 clarify+질문, 최종은 정확 SKU 후보를 반환해도 earlier_turn_oracle_failure로 실패한다. prior_case가 최종 label=clear를 상속하여 정상 첫 질문을 unnecessary_clarification으로 처리한다. turn별 label/oracle의 적용으로 이 정상 흐름을 보존해야 한다. 실패 사례 차단만으로 승인하지 않았으며 evaluator에 재현 조건을 전달했다.

## 3차 최종 bounded 판정 — PASS (평가 장치 범위)

독립 self-tests **32/32 PASS**, skip/error 0. 별도 프로세스에서 모호 최초 입력→정상 질문→명확 SKU 응답이 성공하고, 이전 관측의 잘못된 case_id는 실패함을 확인했다. 기존 EV-01~04와 EV-05 부분/단계 판정 분리 요청을 닫는다. 이는 실제 제품 자연어 정확도 PASS가 아니다.

새 공개 `evals/manifest.json`의 산술을 taxonomy와 프로그램으로 대조했다. 총420, 고객300/경영주120, dev252/validation84/holdout84 및 각 role/split/category 수가 일치한다. 공개 family hash 세 집합의 교집합은 0이다. private 본문은 접근하지 않았으므로 holdout의 의미 정답·실제 내용의 독립성은 본 검토가 보장하지 않는다. 모델 호출0, 현재 catalog_size220/hash `9d650de38a2e185a018c48a276927b18359f8b7e51114113849afa4c6778eb6b`; 최종248 카탈로그로 재동결 예정이므로 이 데이터 hash는 baseline 실행 승인으로 사용할 수 없다. 재동결 후 메타데이터 최신성 확인 및 실행 전 reserve 검사 필요.

최종 검토 fingerprint:

- scorer.py: `adf098b727f2f79651d3fb7dd7be80e1b733749f7eec97f83accb0b8cc4283d3`
- case.schema.json: `c45ab14aecb5b3db3f06e491d3e661d62a6cf6fad51e7bb071e7ef31042fd311`
- tests/test_scorer.py: `a978fa04cdca3f66735adf83d7986e374fde5f71d1fa25487161bcbee2d19dcf`
- manifest.json: `d816ccc52c4eecd044b99a1e0d2d5deaa03d83f4f82fe8f4a6c09d7104823db7`

초기 FAIL과 수정 과정은 감사 기록으로 보존한다. 현재 판정은 공개 평가 장치의 bounded PASS, baseline/validation/live/holdout/제품G3~G6는 모두 not_run이다.

## 최종248 재동결 메타데이터 갱신

공개 manifest만 재확인: catalog_size248, catalog_hash `f2696abe92521e3ff8f9ab43cb36a1d297a6fd23d272e239605b49fab4343b1e`, validation hash `180e1ef3890bbde535e4be29a75698b5fa42d9e77a915da9d3d3646c9e486f46`. 총420 및 split family hash 교집합0 유지. repeat_ready에 stage_ready 필수 조건이 추가되어 부분/fixture 반복은 release-ready로 승격되지 않는다. holdout 본문 접근 없음. 실제 live 평가는 여전히 not_run. scorer SHA256 `92caabf7aefbdc68e7d36e34772d8034a0b2260f1ce3ac1ade43ae475cc82f74`.
