# N06 C5 보호 holdout 독립 최종 평가

판정: **NL 최소 기준 FAIL / 최종 출시 NOT_READY**. 고정 holdout84개를 단1회 실행해82/84 성공했으나 경영주 명확 지시14/15=93.33%로 필수95%에 미달했다. 전체 성공률로 역할별 기준을 상쇄하지 않는다. stage_ready=false, nl_minimum_pass=false, independent attestation=FAIL이다. 원문·정답·개별 사례 ID는 보호 저장소에만 남긴다.

## 동결과 실제 실행

- C5 동결 시각 `2026-09-21T12:15:02.537642+00:00`, frozen-best SHA `6fc37ff892868cda2d9294fc6045356935a2fa5342509622a6fc98f212ec705f`. 두 validation 보고 hash·별도run_id·같은config/fingerprint·각각최소통과를 확인했다. 기존 timeout/의미 오류는 불변이다.
- exact source `f6a34def5dd6cc6287c3dedba805824974d67db8`, Preview `dpl_8YECM1r2msmSCtjLKGNSPvVYqKKV` / `https://wanna-qcrmzotip-beatrain-4635s-projects.vercel.app`, target null/READY. source28/runtime45의 현재/exact git bytes와 종료 후 runtime hash `7b24123e8067c4e83d3accce4197992d059f1705b4f56274fb4287e11d37aa5a` 일치를 확인했다. 암호학적 원격 API 증명은 아니다.
- model `gpt-4.1-mini-2025-04-14`, prompt `packed-refs-v5`, catalog248 불변. holdout config SHA `dc1699f39171173c996720b09813b093d88b51e14d6e5c35749e9c62d131ba48`, 미래156calls/$1.638, prior50/unknown$.05/2400calls/$20 유지.
- evaluator만 기존 SQL generator로 보호 업무상태를 생성했다. model에 정답/label/oracle는 전달하지 않았다. state SHA `d59c2f720325d8adf9761b3b7ed0c4aa9e3dfdfd65e67cc0c83919ef75d6ef0e`.
- PLAN_VALID84/92 및 기존claim0 확인 후 명시 GO로 단1회 실행했다. 종료claim1. run_id `b0035322-1025-4574-bfcb-5100006b604d`, fingerprint `d0516a526d9201628542fab837c1c252d5763bf23adb6843629ef278e6264927`. 동결 시각은 실제 실행 경계보다 이르다.

## 공개 집계

| 역할/그룹 | 성공/전체 | 기준 | 판정 |
|---|---:|---:|---|
| 고객 명확 |40/40(100%)|95%|PASS|
| 고객 불확실 |19/20(95%)|90%|PASS|
| 경영주 명확 |14/15(93.33%)|95%|FAIL|
| 경영주 불확실 |9/9(100%)|90%|PASS|

오류 범주는 고객 C08(범위밖)1건과 경영주 M03(scope)1건이다. 개별 내용·정답·ID는 구현자에게 전달하지 않았다. 미완료0·mandatory0·재시도0·usage미확정0, 실제92attempt/92발화다. P50 2467ms/P95 5681ms, 알려진 토큰1,014,728, 추정 비용$0.4182056이며 실제 청구 확정값이 아니다.

종료 장부 upper1064calls/known_provider1014/unknown_provider0, 알려진 비용$4.6495789 + prior계획$2.50 + 이전 validation 미확정usage$.05 = upper$7.1995789. 기존 실패/미확정 예약은 보존했다. pending=false·stop=null은 실행 완료만 뜻하며 품질 성공을 뜻하지 않는다.

## 증거와 종료

private `n06-c5-holdout-01`에 raw 원본, `n06-c5-holdout-01-analysis`에 비공개 상세채점과 집계를 보존했다. 공개 `quality/release/evidence/c5-holdout/`의 report/execution/binding/independent-report/bundle은 금지key·비밀값 검사 후 원문·정답·case_results·개별ID 없이 export했다. public report SHA `1afe848ea31ed67e71dfd539a867c9b68d526c0c640eda555e5941011ddcd543`.

최신 release checker의 bounded NL 검사를 실제 실행해 **NL_MINIMUM_FAILED** 차단을 확인했다. 최초 메타counts 누락과 과거 오류코드 기대를 수정한 것은 로컬 검증 호출만이며 모델/기준/원본 변경0이다. release-block.json에 실제 차단 코드를 보존했다. 본 평가자는 C5 앱 비구현자이고 본인 작성 scorer/runner 자체의 독립성은 research/builder 별도 검토와 구분한다.

추가 holdout 실행·holdout 기반 튜닝·정답/최소기준 변경·후보 자동교체는 하지 않는다. C5는 validation 기반 선정 후보지만 release-safe 최종 best로 승격할 수 없다. 두 역할 브라우저/UXv3/G5/G6 완료를 선언하지 않는다. 고객 QA는 준비 문서만 존재하고 실제실행0이며 후속 유료 작업을 자동 착수하지 않는다. 모든 워크트리·로그·브랜치·실패 원본을 보존한다.
