# E02 평가 전송 실행기 독립 검토

- 검토자: `/root/preflight_builder` (해당 실행기·자체 테스트 작성자 아님).
- 구현 소유자: `/root/method_auditor`; 소스·자체 테스트 수정 없음.
- 범위: `scripts/run_nl_eval.py`, `tests/eval-runner/test_nl_transport.py`, 호출하는 공개 adapter/scorer 계약. 실제 보호 holdout 원문·정답 파일은 열지 않았다.
- 방식: 검증 스킬 및 docs/09·13·14·23·25, ADR003 기준. 독립 합성 사례와 localhost 가짜 HTTP만 사용. 실제 모델 호출 **0**.
- 목적 보존: 정상 다회 대화의 실제 응답 이력, 사례 전체 분모, 모의/실제 구분을 유지하면서 재시도·예산·재개·최종 후보 동결 경계를 검사한다. 기존 도메인/UI 자체 테스트를 E02 독립 증거로 사용하지 않는다.

## 초기 판정: FAIL — 수정 후 재검증 필요

2026-09-21 최초 독립 실행 대상:

| 파일 | SHA-256 |
|---|---|
| 실행기 | `13c095a95eb36aae28c30d6fcb5df7e7ef09894524d48a9d647651a131cf6012` |
| 구현자의 자체 테스트 | `b36721a6b47f09ed7a6511768bc07bac37e363406ebeb56b680c5414f731911d` |

독립 실행: `python3 artifacts/private/run-20260921/e02-independent/probe.py` — **8 tests, 6 PASS, 2 FAIL**. 복구 담당에게 반례를 전달했다. 상세 합성 입력·출력은 해당 비공개 경로의 `probe.py`, `probe-output.txt`에 보존한다. 이 디렉터리에는 실제 holdout 내용이나 비밀값이 없다.

### 수정 요청

1. **다른 후보의 validation 보고서가 holdout 진입을 승인한다.** frozen best에는 현재 source/prompt/catalog를 지정하고, 보고서 두 개에 `source_sha=old-source`, `prompt_hash=old-prompt`, `model=wrong-model`을 넣었다. 두 보고서끼리 run fingerprint/dataset hash가 같으면 `check_inputs`가 통과했다. 보고서가 선택 후보의 source/prompt/model/설정 및 고정 validation 분모를 검증한 결과인지 직접 연결해야 한다. 현재 상호 일치만으로는 과거 후보 PASS를 새 후보에 사용할 수 있다.
2. **실행기 소스 fingerprint가 필수 항목이 아니다.** config `source_files`에서 `scripts/run_nl_eval.py`를 삭제한 뒤 정상 입력 검사를 통과했다. 실행기 자체·adapter/scorer와 실제 요청/응답을 바꾸는 서버 구현의 동결 파일 집합을 고정해야 한다. VERSION 문자열이 그대로인 구현 변경을 resume fingerprint만으로 찾을 수 없는 공백이다.

### 독립 통과 경계

| 검사 | 실제 결과 |
|---|---|
| 사례 2개 모두 지속 429 | 사례별 최대 3회, HTTP 총6회. expected2/recorded2/failed2 유지. quality는 not_scored |
| HTTP 성공 직후 ledger finish 전 중단 | pending 유지. resume은 UNCERTAIN_PENDING으로 중단, 총 HTTP 1회, unknown call 1 유지 |
| 2턴 사례 다음 새 사례 | 두 번째 턴에 이전 실제 JSON 응답만 전달. 새 사례 history 빈 배열. 정답/research sentinel 전송 없음 |
| $15 소프트 한도에 필수 reserve 포함 | HTTP 호출 전 COST_SOFT_STOP |
| call upper bound 2399→2400 | 마지막 1회 예약 가능, 다음 예약 CALL_RESERVE_STOP |
| provider 호출 후 timeout usage 미제공 | usage/cost null, provider_called true 보존. 0 토큰으로 조작하지 않음 |

정적 확인: endpoint origin 제한, redirect 차단, 보호 bypass를 요청 헤더에만 배치, CLI 기본 plan-only, content 파일 0600, holdout 플래그·private 출력 경로·동일 dataset 중복 claim 방지 코드가 있다. 구현자 테스트를 독립 통과로 재분류하지 않았으며, 이후 독립 재실행 결과를 아래에 추가한다.

실제 모델 품질·전체 336/84 실행·앱 UX·Preview·G5/G6는 본 검토의 PASS 대상이 아니다.

## 보조 상태 생성기 독립 검사: PASS

