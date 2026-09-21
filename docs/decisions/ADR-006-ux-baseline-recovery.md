# ADR-006 — 중단된 UX 기준선의 제한된 재측정

- status: adopted; 실행 검증 전
- authority: user-delegated; 사용자 직접 결정 아님
- proposer/coordinator: root, 2026-09-21
- policy_key: ux.baseline_recovery_provenance
- effective_scope: N02 B0 UX 측정 복구 한 번, 출시 기준 변경 없음
- depends_on: ADR-003, CORE-17/18/21/25, docs/15/17/21/23
- supersedes: 없음; conflicts_with: 없음
- context: N02-v6 `0555063cc1bca9224124b2522d9371bf8ec8178ada49083c9bd306ae0d738a3b`; 제품 B0 source `10c00723d0b64ea47a06dcbd00e2b671e7c62daf`

## 공백과 선택

최초 UX 실행 `ux-baseline-b0-v2-01`은 24계획 중 2PASS/1FAIL/21미실행이다. 세 번째 모델 호출 HTTP502는 usage가 확인되었으나 원인은 미확정이다. 결과 SHA는 `4989b1053468134ff8a3099b951493ba483687f57fb14de49db48ea4e87b4209`. 이 결과는 비교에 부족하며 성공으로 바꾸지 않는다. docs15의 제한된 재검증과 ADR003의 동일 workload 비교를 연결하는 참조 실행 선택 규칙만 보완한다.

무제한 반복·실패 사례만 재시도·성공 조각 합치기·후보 코드를 기준선으로 바꾸기·fixture 대체는 기각한다. 비교 미완료를 유지하면서 동일 B0 전체 측정을 정확히 한 번 추가하는 최소안을 제안한다.

## 사전 고정 규칙

1. 추가 실행 ID를 **`ux-baseline-b0-v2-recovery-01`**로 지금 지정한다. 전체8 workload×3회=24를 동일 순서로 한 번 측정한다. 결과를 보고 다른 실행을 비교 기준으로 선택하지 않는다.
2. B0 제품/서버 소스·모델·프롬프트·catalog·schema·seed·clock·viewport·workload·harness를 그대로 유지하고 실행 전 hash/build 일치를 확인한다. 독립 새 브라우저/SQLite 상태를 사용한다. 기존 성공2개를 재사용하지 않는다.
3. 기존 no-retry·모델 오류/unknown usage 중단 규칙을 유지한다. 추가 실행이 실패/누락되면 비교 NOT_READY이며 이 ADR은 세 번째 실행을 허용하지 않는다. 원인 새 증거·독립 검토 없이 반복하지 않는다.
4. 추가 단일 실행이24/24 정상일 때만 그 실행의 workload별 최대 조작/화면이동 및 완료시간 중앙값을 best와 비교한다. 기존 기준인 정상100%, 조작/이동 증가0, 비모델 중앙값10% 초과악화 금지와 모든 필수 품질 기준은 유지한다.
5. 최초 실패 run은 영구 보존하고 실패 해결/기준선100%로 표현하지 않는다. 최초24와 추가24 각각의 예정/실행/성공/실패/미실행 분모와 누적48을 공개한다. 실패시간은 성공시간 중앙값에 섞지 않는다. NL B0 227/336 및 실패109는 변경하지 않는다.
6. 추가 모델 호출은 동일 Budget50 장부에 기록한다. 전체2400회/$15 소프트중단과 prior50, best validation/holdout/best UX/G5/G6 예약은 유지한다. 초기3회/$0.013441를 제거하지 않는다.
7. G5 공개 증거는 원본과 추가 실행의 해시·사전 지정 ID·관계·각 분모를 함께 요구한다. gate 변경은 복구 provenance 검사 추가만 허용하며 성공/성능 조건을 완화하지 않는다. 제품/동의/상태/API/seed/eval 정답 변경은 없다.

## 독립 검토·검증

제품 관점 research와 상태/실패 관점 method_auditor가 각각 선행 검토를 작성했다. 두 검토자가 초안 SHA `4334f594e1e11419da3118cb7253c01b4ab5b6313c444919994360c36899bad7`에 독립 동의하여 조정자가 채택했다. 원본: `docs/execution/run-20260921/ux-baseline-recovery-product.md`, `ux-baseline-recovery-state.md`.

정상 기대: 새24PASS여도 최초1FAIL은 남으며 상대 비교 자료만 확보한다. 경계: 소스/harness/hash 불일치는 실행 금지. 실패: 새 오류·누락은 NOT_READY, 자동 추가 실행 금지. release checker의 정상/변조 회귀와 독립 검토를 연결한다. 실행 미검증이며 후속 PR/context/ACK에서 추적한다.
