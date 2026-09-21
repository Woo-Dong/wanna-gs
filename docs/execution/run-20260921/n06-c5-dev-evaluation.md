# N06 C5 공개 dev30 독립 평가

판정: **선별 dev30 통과 / 고정 validation 진행 근거 충족 / best 승격 아님**. 30/30 통과, 미완료0, mandatory0이며 B0 및 C1~4와 같은 표본의 회귀0이다. partial nl_minimum_pass=true, stage_ready=false이므로 전체 dev·validation·holdout 또는 최종 제품 통과를 주장하지 않는다.

## 결속과 실제 실행

- exact source `f6a34def5dd6cc6287c3dedba805824974d67db8`, Preview `dpl_8YECM1r2msmSCtjLKGNSPvVYqKKV` / `https://wanna-qcrmzotip-beatrain-4635s-projects.vercel.app`, target null/READY. 28개 source_files를 현재 파일 및 exact git commit과 각각 대조해 불일치0을 확인했다.
- config SHA `f3b4953ca574c77750578ad387d3adf16c8e6c7102f9c6d85f7fd2fa5f105b88`, proof SHA `615e8189e16cd383beae095f7281d5755dbf0abc03f4c85217d3f19c613d4df5`. 독립 PLAN_VALID 30/34/future984 확인 뒤 명시 GO로 실행했다.
- context v13 SHA `f4a0ccd9d96c2536b50476baadf68aa3355533d3c1999d4cea2edeb5d7fe4a43` ACK와42개 입력 대조를 유지한다. 사용자 D-46의 목표 비용20 및 채택 ADR007 UX96 예약을 적용하며 이전15 상한 실행·중단 증거를 변경하지 않았다.
- model `gpt-4.1-mini-2025-04-14`, prompt `packed-refs-v5`, catalog248 hash `f2696abe92521e3ff8f9ab43cb36a1d297a6fd23d272e239605b49fab4343b1e`, state hash `d1a0845a4f45f44af9698963c700e9dfa24d13bb3a4b8b729b9b15e8a15278e1` 유지. 반환 envelope의 버전/model 일치를 실행기가 검증했다.
- C1 이전 동결한 dev30/34발화 dataset `0d394d463679189b082390219e74725e7a310f5173a5613d0bd87b5af85d26c7`. run_id `5914b25b-ef52-4b5a-979b-e3389230c385`, fingerprint `bc984cb2a4c7054174e69ea4f3fe85e1617ab83650f0f2105edac6fc5d1fe404`.
- 원본은 private `n06-c5-dev30`, 전체 채점·비교·장부 스냅샷은 `n06-c5-dev30-analysis`, 실행 로그는 `n06-c5-driver.log`에 보존했다. 분석 중 재호출0, 이 dev 작업 validation/holdout 호출0·보호 본문 접근0이다.

## 고정 표본 비교

| 지표 | B0 | C1 | C2 | C3 | C4 | C5 |
|---|---:|---:|---:|---:|---:|---:|
| 통과/전체 |17/30|22/30|25/30|29/30|30/30|30/30|
| 미완료 |3|6|3|0|0|0|
| mandatory |0|0|0|0|0|0|
| 실제 호출 |34|33|34|34|34|34|
| P50(ms) |2337|3138|2720|2838|2368|2173|
| P95(ms) |4483|15560|36624|5024|5384|5766|

B0/C1/C2/C3/C4 대비 개선은 각각13/8/5/1/0, 회귀는 모두0이다. 고객 명확11/11·불확실7/7, 경영주 명확9/9·불확실3/3이며 표본의18개 범주도 모두 통과했다. 작은 표본과 반복 노출의 한계 때문에 이 결과로 validation 두 반복 또는 holdout을 생략할 수 없다. P95는 B0·C3·C4보다 높으며 UX 조작·시간 개선으로 주장하지 않는다.

C5는 stale 입력의 모델 출력 스키마를 clarify로 제한하는 기술 수정이며 실제 provider 호출과 사용량은 유지했다. 현재 표본의 stale/정상 undo 및 수정 경로도 통과했다. C4 validation 두 번째 M06-validation-002 실패는 그대로 보존하며 이번 dev 성공이 그 실패를 삭제하거나 C5 validation 성공을 대신하지 않는다.

## 비용·목적 보존

34발화 모두 live/알려진 usage, 재시도0·unknown0·pending false·stop null이다. 토큰391,137, 추정 비용$0.1606032, 최대 attempt$0.0053584, 최대 input12828/output207. 실제 청구 확정값이 아니다. 종료 장부 upper787calls / known737 / unknown0, 알려진 비용$3.3801365 + prior계획$2.50 = upper$5.8801365이다. prior50은 과거 실측이 아니다.

실행 전체에 미래984calls/$10.332, unknown$.05, 총2400calls/$20 상한을 유지했다. 정답·시나리오·모델·소스·사례 분모 변경0, 실패 삭제0이며 모델 출력은 고객 동의/경영주 승인을 대신하지 않는다. 독립성 범위는 root 작성 C5 앱의 평가이고, 본인 작성 scorer/runner 자체를 독립 검증한 것으로 세지 않는다. 평가 장치의 별도 독립 검토는 research/builder 기존 보고서를 따른다.

후속은 별도 동결 config 및 GO에 따른 validation84/92 첫 실행이다. 두 번째 동일 설정 반복은 첫 결과 뒤 별도 GO가 필요하다. best 미선정·holdout 미실행·ADR007 UX v3 미실행·최종 G5/G6 미완료를 유지한다.
