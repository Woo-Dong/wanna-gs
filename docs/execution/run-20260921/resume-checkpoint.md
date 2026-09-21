**D47 최신 승인:** 사용자 실제 답변 ‘고객 후보 1개 추가 승인’으로 고객7/경영주6·총13 한정 복구를 실행한다. [C7 계약](c7-customer-contract.md)과 context-n08-v16, root codex/n08-customer-recovery를 따른다. 아래 ‘미승인’은 질문 전 상태의 이력이며 이제 이 추가 한 후보만 승인됐다. 최소기준·예산·실패·최종 검증은 그대로다.

# 현재 재개 체크포인트 — C6 실패와 한도 도달

C6 실제 dev29/30 FAIL(고객 불확실6/7<90%, 기존 정상1회귀). source8397048, PR14 통합311b934, main3ef1ee3. [실패 보고](n07-c6-dev-evaluation.md)·[현재 진행](../../PROGRESS.md)·[자원 장부](resource-ledger.json)를 우선한다. 승인된 고객6/경영주6 후보를 모두 사용했고 출시 적격 best가 없다. 후속 C6 validation/새 holdout/UX/G5/G6는 미실행이다.

D46의 $20 비용 상한 및 ADR007 UX 복구 승인은 유효하지만 후보 수 확장은 포함하지 않는다. 추가 후보·동일 결과 재호출·실패 면제는 아직 승인되지 않았다. 원래 보호84는 은퇴한 실패 이력이며 재호출 금지, 독립 신규84는 아직 한 번도 모델로 실행하지 않았다. 이전 실행의 PASS를 현재 게이트로 옮기지 않는다.

누적 upper1098회/$7.3603041, known1048/$4.8103041 + prior50/$2.50 + 이전unknown$.05. 실제 계정 청구액이 아니다. C6 원본은 private n07-c6-dev30 및 n07-c6-dev30-analysis, 소스32 결속·runtime47 검증·세션 로그와 모든 worktree를 보존한다. C6 전용 runtime은 build 완료/서버 미시작이다. 고객 QA 준비물의 independent mock 검사와 실제 고객 모델/브라우저 PASS는 구분한다.

아래는 승인 전/초기 C5 시점의 기록으로 보존한다. 현재 상태가 아니다.

---

# 실행 보존과 재개 체크포인트

**후속 사용자 승인 D-46:** 사용자가 아래 두 변경을 명시 승인하고 계속 진행하도록 지시했다. goal 비용 soft cap20을 실행기에 반영하고 독립 검증을 통과했다. UX 세부 절차는 ADR007의 두 독립 동일초안 검토 후 채택했다. v3 실행기 독립 검증은 별도 진행 중이다. 아래15초과는 승인 전 차단의 역사적 근거로 보존한다. 목표의 최소품질·실패기록·최종게이트는 불변이다.

목표는 미완료다. 현재 앱 구현·과거 두 역할 SQLite/live 흐름·기술 PR/CI/Preview는 존재하지만 최신 후보의 필수 자연어·UX·G5/G6 게이트가 남아 있다. 사용자가 요청한 프로젝트 폴더와 기능별 worktree, 실패/원본 로그는 삭제하지 않았다.

## 현재 코드와 증거