Root가 별도로 작성한 `scripts/build-eval-state.mts`를 추가 검토했다. 소스 수정 없음. fingerprint `f453a2495bdb7a54f99d2a4a2379bc65f5be576a172bfb77d05874c05599a915`.

- 공개 baseline 전체에서 경영주 96개 상태를 실제 seed SQLite로 독립 재생성. 출력 SHA-256 `d1a0845a4f45f44af9698963c700e9dfa24d13bb3a4b8b729b9b15e8a15278e1`로 기존 root 산출물과 정확히 일치했다.
- 96개 모두 입력 context의 점포/SKU 집합과 출력 group을 대조했다. SKU별 유효수요·신규발주 필요량 12, 매입단가 양수, 정책예산 100,000원과 일치했다. 거래 명령은 실제 domain dispatch와 invariant 검사를 통과한다.
- 96개 중 93개에는 일부 희소 조건 추가가 필요했다. trace에 추가 SKU를 기록하며 소스·reason에 **합성 평가 조건이며 실제 점포 사실이 아님**을 명시했다. 실제 매장 수요나 상품 취급 증거로 해석하지 않는다.
- 공개 사례 3개의 expected/expected_prior/turns/label/research_ids/scenario_id 전체를 sentinel 문자열로 바꾸고 재생성했다. 정상본과 변경본 출력이 byte-identical(`0305219d8ad3454d0c1ff057a44da9bac7c81d2b2af9f6c01e7e3b1b79257ee3`)이며 sentinel이 출력에 없다. 입력 state는 storeId/proposalProductIds로 정해지고 정답을 사용하지 않는다.
- 같은 합성 사례를 split=holdout으로 표시하자 `--independent-holdout` 없이 종료코드1로 거절하고 출력 파일을 만들지 않았다. 실제 비공개 holdout은 사용하지 않았다.
- 실행기는 proposal identity/revision/constraints를 이 생성 결과에서 추정하지 않고 별도로 고정한 공개 context와 결합한다. 이것은 모델 입력용 합성 업무 상태의 명시적 분리이며 정답을 적용한 발주 결과가 아니다.

명령: `node --import tsx scripts/build-eval-state.mts evals/baseline.jsonl artifacts/private/run-20260921/e02-independent/state-rebuilt.json` (Node22). 3개 정상/오염입력 및 보호 거절 산출물도 같은 private 디렉터리에 보존. 모델 호출0. 이 PASS는 위 전송 실행기의 두 버전 동결 결함을 해소하지 않는다.

보조 증거: 구현자 자체 transport 22개 테스트를 재실행해 22 PASS였다. 이는 독립 반례 8개의 판정과 별개이며, 자체 테스트 통과로 독립 FAIL을 대체하지 않는다.

## 수정 후 최종 판정: PASS (전송 실행기 경계 한정)

구현자가 두 반례를 수정한 뒤 같은 독립 검토자가 실제 재실행했다. 첫 FAIL 기록은 위에 그대로 남겼다.

- 실행기 SHA-256: `ae3450d3009f59cf344cdaac10f1ca42999f6daaacdb488bd61837a9ad2f008d`
- 자체 테스트 SHA-256: `68826a570bfe2f765d84c8cf387eaac7246465e1513e306f5506b231ead9a01e`
- 실행: `python3 artifacts/private/run-20260921/e02-independent/probe.py`
- **독립 11 tests / 11 PASS / 0 skip.** 상세 `probe-retest.txt`; 초기 반례는 `probe-initial.py`로 보존.
- 실행기/adapter/scorer/공개 평가 manifest/validation/서버/API route/contract/catalog/package-lock 소스 fingerprint가 필수로 고정됐다. 실행기 hash 생략 반례는 SOURCE_BINDING_REQUIRED로 차단됐다.
- validation config/state artifact의 해시와 실행 fingerprint를 재계산해 선택 후보의 source/prompt/model/API/catalog/config와 연결한다. 다른 후보·다른 validation dataset의 보고서는 VALIDATION_CANDIDATE_PROOF_MISMATCH로 차단됐다.
- 정상적으로 연결된 두 repeat 보고서는 통과했다. 별도 다른 model binding과 state artifact 변경도 각각 차단했다. 모든 요청을 거절해 얻은 PASS가 아니다.
- 최초의 재시도 최대3/전체 분모/실제 응답 history/정답 제외/중단 후 재전송 방지/호출·비용 예비량/unknown usage null 검사는 수정본에서도 계속 PASS.

