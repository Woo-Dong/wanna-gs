# B01 독립 bootstrap 검증

- 판정: **PASS — B01 gate/framework 범위만**. 제품 도메인·거래·실제 모델 품질·브라우저 G3~G6·최종 배포 완료를 뜻하지 않는다.
- 검증자: `/root/research`, 구현자: `/root`; bootstrap 구현파일 수정 없음.
- consumed_context: `CTX-20260921-APP-v3` / `e8d6eb6ffef8765544e3aeeeb9c27b1e98f0c7cb5131202712ec4d32d806ea99`.
- 원래 context-app-v2도 읽었으며 v3의 PLAN 상태·소유권/preflight 확인 갱신을 ACK했다. 정책 변경은 없다.
- code fingerprint: `a65f0f2d5f3fe0ae8bafffb2696d451f23f778cbdfdf42fe80b1643dacdb17b4`.
- CORE-16/17/18/22, plan B01, card 목적 보존, 09/13/14 및 wanna-gs-verify 적용.
- 독립 승인 파일: `quality/reviews/B01.json`. signed identity가 아니므로 reviewer 이름의 암호학적 신원/위조방지 보장을 주장하지 않는다.

## 실행 증거

| 명령/검사 | 실제 결과 | 증거 |
|---|---|---|
| `python3 scripts/check_contracts.py` | PASS, 현재 context 원본 hash/CORE 참조 일치 | 도구 실행 출력, full-gate.log |
| `python3 scripts/test_runner.py` | 33 tests, skipped/failures/errors 모두0 | `artifacts/raw/b01-independent/python-tests.log`, `artifacts/raw/python-tests.json` |
| `python3 artifacts/raw/b01-independent/verify.py` | 독립 assertion33개 PASS | `artifacts/raw/b01-independent/adversarial.json`, 재현 스크립트 verify.py |
| `npm run typecheck` | exit0 | `artifacts/raw/b01-independent/typecheck.log` |
| `npm run build` | exit0, Next16.3.5 production build, `/` 및 `/api/health` | `artifacts/raw/b01-independent/build.log` |
| 로컬 서버3035 `/api/health` | HTTP200, bootstrap / transactions not_implemented / model not_checked | 독립 도구 출력, 본 보고서 |
| `npm run gate` | 독립 승인 파일과 현재 fingerprint로 전체 CLI 실행 | `artifacts/raw/b01-independent/full-gate.log`, `artifacts/raw/gate-report.json`; 최종 exit 결과 아래 추가 |

독립 adversarial33개는 도메인 제품 테스트가 아니다. 검증기 정상입력, stale parent/child/review, child 누락, tests0/skip, fixture의 live 대체, 자기검증, 목적/정상/인접회귀 누락, claimed PASS+nonzero exit, review 누락, 잘못된 JSON 필드 타입/누락, 중복 review를 검사했다. 실제 복사본 CLI에서는 review 누락 거절·유효 증거 통과·첫 명령실패 시 다음 명령 미실행·0 test counts 거절을 실행했다. 실제 test_runner 복사본으로 수집0/필수skip이 nonzero이고 정상1개는 exit0인지 확인했다. context checker 복사본에서 원본 변경/삭제가 nonzero이고 원본 유지 때 exit0임을 확인했다. 임시 복사본이므로 프로젝트 구현과 실제 context 원문을 변경하지 않았다.

## 발견과 수정 확인

첫 독립 반례에서 다음5건이 validate의 오류 없는 결과로 잘못 통과했다: tests만 있고 skipped/failures/errors 누락, purpose_preserved 문자열 `'false'`, 공백 evidence, boolean test count, 같은 task의 FAIL/PASS 중복 review 마지막값 우선. 구현자에게 재현을 전달했고 구현자가 typed 필수 count·정확한 True·비어있지 않은 문자열 list·중복 task 거절로 수정했다. 검증자는 구현을 고치지 않았다. 수정 후 같은 반례와 정상 계약을 재실행해 전부 기대 결과를 확인했다.

계약/context freshness 검사도 구현자가 추가했으며 검증자가 현재 원문 hash와 누락/변경 거절을 실행했다. 독립 CLI harness 초안의 positive fixture에 새 context config 필드가 빠져 1회 실패했으나 fixture에 필드를 추가한 뒤 정상·실패 양방향을 다시 확인했다. 이 harness 설정 오류를 제품 버그나 성공 증거로 세지 않았다.

## 목적 보존·범위

- 정상: 완전한 실행 증거와 별도 검증자가 있으면 bootstrap gate가 통과한다. 안전 검사 때문에 모든 증거를 일괄 거절하지 않는다.
- 실패: 미실행/누락/구버전/0/skip/live 혼용·자기검증·목적누락은 거절하고 명령 실패 뒤 후속 검사를 실행하지 않는다.
- 인접: OpenAI 환경 파서 테스트, Next type/build, context 원본/요구 참조를 유지한다. 실제 모델 호출이 없는 초기 shell은 모델 성공이라고 표시하지 않는다.
- shell은 ‘개발 중’, 요청·발주 아직 준비 중, 모의 거래와 한 탭 범위를 DOM에 표시한다. 브랜드 발음 ‘원하지쓰’가 실제 텍스트로 있다. 이는 정적 구현 검토이며 실제 시각/모바일 접근성 PASS가 아니다.
- CUA의 Chrome 생성은 `Browser is not available: chrome`, inventory는 빈 배열이었다. 따라서 이 검증자의 실제 브라우저 관측은 **not_run**. HTTP200/빌드를 브라우저 QA로 대체하지 않는다. 독립 local Next 서버 session과 artifacts는 재개 가능하게 남겼다.
- GitHub required-check/branch protection과 exact-source Preview 배포는 조정자 외부 작업이며 이 로컬 검증으로 완료를 선언하지 않는다. Vercel git 설정의 main true/나머지 false는 정적 확인만 했다.
- source가 바뀌면 이 fingerprint 승인도 stale이다. 이후 영역별 체크·live evidence 생산기·G3~G6는 각 scope에 맞춰 확장하고 독립 검증해야 한다.

## 최종 config 보강 확인

첫 full gate는 exit0/PASS였다. 이후 구현자가 Vercel git branch glob에 `codex/**: false`를 추가했다. `main: true`와 `*: false`는 유지되며 앱 동작/정책 변경은 없다. 이 변경을 정적으로 확인해 최종 승인 fingerprint를 `67a90d155e4559c637e1ee709aaef026da47fabcc8f493da192b8aee2fdf78cb`로 갱신했다. 앞의 fingerprint는 최초 독립 실행 이력이다. 실제 branch 배포 제어 검증은 조정자가 수행한다. 변경된 정확 source에서 full gate를 다시 실행한다.

최종 full gate: **exit0 / PASS**, contracts·33 Python tests·typecheck·production build 모두 PASS. 증거: `artifacts/raw/b01-independent/full-gate-final.log`, `artifacts/raw/gate-report.json`. 승인 fingerprint와 실행 fingerprint 일치 확인.
