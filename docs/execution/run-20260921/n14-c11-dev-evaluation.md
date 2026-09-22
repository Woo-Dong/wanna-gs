# N14 C11 공개 dev30 독립 평가

**30/30 PASS, incomplete0·mandatory0·B0/C1~10 정상 회귀0.** 원래 선택30개 선별의 최소 기준 통과이며 전체 dev 평가가 아니므로 stage_ready=false다. validation·holdout·실제 역할 QA·UX·G5/G6를 대신하지 않는다.

## 목적·정확한 실행 결속

D48/D49와 [C11 계약](c11-recovery-contract.md)에 따라 고객의 상품 식별·모호/미등록/범위밖 행동을 보수적으로 구분하면서 정상 요청을 유지하는 후보를 앱 비구현자가 평가했다. 원래 정답·분모·scorer·95/90·불완전0·mandatory0·회귀 금지를 유지했다. 니즈 근거 보존 수리는 같은 배포에 포함됐지만 이 API 평가로 고객 UI/SQLite 저장 검증까지 통과했다고 주장하지 않는다.

- source `cd29a2bc3be8c80fa00c03c2985f06819bef7255`, PR22 CI35682405032/35682389793 SUCCESS, 통합 merge d0265035b6d624831d250c7edcf96857475d5e06 및 mergeCI35682523210 PASS 통보.
- Production `dpl_4p4q7iHyuQ1mgMzDDbwcKnzuBGHU`, 불변 URL `https://wanna-j9hxy4yum-beatrain-4635s-projects.vercel.app`, READY/target production/exact source. 공개 배포 원본을 private 불변 proof로 복사해 결속했다.
- context v21 `e6512b02cac714b66845dda8be5648094d8967155c624016003b7c6b6ed136b0` ACK87. source38/runtime50의 현재 파일과 exact Git 바이트 전수 대조, runtime hash `d49c13dcbe3f5b358b8f7fb80d4316a68fd738c9f83a0e6395ec6f56a5dfbb9d`. 종료 source38 불변.
- model `gpt-4.1-mini-2025-04-14`, prompt `customer-classification-v11`, prompt hash `16e967e7f0adf1cfff7ff16e994a0e82e6ff09cf09ac6cc2e5fc0303f51a6d5a`. catalog248 `f2696abe92521e3ff8f9ab43cb36a1d297a6fd23d272e239605b49fab4343b1e`, 공개 SQL state `d1a0845a4f45f44af9698963c700e9dfa24d13bb3a4b8b729b9b15e8a15278e1` 유지.
- dev config `4ea0556c42ab3c2df6bf8bb3ddf37e0f3ac3aade5efff765bca2929ae77cac05`, proof `0c693ec63963f518618bb957da89bf3094ea15d842b0e17936786dff8d4d238c`, binding `b2878093b24a2635262e2e533cdcd7bcae534f6ef9942d14cd7e1b7d1493a0a0`.
- 원래 선택 dataset `0d394d463679189b082390219e74725e7a310f5173a5613d0bd87b5af85d26c7`, run `8d9c6e4d-640f-4671-99e7-a5850df597c3`, fingerprint `4c268f003a315332aa7dfd6e3c75e1b39346cb894ca623a97c3f1a61a97d35bc`.

PLAN_VALID30/34/후속372 이후 dev만 명시 GO를 받아 최초1회 실행했다. max_attempts=1을 사전 고정해 같은 요청 재시도는 하지 않았다. 첫 정규 호출은 HTTP200/provider true/input3887/output133/$0.0017676. 매 성공 응답의 mode/model/promptVersion/catalogVersion/envelope를 고정 설정과 엄격 대조했다. 응답 모델 문자열을 별도 원문 필드로 저장하지 않는 현재 runner의 한계는 남는다. API 자체의 commit 원격 attestation은 false이고 exact source 결속은 불변 Vercel 배포 proof+Git 바이트 대조 근거다. 별도 smoke0, 첫 호출도 정규 분모/비용에 포함했다.

## 역할·범주·동일 표본 비교

고객 명확11/11·불확실7/7, 경영주 명확9/9·불확실3/3. 적용18범주 전부 통과했다. 고객 C01~09 각2개, 경영주 M01/M03/M09 각2개·나머지 각1개인 원래 선택 분모를 유지했다. 이 작은 선택표본을 전체 split의 범주당 최소2개 평가로 표시하지 않는다.

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
| C9 |30/30|0|0|
| C10 |30/30|0|0|

C10 대비 선택 표본은 동률이다. 과거 후보의 max3 설정은 그대로 보존하고 C11의 max1로 재표시하지 않는다. 이번34개 최초 호출은 모두 성공했으며 재시도 축소를 모델 품질 개선의 근거로 삼지 않는다.

## 사용량·장부·후속 경계

34turn/34attempt, 실패0·retry0·이번 usage unknown0·provider unknown0·pending0·stop null. 토큰447,054, 추정비용 **$0.1837764**, 최대attempt $0.0066788/input15674/output290. P50 2218ms/P95 4294ms. 지연의 단일 선택표본 차이만으로 안정된 성능 개선을 주장하지 않는다.

종료 upper **1820회/$11.1932501** = known1770회/$8.6432501 + prior50회/$2.50 + 이전 unknown usage$.05. prior는 실측이 아니며 비용은 계정 청구 확정액이 아니다. 종료 ledger SHA `98c1b4704af102b353cc567a00908b6c8d1c593465733c1885a394143d932aa6`. dev 후속372/$7.698·현재 남은turn×1·2400/$20 STOP을 유지했다.

원본 private `n14-c11-dev30`, 분석 `n14-c11-dev30-analysis`, 준비 초안/불변 설정/proof를 보존한다. candidate-report SHA `c014e42698049a7f88dcd42ce0a5437a501964f4ea8fecd2067c9fe1506536ff`. 분석기 작성자의 분석 실행 자체를 독립 장치 검증으로 세지 않는다. 새 평가 요청에 보호 원문 접근0·정답/분모/기준 변경0·응답 보정0·추가 모델 분석 호출0.

**이 보고 시점 C11 validation01/02·fresh holdout-v3·역할 QA·UX 실제 실행은 모두0이다.** dev GO만 수행했으며 후속은 별도 GO와 최종 같은 설정 결속이 필요하다. C5/C10 보호 실패·이전 후보 실패·미실행 게이트를 그대로 보존하고 현재 Production을 최종 완료로 기록하지 않는다.
