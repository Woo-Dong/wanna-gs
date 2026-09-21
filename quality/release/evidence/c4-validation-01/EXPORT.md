# C4 validation-01 공개 집계

2026-09-21 preflight_builder. 완료된 validation-01의 원본에서 집계를 내보냈다. **84/84 품질 PASS 및 현재 소스 결속의 부분 검사 PASS**이며 best 선정, 두 validation 완료 또는 G5/G6 완료 선언이 아니다. validation-02/보호 holdout 접근0, 추가 모델 호출0, 실제 장부 쓰기0, 원본/앱/평가/검사기 변경0. 이 디렉터리의 5파일만 작성했다.

## 원본과 변환

원본: `artifacts/private/run-20260921/n05-c4-validation-01/`, 분석: `n05-c4-validation-01-analysis/`, 설정: `n05-c4-validation-config.json`, 공개 validation 상태 결속: `eval-state.json`, runtime inventory: `c4-local-runtime-binding.json`. execution.json에 9개 원본 바이트SHA를 기록했다. private 파일 경로는 provenance 설명이며 공개 artifact 참조는 본 디렉터리만 가리킨다.

- report.json: 실제 candidate-report의 scorer 허용 집계 필드를 그대로 유지. case_results는 제거했고 보조 comparison_scope/source_sha는 execution에 옮겼다. 질문/정답/모델 원문은 내보내지 않았다.
- execution.json: checkpoint의 case→turn→attempt를 중복 없이 집계하고 summary/progress/coverage/scorer와 대조했다. 실행 시간 출처와 비용 부동소수점 정밀도도 기록했다.
- binding.json: 원래 비밀 없는 config를 그대로 보존하고 상태의 canonical hash를 연결했다. source/proof 경로를 임의로 바꿔 원래 fingerprint를 변경하지 않았다.
- bundle.json: 세 공개 JSON의 경로와 바이트SHA만 가진다. 실제 G5 manifest는 만들지 않았다.

| 파일 | SHA256 |
|---|---|
| report.json | 684e1697f919d0cf8e96fbe03addec5c915a49e2ab7f50d2a4170235763de322 |
| execution.json | bdc369200c57e1c520de66d9fcd237e539af573d4d16755b6e31744adfddf353 |
| binding.json | 6cc7f634855a56d69e3bcda540ad4b575e30ac29d9f526a0fb1aa086f1f764c5 |
| bundle.json | 1dbeba0096df1bd557a46cb3dbc8bc72a266a614f388d914e906475680e2e49b |

## 원본과 일치하는 결과

run_id는 `41e43c20-9e09-480b-8c04-511c95718e08`, run_fingerprint는 `d64cea5c5afb5dcced42b310b27c5baeb6198ded4cca7c66385756111459158f`다. 원래 config+state binding을 다시 계산한 지문이 checkpoint/summary/scorer와 일치한다.

| 항목 | 결과 |
|---|---:|
| 계획/시도/기록 사례 |84 /84 /84|
| 품질 PASS/FAIL/incomplete |84 /0 /0|
| 계획/기록 user turn, 미시도 |92 /92 /0|
| HTTP attempts / provider true / false / unknown |92 /92 /0 /0|
| HTTP 성공/실패 |92 /0|
| 중복 attempt ID / pending |0 /0|
| 알려진 토큰 |1,037,782|
| 비용 표시 합계 |$0.426964|
| unknown usage / mandatory / fatal 오류 |0 /0 /0|
| latency P50 / P95 |2,437 /4,389 ms|

원본 각 JSON float를 decimal 문자열로 합산한 값은 `0.4269640000000000324`다. 최초 exact-decimal equality 검사는 이 기계 정밀도 차이로 실패했으며, 원본을 바꾸지 않고 차이 <1e-12와 표시 합계 $0.426964를 확인했다. execution에 그 합계와 출처를 남겼다. 실패0·누락0 수치는 이 반올림과 무관한 실제 정수 집계다. scorer의 stage_ready/nl_minimum_pass true를 유지하며 독립 역할 SQL/브라우저 게이트를 이 자연어 집계로 대체하지 않는다.

## 현재 소스·runtime과 시간 출처

candidateId C4, source `48bdb4f18f6c769806fbfa9399ea2cf6af2b5f6f`, model `gpt-4.1-mini-2025-04-14`, prompt `packed-refs-v5`다. 현재 실제 runtime 파일 전체 45개가 private local binding의 목록/각 hash와 완전히 일치하며 canonical inventory hash는 `64cf6c72f7596674456b7075e0e6c82796b3e735953e9aa8f76882a6c742703a`다. validation origin은 원래 config의 remote Preview다. 로컬 inventory 일치는 원격 실행 소스를 암호학적으로 보증하지 않는다. 원래 runner도 remote_source_attestation=false라고 기록했다.

시작 `2026-09-21T11:22:08.991294+00:00`는 원본 run.lock filesystem birthtime, 종료 `2026-09-21T11:26:19.763858+00:00`는 summary.json mtime이다. provider wall-clock이 아닌 실행 경계 근사 metadata다. runtime binding의 createdAt은 `2026-09-21T11:22:13.376589+00:00`로 lock 생성 약4.385초 뒤다. 따라서 이 local binding 파일만으로 **실행 전 동결 시각**까지 증명했다고 주장하지 않는다. config의 source hash와 원래 Preview proof 및 조정자의 배포/동결 로그는 별도 provenance다.

## 자체 형식 검사와 인계

기존 checker를 수정 없이 import해 공개 refs에 `Checker.nl(bundle, frozenValidationDataset, best=True, candidate=C4)`를 실행했다. 여기서 best=True는 기존 함수의 **현재 binding 및 최소 기준 검증 분기**를 고르기 위한 것이며 C4를 best로 선정하는 동작은 아니다. 공개3파일 sanitizer, 현재 모든 선언 source hash/필수 source, 재계산 run fingerprint, 고정84/범주별 분모·합계·최소 기준·pending0가 PASS했다. runtime 전체45 비교도 따로 수행했다. 실행기/manifest를 고치거나 판정 기준을 낮추지 않았다.

이것은 export 작성자의 정합성 검사다. 원본 수치/필드 누출/소스 및 시간 출처에 대한 독립 검토는 research에 인계한다. validation-02, 보호 holdout, 실제 두 역할 QA, UX 기준과 B0 비교 미완료, 정책 검토, G5/G6는 이 bundle의 범위 밖이며 완료로 표시하지 않는다.

## 후속 상태

C4 두 번째 검증83/84는 최소 기준에 미달했다. 이 bundle은 첫 번째 실행만의 역사적 증거이며 C4 best 승격이나 C5 source의 현재 품질 증거가 아니다. root가 원본 집계·설정·92개 시도·사용량을 독립 재계산했다(실제 호출0).
