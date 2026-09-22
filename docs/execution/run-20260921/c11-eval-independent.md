# C11 retry allowance / holdout-v3 gate 독립 기술검토

reviewer final_ux_state; root 작성기구와 분리된 독립검토. **PASS — 아래 exact source의 제한된 기술범위**. C11 모델후보·fresh holdout-v3 데이터·실제 제품QA/G5/G6 PASS를 뜻하지 않는다. C11 customer prompt 내용은 읽지 않았다. 데이터검토는 dataset작성자 method와 분리하여 준비완료 뒤 별도 수행한다.

## 목적 및 코드검토

ADR003 최초포함최대3회 안에서 새C11의 사전고정1회 조건을 실행하면서 기존 분모/최소/실패·원장보존을 유지한다. attempt_limit은 omitted3·정수1..3만 허용하고bool/부정/초과/문자/float/null을 거절한다. check_inputs와Runner 직접구성 모두 같은함수로검증한다. runtime retry range·마지막attempt 종료·current-stage remaining 예약에같은cap을사용한다. 원본config를새default key로변경하지않고명시cap을기존configfingerprint로결속한다. 받은실패journal은resume에서다시시도하지않으며config변경은fingerprint거절이다.

validation 두run의동일fingerprint 외에 validation↔holdout effectivecap 비교를check_inputs에추가했다. release package에서도두validation+holdout cap의타입/범위/동일성을검사해cap만다른보고서조합을거절한다. 새실행의값1은freeze/config소유자가명시적으로고정해야하며기구의허용1..3자체가C11용3회재허가는아니다.

manifest-v3는정확path/version/revision만허용하고직전v2를단순hash참조로믿지않고재귀검증한다. 원본dev/validation불변,84case/92turn/18category분포·customer40/20/merchant15/9,기존worst_attempt276메타보존과현재cap1실행은별개다. 원본+v2 family중복을제외하며은퇴기록prefix바이트의미동일·새원본실패84/nl_minimum_pass false·replayfalse·신규dataset이모든은퇴hash와상이함을검사한다. 데이터의실제의미중복/난도는기구hash만으로증명하지않고별도독립데이터감사의책임이다.

## 실행 검증

- tests/eval-runner35/35, tests/release89/89를독립실행하여PASS. 임시protocol fixture/localhost fake HTTP만사용했으며실제앱서버·모델·공유goal장부는사용하지않았다.
- 별도17직접반례그룹PASS: cap2최대2와재시도성공,생략default3와원config보존,cap1다턴첫실패의incomplete분모와인접정상·두번째턴실패·auth즉시중단,cap2다턴의잔여reservation12/11/10/9/8/7,cap1/2 완전releasepackage긍정,첫validationcap변조와bool거절,v3잘못된revision·은퇴순서교환·최신replay허용·은퇴행추가·overlap false를0처럼사용·선대실패를hash까지재결속한변조거절.
- 최초독립probe가cap2의첫transient뒤허용된성공을최종실패로잘못기대해group6에서멈췄다. 앱동작은정상이었다. 원probe와실패설명을보존하고cap1의확정실패에만incomplete단정을적용하도록probe조건만수정했다. 기존테스트기대값이나앱/평가기준은수정하지않았다. 최종17그룹출력은probes-result-v2.json이다.

## 한계 및 인계

실제C11 config·배포·context/freeze/평가결과는미완료다. 새runnerhash 때문에과거QA/UXdraft의budget_source는stale이므로최종후보용새결속을만들어야한다. 보호v3본문/정답/생성기는이기술검토에서열지않았다. 두과거실패holdout은은퇴보존,새84/92의사실·난도·원oracle은별도검토할것이다. 실제model/외부HTTP0, 공유장부읽기/쓰기0, 앱/공개평가기구파일수정0. 작성은이private기술보고·자체probe/log뿐이다.

## 검토한 exact source

- scripts/run_nl_eval.py: `3f158b5627873f5634bb13d0ec104f1f3177ef1f4fd493211028fb5fa036edd5`
- scripts/check_release_evidence.py: `ce4b9e62349790ca78d87d561a23342376702a18c69599486941758643490b6f`
- tests/eval-runner/test_nl_transport.py: `e85b016bda94a32fe8592c4f0618159c85c7d58ff97fcd9bd7fe9cb430d36fe5`
- tests/release/test_holdout_revision.py: `18ceef116a400bdae5dc281a3c09d41539d428f471755a014adbf2ecd5e58be0`
- tests/release/test_release_evidence.py: `f6f47057949698349a2c854de1e33ac0d4ae75f4fbce1011fbcd5c40abf59aab`
