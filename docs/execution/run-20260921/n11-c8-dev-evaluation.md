# N11 C8 공개 dev30 독립 평가

**선별30/30 PASS, incomplete0·mandatory0·B0/C1~7 정상 회귀0.** 선택 표본의 `nl_minimum_pass=true`, 전체 dev가 아니므로 `stage_ready=false`다. C7보다 정확도가 높아졌다고 주장하지 않으며 validation/holdout/UX/G5/G6를 대체하지 않는다.

## 목적·실제 결속

D48의 잔여 복구 판단 위임에 따른 고객 C8이다. 고객 action/question/primary 생성 계약과 서버 검증 사이의 합성 반례를 수리하되 정상 상품 탐색·confirm·질문·미식별·대체/정정·명시 동의를 유지한다. 실제 C7 실패의 provider 원문은 없어 그 단일 원인을 확정하지 않았다. 경영주·공통 모델/provider/catalog/retrieval/packing/거래 도메인은 변경하지 않았다.

- source `bb2ab8056716c6d32669c1f8c6103a4a2ca397dd`, PR19 CI35672436354/35672452291 PASS 통보, Preview `dpl_ALPxiLtpYPN3xSLMb1bKsri5cLe9` / `https://wanna-ee7w1ldd1-beatrain-4635s-projects.vercel.app`, READY/target null/exact source proof 대조.
- 신규 `src/server/customer-wire.ts`를 포함한 source33 및 runtime48을 현재 파일과 exact git에서 전수 비교했다. runtime hash `66c63fad2b53398b1ffaa3d4230e1c0d5bae551f876daa91e94e88ed41573ec0`. 종료 source33도 불변이다.
- context v18 SHA `b2d55452e0dd9b4efe9f72082f7e5c41618c486ecc4e710de640de3a3217644f` ACK, 입력68개 해시 일치. D48 원장·C8 계약의 품질/독립성/예산 불변을 확인했다. D47의 이전 자동추가 금지는 당시 실패 기록으로 보존하고 현재 D48의 구체 복구 판단 위임과 구분한다.
- model `gpt-4.1-mini-2025-04-14`, prompt `customer-action-wire-v8`/SHA `b263e389554d15e42f2d7cf23f951d88eae2b86ddddaff1f60d4ae4e7a4a36e1`, catalog248 hash `f2696abe92521e3ff8f9ab43cb36a1d297a6fd23d272e239605b49fab4343b1e`, 공개 업무 state hash `d1a0845a4f45f44af9698963c700e9dfa24d13bb3a4b8b729b9b15e8a15278e1`.
- dev config SHA `36b0113fa023ecf6d18e5be7c4f8448fc1df4bc3ec4ff4ebcda1ec394a4eb60f`, immutable proof SHA `878f379e03246374db362fe5db6c573c09f229320c852ed95c2682a082a0dbcd`. 기존 미결속 초안과 bound draft도 덮지 않고 보존했다. PLAN_VALID30/34/984 확인 후 root 명시 GO로 한 번 실행했다.
- 원래 고정 dev dataset `0d394d463679189b082390219e74725e7a310f5173a5613d0bd87b5af85d26c7`, run_id `6ce4c1bf-7b57-4f12-959f-a17d6bc5c838`, run fingerprint `47f8a7b2ca14a3945081c05bdae7de2577d21da27512c46ca94c4a206b3b62c1`.

첫 정규 호출에서 HTTP200/구조화 응답/모델·버전 envelope/알려진 usage를 검증했다. input3470/output114/$0.0015704이며 별도 live smoke를 추가하거나 평가 분모에서 제외하지 않았다. 이는 첫 경로에서 provider가 새 형식을 수락한 실제 증거이며 모든 상황의 모델 정확성을 보장하지 않는다.

## 동일 표본 비교

| 비교 대상 | 이전 통과 | C8 개선 | C8 회귀 |
|---|---:|---:|---:|
| B0 |17/30|13|0|
| C1 |22/30|8|0|
| C2 |25/30|5|0|
| C3 |29/30|1|0|
| C4 |30/30|0|0|
| C5 |30/30|0|0|
| C6 |29/30|1|0|
| C7 |30/30|0|0|

고객 명확11/11·불확실7/7, 경영주 명확9/9·불확실3/3, 18개 범주 전부 통과했다. C6/C7 이전 오류·미완료 분모는 원본에 유지한다. 반복 노출된 작은 dev 표본의 동률/개선을 일반화하지 않고 원래 두 validation 반복으로 진행한다. P50 3173/P95 5994ms는 B0의2337/4483보다 느리며 UX 시간 개선이 아니다.

## 사용량·목적 보존·후속

34turn/34attempt, 실패0·retry0·usage unknown0·provider unknown0·pending false·stop null이다. 토큰433,712, 추정 비용$0.1787624, 최대 attempt$0.0067536/input15153/output475다. 청구 확정액은 아니다. 종료 공유 장부 upper1258calls/$8.1365397 = known1208calls/$5.5865397 + prior50/$2.50 + 이전 unknown usage$.05. 과거 prior는 실측이 아니다.

실행 중 미래984calls/$10.332·다음unknown$.05·총2400calls/$20을 유지했다. 정답/분모/출시 최소/소스/설정 변경0·출력 오류 보정0·분석 재호출0·보호 원문 접근0. 원본 private `n11-c8-dev30`, 분석/paired/장부 스냅샷 `n11-c8-dev30-analysis`, driver 로그와 모든 초기 초안을 보존한다. 본인 작성 평가 장치를 독립 검증한 것으로 세지 않으며, 별도 research/builder 검증과 앱 비구현 평가를 구분한다.

dev 선행PASS와 원래 회귀기준을 확인한 뒤 root의 사전 조건부 GO에 따라 config `091b56c38acbbee03cc3ee0761e725c1dcbef098ab6f8d304465df3217b74441`의 validation84/92 첫 실행을 시작했다. 두 번째는 첫 반복 PASS일 때만 같은 config/새 run으로 진행한다. 미래708/$7.434의 보수적 중복 예약/STOP을 유지하며 실패/unknown/auth/한도 시 후속 자동 실행하지 않는다. 새 보호84는 root freeze·별도 GO 전 접근/실행0이다. 최종 제품/G5/G6는 아직 미완료다.
