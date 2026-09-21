# N02 G5 증거 검사기 독립 검토

- 상태: **측정·증거 검사기 독립 PASS**. 아래 최종 재검증은 기구 범위이며 G5 제품 PASS가 아니다.
- 검토자 research, 기구 작성자 preflight_builder, root는 gate/CI 통합 작성자.
- context-n02-v6 `0555063cc1bca9224124b2522d9371bf8ec8178ada49083c9bd306ae0d738a3b` 직접 ACK. 입력29개 hash 모두 일치.
- 모델 호출0, 실제 예산장부 쓰기0, 보호 holdout 본문/생성기 접근0. 모든 반례는 TemporaryDirectory의 명시적 synthetic evidence package로 실행했다.
- 소유 보고서만 변경하며 checker/공통파일은 수정하지 않았다.

## 초기 독립 반례

1. R01: ux.best의 모든 liveUsage를 usage={} / cost_usd=null로 바꾸어도 PASS. unknown usage/cost는 정상 live로 인정하면 안 된다. 관측된 숫자와 보수적 null 중단을 구분해야 한다.
2. R02: ux.best row의 elapsedMs=120을 유지하고 modelNetworkMs=1000000 / nonModelMs=0으로 바꾸면 PASS. max(0,elapsed-network-budget) 잔여식만 맞추면 불가능한 대기를 숨기고 성능회귀를 상쇄한다.
3. R03: ambiguous workload의 questions=99가 PASS. 최대질문2 규칙이 clear에만 적용되어 있었다.
4. 역할 독립 정상 반례: customer implementers=['research','root','builder'], reviewer='auditor'; merchant implementers=['root','builder'], reviewer='research'면 해당 역할 독립 조건을 만족한다. 초기 cross-role union 검사는 이를 거절하는 과도한 제약이었다. root가 해당 role+공통실제작성자 기준으로 확인했으며, cross-union 제거 후 독립 실행한 이 정상 package는 PASS했다. 해당 역할 자기검증과 두 역할 동일 검토자는 계속 거절해야 한다.

위 결함은 builder/root에게 전달했다. 실제 출시 증거를 만들어 넣거나 검증 기준을 낮춘 것은 아니다. R01~03 최종 수정 및 기존 정상/인접 회귀를 실행하기 전 PASS 리뷰 JSON을 발급하지 않는다.

## root gate/CI 읽기 검토

현재 quality/gates.json은 quality-preparation 단계이며 N02-UX-INSTRUMENT 및 N02-RELEASE-INSTRUMENT 기구 task만 선언한다. scripts/test_runner.py는 tests/release와 tests/ux-benchmark를 실제 수집하고 누락/0test/skip/실패를 거절한다. run_gate.py는 현재 fingerprint와 실행·리뷰 fingerprint, 정확한 CORE coverage 및 컨텍스트 ACK를 대조한다. .github/workflows/gate.yml은 npm ci 후 npm run gate를 실행하며 실패시에도 artifacts/raw를 업로드한다.

이 준비 CI 성공이 G5 live 통과를 뜻하지 않도록 phase/scope가 분리돼 있다. 실제 G5 단계에서는 check_release_evidence.py의 정식 manifest 검사를 required check로 연결해야 한다. 기본 manifest 부재는 NOT_READY이어야 하며 기구 단위테스트의 가짜 positive를 실제 manifest로 채택하면 안 된다. 아직 최종 통합 코드는 동결 전이다.

## NL 재시도 정상 경계 확인

UX의 unknown 즉시중단/no-retry와 NL E02의 ADR003 일시 timeout/429 최대3회는 별도 계약이다. NL의 실패 attempt usage/provider unknown 기록 뒤 최종 성공은 허용될 수 있으므로 unknown 이력을 일괄0으로 요구하거나 지우면 안 된다. 초기 best NL unknown-provider==0 조건을 builder가 제거하기로 했다. 최종 frozen stage/correctness/누락0/pending0/중단없음 및 원래 attempt 분모는 유지한다. 검토 중 제안했던 NL usage_unknown_attempts 일괄거절은 E02 원문 재확인 후 즉시 철회했으며 신규 기준으로 채택하지 않는다.

scorer의 필드명 outbound_attempts는 provider_called=True인 attempt 합계이다. HTTP 전송 총수와 동일한 뜻이 아니므로 execution.provider_called_count와의 equality는 맞다. false/null HTTP attempt 이력과 최종 성공 판정을 혼동하지 않는다.

## 최종 독립 판정 — PASS, 기구 범위

