# E01 평가 준비 및 D01 독립 원본 검토

- evaluator: `/root/method_auditor`, 앱 기능/NL prompt/search 후보 구현자가 아니다.
- consumed_context_hash: `e8d6eb6ffef8765544e3aeeeb9c27b1e98f0c7cb5131202712ec4d32d806ea99` (APP-v3).
- 적용: ADR-002/003 adopted, 정책/거래/평가 불변식 유지. E01 소유 evals/* 및 private holdout 경로, 공통 package/lock 수정0.

## E01 단계1 — taxonomy/scorer 구현

현재 공개 산출물은 evals/taxonomy.json, case.schema.json, scorer.py, adapter.py, tests/test_scorer.py, README.md다. 고객300+경영주120, 공개dev252+validation84, 보호holdout84 및 범주당 각split최소2를 고정했다. source/catalog/scenario를 확인하기 전 가짜 SKU로 dataset을 채우지 않는다.

`python3 -m unittest discover -s evals/tests -v` 실제 실행: **32 tests PASS, fail0/skip0**. 작성자의 자체검사이며 독립 검토는 research 배정 후 별도 기록한다. 테스트용 세 가상 ID는 test fixture 내부에만 있고 제품/eval catalog가 아니다.

반례 검사는 0case·누락/중복/추가 observation, pending binding·unknown oracle SKU, dataset/run/catalog fingerprint stale, family 및 동등 텍스트 split중복, 정상후보 과잉거절, 잘못된 primary 후보·확정, 합법적 명시대체와 가짜대체 분리, merchant 부분필드·타입 혼동, schema/transport 실패·실제 attempt와 unknown usage, live/fixture 위장, mandatory/domain 위반, 예산reserve, 비교대상변경, latency 회귀·validation repeat 상쇄를 포함한다.

scorer는 네트워크나 모델을 호출하지 않는다. 보고서의 `nl_minimum_pass`는 해당 입력셋/모드의 점수이며 `product_gates=not_assessed`를 항상 반환한다. 실제 FE확인·DB거래·브라우저 게이트를 대체하지 않는다. live mode에 fixture observation이나 provider attempt 없는 성공을 넣으면 실패한다. baseline은 dev+validation만, protected holdout은 frozen best 뒤 evaluator가 실행한다.

초기 단계1의 dataset 대기는 아래 단계2에서 해소했다. 실제 live baseline/N01/N02/G5 성능은 아직 not_run, holdout 호출0이다. private exact 발화/정답은 구현자에게 전달하지 않는다.

## D01 원본 후보의 독립 표본 검토

범위는 source_candidates_only다. 414개 전 상품 사실의 전수 현장 확인이나 seed/서비스 품질 검증이 아니다.

- catalog SHA-256 `0a148016ae38dd23d2dadf9e1757b8125e6e992eadc36caae493064aec6c1dd0`.
- stores SHA-256 `f421e2a650b432066b708b0afd3851d173f6e91fea3535b28541f0a0037d4c85`.
- `python3 data/research/validate-candidates.py` 실행 PASS. 별도 Python count/hash 검사로414고유SKU, 8개분류,9고유주소/좌표와 서울 범위, 판매가 simulated/실제가격미복사 라벨을 재확인했다.
- 분류 counts: 밥19/면36/간편조리226/스낵29/디저트36/빵19/유제품커피26/음료23. 이는 raw pool이며 최종균형seed가 아니다.

2026-09-21에 다음 원문을 별도 웹도구로 열어 대조했다.

1. [오뚜기 공식몰 3043](https://www.otokimall.com/front/product/3043): 원문의210g·36개 묶음과 후보의 단위중량을 대조했다. 배송/묶음표현 제거와 원문 raw_name 보존이 일치한다. 판매가격은 채택하지 않았다.
2. [오뚜기 공식몰 850](https://www.otokimall.com/front/product/850): X.O. 교자김치의360g×2 표기와 후보 단위중량·raw_name이 일치한다. 웹도구가 오래된 crawl로 표시했으므로 현재판매/현재재고 근거로 확대하지 않는다.
3. [GS25군자 공개 위치 자료](https://sav.purpleo.kr/article/39204): 도로명주소·공공 원본상가ID 및 latitude37.5499659981206/longitude127.069573880996이 후보와 일치한다. 2차 공공재게시자료이며 현재영업/GS공식제휴/해당상품취급 근거가 아니다.
4. [빙그레 공식 목록](https://www.bing.co.kr/product/list)은 별도 열람했다. 생크림빵 세부페이지(PDT156)는 웹도구 오류로 정확 맛/규격을 독립 재확인하지 못했다. 이 표본의 detail 재확인은 `not_run/접근불명확`이며 전체 빙그레 SKU를 별도 승인한 것으로 기록하지 않는다.

**D01 raw 후보 수집 단계는 제한된 표본·구조 검토 기준으로 진행에 동의한다.** 명백한 출처 왜곡·미검증영양속성·실제GS가격/재고 주장으로 확대되지 않도록 field_origin·confidence·simulated 구분을 유지해야 한다. source 목록과 hash를 갖췄다는 사실만으로 각각의 상품 팩 단위를 실제GS 판매 SKU라고 주장하지 않는다.

남은 D03/SEED-READY 조건: 단일 작성자의 최종SKU선택/카테고리분산, 최근20~30상품 날짜 있는출처 보강(현재trend 전부unverified), importer/실제SQL FK·rollback·반복성, 공개catalog/seed 동일hash, 실제지도 marker/주소 연결, eval바인딩검사. 현재 원본 풀의 간편조리226편중을 그대로200다양상품의 최종분포로 보고하지 않는다. 초기 소수 근거를 전체 source 독립검증으로 부풀리지 않는다.

## R02 최근 상품 독립 표본

최근28개 파일 SHA `2001ca1ae6f9a7d5537d449510fb924a6d3a8d6d87c2c85af4bdf3f5b7c42cb0`의 경계 사례를 2026-09-21 직접 원문과 대조했다. [GS리테일 버터떡 보도자료](https://www.newswire.co.kr/newsRead.php?no=1031677)의 2입/4입 구성과 출시일, 예약판매 사실의 범위가 일치한다. [복날 상품 보도자료](https://www.newswire.co.kr/newsRead.php?no=1038000)에서 훈제오리140g은 일부 구성품 중량이므로 전체size=null이 타당하며 7월 상품의 현재 취급을 확인했다고 쓰지 않았다. [라라스윗 보도자료](https://www.newswire.co.kr/newsRead.php?no=1041291)의 기존 메론/망고 누적판매를 새 복숭아 제품으로 전가하지 않은 점이 맞다. 제한된 3원문/6상품 표본에 대해 PASS이며 28개 전체 사실 전수검증은 아니다.

## E01 단계2 — 실제248 SKU 바인딩·420 사례 작성

- D02 catalog-248-v1과 일치하는 JS직렬화 hash `f2696abe92521e3ff8f9ab43cb36a1d297a6fd23d272e239605b49fab4343b1e`에 결속했다. 정확SKU 정답은 선택된248안에만 존재한다.
- 공개 dev252/validation84, evaluator-only holdout84. 고객300/경영주120, 각 role/split/범주 최소2, 실제 counts와 dataset hashes는 `evals/manifest.json`에 고정했다. 공개 baseline336은 dev+validation이다.
- 실제 user turns dev276/validation92/holdout92. baseline368턴, 최대3attempt 가정1104; best validation 반복276+holdout276+UX48회에 최소1턴씩 retry reserve144=합계1800. 별도 G5/G6 및 UX 추가턴은 root 실행전 추가 예약해야 한다. 남는600을 무조건 선택실험권한으로 사용하지 않는다.
- source-grounded synthetic_expansion이며 실사용자 발화라고 표시하지 않는다. 상품 단위 family를 split에 배정한 다음 명칭/오타/설명/정정 등을 만들었다. 최근상품 공개 demo_input_candidate에 해당하는 exact/동등 family는 dev only. source/catalog 자체는 공개 사실이고 holdout 질의·정답은 비공개다.
- 실제 검사: 전420 `validate_dataset(require_full=True)` PASS, family교차0/정규화동일발화교차0. private holdout git check-ignore PASS. src/public JSON/data JSON을 대상으로 protected exact utterance 유출검사0. 이 검사는 완전한 의미누출 탐지나 최종배포bundle 검사 대체가 아니다.
- protected JSONL/생성기/무작위seed는 artifacts/private/run-20260921/holdout에만 저장했다. root/기능구현자는 공개 manifest counts/hashes만 받았다. public dev/validation/scorer의 독립검토를 research에 요청했다.

독립 검토자가 발견한 fail-open 반례를 실행 전에 수정했다: 빈 이전턴 응답, timeout-only provider 성공위장, 동일실행/config다른repeat, clear oracle의 candidate pool누락, 부분입력셋의 출시완료 오인. 이전턴에는 transport/schema/provider시도와 독립정답을 요구하고, live는 성공 provider attempt를 요구한다. 보고서에 run_id/config를 보존하며 repeat는 다른실행·같은설정·frozen coverage가 필요하다. partial metric과 `stage_ready`를 분리하고 CLI는 고정coverage가 없는 통과를 거절한다. 후속 정상회귀인 모호질문→명확대답도 이전턴label을 분리해 복구했다. 수정은 기준완화가 아니라 실제 증거/정상흐름 보존이다.

현재 상태: **E01 산출물 작성·자체검사 완료, 독립 공개dataset/scorer 최종검토 진행. 실제 모델 baseline/후보/holdout/G5/G6 not_run.**


## E02 bounded HTTP 실행기 자체 증거

`scripts/run_nl_eval.py`와 `tests/eval-runner/test_nl_transport.py`를 작성했다. 로컬 fake HTTP/selftests 23개 PASS, 실제 OpenAI 모델 호출0이다. 실제 공개 baseline plan-only는336사례/368user turns를 읽었고 future reserve744(그 안의 G5/G6 48은 계획값), prior reserve20/실제 과거호출수 unknown으로 출력했다. 실행 권한이나 제품 품질 PASS를 의미하지 않는다.

독립 builder가 발견한 두 연결 공백을 수정했다: validation 보고서가 frozen best 모델/소스와 연결되지 않은 경우, runner/scorer 소스가 source_files에서 빠져도 진행하는 경우. 필수 source 집합을 강제하고 validation config/state artifacts로 run fingerprint를 재계산하며 frozen validation dataset·model/source/prompt/catalog/API 지문을 현재 후보와 대조한다. 현재 수정본의 독립 재검토가 진행 중이며, 실제 baseline/후보/holdout은 아직 not_run이다.

E02 수정본 runner ae3450d3009f59cf344cdaac10f1ca42999f6daaacdb488bd61837a9ad2f008d에 대해 builder 독립11/11 PASS 수신·보고서 확인. e02-independent.md의 최초 FAIL2건 및 재검증 기록을 유지한다. 상태 생성기96개도 별도 독립 검토되었다. 이 PASS는 전송/상태 경계에 한정하며 실제 모델 품질은 아직 not_run이다.

## N02 기준선 실행 준비 (실제 실행 전)

2026-09-21 I01 소스지문8d94bcb2… 동결 후 evaluator가 공개 baseline336/368user turns와96개경영주상태,248SKU 바인딩 및frozen coverage를독립재확인했다. baseline canonical dataset hash `316ad33b9d6f47e217a96246e81990b8fae0e11fd162dd31385715247ab4cb02`. driver `e0d2162c04cabada3212f13eec54685082da6384a06c063b846e1129db371444`, state `d1a0845a4f45f44af9698963c700e9dfa24d13bb3a4b8b729b9b15e8a15278e1` 일치.

추가smoke를보수적으로덮는prior50은실제50회주장이아니다. future reserve best validation552(전체2repeat의3attempt상한)+holdout276+UX144+G5G6 60=1032, baseline최대1104와prior50합계2186≤2400이다. 필수호출최악치예약후214여유만남는다고해석하며유료한도확장이아니다. priorcost planning$2.50+futurecostplanning$10.32+다음unknownattempt$0.05를제외하면현재stage실지출여유$2.13이다. 건강한기존smoke와유사한단가라면baseline약$1.6~1.7로예상되지만이를미래사용량실측이나hardcap보장으로표시하지않는다.

준비결과는private n02-preparation.json, 공개실패분석용analyze-public-run.py에보존했다. 분석기는기존독립검토scorer를호출하여baseline/dev/validation의동일run_id 보고서와실패분류를만들며, 이3보고서를서로다른repeat로세지않는다. 실제평가분모를부분성공으로바꾸지않고실패/미응답도유지한다. 보호holdout은읽지않았다. 정확I01Preview READY/source증거와명시실행GO 수신전actualbaseline호출0으로유지한다.

## N02 baseline 실제 실행 시작

Preview `dpl_73afciHs7CadEfeNSzpzz86sRmXz`, exact commit `10c00723d0b64ea47a06dcbd00e2b671e7c62daf`와 평가 config의 tracked24개 파일을 `git show <sha>:<path>`로 독립 byte 대조했다. private driver는 별도 SHA로 결속하며 public READY artifact를 private 불변 proof로 복사했다. 최종 config SHA `0f0ecca371e26561ba660997a544485955c77958bfb1783d2985417c4e9d754f`. 원격 API가 source SHA/prompt hash를 직접 증명하지 않는 한계는 유지하며 immutable Vercel source artifact와 로컬 source byte 대조로 연결한다.

조정자의 Preview 두 역할 실제 UI smoke PASS 및 명시 실행 GO를 받은 뒤 dry-run `PLAN_VALID` 336사례/368턴/prior50/future1032를 확인했다. 실제 baseline run_id `214fba09-c781-43e6-94aa-bec437f305b2`를 한 번 시작했다. 출력은 private `n02-baseline/`, ledger `nl-budget.json`에 누적한다. 실패를 포함한 전체 분모를 유지하고 pending 불확실 시 자동 replay하지 않는다. holdout 본문/호출은 0이며 최종 품질 판정은 완료 후 별도로 기록한다.

## N02 baseline 완료 및 독립 판정

정식baseline336개 모두 결과보존, PASS227/336, transport/schema미완료51, mandatory0, 최소기준 FAIL. 실제367회/6,208,489tokens/$1.659112/P95 4460ms. C06-dev-017 첫턴실패 때문에 계획368턴 중후속1턴 미호출이며 해당사례도실패분모유지. private n02-baseline 및 n02-baseline-analysis에config/run/원응답/attempt/공유ledger/분할채점 보존. 자세한role/split수치와실패가설은 n02-baseline-report.md. 동일run의dev/validation을독립repeat로세지않는다. holdout접근·호출0. baseline최소FAIL이므로출시best채택불가; C1기술회귀수정만PASS이고live품질미실행.
