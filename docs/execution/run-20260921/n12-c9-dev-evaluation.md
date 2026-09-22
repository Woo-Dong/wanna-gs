# N12 C9 공개 dev30 독립 평가

**고정 dev30/30 PASS, incomplete0·mandatory0·B0/C1~8 정상 회귀0.** 선택30개의 최소 기준만 통과했으며 전체 dev가 아니므로 stage_ready=false다. validation/holdout/UX/G5/G6 통과로 확대하지 않는다.

## 목적·결속

D48의 구체 복구와 D49의 Production 유지 지시에 따라, 고객의 불필요한 추가 primary 억제와 경영주 행동 생성 계약을 검증한다. catalog/정답/분모/95·90% 기준·최종 동의·거래검증은 유지했다. C8 validation79/84 실패와 중복표기 상품/정답 모호성은 변경하지 않고 보존한다. 본 평가는 앱 비구현자의 독립 실행이며 본인 작성 분석기를 독립 장치 검증으로 세지 않는다.

- source `8b52a2e8395e94c5f9b76df9e232ff2f37f70e6c`, PR20 CI35675635493/35675619863 SUCCESS 통보. Production `dpl_A3BiNBoshJK7QTgxLC47V5jjNLc4`, 불변URL `https://wanna-4r7aqsimm-beatrain-4635s-projects.vercel.app`, READY/target production/exact gitSource 확인. 가변 제출 alias의 G6 검증은 별도다.
- context v19 SHA `44e82074148e322215f0df95f3358b88e24211f6a8f8cc2dfbc5101a52b3db36` ACK,72입력 해시 일치. 신규 merchant-wire를 포함한 source34/runtime49를 현재 파일과 정확한 git source에서 비교했다. runtime hash `4ec9b26074d617a9a16e21d5e681088a7c611e90d8231c2d12bc32881ca3e3ef`. 종료 source34 불변.
- model `gpt-4.1-mini-2025-04-14`, prompt `action-contract-v9`/SHA `ee0b2aa9fd68a45d570d12b606e6bfa49d2f736a677285e9d5f3ee4734d290ec`, catalog248 hash `f2696abe92521e3ff8f9ab43cb36a1d297a6fd23d272e239605b49fab4343b1e`, 공개 SQL 업무state hash `d1a0845a4f45f44af9698963c700e9dfa24d13bb3a4b8b729b9b15e8a15278e1`.
- config SHA `6b96b4e46629f6e467e60d092acbfbda91d772112fc0effa7a5fba647dcac46e`, 불변 deployment proof SHA `062e7976c36c0fc3b8387497c068415eb3c74a35cb0b7c360343f998652ebe1e`.
- 고정 dataset `0d394d463679189b082390219e74725e7a310f5173a5613d0bd87b5af85d26c7`, run `99f229dd-d460-4a19-83e6-2003258c23f5`, fingerprint `62721f44974ce2b0430249de7ebd98077dc92de1ae2c0ecf950db62b7e4f3013`. PLAN_VALID30/34/924 확인 후 명시 GO로 최초1회 실행했다.

첫 정규 호출은 HTTP200/provider true/input3547/output123/$0.0016156으로 모델·버전 envelope와 새 생성형식 수락을 확인했다. 별도 smoke를 추가하지 않고 정규 분모/비용에 포함했다. 이는 해당 첫 경로의 실제 수락 증거이며 모든 의미적 동작의 정확성을 뜻하지 않는다.

## 고정 표본 결과

고객 명확11/11·불확실7/7, 경영주 명확9/9·불확실3/3,18범주 모두 통과했다. 반복 노출된 작은 dev의 결과를 일반화하지 않는다.

| 비교 | 이전 통과 | 개선 | 회귀 |
|---|---:|---:|---:|
| B0 |17/30|13|0|
| C1 |22/30|8|0|
| C2 |25/30|5|0|
| C3 |29/30|1|0|
| C4 |30/30|0|0|
| C5 |30/30|0|0|
| C6 |29/30|1|0|
| C7 |30/30|0|0|
| C8 |30/30|0|0|

P50 2776/P95 4557ms. B0 P95 4483ms보다 빨라졌다고 주장하지 않는다. 후보 정확도 동률은 정식 validation 채택 판단을 대신하지 않는다.

## 사용량·예약·후속

34turn/34attempt,실패0·retry0·이번 usage unknown0·provider unknown0·pending0·stop null. 토큰439,237,추정비용$0.1807756,최대attempt $0.0065532/input15246/output326. 종료 upper1384/$8.8025473 = known1334/$6.2525473 + prior50/$2.50 + 이전 unknown usage$.05. prior는 실측이 아니며 비용은 계정 청구 확정액이 아니다.

사전 예약은 dev후속924/$9.702, validation 동일두반복648/$6.804, holdout후속96/$1.008로 고정했다. UX84 및 QA/G6필수8+복구4를 유지하며 미배정 여유만 실제 계획으로 재산정했다. 현재stage는 모든 잔여turn×3도 예약하므로, 정상dev34/val0192 뒤 val02 최초예약은1476+276+648=2400이다. 앞단 추가retry나 비용 증가가 있으면 후속STOP 가능하며 최악 완주를 보장하지 않는다. 이전948/672안은 같은 지점2424로 차단됨을 임시Budget으로 재현했다. 평가자의 최초 산술 설명이 현재stage 예약을 누락했던 오류와 그 정정도 private reservation-probe에 보존했다. 한도2400/$20·prior50·unknown$.05·원래 transient 최대3회·실패보존 불변이다.

원본 private `n12-c9-dev30`, 분석 `n12-c9-dev30-analysis`, driver 로그와 모든 초안 보존. candidate-report SHA `e09bd1cb59a7562b631e96297e3e75655cf9a7e85094013360cbc3cb0f2e0cc6`. 보호 원문 접근0·정답수정0·출력보정0·진단 재호출0.

선행 dev 기준을 통과하여 사전 조건부 GO에 따라 config `4952022eb3334301a9751c91968756ee8d5bd9b398332da60b1977394e4a6f3e`의 첫 validation84/92를 시작했다. 둘째 반복은 첫 반복의 원래 역할 최소/mandatory/incomplete/회귀 기준 통과 후에만 같은 설정·새 run으로 진행한다. 신규 holdout은 freeze와 별도 GO 전 미실행이며 Production 배포 자체를 최종 완료로 세지 않는다.