- 동결 v1을 직접 읽고 Python44개 selftest를 독립 실행:44 PASS, skip0/failure0/error0. 테스트는 TemporaryDirectory의 명시적 synthetic protocol만 생성하며 실제 evidence manifest를 만들지 않는다.
- 원래 발견 반례를 별도 실행한6개 delta probe: R01 unknown usage/cost→UX_UNKNOWN_USAGE_OR_COST, R02 불가능 시간→UX_TIME_ACCOUNTING, R03 질문99→UX_QUESTION_LIMIT로 모두 거절. 역할별 독립 QA 정상 허용, NL 합법 unknown/not-called 재시도 이력+최종 정상 허용, HTTP 분모 조작 거절까지6/6 PASS.
- 실제 root에 checker CLI 실행:exit1/NOT_READY_MANIFEST_MISSING. 이는 예상된 정상 거절이며 G5 통과 증거가 아니다. 실행 과정의 모델/브라우저/실장부/holdout 접근0.
- baseline336은 모든 시도·실패를 보존하되 품질 미달을 허용한다. validation84 두 회차는 서로 다른 run ID 및 같은 binding으로 각자 최소·불변식 통과해야 한다. holdout84는 public manifest의 hash/분포와 aggregate attestation만 읽고, 후보 동결 및 두 validation 이후의 실행 순서를 확인한다. 실제 정답/발화는 열지 않는다.
- UX baseline/best는 동일8종×3유일반복·seed/clock/workload/harness를 요구하고 cached summary 대신 raw row의 최댓값/중앙값을 재산정한다. network interval union과 budget 합계·잔여시간을 다시 계산하고 실제provider 여부/known token 합계/known cost를 대조한다. 결과의 SQLite hash/정확성 보고를 검증하지만 실제 browser session을 JSON만으로 재현하거나 암호학적으로 증명하는 도구는 아니다.
- runtime 전체 파일집합/필수anchor·Prompt/catalog/source binding, 두 역할 독립 live browser/SQL 보고, 두 정책 관점·해결안, CORE01~26 evidence, 정확 Preview SHA를 요구한다. G6는 항상 pending이고 CORE13만 지정된 G6_PENDING을 허용한다.
- 역할별 implementers에는 실제 영향 공통작성자도 포함해야 한다. 검사기 자체는 선언된 명단·hash의 일관성을 검사하므로 작성자 명단 누락/실행 사실 허위 자체를 암호학적으로 판별하지 않는다. 최종 독립 보고와 실제 원본 증거 검토 책임은 남는다.
- 공개 scripts/run_goal_eval.py 편입 delta는 e02-driver-review.md에 별도 기록했다. 현재/best binding은 공개 경로로 등록하여 private 경로 금지 규칙을 유지한다. baseline의 원래 private driver/hash는 역사적 binding metadata로 보존한다.

### 동결 소스
- `scripts/check_release_evidence.py`: `1032668e33e7de788a7638088f574158b0a27a3d6b0352b76568d64607fd1d04`
- `tests/release/test_release_evidence.py`: `255f6bf5896290752659ca6ecd021b87bf2b745088ae37607ccdba3dd0f788f2`
- `tests/release/README.md`: `c820b2b4e931abd4cf0c4b5445d9218da8c9b2248e318eabe1b7d1be21b5d4f0`

현재 root 통합 및 전체 fingerprint 확정 전이므로 quality review JSON 발급은 동결 통합본 대조 후 수행한다. 실제 NL 기준선/선정 best/holdout/UX live/G5/G6 결과는 이 기구 PASS로 대체하지 않는다.

검토시각: 2026-09-21T10:25:43.212166+00:00

## root 최종 통합 ACK

- source fingerprint `89a5ff23ad60442a02e05550094f301c1f56932539640334b20a2fbba829196c` 직접 재계산. context-v6 및29개 입력hash 다시 일치. 두 quality review JSON 발급 완료.
- root/domain 기구 파일12개 byte-for-byte 비교 일치. Python6필수suite 실제 수집142개(scripts18/gates18/evals32/eval-runner23/UX7/release44), UX Node test2mts+1mjs 존재 및 source fingerprint 포함 확인. 이 단계에서는 수집 확인이며 전체 gate 실행은 root가 후속 수행한다.
- TS noEmit+allowImportingTsExtensions 조합과 typecheck/build required check, CI npm ci→npm run gate→always artifacts/raw 수집 경로를 확인했다. 본 ACK로 실제 모델/G5/G6 검증 범위가 늘어나지 않는다.

## Optional Next config 및 실제 B0 공개 집계 — 독립 delta PASS

조정자의 좁은 정정 배정에 따라 검토했다. 기구/실제baseline 공개 증거 정합성 범위이며 G5 제품 PASS나 UX 예외를 만들지 않았다. 실제모델0/장부쓰기0/보호holdout 및 생성기열람0, 소스수정0. 이전48회 UX 실패분모 및 비교 NOT_READY는 그대로다.

