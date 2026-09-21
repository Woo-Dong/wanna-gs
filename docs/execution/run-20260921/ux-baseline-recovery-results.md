# UX B0 실제 기준선 및 ADR006 복구 결과

- 실행일 2026-09-21, 실행자 preflight_builder, 승인/조정 root. 독립 두 관점 검토를 거쳐 채택된 ADR006에 따라 전체24 한 번만 추가했다.
- **결과: NOT_READY.** 최초 실행과 단일 복구 모두 모델 HTTP502로 중단되어 정상24개 비교 기준선이 없다. 기존 실패를 해결·삭제·성공으로 바꾸지 않았다. best와 편의성 합격 비교를 할 수 없으며 G5/G6 완료가 아니다.
- 실제 baseline 측정은 고객/경영주 독립 G5 QA를 대체하지 않는다. fixture 결과를 live로 재사용하지 않았다.

## 각각의 분모와 누적

| 실행 | 예정 | 실행 | PASS | FAIL | 미실행 | 실제 outbound/provider true | unknown | 확인 비용 USD |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| ux-baseline-b0-v2-01 |24|3|2|1|21|3|0|0.01344100|
| ux-baseline-b0-v2-recovery-01 |24|12|11|1|12|14|0|0.06375175|
| 누적 (성공 조각 합산 비교 금지) |48|15|13|2|33|17|0|0.07719275|

두 실행 모두8 workload×3회 계획이다. case/run과 실제 모델 호출은 다르다. 모호한 요청은 질문→답변으로2호출이 생길 수 있어 복구의12실행과14호출을 동일 분모로 표현하지 않는다. 실패시간을 성공시간 중앙값에 섞지 않으며 누적13PASS를 완주24PASS로 재구성하지 않는다.

| workload | 최초 PASS/FAIL/미실행 | 복구 PASS/FAIL/미실행 |
|---|---|---|
| clear-1 |2/1/0|3/0/0|
| clear-2 |0/0/3|3/0/0|
| clear-3 |0/0/3|3/0/0|
| ambiguous |0/0/3|2/1/0|
| reconsent |0/0/3|0/0/3|
| batch-10 |0/0/3|0/0/3|
| auto-normal |0/0/3|0/0/3|
| exception-batch |0/0/3|0/0/3|

## 중단과 정상 보존

최초 clear-1 반복3은 모델응답 HTTP502를 받았고 응답 usage/input16633/output196/total16829/cost0.00455025를 보존했다. UI는 확인할 수 없는 응답 오류와 기존 입력을 표시했다. 실패 시 SQLite 요청0. 정확한 서버 diagnostic은 당시 측정기 기록에 없어 추정하지 않는다.

복구는 clear3종×3=9회와 ambiguous2회가 실제 UI→모델→SQLite/IndexedDB 내구 저장까지 통과했다. ambiguous 반복3의 첫 응답에서 HTTP502가 발생했다. 마지막 attempt usage=input16629/output440/total17069/cost0.00503725, provider_called=true, status=failed. 실패 snapshot의 요청0. API 원인을 원문 없이 특정할 증거는 이 결과에 없다.

두 실행의 stopCode는 `HTTP_MODEL_ERROR_OR_UNKNOWN_USAGE_STOP`. 오류를 받은 뒤 추가 실제 호출0/자동 재시도0이다. 측정기의 다음 UI locator가60초 대기 후 FAIL을 기록한 것은 추가 모델 전송이 아니다. 각 프로세스 exit1, finally browser.close 및 budget-final 기록 완료. pending=false. 추가 실행은 없으며 ADR006은 세 번째 실행을 허용하지 않는다.

## 동일성 및 원본 보존

복구 직전 이전 result의 sourceFiles/harnessHashes/seedHash와 현 파일을 대조해 전부 일치했다. BUILD_ID도 정확히 일치했다. 별도 브라우저 context/SQLite seed로 전체24를 새로 시작했고 기존 두 성공을 재사용하지 않았다.

- B0 제품 source: `10c00723d0b64ea47a06dcbd00e2b671e7c62daf` (조정자의 frozen B0 연결).
- BUILD_ID: `oNn70kBV2ANXxEtN5RXWr` (두 raw result 동일).
- workloadHash: `613bbb701a155913f02f2de4bf6f45fef793b1d3fa5e61cd5a5211a25e32d71d` (두 raw result 동일).
- seedHash: `4cb10e899c9706bb0a9278b458bd7b70d3c34bf28f649b62ffae0894794a2b45`.
- prompt source SHA256: `62242b67db9a9f3d6f2297e1c54fa349809c5fc305526564e83532f5bf2775b0`; 모델/프롬프트는 승인된 B0 live 경로 그대로이며 C1은 별도 worktree에서 준비됐다.
- 최초 원본: `artifacts/private/run-20260921/ux-baseline-b0-v2-01/result.json`, SHA256 `4989b1053468134ff8a3099b951493ba483687f57fb14de49db48ea4e87b4209`.
- 복구 원본: `artifacts/private/run-20260921/ux-baseline-b0-v2-recovery-01/result.json`, SHA256 `2b9839efff2d118b48751642e7382b41d6e41fa49b837ccb4beff56fd1433c4b`.
- 각각의 같은 디렉터리에 screenshot·실제 usage·network/time·source/hash·분모·budget-final.json을 보존했다. 복구 종료 후 최초 result hash가 그대로임을 재확인했다. raw result에 field 추가/수정0.

## 공유 예산 확정

| 시점 | prior 포함 호출 상계 | known provider calls | unknown calls | 확인 비용 | prior 포함 비용 상계 |
|---|---:|---:|---:|---:|---:|
| 최초 종료 |420|370|0|$1.67255300|$4.17255300|
| 복구 종료 |434|384|0|$1.73630475|$4.23630475|

두 실행 모두 root의 동일 `nl-budget.json`/prior50 예약 경로를 사용했다. 전체2400/$15 소프트중단·미래 필수 호출960/$7.68 예약을 승인 config로 유지했다. 이 예약은 실측 기반 추정이며 공급자 최악 비용 보장이나 계정 hard cap은 아니다. 기존3회 비용은 제거하지 않았다. 최종 pending=false.

실행 명령은 root `tests/ux-benchmark/run.mts --app-root <root> --live --budget-config <root>/artifacts/private/run-20260921/ux-baseline-b0-recovery-config.json --output <root>/artifacts/private/run-20260921/ux-baseline-b0-v2-recovery-01`에 기존 승인 Node22/Playwright/Chrome 경로를 사용했다. 키/토큰은 출력하지 않았다.

## 다음 상태

조정자에게 live 완전 종료와 위 장부를 통보했다. G5 recovery provenance 검사기 구현은 조정자의 지시에 따라 보류했다. 새 정책 권한/독립 근거 없이 추가 baseline 반복을 시작하지 않는다. B0 비교 미완료를 유지하며 후속 C1 연구·제품 복구는 조정자 소유다.
