# E02 실행 연결 코드 독립 검토

- reviewer: `/root/research`; 작성자: `/root`.
- consumed_context_hash: `10701ed7619c86fe94cec16a31b6ac8b02a1afa9f2843ffdcce4ec446e952234`.
- 검토 대상: `artifacts/private/run-20260921/run-eval.py`와 기존 검증된 `scripts/run_nl_eval.py`의 호출 계약. 실제 보호 holdout 본문 접근0, 모델 호출0, 실제 goal ledger 변경0.
- 최종 판정: **좁은 glue 검토 PASS**. 아래 1차 지적을 작성자가 수정했고 합성 반례를 재검증했다.
- 1차 판정: **보완 필요**. 실행기 로직을 재구현하지 않고 기존 검증기를 호출하는 방향은 적절하나 아래 연결 경계를 보완해야 한다.

## 확인한 정상 계약

`check_inputs`에 cases/config/coverage/catalog/states/holdout flag/frozen-best를 전달한다. 기존 검증기는 source hash, catalog, 전체 분모, 실제 사용자 turn, frozen best와 두 validation 보고서 및 동일 후보·설정 결합을 검사한다. driver가 이를 우회하는 별도 실행 경로는 없다. protected 출력은 artifacts/private 아래로 제한한다. Runner의 원자적0600 checkpoint·pending 재실행 차단·holdout claim·resume 계약을 그대로 사용한다.

`--execute`가 없으면 PLAN_VALID만 출력하고 HttpTransport/Runner.run을 만들거나 호출하지 않는다. Budget 객체 생성 자체는 파일 쓰기나 호출이 아니다. prior_reserve50을 지정하고, prior_actual_calls='unknown'으로 보고한다. 이는 초기smoke/I01을 덮는 보수 예약이며 실측50회가 아니다. 기존 Budget의2400회/$15 기준은 변경하지 않고 미상 비용도50×$0.05=$2.50 예약한다. 같은 ledger 파일을 사용하려는 문자열은 일치한다.

## 좁은 수정 요청

1. **holdout 읽기 전 검사 누락.** 기존 CLI는 파일명/경로에 holdout이 있고 evaluator flag가 없으면 `read_jsonl` 전 거절한다. driver는 먼저 cases를 읽고 check_inputs에서 뒤늦게 거절한다. 보호 원문 접근 경계를 유지하도록 사전 flag 검사를 복원해야 한다. 합성 stub에서 --holdout 없이 `synthetic-holdout.jsonl`의 read_cases 이벤트가 먼저 발생한 뒤 STOPPED가 되는 것을 확인했다. 실제 holdout은 사용하지 않았다.
2. **동일 ledger가 cwd에 의존.** ledger/bypass/catalog 경로가 상대경로다. 다른 cwd에서 실행하면 다른 `artifacts/private/.../nl-budget.json`을 사용할 수 있어 기존 예약/시도 장부를 이어쓰지 못한다. r.ROOT 기준 절대 경로를 사용하거나 진입시 작업디렉터리를 고정해야 한다. output 상대경로와 config/state 경로의 해석도 일관되게 명시하는 편이 안전하다.
3. **prior 설정 검사에 assert 사용.** `assert config['prior_call_reserve']==50`은 python -O에서 사라지고 50.0도 통과한다. 명시적 정수 타입+값 검사와 RunnerError로 바꾸면 잘못된 config의 fingerprint/계획과 실제 Budget50 불일치를 막는다. optimize=1로 컴파일한 driver에 prior0 합성 config를 주자 PLAN_VALID/50으로 통과함을 확인했다. Budget 자체는 여전히50이므로 상한이 늘어난다는 의미는 아니다.
4. **비보호 출력은 private 위치 강제 없음.** driver의 output 검사는 protected case에만 적용된다. 합성 dev+--execute+artifacts/raw 출력에서 Runner.run까지 도달했다. 이번 운영 계약이 모든 content 출력을 private 아래에 모으는 것이라면 모든 실행 출력에 동일 경로 조건을 적용해야 한다. 파일0600과 저장소의 비공개 경로는 서로 다른 조건이다.

추가로 기존 CLI와 같이 일반 JSON/파일/키 오류를 고정 오류코드로 변환하면 traceback 대신 일관된 STOPPED 보고를 유지한다. source_files에 driver 해시를 등록하는 일은 baseline config 작성 시 조정자 예정 작업이며 현재 구현 완료로 세지 않았다.

## 실제 확인 방법과 범위

원본 driver 코드를 compile/exec하되 run_nl_eval 의존만 메모리 stub으로 대체한5개 합성 probe를 실행했다: 기본 미실행, holdout 사전읽기, dev 공개경로 실행, 최적화시prior검사, protected 공개출력 차단. 정상 2경계는 확인했고 위 연결 문제들을 재현했다. 이것은 실제 runner/Budget 회귀나 live 성능 평가의 대체가 아니다. 실제 파일의 holdout·비밀값·장부는 열거나 바꾸지 않았다. 제품/공통 코드를 수정하지 않고 이 보고서만 작성했다.

## 작성자 보완 후 최종 재검증

최종 driver SHA256 `e0d2162c04cabada3212f13eec54685082da6384a06c063b846e1129db371444`; 기존 runner SHA256 `ae3450d3009f59cf344cdaac10f1ca42999f6daaacdb488bd61837a9ad2f008d`.

작성자가 ROOT 기준 경로 고정, 대소문자 무관 holdout 파일 사전 차단, 명시적 int+50 검사, 일반 오류의 정적 STOPPED 변환 및 모든 출력의 ROOT/artifacts/private 제한을 반영했다. 수정 후 합성 stub6개를 실행했고 기본미실행·사전읽기0·다른cwd(/tmp)의 동일ledger/출력·최적화(-O 상당)에서도prior0차단·50.0차단·일반오류코드가 모두 기대대로였다. 마지막 출력 보완은 dev+execute의 artifacts/raw 및 private/../raw가 Budget/Transport/Runner 생성 전에 exit2, 정당한private 경로는 mock run까지 도달함을3개추가probe로확인했다. 실제 모델·보호본문 접근·goal ledger 쓰기는 계속0이다.

prior50은 여전히 보수 예약이며 실측이 아니다.2400회/$15 상한은 기존 Budget 그대로다. 최종 driver hash를 baseline source_files에 등록하고 같은 config/ledger로 실행하는 것은 조정자의 후속 작업이며, 정식 baseline·validation·holdout 실행 성공을 이 검토가 대신하지 않는다.

## 공개 실행기 경로 편입 delta

- `scripts/run_goal_eval.py` SHA `7b4d52598a127272d0a382409683fc2bb76f141b8eedc59bd38844a13e188795`. 이전 private driver SHA `e0d2162c04cabada3212f13eec54685082da6384a06c063b846e1129db371444`는 그대로 보존됐다.
- 직접 diff 및 정확문자열 비교에서 유일한 차이는 run_nl_eval import 경로가 기존 parents[3]/scripts에서 새 파일의 parent(scripts)로 바뀐 한 줄이다. 실행 정책/argparse/check_inputs/holdout guard/private output/prior50/Budget/실행 기본off 로직은 동일 바이트다. py_compile PASS.
- baseline은 기존 sourcehash를 유지하고 다음 candidate/best source_files는 공개 script 경로를 사용할 수 있다. private 경로 금지 G5 규칙을 완화할 필요가 없다. 새 실제 모델/holdout/장부 접근0. 기존9개 mock 검토의 로직 동일성에 대한 좁은 경로 delta 승인이다.
- 확인시각 2026-09-21T10:25:17.069786+00:00