### 설정 파일 존재 가정 정정

- git diff로 확인한 checker의 유일한 동작변경은 next.config.{mjs,js,ts} 중 하나가 반드시 있어야 한다는 require1줄 삭제다. 이 앱은 해당파일이 없는 기본설정으로 실행되므로 이전기구가 과도한 파일존재를 가정했다. RUNTIME_CONFIGS의 존재하는 파일 hash 수집과 필수 runtime anchor들은 그대로다.
- 독립 unit suite48/48 PASS. 추가로 reviewer 별도임시package에서 설정 없음 정상1 + mjs/js/ts별 추가/변경/삭제9 =10개 반례를 직접 실행했다. 없음은PASS, 실제파일집합/내용이 변한9개는RUNTIME_SET_OR_HASH_MISMATCH로 모두 거절됐다.
- 실제root runtime_files를 호출해43파일을 수집했고 next.config를 만들지 않았다. 기본CLI는exit1/NOT_READY_MANIFEST_MISSING을 유지했다. 초기 검토의 기본CLI 검사는 manifest 없음에서 먼저 거절되어 이 runtime 존재 가정까지 실행하지 못했던 범위였으며, 이번 실제runtime 검사로 그 공백을 닫았다.

### 공개 B0 bundle 검토

- quality/release/evidence/baseline의 report/execution/binding/bundle JSON 및 EXPORT.md를 읽었다. 실제정식release manifest는 미생성이다. 공개 bundle을 Checker.nl(best=False)로 독립 실행해 형식/역사적binding/집계정합성PASS를 확인했다.
- 원래 report에서 case_results만 제거한 결과가 공개report와 정확일치, 원래 n02-baseline-config.json과 공개binding.config도 정확일치. 실행출처8개 파일의 바이트hash를 직접 대조했다. canonical binding fingerprint는 원래80f9a9a1e7106ae84dd3797d2ca45f825a3f3eef4a2623d8ac3083e400e5f11b 그대로다.
- original checkpoint에서336case/367turn/367unique attempt를 독립집계했다. provider true367/false0/unknown0, HTTP성공316/실패51, 알려진token6,208,489/비용$1.659112, pending0을 공개집계와 대조했다. 공개baseline336의 planned user turn368 중 미시도1개를 유지한다.
- 품질227/336 PASS·109FAIL, incomplete51, stage_ready=false/nl_minimum_pass=false가 그대로다. 처리complete와품질합격을 구별한다.
- checker에 private 경로 접근을 거절하는 reviewer guard를 걸고 실제 baseline.nl을 실행했다. 읽은 경로는 공개report/execution/binding3개뿐이었다. 역사적 private driver/proof **문자열**은 hash 재현을 위해 보존하지만 따라 열지 않는다. best/current에서private파일접근을 허용하도록 기준을 바꾸지 않았다.
- 모든 공개JSON이 sanitizer를 통과했고 원문case_results/질문/정답/응답·비밀값을 새로내보내지 않았다. 공개원본hash/경로메타데이터와 비밀파일내용은 구분한다. 집계report는원본에서case_results만제거되어 원문본문이 없는 것을 직접대조했다. sanitizer는일반DLP보장이 아니므로 이 검토는 실제export내용대조를 포함한다.
- 시작/종료시각은원본run.lock birthtime/summary mtime의근사치로명시됐고, provider시간증명으로격상하지않는다. historical 전체runtime hash는null이며 현재best전체source라고주장하지않는다.

### delta 동결
- `scripts/check_release_evidence.py`: `47c99b09f4debdf4476c81e72fa7a1d155ff339fd14180040ebf01c5d6056add`
- `tests/release/test_release_evidence.py`: `40eec360c26c95e8b7b9d064a838a5eaa22395e6ac3d1c299bec4ddae70b8315`
- `tests/release/README.md`: `081280f55281871a1c81bfe468508c341d72f42a1968bd30de1ab2081527e158`
- baseline/report.json: `dcb9485f6c70292148575463d35a245d08f72195fb7518e8f9f35f336c9ca272`
- baseline/execution.json: `4609589d0a06107efad6f5eafaabbb85e18a5de6cd659c924c942eb956fef0cb`
- baseline/binding.json: `1817a4d2692c7c72e27624ce7620406b953d875aef3d0c89a69cf63953421300`
- baseline/bundle.json: `7c60027b42722809306fcd51e17962fddf9ea270b064f85859eb425a7ef610ca`

검토시각: 2026-09-21T10:51:03.747319+00:00
