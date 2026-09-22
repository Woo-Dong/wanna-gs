# ADR-003 독립 평가·분모·holdout·예산 검토

- reviewer: `/root/method_auditor`, proposer와 별도 agent. 다른 reviewer의 결론을 읽지 않았다.
- 검토 회차: 1/2.
- consumed_context_hash: `74bf125ebe9c8ed2f7933abb55b08c904400f3a7ba1319c395a2429c32c20679` + ADR-003 SHA-256 `7a83348b51667d5f5ab15c60ab3b15d51a382b87e892a9435c2c5e3bc7f3fb67`.
- 적용 기준: card, CORE-14/17~23/25/26, docs/17/20/23 및 ADR-002의 2차 상태검토. 이 문서만 작성하며 정책/평가셋/실행기를 수정하지 않는다.
- 실행 상태: 정책 의미·반례 검토다. 평가 dataset·baseline·candidate·holdout·latency/UX 계측은 `not_run`.

## 판정

**아래 3개 보완 후 채택 여부를 2차에서 닫을 수 있다.** 역할별 기준, mandatory 오류0, 가족 단위 분할, 후보/정체 한도, 정확도와 transport 분모 공개, 절대 편의성/회귀 기준은 적절하다. 그러나 holdout 실행 순서, 다회 대화의 실제 호출 예산, best 반복 결과의 판정이 현재 해석에 따라 달라진다. 사용자 판단을 새 선행조건으로 만들 필요는 없다.

## 1. [높음] baseline420/모든 case 1회가 holdout 선실행과 충돌

300+120=420이며 각 역할의 holdout20% 합계는84다. 따라서 “모든 case 기준선1회”, “baseline420”을 그대로 실행하면 최종 보호 holdout까지 후보 선정 전에 사용한다. 정확 발화/정답을 숨겨도 후보 담당이 holdout 집계로 반복 선택하면 홀드아웃이 검증셋이 된다.

보완: baseline은 dev+validation만 실행한다(정확 비율 기준252+84=336, 실제 family 배치 분모는 manifest로 고정). 최종 best의 code/model/prompt/search/seed/config를 freeze하고 독립 평가자가 holdout84를 처음 실행한다. 후보 담당에게 holdout 내용·case별 오류를 넘겨 튜닝하지 않는다. 초기 baseline을 holdout에서 비교할 필요가 있다면 최종 시점에 evaluator가 함께 실행하고 그 결과로 후보 재선정 루프를 열지 않는 별도 사전 계약이 필요하다. 현재 단순화는 best만 평가하는 것이다.

반례: baseline holdout accuracy92%를 보고 prompt를 바꾸고 holdout95%가 될 때까지 다시 실행. 원문을 비공개로 두었어도 selection leak다. 기대값: 해당 데이터는 regression으로 전환하고 독립 새 family를 마련한 뒤 frozen version 최종 평가하며 노출/교체/추가 호출을 기록한다. 첫 실패를 삭제하거나 PASS만 남기지 않는다.

## 2. [높음] case 수와 실제 model call 수를 구별하고 필수 평가 reserve를 확보

“고유 발화/대화” 한 case가 확인질문→정정→재질문 등 2~3회 모델 요청을 만들 수 있다. 현재 baseline420/validation84의 비용 산식은 case=call 가정이며 자동 재시도까지 포함한 전체2400 제한을 보장하지 못한다.

보완할 최소 계약:

- dataset manifest에 `case_id/family/split/role/max_model_turns`를 고정한다. case 정확도 분모와 outbound provider attempt 분모를 별도로 집계한다. 401 입력 거절처럼 모델 전 단계의 HTTP 요청은 model attempt가 아니며 별도 요청 수로 기록한다.
- baseline·각 후보·best repeat·holdout·필수 browser/G5/G6의 상한을 실제 case별 최대 turn 및 허용 transport retry로 계산한다. per-role validation은 nominal customer60/merchant24이고 combined84라는 점을 명시한다. 한 역할 후보에 combined84를 쓰는 보수 추산은 허용되나 실제 표본 축소 근거로 쓰지 않는다.
- 다음 선택 후보를 시작하기 전 `used + candidate upper bound + remaining mandatory reserve <= total cap`인지 검사한다. reserve에는 아직 남은 best 검증·holdout·필수 회귀·G5/G6와 그 허용 재시도가 포함된다. model/config 변경이면 영향 재검증 reserve도 갱신한다. reserve가 부족하면 선택 실험부터 중단한다.
- $15는 로컬 추정 soft stop이다. 모델/단가 출처·확인일·token accounting과 추정 unknown을 명시하며 계정 공급자 hard cap으로 주장하지 않는다. 응답 없는 실패에서도 시도 수는 소비하고 실제 비용 미확정은0이라고 단정하지 않는다.
- cap 도달로 필수 검증을 못 하면 완료가 아니라 미완료다. 호출한도/후보한도를 task 이름 변경이나 새 모델 선택으로 초기화하지 않는다.

반례: 각 validation 대화3turn이면84case=252calls이고 transport retries가 더해진다. case 수84만 차감하면 상한을 초과하거나 G6 예산을 선택 후보가 먼저 소진한다. 기대값은 사전 예약 검사에서 후보를 중단하고 필수 경로를 남기는 것이다.

## 3. [중간] best 추가 validation의 미달·회귀 판정 필요

