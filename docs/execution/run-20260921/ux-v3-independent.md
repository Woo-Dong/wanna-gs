# ADR007 UX-v3 기구 독립 검토

판정: 기구 구현·모의 경계·fixture 브라우저 범위 PASS. 작성자 preflight_builder/root, 독립 검토자 research. 검토자가 구현한 고객 UI의 독립 제품 QA로 세지 않는다. 실제 새 UX 연구/두 역할 최종 live QA/G5/G6는 별개이며 이번 검토의 모델호출·goal 장부쓰기·보호 holdout 접근은0이다.

## 계약·소스 ACK

채택 ADR007 SHA114c9528329ac1c5ee38b6a59ec3d3c1d8a69c404752e90bc94e622756612a94와 D46을 직접 대조했다. 초기16파일 SOURCE-HASHES 73801c6f…를 확인한 뒤 발견한 반례를 구현자가 수정했다. 최종 inventory e434dae83ef83021c7bf9956276f1e02cfb5a5520f0a72bd06ac9d84bf4f5736의16파일을 worktree/root에서 각각 다시 계산해 모두 일치했다. 최종 checker5e2a09d291d8224d1b629cb46bcc4c70359dba175156761187e7529a8849bb23, release-v3 testdd058aadf52f89438c9e2d4dfa7ec34931b06e7f1d40c2cd224a30caf21a0d5a다.

root context-ux-v14 SHA3a75d272e19803bcf168bb7576860dea798f0ae3fd5a40f291c48239a0f038e3와55입력 해시 ACK. root aggregate fingerprint fafda917e36bfe30a16a42046e69f907420663107a37b565e71c09d237c6b5bd 직접 계산. script/test collector는 v3 Python 디렉터리를 별도 필수 nonzero suite로, Node는 mjs/mts 양쪽 glob을 필수 수집하며 원래 v2를 유지한다. root gate 실제 raw 수집은 Python189(그중 v3bridge12/release72), UX Node19(기존10+v3 9), missing/skip/failure/error0이고 작성자 통합 실행 증거로 구분한다. 독립 check_contracts CLI PASS. 원래 v2 run/seed/metrics/live/bridge 5파일은 base560706f와 byte 동일함을 확인했다.

## 발견·수정한 필수 반례 F-V3-01

초기 releasechecker의 성공 observation은 provider_called가 bool이면 허용했다. synthetic best의42 liveUsage/network를 provider_called=false로 바꾸고 modelCalls=0으로 맞추면 전체 G5 검사기 synthetic positive가 PASS했다. 이 반례는 기존89개 자체 시험에 없었고 독립 직접 재현했다. 구현자가 statusok는 실제 providertrue여야 하며 PASS trial도 실제 providertrue observation으로 연결되도록 수정했다. best false/0call, baseline false-success, UI FAIL 뒤 숨은 false-success가 이제 거절된다. 정상적으로 알려진 baseline 실패 providerfalse/usage0/cost0는 실패 그대로 보존하며 다음 사전 trial 진행 가능하다. 범위/분모/정책을 완화하지 않았다.

독립 최종 실행: bridge12 + release72 + Node9 =93 unit/mock 검사 PASS, 독립 typecheck PASS. 별도 직접 반례7개는 provider없는 best/기준선 성공 거절, 알려진 false-provider baseline실패 정상 허용, 충분한 성공 뒤 STOP 우선,56행 중 미시도 거절, 옛 실패 제거 거절, 누적160→112 축소 거절을 확인했다. 추가 임시 장부2경계는 과거 NL providertrue/usageunknown 비용$.05 보존한 상태에서 새 study 정상 시작 가능, 새 UX unknown은 양쪽 arm 전체 STOP/추가 claim 거절을 검증했다. 이 합성 장부는 테스트 임시폴더에만 만들고 삭제했다. 초기 독립 probe에서 기대한 오류 코드 문자열 이름이 실제와 달라 검사장치 assertion이1회 실패했으나 올바른 거절 동작이었으며 실제 코드 문자열로 바로잡아 재검증했다.

