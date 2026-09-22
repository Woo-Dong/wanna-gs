# N12 C9 공개 validation 첫 반복 독립 평가

**83/84로 역할별 최소 기준은 PASS, C5 대응 반복의 핵심범주 회귀 때문에 후보 채택은 FAIL이다.** incomplete0·mandatory0, scorer의 stage_ready=true와 채택 가능 여부는 별개다. 둘째 validation·신규 holdout·UX 실행0을 유지한다.

## 목적·정확한 실행 결속

D48/D49에 따른 C9 고객 추가 후보 절제와 경영주 행동 생성 계약을 앱 비구현자가 평가했다. 명확 탐색·모호/미식별·정정·경영주 현재/미래/undo를 유지하며 원래 공개 데이터·정답·scorer·95/90/mandatory0/incomplete0·정상 회귀0를 바꾸지 않았다. 고객/경영주 확인·동의와 SQLite 거래 검증은 모델 응답으로 대체하지 않는다.

- source `8b52a2e8395e94c5f9b76df9e232ff2f37f70e6c`, Production `dpl_A3BiNBoshJK7QTgxLC47V5jjNLc4`, 불변URL `https://wanna-4r7aqsimm-beatrain-4635s-projects.vercel.app`. READY/target production/exact gitSource 증거를 확인했다. PR20의 두 CI SUCCESS 통보와 source34/runtime49 현재/git 비교를 결속했다.
- context v19 `44e82074148e322215f0df95f3358b88e24211f6a8f8cc2dfbc5101a52b3db36` ACK72, runtime hash `4ec9b26074d617a9a16e21d5e681088a7c611e90d8231c2d12bc32881ca3e3ef`. 종료 source34 불변.
- model `gpt-4.1-mini-2025-04-14`, prompt `action-contract-v9`, catalog248·공개 SQL 업무 state·정답은 dev와 동일하다.
- config SHA `4952022eb3334301a9751c91968756ee8d5bd9b398332da60b1977394e4a6f3e`, proof SHA `062e7976c36c0fc3b8387497c068415eb3c74a35cb0b7c360343f998652ebe1e`.
- 고정84case/92turn, dataset `180e1ef3890bbde535e4be29a75698b5fa42d9e77a915da9d3d3646c9e486f46`, run `80ea5ee9-c828-47cd-a068-6aa982ef00da`, fingerprint `7a841e5c4d778804a0b11314ebb8efcf6fa4d4941b0d8d22f49499f2d3274236`.

선행 dev30/30과 정상 회귀0, PLAN_VALID84/92/648 확인 뒤 root의 조건부 GO에 따라 첫 반복1회만 실행했다. 별도 smoke/선별 재호출/정답 보정은 없었다.

## 최소 기준과 범주

| 역할/입력 | 통과/전체 | 응답 완료 | 최소 | 판정 |
|---|---:|---:|---:|---|
| 고객 명확 |39/40|40/40|95%|PASS 97.5%|
| 고객 불확실 |20/20|20/20|90%|PASS|
| 경영주 명확 |15/15|15/15|95%|PASS|
| 경영주 불확실 |9/9|9/9|90%|PASS|

고객 C01 9/9, C02 7/8, C03 8/8, C04 7/7, C05 6/6, C06 6/6, C07 6/6, C08 5/5, C09 5/5. 경영주 M01~M06 각각3/3, M07~M09 각각2/2. 최악범주는 C02 87.5%다. 누락/스키마 오류/미완료/mandatory 오류0이며 전체83/84다.

유일한 공개 실패 `C02-validation-007`은 명시한 도라지차500ml 정답에 더해 중복표기500ml와340ml를 모두 confirm 후보로 추가했다. 실제 응답 differences에340ml를 명시하므로, 알려진500ml 중복ID/정답 집합의 모호성만으로 이 실패를 없앨 수 없다. 조건과 다른340ml를 primary 확인 후보로 제시한 의미 오류가 남는다. catalog·candidate_pool·점수는 변경하지 않았다.

## Paired와 채택 기준

| 동일84 비교 | 이전 통과 | 개선 | 회귀 |
|---|---:|---:|---:|
| B0 |58/84|25|0|
| C5 대응 첫 반복 |84/84|0|1|
| C7 첫 반복 |83/84|1|1|
| C8 첫 반복 |79/84|4|0|

C8의 다른 고객3건과 경영주 undo OUTPUT_CONTRACT1건은 이번에 통과했다. 단일 관측으로 원래 경영주 실패의 정확한 원인을 소급 확정하지 않는다. C7의 C04-validation-001도 통과했다. B0 incomplete10을 보존하고 compare_candidate의 invalid_baseline을 PASS로 바꾸지 않는다.

`c6-recovery-plan.md`의 C5 대응 repeat 핵심범주·필수정상 회귀0, C7 계약의 같은 조건, C8 계약의 C5 고정비교/정상회귀0와 C9의 기존 기준 유지에 따라, C02 명시 속성 범주가 C5첫반복8/8에서7/8로 감소한 사실은 채택 조건을 충족하지 못한다. B0 대비25개 개선이나 역할95% 달성으로 상쇄하지 않는다. 따라서 평가자 판정은 **split minimum PASS / adoption FAIL / validation02 STOP**이다. 실패 후 같은 설정을 다시 뽑아 좋은 결과를 선택하지 않는다.

## 비용·중단·원본

92attempt/92turn 전부 HTTP200, retry0·이번 usage unknown0·provider unknown0·pending0·stop null. 알려진 토큰1,187,424, 추정 비용$0.4890228, 최대attempt $0.0065552/input15254/output329. P50 2602/P95 5111ms로 B0 P95 4052ms보다 느리다. 시간 개선 채택 근거도 아니다.

종료 공유 장부 upper1476/$9.2915701 = known1426/$6.7415701 + prior50/$2.50 + 이전 unknown usage$.05. prior는 실측이 아니며 비용은 공급자 청구액/잔액과 구분한다. ledger SHA `ca28bfb22c155144838ee73ac42eaa19b584b2fbd789bc0992e68a10d821c3f2`. 실행 중 후속648/$6.804, 현재 잔여turn×3, 다음unknown$.05와2400/$20 STOP을 유지했다.

private 원본 `n12-c9-validation-01/`, 분석 `n12-c9-validation-01-analysis/`, driver로그를 보존했다. candidate-report SHA `cf7adf7ca32ad9ef72476243704784be0167152a95e76d9e2730b2e4e3a5c0cb`. 본인 분석기 실행은 모델0이며 자체 작성 평가 장치의 독립 검증으로 세지 않는다. 이전 후보의 성공·실패·초안·예산 재산정 정정 기록을 덮지 않았다.

둘째 validation84/92와 신규 보호84/92는 미실행, 보호 원문 접근0이다. release evidence 성공 bundle이나 best freeze를 발급하지 않았다. Production 배포는 사용자의 D49에 따른 중간 배포이며 UX/G5/G6 또는 목표 완료 증거가 아니다. 새 근거에 따른 다음 bounded 복구는 root 결정과 새 결속/GO를 기다리며 현재 추가 호출0이다.