현재 “best validation 추가1회로 변동성 점검”은 실행 횟수는 고정하지만 점검 결과가 첫 실행과 다를 때 출시·채택 판정이 없다.

반례: 1회차 customer clear accuracy96%, 2회차90%; 평균93%로 실패일 수도 있고 첫 결과만 사용하면 통과일 수도 있다. 또는 2회차에 허구SKU1개가 있지만 1회차 mandatory0만 보고 통과시키는 구현이 가능하다.

보완: 사전에 고정한 repeat 각각의 role/핵심 지표·분모·mandatory 오류를 보고한다. mandatory 오류는 어느 반복에서든0이어야 한다. 출시 최소는 두 반복 모두 충족하도록 고정하거나, 독립 검토한 합산 판정식을 baseline 전에 명시한다. 이번 최소 정책으로는 각 반복 통과를 권고한다. repeat가 미달/회귀하면 해당 candidate 승격을 보류하고 이전 release-safe best가 있으면 되돌린다. 이전 best도 현재 seed/model/config에서 유효한 증거가 없으면 자동 PASS하지 않는다. 허용한 추가 repeat 수를 넘어 좋은 결과가 나올 때까지 다시 실행하지 않는다.

## 유지할 범위 및 비차단 명확화

- 범주별 실제 분모와 최악 범주 공개, role/split별 출시 기준은 전체 평균으로 정상/예외 실패를 숨기는 것을 막는다. 필수 정상 시나리오100%와 mandatory 오류0이 우선이다. 작은 validation에서 오류2건 개선이 어려우면 ceiling/plateau가 될 수 있으며 이를 합격선 완화 이유로 쓰지 않는 정책은 적절하다.
- latency P95 목표 미달은 UX 회복 한계이며 정확도 면제가 아니라는 구분은 적절하다. model/config/자료를 바꾸면 같은 validation 조건과 영향 회귀 증거가 필요하다.
- paired 1회만으로 확실한 통계적 향상을 주장하지 않는다. 추가 repeat의 안정성과 case별 paired 결과를 근거로 “이 평가셋에서 개선”이라고 보고하고 모집단 성능 보장으로 확대하지 않는다.
- 지도 제공자 실제 사용과 접근 제한의 기술 가용성은 구현/배포 조사 및 실행 증거가 필요하다. 이 검토는 라이선스/서비스 최신 정책 확인이나 비용 산정 성공을 대신하지 않는다.
- 공개 example는 dev only, holdout은 evaluator 소유, leakage시 새 family 보충, role별 연속3·최대6/전체12 및 mandatory 면제 금지는 유지한다.

## 후속

조정자가 위 1~3을 보완하고 새 hash를 전달하면 2차 검토로 종료한다. 아직 dataset/측정/계측이 없으므로 이 보고서가 PLAN-READY 전체·실험 성공·G5의 증거가 되지는 않는다. 기준을 채택한 뒤 evaluator가 분모/turn/정답/split hash를 고정하고 구현자와 독립적으로 품질을 판정해야 한다.

## 2차 검토 — 채택 동의

- 검토 대상 SHA-256: `05aa01b14b7f65ce3b9376420a02a6ed6f774542eb8e889e62f34e2e4c2c9d34`.
- consumed_context_hash: 초기 hash + 위 ADR-003 fingerprint. 검토 회차2/2; 다른 reviewer의 보고서는 읽지 않았다.

**보완본의 채택에 동의한다. 1차 지적 3개는 해소됐다.** baseline336은 dev+validation으로 제한되고 protected holdout84는 frozen best 이후 독립 평가자가 한 번 실행한다. case/turn/retry와 실제 호출의 차이를 명시하고 best·holdout·G5/G6 및 재시도분을 먼저 예약한 뒤 선택 후보만 남은 자원으로 실행한다. 두 validation repeat는 각각 출시 최소/mandatory 기준을 통과해야 하며 미달을 합산으로 상쇄할 수 없다.

범주당 각 split 최소2, baseline 전 family manifest 고정, 정답 SKU 포함+오답 유도 없음+고객 확인 경로의 composite, 경영주 모든 제약 필드 일치, UX activation 정의와 workload별 최댓값/중앙값 측정도 재현 가능한 기준이다. 실패 실행수는 별도로 공개하므로 편의성 성공 분모에서만 관측해 실패를 숨길 수 없다.

실행 담당은 명목상 “브라우저·G6 여유40case”를 실제 측정 계획의 hard reserve로 그대로 쓰지 않는다. UX 8종×3회×baseline/best만으로도48 workload 실행이므로 실제 turn/retry/G5/G6를 합산하는 새 보완 규칙을 적용해야 한다. 이는 보완본이 이미 요구하는 실행 전 예산 계산의 구현 확인 항목이며 합격선·실험한도 변경은 아니다. provider attempt와 token cost 추정, unknown 비용의 처리는 docs/25 및 실행 manifest에 기록한다.

모든 dataset/성능/품질/UX/예산 enforcement는 여전히 `not_run`이다. 이 판정은 사전 기준 채택 동의이며 PLAN-READY 전체 또는 제품 출시 성공을 대신하지 않는다. 새 실제 반례가 없으면 같은 정책 토론을 재개하지 않고 dataset/runner 구현과 독립 실행 검증으로 진행한다.