## 고정 분모·편의성·안전 계약

고정 study/run ID, 동일8×7/56 실제시도·행 순서/중복/NOT_RUN 구분, baseline workload별 최소3 정상·best56정상, 전체 STOP/pending 우선이 코드와 검사기에 유지된다. 모든 성공 trial의 최대 조작/이동 및 비모델 시간 중앙값을 재계산하고 첫3개 선택을 허용하지 않는다. best 조작/이동≤baseline, median≤110%는 그대로다. 원래 v2 두 결과의 source hash/24×2=48/13PASS2FAIL33NOT_RUN을 새112와 함께 총160으로 요구한다. 알려진 실패 trial 내부 미실행 모델단계는 NOT_RUN, trial은 FAIL로 보존한다.

app-root의 전체 runtime/commit/build/server attribution과 현재 budget-root의 runner+adapter+scorer를 분리 결속한다. 각 trial 전후 runtime/harness/budget dependency 변화를 확인한다. bridge는 기존 목표장부만 열고 prior50/2400/$20/unknown$.05 및 남은42호출·미래 필수예약을 유지한다. known 실패 다음 trial은 가능하나 같은 trial 모델 재시도는0, unknown/auth/quota/source contract 오류·pending은 전체 STOP이다. config 승인·서버 PID attribution은 암호학적 원격증명이 아니므로 live 전 조정자가 실제 프로세스·두 arm 사전동결을 확인해야 한다.

## 독립 실제 fixture 브라우저

격리 worktree /Users/gsr/Desktop/workspace/2026-ralphton-ux-v3-instrument에서 builder가 사용 완료한 localhost3231을 양도받았다. .env.local 없음, fixture 서버 PID20952, BUILD_ID yt7fn88eKbcYV9lXwjcLF. 실제 모델 API는42번의 고정 fixture route 응답으로 대체됐으며 Budget 인스턴스가 생성되지 않았다. Node22+Chrome로 --stage best, --live 없이 새 output ux-v3-independent-fixture-01을 실행, exit0. 56계획/56시도/56PASS/0FAIL/0NOT_RUN, stopnull/pending0, 모델·provider outbound0이다. 56개의 fresh context마다 실제 sql.js/IndexedDB 무결성·FK·저장 hash·Worker clock1789959600000과 업무 상태를 확인했다.

clear3종은각7회/activation5, ambiguous7회/activation6·질문1, 재동의7회/activation5·동의버전2,10SKU묶음7회/activation2·화면이동0·승인1, auto7회/전체activation7·건별승인0·사후동일검토중복0, 예외묶음7회/activation2·2보류8lines를 확인했다. 상품·점포·동의 확인을 삭제하지 않았다. clear/batch/auto 실제 screenshot도 직접 확인했다. 원본 결과 SHA184c7316a7f2af62dbda2dbffbfa727b95b940415995049e11186dfdd02699ee, 경로 /Users/gsr/Desktop/workspace/2026-ralphton-ux-v3-instrument/artifacts/private/ux-v3-independent-fixture-01/result.json. 원본과56장 화면은 해당 private폴더에 남겼다. fixture 시간/56PASS를 실제 모델 best 품질이나 UX 개선치로 주장하지 않는다.

## 한계·현재 결과

독립 checker 기본 실행은 NOT_READY_MANIFEST_MISSING(exit1)로 유지됐다. 이번 synthetic package PASS는 검사 장치 정상·거절 경계 증거이며 실제 G5 manifest PASS가 아니다. old 원본 B0 실패, live baseline/best 새112, 최종 역할 QA, 실제 제출 URL/키 비노출과 G5/G6는 이 검토로 대체하지 않는다. 정책 채택과 현재 기구 준비는 완료됐지만 실제 연구 성공은 아직 not_run이다. unsigned review JSON은 review identity의 암호학적 보장이 아니다.