- 후보 C5: `4fc3e1e4e4f55c76b68eb34ba9b89991ab69fbd3`, `codex/n06-stale-candidate`, [PR11](https://github.com/Woo-Dong/wanna-gs/pull/11). root의 기록 브랜치와 후보 source를 혼동하지 않는다.
- [C5 Preview](c5-preview.json): `dpl_Hs5h9zTibohSAfLtxzChBdEHTe8o`, 보호된 검증 URL, target=null/READY. 모델 실제 호출0, 최종 제출 URL 아님.
- 로컬 Python149+Node83/type/build PASS. 독립 stale 상태60조합·paid 오류6·SDK mock10 PASS. [기술 검토](n06-c5-technical-review.md), [현재 지문 게이트](c5-local-gate.json).
- C4 dev30/30, validation84/84 및83/84. 두 번째 경영주 불확실8/9는90% 미달이다. [실패 보고서](n05-c4-validation-evaluation.md). 두 결과를 합쳐 성공 처리하지 않는다. C5는 같은 오래된 상태를 생성 schema에서 제한하며 실제 결과를 사후 교체하지 않는다.
- 보호 holdout84는 미실행이며 평가자만 접근한다. 최종 best는 아직 없다. 기술 후보를 best로 새 이름 붙여 평가 한도를 초기화하지 않는다.

## 승인 전 두 차단 조건의 역사적 기록

[예산 감사](n06-c5-budget-audit.md): 알려진703회/$3.2195333에 과거 보수 예약50회/$2.50를 더한 장부 상한은753회/$5.7195333이다. 다음 후보 dev 실행을 위해 남겨야 할 필수960회/$10.08와 다음 unknown$.05를 더하면$15.8495333이므로 현재$15 soft stop에 걸린다. 실제 계정 잔액·청구 확정액이나 호출 한도2400의 고갈이라는 뜻은 아니다. 실패한 C4 validation을 C5의 필수 두 평가에서 빼지 않는다. 현재 새 유료 호출0·한도 변경0.

[UX 결과](ux-baseline-recovery-results.md): 최초2PASS/1FAIL/21미실행, ADR006 재측정11PASS/1FAIL/12미실행, 누적48 중13PASS/2FAIL/33미실행. 현재 계약은 전체 비교 NOT_READY와 추가 자동 실행 금지를 유지한다. 성공 행 합치기·fixture 대체·현재 후보를 원래 baseline으로 이름 바꾸기는 허용되지 않는다. 이 문제는 API 비용 여유만 확보해도 해소되지 않는다.

조정자는 사용자에게 API 예상비용 상한을$20로 늘리고, 실패기록과 최종 제품 최소기준을 유지하며 UX 복구·비교 절차를 두 독립 검토로 재설계할지 확인을 요청했다. 이후 실제 사용자 응답 ‘두 변경을 승인하고 계속 진행’을 D-46에 기록했다. 단순 시간 경과로 승인한 것이 아니다. 새 크레딧 구매·자동 충전은 요청하지 않았다.

## 답변 이후에도 필요한 순서

1. 실제 사용자 답변·현재 goal 상태·원격 SHA/CI/배포/장부를 확인한다. 조건 변경이 승인되면 권한·정책·실행기·시험에 명시 반영하고 원래 실패는 유지한다. 단순 문서 변경만으로 hardcoded 예산 검사가 바뀌었다고 주장하지 않는다.
2. 승인된 예산/새 유효 계약 안에서 C5 source·Preview·모델·프롬프트·schema·평가 설정을 고정한다. dev30, 동일 validation84 두 회를 각각 통과해야 best를 동결할 수 있다. 다음 모델 호출 전 비용·시도 예약을 다시 검사한다.
3. best 동결 뒤 평가자만 보호 holdout을 실행하고, 두 역할 독립 브라우저 QA·실제 SQL·UX 측정과 비교·정책/운영 감사·G5를 수행한다. 실패/누락/미검증을 통과로 바꾸지 않는다.
4. G5 통과 뒤에만 main 릴리스 PR/CI·Vercel 제출 배포·G6(접근·실제 모델·키 비노출·DB/reset·48시간)를 한다. 현재 Production/global 모델 설정을 미리 후보로 바꾸지 않는다.

## 보존한 실행 공간

- 현재 root: `/Users/gsr/Desktop/workspace/2026-ralphton`.
- 새 v3 기준선 앱: `/Users/gsr/Desktop/workspace/2026-ralphton-ux-baseline-v3`, 원본10c0072/Node22 build PASS, 모델 호출0.
- 격리 폴더: 위 경로 뒤에 `-preflight-20260921`, `-domain`, `-customer`, `-merchant`, `-nl-candidate`가 붙는 worktree. 실제 Git 목록은 `git worktree list`로 대조한다.
- 공개 보고·배포/CI/정책: `docs/execution/run-20260921/`, `docs/decisions/`, `quality/`.
- 원본·실패·예산·비밀·평가/브라우저 로그: `artifacts/private/run-20260921/`, `artifacts/raw/`. Git 제외이며 비밀값/holdout을 공개하지 않는다. Codex 전체 대화 원문의 완전한 복사본이라고 주장하지 않는다.
- private 경영주 QA 실행기와 QA Budget bridge는 후속 독립 실행 준비물이다. C4 설정은 approved:false이며 C5 소스에서는 stale 거절되어야 정상이다. 준비물/모의route시험은 실제 QA 통과가 아니다.
- 옛 B0 테스트 서버 session19063과 C4 준비 서버 session41491은 종료했다. 디스크 `.next`와 소스만 보고 실행 중인 서버가 최신이라고 판단하지 않는다. 새 시연은 정확한 source에서 새 build·별도 process로 시작한다.
- Node22·Python3.10+ 사용. 이 Mac의 기본 Python3.9는 검사기와 호환되지 않는다. `npm run gate`에 실제 번들 Python을 PATH로 지정한다. 사용자 `.env.local`의 서버 키는 값을 출력하거나 Git에 넣지 않는다.
