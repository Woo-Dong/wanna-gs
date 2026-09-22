# N05 C4 공개 dev30 독립 평가

판정: **선별 dev30 통과 / 고정 validation 진행 근거 충족 / best 승격 아님**. 30/30 통과, 응답 미완료0, mandatory0이며 B0·C1·C2·C3의 같은 표본 대비 회귀0이다. partial nl_minimum_pass=true, stage_ready=false다. 이 결과를 full dev252·validation84·holdout·최종 출시 통과로 확대하지 않는다.

## 동결과 실행

- exact source `48bdb4f18f6c769806fbfa9399ea2cf6af2b5f6f`, Preview `dpl_4MmYgaDCps4s6ECYsCA5cYLPMfe9` / `https://wanna-gw30pjecw-beatrain-4635s-projects.vercel.app`, target null/READY. 실행 직전 root·candidate·exact commit의 결속28파일 바이트를 모두 대조했다.
- model `gpt-4.1-mini-2025-04-14`, prompt `packed-refs-v5`, catalog248 SHA `f2696abe92521e3ff8f9ab43cb36a1d297a6fd23d272e239605b49fab4343b1e`, state SHA `d1a0845a4f45f44af9698963c700e9dfa24d13bb3a4b8b729b9b15e8a15278e1`.
- context-n05-v11 SHA `5a3ff25c9b240c1786d2f763e70909017141279bee3c7fcb978dd0c5612c6fe3` ACK, 원본40파일 hash 모두 일치.
- config SHA `adc6b1e7d9fee210c922b7a90ef415cd882d5c84acabbfeae5db5bfb7846d86a`, READY proof SHA `d3a6f1643fcb00569141f0a38744c99c100852b0fe281549ff1b56cfee3af212`.
- C1 전에 동결한 동일 dev30/34발화, dataset SHA `0d394d463679189b082390219e74725e7a310f5173a5613d0bd87b5af85d26c7`. PLAN_VALID 뒤 명시 GO 범위만 실행했다.
- run_id `0928617b-ce0f-42bc-85ae-4c8a21173fbc`, fingerprint `6f368fa3c5e419597e755450628e0dc5366bdd7f149c22a82da68a9f5bed4265`. private `n05-c4-dev30` 및 `n05-c4-dev30-analysis`에 원본과 전체 채점·paired 비교를 보존했다. 이 dev 실행의 validation/holdout 호출0, 보호 본문 접근0.

## 동일 표본 결과

| 지표 | B0 | C1 | C2 | C3 | C4 |
|---|---:|---:|---:|---:|---:|
| 통과/전체 |17/30|22/30|25/30|29/30|30/30|
| 미완료 |3|6|3|0|0|
| mandatory 오류 |0|0|0|0|0|
| 실제 호출 |34|33|34|34|34|
| P50(ms) |2337|3138|2720|2838|2368|
| P95(ms) |4483|15560|36624|5024|5384|

B0 대비 개선13, C1 대비8, C2 대비5, C3 대비1이며 모든 비교의 회귀0이다. 이전 결과는 저장본만 읽었고 재호출하지 않았다. C4의 P95는 B0와 C3보다 높으므로 지연 개선으로 표현하지 않는다. 20초 목표 안에 있지만 실제 UX 완료시간·조작 비교의 대체가 아니다.

고객 명확11/11·불확실7/7, 경영주 명확9/9·불확실3/3이며 표본의 각 category도 모두 통과했다. 표본을 반복 학습한 영향과 작은 범주 분모 때문에 독립 validation/holdout을 생략할 수 없다.

C3 실패 M03-dev-002는 이번에 특정 SKU 제외와 정책 예산12,000원만 반환하고 불필요한 category 제외를 추가하지 않아 정상화됐다. 원래 명확 지시를 clarify로 돌리거나 category 기능을 제거해 얻은 통과가 아니다. 이전 C3 실패 및 연구자의 C4 혼합 제외·명시 참조 보존 기술 반례는 그대로 남긴다. 모델 동작의 추가 범위는 후속 고정 validation으로 확인해야 한다.

## 비용과 목적 보존

34발화 모두 live envelope와 알려진 usage를 확인했다. 재시도0·unknown0·pending false·stop null이다. 토큰392,793, 추정 비용$0.1618284, 최대 attempt$0.0055784, 최대 input12836/output349다. 실제 청구 확정값은 아니다. 공유 장부 upper569calls/known519/unknown0, 측정비용$2.3654181+prior계획$2.50=upper$4.8654181. prior50은 과거 실측이 아니다.

실행 중 미래960/$10.08, 다음 unknown$.05, 전체2400/$15를 유지했다. 좁은 비용 여유 안에 완주했으며 중단 기준을 낮추지 않았다. source·정답·시나리오·사례·분모 변경0, 원본 실패 삭제0이다. 모델 제안은 고객 동의나 경영주 실행 승인을 대신하지 않는다.

다음 단계는 별도로 동결한 validation config와 GO를 통한84개/92발화 첫 평가다. 이후 두 번째 동일 설정 반복은 첫 판정 후 별도 승인 범위다. B0 UX 비교 NOT_READY·best 미선정·holdout/G5/G6 미완료는 그대로 유지한다.