모든 검사는 합성 검토용 사례 및 localhost 가짜 HTTP다. 실제 모델 호출은 계속 **0**, 보호 holdout 원문 접근 **0**. 최종 성능 판정이나 보호 holdout 실행 승인 자체를 대신하지 않는다. 실행 시 조정자가 exact source/deployment 증거와 기존 goal ledger를 연결하고 독립 평가자가 실제 validation/holdout 결과를 채점해야 한다.

## I01 CI delta 독립 점검 (provisional)

추가 배정 범위는 CI 지문·카운트·검증 누락 차단만이다. 검토자가 작성한 domain/AppShell의 제품 검증을 포함하지 않는다. context-app-v5 `10701ed7619c86fe94cec16a31b6ac8b02a1afa9f2843ffdcce4ec446e952234` ACK.

- `python3 scripts/test_runner.py` 실제 재실행: **91 tests / 0 skipped / 0 failures / 0 errors**.
- 5개 작업의 정상 synthetic report 승인, 각 필수 check/review 누락 차단, implementer self-review 차단, context/stale/zero/skip/failure/error 차단을 실제 `gate_contract.validate`로 검사했다. 이 synthetic PASS는 제품 승인 증거가 아니다.
- 실제 config를 복사한 임시 루트에서 CSS/Worker/SQL/WASM/mts 변경 시 fingerprint 변화 확인. 처음 누락한 `tests/merchant/browser-index.html`을 root가 source_patterns에 추가했고 HTML 변경도 fingerprint를 바꾸는 것을 확인했다.
- **수정 요청 1:** Python 수집기의 총합 검사는 필수 디렉터리 3개가 비어도 다른 디렉터리의 단일 테스트만으로 exit0을 반환한다. 임시 root에 실제 수집기를 복사해 재현했다. 각 필수 디렉터리의 수집 수를 별도로 확인해야 한다.
- **수정 요청 2:** Node 수집기에 정상 private 합성 테스트 파일과 존재하지 않는 필수 glob을 같이 전달하면 tests1/exit0이다. 현재 domain-ui-tests가 세 필수 glob을 합치므로 각 glob의 최소 1파일 수집을 보장해야 한다.

독립 반례는 `artifacts/private/run-20260921/e02-independent/ci-probe.py`(6개 중 5 PASS, Python 빈 그룹 반례1 FAIL), Node 증거는 `artifacts/raw/independent-missing-glob.json/.tap`에 보존했다. 소유 소스는 수정하지 않았다. 최종 source fingerprint가 아직 동결 전이므로 `quality/reviews/E02.json`은 생성하지 않았다.

### CI delta 수정 후 재검증: PASS (source 전체 지문 동결 대기)

Root가 수집기 두 결함을 수정한 뒤 독립 재실행했다.

- `ci-probe.py`: **6/6 PASS**. 빈 Python 필수 디렉터리를 두는 원 반례가 nonzero로 차단됨.
- Node 정상 합성 파일 + 누락 glob: **exit1**, `zero collected files for required patterns`. 이전 해당 count JSON도 먼저 삭제하여 오래된 카운트 재사용을 막는다.
- 정상 Python: **91 PASS, skip/fail/error0**; 실제 수집 내역 scripts18 + gates18 + evals32 + eval-runner23. missing_suites 빈 목록.
- 정상 Node domain-ui 수집: **44 tests, skip/fail/error0**. 이 결과는 수집기 정상 회귀 증거이며, 자체 domain 제품 검증을 독립 검증으로 다시 부르지 않는다.
- 기존 5 task/check 누락·자기 검토·context·stale·zero·skip 차단과 정상 완전 report 통과를 유지한다.

| 소스 | 수정 후 SHA-256 |
|---|---|
| quality/gates.json | `048b5c65a4e576438285eabb1f0cddaeaa6e0e30f2c9f076b39c0cfecd21721c` |
| scripts/test_runner.py | `18cc2459a3118fd40d68e8690ec6ed28aa6d134b17c2e00383f11194f5a5e23c` |
| scripts/run_gate.py | `ab960f9f4fa42696147683ede851f47cfd67d8c52eb817e4831cfe98e275aea1` |
| scripts/run_node_tests.py | `a690e39876c9fd9dabbdaf2f5fc1d10e1ab10ac1bc38350daa30df4212189729` |

현재 범위의 추가 필수 지적 없음. 최종 통합 source fingerprint 동결 후 E02 review artifact를 기록한다. 이 CI 검토는 아직 실행하지 않은 formal NL/G5/G6를 통과시킨다는 뜻이 아니다.
