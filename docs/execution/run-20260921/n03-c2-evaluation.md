# N03 C2 공개 dev30 독립 평가

판정: **선별 dev 측정 완료 / C2 채택 불가 / validation 보류 권고**. 같은 공개 30개에서 통과 수가 늘었지만 기존 정상 사례 4개가 회귀했고 응답 미완료 3건과 지연 악화가 남았다. full dev252·validation84·출시 최소 기준의 통과를 뜻하지 않는다.

## 동결과 실행 근거

- 정확한 배포 source는 `e056fce800bd1ea225baf9a0d70e85b0a2d0edf3`, Preview는 `dpl_ASemeiWS9zk1ks44qcizKBhxQ8He` / `https://wanna-7i0nrj2kc-beatrain-4635s-projects.vercel.app`이다. target null, READY 증거를 불변 복사했다. 로컬 root `6f955190692bc11b91bdc338ed9ce83034ccb8f7`의 평가 결속 27개 파일과 배포 commit의 파일 바이트가 같음을 독립 확인했다. API 자체의 source attestation을 주장하지 않는다.
- model `gpt-5-mini-2025-08-07`, prompt `packed-refs-v3`, catalog248 SHA `f2696abe92521e3ff8f9ab43cb36a1d297a6fd23d272e239605b49fab4343b1e`.
- config SHA `ccf3cd59a15b209de50eaa2de215c0f49c558a82c58b1ad8734976ee2710ee8f`, immutable READY proof SHA `862e17b7c9e65302df48a22df44ad10cd1901094c65475a3ea61db6f56d9550e`.
- C1 전에 고정한 동일 dev30 dataset SHA `0d394d463679189b082390219e74725e7a310f5173a5613d0bd87b5af85d26c7`를 사용했다. 30개/34발화, 실행 후 사례·정답·분모 변경 0. dev와 validation 계획의 PLAN_VALID를 확인했지만 실제 GO는 dev30만 적용했다.
- run_id `89673419-dd52-4956-9172-447dc4c3ee46`, fingerprint `4ec9558af84956ce34a5beb18cf58f33f09999f86a951b92aa87d0b804d293a2`. 원본은 private `n03-c2-dev30`, 분석은 `n03-c2-dev30-analysis`에 보존했다. validation/holdout 호출 0, holdout 본문 접근 0.

## 동일 30개 비교

| 지표 | B0 저장 관측 | C1 저장 관측 | C2 실제 관측 |
|---|---:|---:|---:|
| 통과/전체 | 17/30 | 22/30 | 25/30 |
| 응답 미완료 | 3 | 6 | 3 |
| mandatory 오류 | 0 | 0 | 0 |
| 실제 user turn 호출 | 34 | 33 | 34 |
| P50 HTTP 응답(ms) | 2337 | 3138 | 2720 |
| P95 HTTP 응답(ms) | 4483 | 15560 | 36624 |

B0 대비 개선 12개, 회귀 4개다. 회귀는 `C08-dev-002`, `C09-dev-001`, `C09-dev-002`, `M02-dev-001`이다. C1 대비 개선 5개, 회귀 2개(`C02-dev-002`, `M02-dev-001`)다. 전체 ID는 summary.json 및 c1-comparison.json에 남겼다. B0/C1은 저장 관측만 읽었고 재호출하지 않았다. 서로 다른 설정의 비교를 동일 설정 validation 반복으로 세지 않는다.

30개 모두 기록했고 계획 34발화를 모두 호출했다. provider 호출 34회, 재시도 0, usage unknown 0, pending false, stop_code null이다. 토큰 401,611개, 사용량 기반 추정 비용 $0.13242425, 평균 attempt 비용 약 $0.00389483, 최대 $0.00952325였다. 실제 청구서 금액으로 표현하지 않는다. 공유 장부는 upper 501 calls / known 451 calls / unknown 0, 측정 비용 $2.0431865 + prior 비용 예약 $2.50 = upper $4.5431865다. prior 50회/$2.50은 과거 실측이 아닌 보수적 예약이다.

## 실패와 인접 정상 확인

| 사례 | 실제 실패 | 근거 |
|---|---|---|
| C02-dev-002 | INVALID_MODEL_RESPONSE, HTTP 502 | input 12,456 / output 3,200 / 38,146ms |
| C08-dev-002 | wrong_action | clarification 대신 primary 후보 `DEMO-868D929B1816`와 확인 요구를 반환 |
| C09-dev-001 | INVALID_MODEL_RESPONSE, HTTP 502 | input 12,492 / output 3,200 / 36,624ms |
| C09-dev-002 | INVALID_MODEL_RESPONSE, HTTP 502 | input 12,493 / output 3,200 / 29,383ms |
| M02-dev-001 | wrong_action, command_composite_mismatch | 이미 명확한 현재 수정 지시에서 최신 제안 버전 확인을 다시 질문 |

미완료 3건은 모두 출력 3,200토큰에 도달했지만 안전 진단은 없었다. 이 평가 시점에는 C2 서버의 incomplete reason 로그를 독립 확인하지 않았으므로 출력 상한 원인이라고 확정하지 않는다. 원전송 실패와 비용을 그대로 보존했다.

M02-dev-001은 평가 장치의 상태 불일치 여부를 추가 점검했다. 동결된 실제 전송 state의 proposalVersion과 currentProposalVersion은 모두 3이고 stale은 false다. 현재 예산·수량 제약과 이전 제약도 존재한다. 사용자는 이번 발주안의 예산 11,000원 이하, 최대 2개, 특정 SKU 제외를 명시했지만 모델은 제안서 버전 3으로 수정할지 되물었다. 따라서 stale fixture의 정상 질문으로 재분류하지 않았다. 복합 지시 및 불필요한 업무 부담 기준을 유지한다.

## 목적 보존과 다음 단계

상품 식별과 경영주의 명확한 제안 수정이 정상 완료되어야 한다는 목적을 유지했다. 후보 확정·동의 검증이나 불확실성 질문을 제거하지 않았고 실패를 fixture 응답으로 교체하지 않았다. stage_ready와 nl_minimum_pass는 false이며, 작은 dev 표본의 점수 상승만으로 승격하지 않는다.

다음 후보는 별도 가설·설정·정확한 배포 증거·독립 검토 후 판단할 수 있다. 이번 예약은 필수 960 attempts × $0.009 = $8.64였으며 관측 최대 attempt는 이를 약간 초과했다. 다음 모델이나 설정에는 남은 필수 평가 비용을 다시 산정해야 한다. 총 2,400회/$15 및 unknown attempt $0.05 예약을 확대하지 않는다. B0 UX 복구 실패와 G5/G6 미완료는 별개로 남아 있으며 NL 측정 완료로 면제되지 않는다.
