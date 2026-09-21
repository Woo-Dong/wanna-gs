# B0 baseline 공개 집계 export

2026-09-21, preflight_builder. 조정자 지시에 따라 고정 B0의 실제 private 실행/분석 증거에서 집계만 내보냈다. **baseline bundle 형식/정합성 검사 PASS일 뿐 품질·G5 PASS가 아니다.** `stage_ready=false`, `nl_minimum_pass=false`를 유지한다. 실제 release manifest는 만들지 않았다. checker/eval/앱 소스 변경0, 모델 추가 호출0, 장부 쓰기0, 보호 holdout 접근0.

## 원본과 공개 파일

원본은 `artifacts/private/run-20260921/n02-baseline/`, 분석은 `n02-baseline-analysis/`, 실행 설정은 `n02-baseline-config.json`, 공개 baseline 시나리오에서 생성된 상태는 `eval-state.json`이다. 원본별 바이트SHA는 execution.json의 source_artifact_hashes에 보존했다. 어떤 원본 파일도 수정하지 않았다.

- `report.json`: 실제 baseline-report.json에서 `case_results`만 제거. 나머지 scorer 집계 필드/모든 역할·split·category metric은 그대로 유지.
- `execution.json`: checkpoint의 각 case/turn/attempt를 합산해 전체 시도·실패·provider true/false/null·토큰/비용과 누락 분모를 산출. 최종 summary/progress/분석과 대조했다. 중복 attempt ID0.
- `binding.json`: 원래 runner config를 그대로 유지하고 당시 상태의 canonical hash를 연결. 원문 상태/질문/정답/모델 응답을 공개하지 않는다.
- `bundle.json`: 위 세 공개 파일의 path+바이트SHA 참조만 저장. 전체 G5 manifest가 아니다.

| 파일 | SHA256 |
|---|---|
| report.json | `dcb9485f6c70292148575463d35a245d08f72195fb7518e8f9f35f336c9ca272` |
| execution.json | `4609589d0a06107efad6f5eafaabbb85e18a5de6cd659c924c942eb956fef0cb` |
| binding.json | `1817a4d2692c7c72e27624ce7620406b953d875aef3d0c89a69cf63953421300` |

`run_id=214fba09-c781-43e6-94aa-bec437f305b2`, 원래/recomputed `run_fingerprint=80f9a9a1e7106ae84dd3797d2ca45f825a3f3eef4a2623d8ac3083e400e5f11b`가 일치한다. 모델은 gpt-5-mini-2025-08-07, prompt baseline-v1, source SHA10c00723d0b64ea47a06dcbd00e2b671e7c62daf다.

## 보존된 실제 분모

| 항목 | 값 |
|---|---:|
| 전체 사례 / 시도 / 기록 |336 /336 /336|
| 품질 PASS / FAIL |227 /109|
| HTTP/transport 실패 사례 및 incomplete |51|
| transport 성공 사례 |285|
| 계획 user turn / 기록 turn / 미시도 turn |368 /367 /1|
| 실제 HTTP outbound / provider true / false / unknown |367 /367 /0 /0|
| HTTP 성공 / 실패 attempt |316 /51|
| 알려진 토큰 |6,208,489|
| 알려진 비용 |$1.659112|
| 미확정 usage attempt / pending |0 /0|
| mandatory 오류 / fatal 오류 |0 /0|

HTTP 실패51개가 전체 품질 실패109개와 동일한 분모가 아니며, 정확도 실패와 transport 실패를 합쳐 숨기지 않는다. 이전 turn의 실패로 시도되지 않은 후속 turn1개를 실행했다고 표현하지 않는다. runner의 complete=true는336사례를 처리했다는 뜻이고 품질 합격이 아니다.

## 역사적 binding과 시간의 한계

원래 config에는 `artifacts/private/run-20260921/run-eval.py` source hash key와 private deployment proof 경로 문자열이 존재한다. 이를 새 공개 driver 이름으로 바꾸면 원래 run_fingerprint가 바뀌므로 **고쳐 쓰지 않았다**. 기존 checker의 `binding(current=False)`는 baseline의 source map hash 형식/필수 key와 fingerprint를 검증하지만 그 역사적 private 경로를 열지 않는다. 공개 artifact 참조 자체는 모두 quality/release/evidence/baseline 아래다. best/current 경로의 private 파일 접근 금지를 완화한 것이 아니다.

baseline 당시 전체 G5 app runtime inventory는 기록되지 않아 execution.runtime_hash=null로 남겼다. 원래 server/eval source map으로만 실제 provenance를 표현하며 현재 best의 전체 runtime과 같다고 주장하지 않는다.

원래 checkpoint/summary에는 별도의 시작·종료 wall-clock 필드가 없었다. execution.started_at은 원래 run.lock의 filesystem birthtime, finished_at은 원래 summary.json의 filesystem mtime에서 UTC로 변환했다. execution_time_provenance에 이 근거와 한계를 명시했다. 실행 경계의 근사 metadata이며 provider timestamp나 암호학적 시간 증명으로 취급하지 않는다.

## 검증과 남은 제약

기존 `scripts/check_release_evidence.py`를 수정 없이 import하여 공개 refs를 `Checker.nl(bundle, frozenBaselineDataset, best=False, candidate={})`로 검사했다. **PASS**. 필수 분모·카테고리 수·합계·원래 binding fingerprint와 공개 sanitizer를 통과했고 baseline 품질 실패는 허용된 기존 계약대로 유지됐다. 이 검사는 작가의 export 자체 점검이며 독립 평가를 대체하지 않는다.

전체 `runtime_files(root)`를 먼저 호출하려던 보조 점검에서는 `NEXT_CONFIG_REQUIRED`가 발생했다. 실제 root에는 next.config 파일이 없고 Next 기본 설정을 사용하는데, 현재 checker가 이 파일을 필수로 요구하는 과잉 가정이다. 최초 export 단계에는 수정하지 않고 보고했다. 이후 조정자가 명시적으로 검사기 수정 권한을 배정해 해당 존재 요구1줄만 제거했다. 현재 root의 실제 runtime43파일 수집이 성공하며 config가 추가/변경/삭제되면 기존 동결 지문과 불일치한다. 설정 파일이나 G5 PASS를 발명하지 않았다.

질문/정답/case_results/rawmodel/키/토큰 값은 export에 없다. historical source/proof 경로와 hash는 비밀 파일 내용이 아닌 provenance metadata다. 각 JSON은 기존 sanitizer로 검사했다. export된 원본 수치의 진실성을 전자서명으로 보장한다고 주장하지 않는다.

## 승인된 후속 검사기 정정 자체 결과

- C1 config/draft의 modelproof source_files에 release checker/tests가 포함되지 않음을 먼저 확인했다. 모델/앱/evalsource 변경0.
- Next 설정 파일이 없어도 기본값 정상인 경우 PASS, config 추가/변경/삭제 각반례 FAIL. 기존44+새4=48 자체tests PASS. 기존 runtime/필수 route·domain·SQLite·UI/package coverage 유지.
- checker SHA `47c99b09f4debdf4476c81e72fa7a1d155ff339fd14180040ebf01c5d6056add`, test SHA `40eec360c26c95e8b7b9d064a838a5eaa22395e6ac3d1c299bec4ddae70b8315`.
- baseline 공개 bundle3파일 및 원래 run fingerprint는 정정 전후 동일. 전체 G5는 actualmanifest미생성으로 NOT_READY 유지. 독립 reviewer의 delta 검토는 별도이며 자체48PASS를 독립 PASS로 표시하지 않는다.
