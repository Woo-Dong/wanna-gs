# C5 validation-01 공개 export 독립 검토

판정: export 무결성 범위 PASS. 검토자 research, 작성자 root. 실제 모델 호출·브라우저·장부쓰기·보호 holdout 본문 접근0. 공개 validation 원본 관측/평가 보고와 보존된 config·state·배포 proof만 읽었다.

초기 binding의 state_fixtures_hash가 상태 JSON 파일 SHA를 사용해 runner의 parsed canonical state fingerprint와 달랐다. 초기 public binding 지문0774b730…는 실제 run91a7a769…와 불일치했다. root가 최초4파일을 artifacts/private/run-20260921/c5-validation-01-export-before-binding-fix/에 그대로 보존하고 parsed fingerprint0ab9f3bd52026bd13470fcc5e99ce09ca315710c227d1dfea848a5d3e210df24로 교정했다. 수정 후 binding canonical fingerprint가 정확91a7a7695062aec19f504217f98104fde9aa3a4c4a394fe812c33ffceb6f95c2에 일치하며 exporter에 이 equality 단정을 추가했다. report/execution 바이트와 config는 불변, eval-state 파일 SHA d1a0845…도 원본 출처 해시로 계속 보존된다.

직접 재계산: report는 SCORER_KEYS의 정확한 원본 projection이고 case_results/발화/정답/원응답은 없다. 원본9개 해시, config 및 state binding, source28개와 runtime45개 current/git show f6a34def5dd6cc6287c3dedba805824974d67db8가 일치한다. 실제 Preview READY/source/origin의 보존된 proof도 config 해시에 일치한다. 독립 Checker.nl의 현재 후보 validation 경로 PASS이며 이는 best 채택 주장이 아니다.

전체84case/92turn/93 HTTPattempt를 보존한다. 최종84/84 PASS, incomplete0/mandatory0, product_gates=not_assessed. 최초 timeout은 HTTP504/LLM_TIMEOUT/provider_called=true/usage=null/cost=null이며 같은 turn의 다음1회가200/ok다. 최초 포함2회로 기존 ADR003 timeout최대3회 범위이며 재시도 호출도93에 포함된다. providerunknown0은 usageunknown0이 아니다: 사용량 미확정1건을 별도로 남겼다. 알려진 token1,034,785, 알려진 비용$0.42592이고 Decimal 원문합0.4259200000000000298도 일치한다. 이 값은 미확정 호출 비용을0으로 확정한 전체 비용이 아니다. 실제 공유 장부를 이 검토에서 수정하거나 다시 호출하지 않았다.

공개 report/execution/binding/bundle 전부 forbidden-key·비밀패턴 검사 통과. private 원본 경로 문자열/해시는 provenance이며 원문 내용은 공개하지 않았다. 파일 생일/mtime은 실행 경계 근사치이고 공급자 시각·원격 암호학적 증명으로 과장하지 않는다.

최종 bundle SHA32563875bf674992871550e8359cf8e7f7abf1b489cd943116726f2bc8c29734, binding5757ace2484663d0775ffc8ab0dbdd7495c9d34df84d25d8141e7b90876550d2. 재사용 실행 증거는 private n06-c5-export-independent.json와 review-c5-validation-01.py. 이번 결과는 한 validation export만 검증하며 두번째 repeat/bestfreeze/holdout/UX/G5/G6 완료를 뜻하지 않는다.

## validation-02 별도 delta 검토

두번째 공개 묶음도 export 무결성 PASS. bundle SHA406358b73a1bc6c6fa1426e0380563f66995dd8a6922a5adf50e18ed4bebb250. run_id c504135a-b5e0-459d-8158-12ca73d99697로 첫실행과 다르고 binding/config/run_fingerprint91a7a769…는 정확히 동일하다. parsed state 지문 수정이 적용됐으며 원본9hash·SCORER_KEYS projection·source28 current·동일 runtime45 고정목록을 재대조했다. 같은 소스/commit의 이전 직접 git show 증거는 재사용했다.

84case/92turn/92 HTTP 및 providertrue, 재시도0/usageunknown0/누락0. 83PASS/1의미오류를 제거하지 않았으며 incomplete/mandatory0. 고객 clear40/40, uncertain19/20=95%; 경영주 clear15/15, uncertain9/9. 원래 명확95%/불명확90% 합격선 그대로이며 전체84/84라고 과장하지 않는다. 알려진 token1,033,697, 비용 합산 float0.42531680000000005(표시$.4253168), 원본 Decimal합과 일치. 현재 checker.nl validation 경로 PASS다.

public4파일의 비밀/발화/정답/raw 제외 확인. 독립 probe는 private review-c5-validation-02.py, 결과 n06-c5-export-02-independent.json에 보존한다. 이 검토는 두번째 export와 동일 설정·별도run·기존 역할별 최소 충족 증거이며 보호 holdout/실제 UX/최종 두역할/G5/G6의 별도 결과를 대신하지 않는다. 모델·장부쓰기·보호 holdout 본문 접근0.
