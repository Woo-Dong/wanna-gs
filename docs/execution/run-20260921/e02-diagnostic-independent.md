# E02 fixed diagnostic delta — 독립 검증

- 검증일: 2026-09-21. 구현자 method_auditor, 독립 검증자 preflight_builder.
- 범위: `scripts/run_nl_eval.py`의 `parse_attempt` 오류 진단 allowlist 추가와 인접 정상/실패 accounting 보존. 자연어 정확도·제품·G5/G6 전체 PASS를 주장하지 않는다.
- 목적 보존: 모델 실패 원인을 고정 rule ID로 구분하면서 원문·키를 기록하지 않고, 기존 실패 분모/usage/cost/provider 여부·실패 상태·raw 반환과 재시도/예산/holdout 정책은 바꾸지 않는다.
- 코드 수정0, 실제 모델 호출0, 실제 예산 장부 쓰기0, 보호 holdout 내용 접근0.

## 검증 대상

| 파일 | SHA256 |
|---|---|
| scripts/run_nl_eval.py | `5ee03bb164e0610511c25d2934b6e7b6b234ef95a96c2770bf6b7dae08f51d7d` |
| tests/eval-runner/test_nl_transport.py | `ce6c9b7046e2f34ca327680f9ef2e88264f232e2d29cb086a23c64f9a0823626` |

읽은 diff는 실패 반환값을 변수로 분리하고 `INVALID_MODEL_RESPONSE` 및 정확한 allowlist string에만 `diagnostic`을 추가하는 변경이다. 비교 기준은 실행 당시 `git show HEAD:scripts/run_nl_eval.py`의 이전 `parse_attempt`; 해당 파일의 마지막 이전 commit은 `5f2e5d2`다. AST에서 함수만 분리해 같은 현재 모듈의 상수/도우미 namespace에서 이전·현재 함수를 각각 실행했다. 오류 처리의 다른 부분을 새 기대값으로 복제하지 않고 이전 실제 함수의 결과와 대조했다.

## 별도로 생성한 독립 반례

4 error code × 23 diagnostic 값 × provider_called true/false/null = **276 조합 전부 PASS**.

- error code: INVALID_MODEL_RESPONSE, LLM_TIMEOUT, LLM_AUTH_ERROR, 임의 원문 sentinel code.
- 허용11 rule ID: OUTPUT_CONTRACT, OUTPUT_SCHEMA, CANDIDATE_LIMIT, CANDIDATE_DUPLICATE, CANDIDATE_UNKNOWN_ID, OUTPUT_TEXT_LIMIT, CANDIDATE_ACTION_CONTRACT, UNIDENTIFIED_ACTION_CONTRACT, CLARIFICATION_CONTRACT, EXACT_WITH_UNKNOWN_CONDITION, SUPPLIED_CATALOG_SCHEMA.
- 거절12 값: 소문자, 앞 공백, 뒤 공백, NUL 접미사, 개행 접미사, 원문 sentinel 접미사, 전각 문자 변형, dict, list, false, integer1, null.
- 고정 HTTP502/latency7과 알려진 usage input1/output2/total3/cost0.01을 사용했다. provider true/false/null 각각이 유지되는지 확인했다.
- `diagnostic` 키가 존재하는 조건이 **오류 code 일치 AND 정확 allowlist 문자열**과 동일했다. 다른 code는 안전한 rule처럼 보여도 보존되지 않았다.
- 진단 필드를 제거한 현재 결과는 이전 함수의 code/status/provider_called/usage/cost/http_status/latency와 전부 같았다. raw 반환도 모두 동일했다.
- 임의 diagnostic/message/code에 넣은 `PRIVATE_SENTINEL` 문자열이 직렬화 결과에 포함된 사례0.

이는 작가 테스트의 PASS를 독립 검증으로 재분류한 것이 아니라 독립 생성한 입력 matrix와 이전 함수 비교다. 입력은 메모리의 합성 프로토콜 객체였고 HTTP/모델 전송은 하지 않았다. 세션 도구 기록에 실행 코드와 276 결과가 보존되어 있다.

## 정상·인접 회귀

1. 실제 계약을 만족하는 합성 customer `show_candidates` 응답(정확 SKU1/명시 confirmation/알려진 usage)을 현재 함수에 넣어 status=ok, 원래 raw 결과 그대로 반환을 확인했다. 성공 envelope에 임의 diagnostic sentinel을 넣어도 attempt에 진단 키를 새로 기록하지 않았다. **PASS**.
2. 작가 소유 기존 transport suite를 독립 환경에서 다음 명령으로 재실행했다: `python3 -m unittest discover -s tests/eval-runner -p 'test_*.py' -q`. **26 tests PASS**, 7.293초. 여기에는 failure→success 인접 HTTP journal, usage/unknown accounting, 분모·중복/재개 등의 기존 회귀가 포함된다. 이 부분은 기존 suite 재실행이며 위 독립 matrix와 구분한다.
3. 문서화 시 source/test hash를 다시 계산해 위 값이 유지됨을 확인했다.

## 결론

**해당 delta 독립 PASS**. 고정11 diagnostic ID 추가 외에 이전 반환/accounting 의미의 변화는 독립276 조합에서 없었고 정상 성공도 유지됐다. 실패 원문·키를 수집하는 방식으로 확대하면 이 판정은 재사용할 수 없다. 실제 모델 품질 향상이나 UX baseline 복구 성공의 증거는 아니다.

## 후속 UX 복구 대기 상태 (실행 아님)

조정자의 ADR006 채택·별도 실행 지시를 기다리며 추가 모델 호출/새 baseline run은 시작하지 않았다. 읽기 확인 당시 root `.next/BUILD_ID`는 `oNn70kBV2ANXxEtN5RXWr`; 기존 UX baseline 원본에 기록된 sourceFiles/harnessHashes/seedHash와 현재 파일은 모두 동일했다. prompt SHA256는 `62242b67db9a9f3d6f2297e1c54fa349809c5fc305526564e83532f5bf2775b0`. localhost3217 health GET만 확인했으며 모델 호출은 아니다. 실제 실행 직전에는 같은 상태를 다시 확인해야 한다.
