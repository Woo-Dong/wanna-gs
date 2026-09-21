# 2026-09-21 goal 실행 중 — 현재 포인터

- task: I01 앱 통합 PR #4 merge 완료, N02 기준선 완료/품질 FAIL, C1 개선 후보·편의성 측정 중. root `codex/n02-quality`, 통합 `5f2e5d2`. 최종 G5/G6 완료 아님.
- [PR #4](https://github.com/Woo-Dong/wanna-gs/pull/4): head `10c00723d0b64ea47a06dcbd00e2b671e7c62daf`, CI35587047192/35587057239 PASS. 전체 로컬 gate fingerprint `6ab487de4e1e7bc69cc3b1805ed01e35a897c30787351d5f737811a3734a92f3` PASS. 통합 merge CI35587268459 PASS.
- I01 Preview `dpl_73afciHs7CadEfeNSzpzz86sRmXz`, source10c0072, target=null READY. [배포](execution/run-20260921/i01-preview.json)·[실제 두 역할 브라우저](execution/run-20260921/i01-preview-browser.json): 고객 자연어·명시 동의→경영주 자연어 현재 예산 수정·묶음 승인→공급/모의 결제/입고48h→픽업/refresh PASS. 최초 own harness의 잘못된 scope 기대값 실패를 private 원본으로 보존했고 수정 후 2 live 호출 PASS(총4호출).
- D02 SQL36 + C01 상태5 + M01 매핑3 + 서버9 = 단위53 PASS, Python91 PASS. 독립 고객 정상5/경계12 및 경영주 실제SQLite12·live 검증 PASS. [고객](execution/run-20260921/i01-customer-browser.md)·[경영주](execution/run-20260921/i01-merchant-browser.md).
- ADR002~005 각 두 관점 검토로 위임 채택. schema-v2/seed248v2, cataloghash f2696abe…343b1e. 248상품·9공개 점포위치와 모의 거래/가격/재고 구분 유지.
- N02 공개 dev252+validation84 =336case/368turn 기준선은 정확한 I01 Preview에서 227/336 PASS, 109 FAIL(51 응답 실패 포함). 실제367호출·$1.659112, 후속1턴 미호출 포함 실패분모 유지. 별도 보호 holdout84는 best 고정 후 평가자만 실행. prior50회/$2.50 보수 예약, 전체2400회/$15 및 필수 후속 예약 유지. 기준선 최소미달로 채택하지 않음. [보고서](execution/run-20260921/n02-baseline-report.md).
- UX 8workload×3 baseline/best 측정기 자체fixture24 PASS, 독립 검토에서 반복분모·누락/시간분리 결함을 수정하고 독립fixture24/24·기구반례 PASS. 실제 baseline24 측정 실행 중, 비교 완료 아님.
- main3ef1ee3, main/integration required gate+strict+enforce_admins 유지. Production 서버 키는 설정했으나 제품 Production/G6 미실행. [배포 사고·복구](execution/run-20260921/deployment-recovery.md) 보존.
- root 및 preflight/domain/customer/merchant worktree, `artifacts/private/run-20260921/` 원본/실패/실행 로그를 보존한다. [작업공간 안내](execution/run-20260921/README.md). 비밀값/holdout은 Git 제외.
- 다음: 기준선/제한 후보 실험·UX비교·보호84→G5 두 관점 정책/운영 감사→main release/CI→실제 제출 URL G6.

---

# 이전 준비 기록 (goal 시작 전 이력)

아래 상태는 과거 시점의 기록이며 현재 상태는 맨 위 포인터를 따른다.

## 현재 포인터

```text
현재 task: Vercel 프로젝트·GitHub 연결 확인 완료
branch: main (origin/main tracking)
PR: 없음
마지막 유효 게이트: 제품 게이트 미실행
마지막 Production deployment: 없음
다음 한 가지: OpenAI 키 주입 후 연결 점검 및 남은 preflight 수행
```

## 현재 상태

| 항목 | 상태 | 증거 |
|---|---|---|
| 요구사항·실행 계약·스킬·템플릿 | 최신 지시 반영·문서 검증 완료 | README·card·02·WORKPLAN·GOAL |
| 위임 운영 결정 | ADR-001 채택, 실행 검증 전 | DECISION_INDEX·ADR-001 |
| GitHub | 원격 09c3cc3의 경영주 조회 명세와 로컬 63535e6의 SQLite/OpenAI 변경 통합 | 현재 branch·merge 결과는 Git 이력과 아래 기록 확인 |
| 로컬 설정/사전점검 검사기 | OpenAI 15개 + inventory 10개 테스트 통과 | scripts/ 및 .agents/skills/wanna-gs-preflight/scripts/ |
| 앱·CI·게이트 실행기·DB seed | 미구현 | 기능 개발 goal 미시작 |
| SQLite | D-44 한 PC·한 탭 구조 확정, 실제 앱/seed/WASM은 미구현 | 06/29번, Neon은 현재 준비 대상 제외 |
| Vercel | 개인 Hobby 프로젝트·GitHub Woo-Dong/wanna-gs 연결 확인, Production branch main, 배포 전 | CLI 59.23.2, Node 22.22.3, 아래 준비 기록 |
| OpenAI | 정적 검사에서 OPENAI_API_KEY 누락, 실제 호출 미실행 | D-45·25번·P08, 키 값 비노출 |
| 앱 단위·통합·E2E·실제 모델 평가 | 미실행 | 문서 검사와 구분 |
| 최종 제출 URL | 없음 | 실제 배포 전 |

## 반영한 기준

- 자연어 요청부터 한 점포 수요, 보수적 발주, 공급 확보 후 모의 결제, 입고·픽업 알림부터 정확히 48시간 수령까지 연결한다. 세부 요구는 CORE와 02번을 따른다.
- 문서는 최초 구현의 현재 기준으로 관리하고 Git/결정 이력으로 변경을 추적한다. 재현용 schema·seed·모델·평가 식별값은 유지한다.
- clone/worktree 경로를 실행 시 확인한다. 특정 사용자 홈 경로에 의존하지 않는다.
- card.md의 목적 보존 기준을 시작·인계·복구와 작업/실패/검증 보고서에 연결한다. 실행기·CI 강제는 초기 구현에 포함한다.
- ADR-001에 따라 최소 seed 이후 기능 구현과 전체 자료 수집을 병행한다. 정식 QA·자연어 기준선·최종 게이트는 전체 seed를 요구한다.
- D-44 SQLite와 D-45 OpenAI API를 현재 기준으로 한다. 이전 Neon/Gateway/Gemini 준비 조건을 대체했다. 실제 앱·모델·최종 배포 검증은 남아 있다.
- 강제 full-access 설정과 fixture 기반 중간 Production 제안은 현 실행 계약으로 채택하지 않았다. 중간 공유는 Preview, 최종 Production은 G5 후 G6 검증이다.
- 중복된 과거 리뷰 5개는 [통합 검토 기록](reviews/2026-09-21-execution-proposals.md)에 결론·기존 검사 범위를 보존하고 삭제했다. `.gitignore`로 비밀값·로컬 연결·테스트 부산물·임시 파일을 제외했다.

## 이전 초기 커밋의 검증 기록

아래는 디자인·가치 추가 전 2026-09-21 실제 실행 결과다. 최신 파일 수/ID 수로 오해하지 않는다:

- Markdown 56개: 로컬 링크 242개와 코드 블록 검사 통과. 고정 사용자 홈 경로·문서 릴리스 번호 잔재 없음.
- D 34개·CORE 23개·AC 29개·O 12개·R 44개 ID 순서·중복·누락 검사 통과.
- WORKPLAN Mermaid DAG 35개 노드·55개 간선: 순환 없음. F00은 전체 수집/D05를 기다리지 않고 N01/Q01/Q02/G5는 D05에 의존함을 확인.
- 프로젝트 스킬 8개 `quick_validate.py` 통과.
- `python3 .agents/skills/wanna-gs-preflight/scripts/test_inspect_environment.py -v`: 7개 테스트 통과. 비밀값 정제, docs-only의 READY 오판 방지, timeout, 기존 보고서 보존, 임시 Git 관찰 등을 검사.
- 게시 대상 59개 텍스트 파일의 알려진 토큰·개인키·DB 인증 URL 패턴 검사: 후보 없음. 패턴 검사로 모든 비밀정보 부재를 보증하지 않음.
- 두 독립 검토자 `review_release_proposals`, `review_seed_proposals`가 실행/데이터 의존성과 제품/목적 보존을 검토. README의 전체 seed 대기 표현과 10번의 미구현 화면/API 의존을 수정한 뒤 재검토에서 추가 필수 문제 없음.

문서·스킬과 로컬 검사기 검증이다. 앱 기능·실제 외부 연동·CI 강제·배포 게이트 PASS를 뜻하지 않는다.

## 다음 작업

1. 이번 문서·홍보 시안을 검토한다. 사용자가 기존 main push를 완료했으므로 init/push 인증 문제를 현재 차단으로 취급하지 않는다.
2. README의 계정·키·연동 준비 후 preflight inspect/live를 수행한다.
3. 실제 연동 결과를 확인한 뒤 별도 `/goal`로 앱 개발을 시작한다.

## 기록 원칙

작업 ID·사용자 목적·변경·적용 결정·실제 검증·증거·미실행/차단·다음 행동을 남긴다. 오래된 세부 기록은 통합할 수 있으나 실패·블로커를 지우거나 실행 전인 기능을 완료로 표시하지 않는다. 이전 문서 감사와 로컬 검사 이력은 통합 검토 기록에서 확인한다.

## Git 초기화·커밋과 게시 상태

문서 검증과 독립 재검토를 마친 뒤 `git init -b main`을 실행했다. origin은 `https://github.com/Woo-Dong/wanna-gs.git`이다. 59개 파일을 대상으로 `git diff --cached --check`를 통과한 뒤 초기 커밋 `940c31b` (`docs: initialize WANNA GS implementation plan`)을 만들었다.

`GIT_TERMINAL_PROMPT=0 git push -u origin main`은 `could not read Username`으로 실패했다. 현재 Git은 osxkeychain credential helper를 사용하지만 이 실행에서 사용할 HTTPS 인증을 얻지 못했다. 기존 SSH 경로도 BatchMode·StrictHostKeyChecking을 유지해 확인했으나 `Permission denied (publickey)`였다. 계정·키를 새로 만들거나 읽어 출력하지 않았고 원격 이력은 변경하지 않았다. GitHub CLI도 현재 설치돼 있지 않다.

이후 사용자가 직접 push 완료를 알렸다. 2026-09-21 로컬 HEAD와 origin/main이 모두 `8f1765ab8f43d09ac447331fc127a373d174f2f7`임을 확인했다. 후속 원격 읽기는 실행 환경의 DNS 제한으로 확인하지 못했으며 이를 GitHub 인증 실패로 재분류하지 않는다. 위 실패는 과거 이력이고 현재 앱 preflight·배포 완료 근거는 아니다. 이 확인 당시 디자인·가치 관련 변경은 로컬 미커밋 상태였다. 이후 정리 작업은 아래 기록을 따른다.

## 디자인·서비스 가치 추가 작업

- D-35의 ‘원하지쓰’ 가시적 발음 안내와 우리동네GS 참고 디자인, 후속 시안·블루 색상 지시를 26번에 반영했다.
- D-36 입력 예시·조사 날짜·seed 연결·공개 예시/holdout 분리, D-38 캐릭터 참고와 방해 금지 규칙을 추가했다. built-in image_gen으로 색상을 보정하고 무무씨를 참고한 컨셉 일러스트를 넣어 `docs/assets/wanna-gs-promo-mascot.png`에 저장했다. 공식 원본 에셋은 아니다.
- D-37·CORE-25·AC-31과 27번을 추가했다. SKU 매핑·니즈/대체 확인·묶음/보수적 자동발주·분석 기록을 연결하고 동의 없는 대체, 관심의 확약 합산, 미취급/품절/오류 혼동, 반복 승인·과잉 발주를 실패 조건으로 정했다.
- read-only `review_design_contract`는 상태 구별 데이터 부족과 인근 수요 범위 충돌, 대체 동의·편의성 회귀 지표를 지적했다. 01/04/05/07/09/21/23/27 및 작업·완료 계약에 반영했다.
- 추가 외부 피드백은 reviews 기록과 18번/README를 보완했다. 설정 위치를 바로잡고 자동화 bypass와 심사자 공유 접근을 구분했다. forced full-access·checkpoint Production은 채택하지 않았다.

앱·실제 LLM·단위/통합/E2E·배포는 여전히 미실행이다. 그림과 문서 검토는 실행 증거가 아니다. 최신 문서 정적 검사 결과는 아래에 추가한다.

## 디자인·가치 추가 시 문서 검증 결과

2026-09-21 디자인·가치 추가 후 Markdown 59개, 로컬 링크 284개, 코드 블록 짝 검사 통과. D 38개·CORE 25개·AC 31개의 순서/중복/누락과 UX-B01~10·VAL-01~08을 확인했다. `git diff --check` 통과. 구현 시작 토큰의 대비는 흰 글자/행동 블루 4.91:1, 제목/밝은 시안 11.99:1, 보조 글자/흰 바탕 6.04:1이다. 이 계산은 생성 이미지 픽셀이나 아직 없는 실제 UI의 접근성 통과를 뜻하지 않는다.

독립 검토자 `review_design_contract`의 최종 문서 재검토에서 차단할 모순이 없었으며 작업 ID D04A/D04B와 전체 결과 요약 문구 두 곳을 정리했다. 이번에는 앱/스킬 실행 코드를 변경하지 않았고 앱 테스트·preflight live·외부 배포를 실행하지 않았다. 이전 로컬 검사기 7개 테스트 기록은 과거 검증으로 유지한다. Git commit/push도 이번 변경에는 실행하지 않았다.

## 이미지 구현 참고·경영주 팀원 자료 검토

2026-09-21 후속 요청 반영. D-39는 최종 시안을 공통 시각 참고로 채택하고 26번에 이미지 영역→실제 UI/상태→QA 매핑, P02·영역 FE·실제 브라우저 비교·영향 범위 수정·재개 절차를 추가했다. GOAL/WORKPLAN과 작업·UX 보고서 양식에 연결했다. 이미지의 고정 숫자·누락 상태를 기능 명세로 복사하지 않으며 매 반복 재생성하지 않는다. 효율 개선은 설계 판단이고 실제 개발 시간 측정은 아니다.

팀원 폴더 `reviews/wanna-gs-team-handoff-2026-09-21`의 원본 10개를 모두 읽고 현재 상태·업무·데이터·검증/가치 계약과 비교했다. `reviews/2026-09-21-merchant-handoff-review.md`에 M-01~13 후보, 8개 충돌/주의점, 스키마 대응과 사용자 선택 후 병합 순서를 기록했다. D-40에 따라 모든 후보는 미채택이며 실제 제품 기능·스키마·테스트 기대값에 병합하지 않았다. 원본의 픽업 제외/확정 스키마를 이 프로젝트의 최신 지시로 취급하지 않도록 AGENTS/GOAL/리뷰 목록에 경계를 명시했다. 기존 확정 기능의 독립 작업은 진행 가능하다.

이번 정적 검사는 Markdown 71개·로컬 링크 319개·코드 블록, D 40개·CORE 25개·AC 31개와 M-01~13 순서/중복/누락, `git diff --check`를 통과했다. 원본 10개는 작업 전후 SHA-256이 동일하다. 팀원 코드/SQL/실행 로그는 없고 앱·DB·외부 서비스 검증은 수행하지 않았다. 이번에도 commit/push는 실행하지 않았다.

## Neon 후속 설정 안내 반영

2026-09-21 계정 생성 완료를 사용자 보고로 기록하고 `green-unit-60810095`/`production`은 제공된 연결 대상, 실제 존재·접근·역할은 미검증으로 구분했다. 28번 가이드와 README·06/08/18/25번·문서/출처 목록을 연결했다. Neon 배포와 Vercel 배포, Neon AI Gateway와 기존 모델 경로를 구별하고 CLI/MCP/skills/config의 선택 범위를 명시했다. `.gitignore`에 로컬 연결 포인터 `.neon`을 추가했다.

명령 설치/로그인·MCP/skills 설치·키 생성·link·config init·deploy·DB 쓰기·유료 변경은 실행하지 않았다. Neon 계정 생성만으로 preflight READY를 선언하지 않았다. 팀원 자료의 D-40 미병합 상태는 유지한다. commit/push도 실행하지 않았다.

이번 문서 정적 검사는 Markdown 72개·로컬 링크 326개·코드 블록·D 40개/CORE 25개/AC 31개를 통과했다. `git diff --check`와 `.neon`/`.env.local`의 ignore 동작을 확인했다. 앱·Neon 실제 접속 테스트는 실행하지 않았다.

## 경영주 기능 재판단과 사용자 기준 반영

2026-09-21 D-41 모집 목표 초과 접수 유지, D-42 잘못된 자동 구매·입고 전 수령 만료를 일으키는 기한 결합 기각을 사용자 직접 결정으로 기록했다. 03/04/07/09·결정 인덱스·card·GOAL·README에 연결했다. MOQ는 접수 상한이 아니며 동의 유효기간 O-03의 구체 값과 부분 배정 O-01은 미정으로 유지한다.

경영주 비교 검토 보고서에 M-01~13의 최신 채택/수정/보류 권고와 원본 그대로 기각할 8개 동작을 정리했다. 나머지 기능은 사용자 선택 전이며 D-40의 경계를 유지한다. 팀원 원본 10개 SHA-256은 기존 보존 기록과 동일하다.

문서 정적 검사: Markdown 72개·로컬 링크 327개·코드 블록·D 42개/CORE 25개/AC 31개 검사 통과. `git diff --check` 통과. 앱/DB/LLM 테스트·배포·commit/push는 실행하지 않았다. 다음은 사용자가 권고 항목을 선택한 뒤 관련 기능 명세·작업 계약에 병합하는 것이다.

## 경영주 상품↔고객 요청 상세 조회 추가

2026-09-21 사용자가 경영주가 상품 단위 집계에서 고객 단위 요청 상세로 내려가 상품·수량·가격·동의 여부/시각·접수 순번·발주 연결·확보/배정/결제/예약/픽업 상태를 확인하도록 요구했다. 이를 새 거래 생명주기나 건별 승인으로 확장하지 않고 D-43 직접 결정, CORE-26, FR-13, AC-32로 추가했다.

- 03/05/07: 상품 집계→고객 상세 흐름, 기존 관계를 이용하는 읽기 전용 조회, 제안 API와 필드/권한 계약을 연결했다.
- 20/21/27: merchant UX/FE/BE 책임, 독립 merchant-qa 항목, 상품 합계·고객 행 합계와 세션/점포 격리 불변식을 연결했다.
- 09/WORKPLAN/GOAL/README: 단위·실제 DB·G3·경영주 G4·G5/G6 적용 범위와 완료 체크를 추가했다.
- `.agents/skills/wanna-gs-ux-audit/SKILL.md`와 `wanna-gs-verify/SKILL.md`: 5개 정보, 합계/상태/권한 대조를 실행 규칙에 추가했다.
- 아직 앱·DB·API·브라우저·독립 QA는 실행하지 않았다. 동의 유효기간 O-03 등 기존 미정 정책은 임의로 확정하지 않았다.

## 문서 정리·커밋 대상 요약

2026-09-21 사용자가 현재 변경 전체의 정리와 로컬 Git commit을 요청했다. push는 사용자가 직접 진행하므로 실행하지 않는다.

- 26번: 우리동네GS 참고 색상·원하지쓰 발음·두 역할 입력 예시·캐릭터·시안에서 실제 화면으로 구현하고 검증하는 절차. 이미지 3개와 생성 기록 포함.
- 27번: 정확한 SKU/대체 후보·미충족 니즈 보존, 경영주 묶음 처리·보수적 자동발주, 불편을 늘리지 않는 검증 기준. CORE-24/25·AC-30/31 및 작업 계획에 연결.
- 28번: Neon 계정 생성 이후 인증·브랜치 분리·연결 검증과 선택 CLI/MCP/skills 안내. `.neon`은 로컬 설정으로 제외.
- 경영주 검토: 팀원 원본과 비교·재판단 기록을 보존. D-41/42는 반영하고 나머지 M 기능은 사용자 선택 전 상태를 유지.
- 실행 준비: Codex 설정 위치·실제 권한 확인, Vercel 자동 테스트 접근과 심사자 공유 접근의 구분을 보완. 기존 릴리스 계약 유지.

문서 링크·코드 블록·결정 ID·공백 검사를 최종 실행하고 커밋한다. 앱 기능·배포·외부 연동은 이번 작업에 포함되지 않으며 기존 테스트 계획을 실행 완료로 표시하지 않는다. 아래의 과거 미커밋·미실행 기록은 각 작업 당시 상태다. 커밋 결과와 실제 SHA는 Git 이력에서 확인한다.

## 고객 상세 조회 요구사항 커밋·게시 요청

2026-09-21 사용자가 직전 D-43 변경의 commit과 push를 요청했다. 변경된 문서·스킬 21개만 대상으로 하며 관련 없는 `.idea/`는 제외한다. 커밋 제목과 본문은 각 줄 50자 이내로 작성한다.

`git diff --check`, 변경 문서의 코드 블록 짝·추가 로컬 링크, D 43개·CORE 26개·AC 32개·FR 13개의 순서/중복/누락 검사가 통과했다. 원격 main과 작업 전 HEAD의 일치를 확인했다. 앱·DB·브라우저 테스트와 독립 제품 QA는 미실행이다. 게시 완료는 push 결과와 원격 SHA 대조로 확인하며, 이후 README의 환경 준비·preflight와 별도 goal에서 CORE-26/AC-32를 구현·검증한다.

## SQLite·OpenAI API 전환 — 2026-09-21

사용자 D-44/45를 반영해 아키텍처·서비스/API 계약·goal·WORKPLAN·검증/복구·데이터·UX·배포·핵심 요구·결정 인덱스와 관련 스킬을 갱신했다. DB는 로컬 생성 seed.sqlite를 Vercel 정적 자산으로 제공하고 한 탭의 sql.js가 실행하며 IndexedDB에는 SQLite 사본을 저장한다. 서버는 OpenAI 모델 API만 담당한다. 200개 이상 상품 생성, 동일 seed/catalog manifest, 실제 SQL 및 브라우저 저장·복원 검증은 goal 구현 작업이다.

.env.example과 빈 키의 .env.local을 준비했다. .env.local은 Git 무시 대상으로 확인했다. 키 값 없이 모델/모드만 안내하며 scripts/check_openai_env.py의 기본 실행에서 OPENAI_API_KEY MISSING, live=not_run, ready_for_goal=false, 종료코드 2를 확인했다. 실제 OpenAI 요청은 보내지 않았다. --live는 사용자가 키를 넣은 뒤 별도로 실행할 소량 연결 시험이다.

실제 검증: OpenAI 검사기 15개 unit test, inventory 10개 unit test, 스킬 8개 quick_validate 통과. Markdown 73개·로컬 링크 337개·코드 블록·D44/CORE25/AC31 순서·중복·누락 검사 및 git diff --check 통과. 팀원 원본 10개의 SHA-256은 작업 전과 동일하다. sqlite_migration_review와 openai_env_checker의 독립 문서 검토에서 지적한 서버 상태·예비 모델 경로·검사 결과 설명을 수정했다. 이 증거는 문서와 설정 검사기의 검증이며 앱 SQL/WASM·live API·Vercel·제품 G1~G6 통과가 아니다.

직전 문서 정리 커밋은 1a5e8a2다. 이번 변경은 로컬 미커밋 상태이며 commit/push·goal 실행·외부 배포는 하지 않았다. 키 입력·연결 점검 후 별도 goal로 앱 구현을 시작한다.

## 원격 main과 SQLite/OpenAI 문서 통합

2026-09-21 `git fetch origin`으로 원격 `09c3cc3`의 경영주 상품→고객 상세 명세를 확인했다. 로컬 변경을 `codex/sqlite-openai-docs-sync`의 `63535e6`으로 보존한 뒤 일반 merge로 통합했다. 12개 파일의 충돌은 양쪽 요구를 대조해 해결했고 원격 커밋을 제거하거나 공유 이력을 재작성하지 않았다.

이미 게시된 D-43(경영주 상세 조회)을 유지했다. 미게시 SQLite D-43은 D-44, OpenAI D-44는 D-45로 변경하고 문서·스킬의 참조를 함께 갱신했다. 과거 검증 기록의 ID 개수는 당시 기준이다. 최종 원장은 D 45개·CORE 26개·AC 32개·FR 13개다.

경영주 상세는 로컬 조회 서비스로 연결하고 합성 고객·읽기 전용·동의/순번/발주/이행 상태·집계 일치·불일치 시 승인 중단을 유지했다. 같은 SQLite snapshot과 요청별 집계로 중복 합산을 막는 계약을 보완했다. 다중 브라우저 공유·서버 거래 DB·다중 사용자 경합 검사는 되살리지 않았다.

통합 검증은 설정 검사기 15개·환경 inventory 10개 unit test, Markdown 73개·로컬 링크 337개·코드 블록·결정/요구/AC 순서 검사, 충돌 표시 및 diff 공백 검사다. 실제 앱·API·배포 검증은 미실행이다. 독립 검토자 review_remote_integration이 원격 요구 보존과 SQLite 경계를 확인했으며 병합을 막을 문제가 없다고 판정했다. 스킬 8개 형식 검사·FR 13개 순서 검사·팀원 원본 10개 hash 보존도 확인했다. 기본 Python의 PyYAML 누락으로 형식 검사 실행이 한 번 실패해, PyYAML이 설치된 기존 Anaconda Python으로 재실행했다. 게시 절차는 16번에 fetch→작업 커밋→merge→영향 검증→main fast-forward→일반 push로 보강했다.

통합 커밋 이후 사용자가 push한다. 최종 merge SHA와 원격 대비 상태는 `git log` 및 `git status -sb`로 확인한다. push 전 원격이 다시 바뀌면 새 변경을 통합·검증하며 force push하지 않는다.

## Vercel 계정·CLI 준비

Vercel CLI 59.23.2 설치 후 사용자가 브라우저 로그인을 완료했다. Node 22.22.3으로 CLI version·whoami·teams ls가 성공했으며 계정은 beatrain-4635다. 기본 Node 23에서 의존성 지원 경고가 있어 기존 Node 22 LTS로 CLI를 실행했다. 최초 조회는 세션 네트워크 제한으로 실패했고 네트워크 권한 허용 후 성공했다. 이를 인증 실패로 분류하지 않는다.

사용자가 개인 공간 beatrain-4635s-projects(Hobby)를 선택했다. wanna-gs 프로젝트를 생성하고 현재 clone을 연결했다. 프로젝트 ID는 prj_T6x8XA3XyaNTgjMmvp7p9CgGCsks이며 Next.js·Node 22.x·루트 디렉터리 기본값을 project inspect로 확인했다. OPENAI_MODEL=gpt-5-mini와 LLM_MODE=live를 Production/Preview/Development의 일반 설정으로 등록했다. 이는 모델 접근이나 배포 성공 증거가 아니다.

GitHub Woo-Dong/wanna-gs 연결 시도는 Login Connection 누락(HTTP 400)으로 실패했다. 사용자에게 Vercel 계정 Authentication에서 GitHub를 연결하도록 안내했다. 이후 사용자가 GitHub 계정 연결을 완료했고 재시도 결과는 아래에 기록했다. 로컬 Git의 기존 원격 설정과 Vercel의 GitHub 연동은 별개다.

CLI link가 .env.local에 Vercel OIDC 토큰을 추가했다. 기존 OpenAI 필드 보존, 파일 권한 600, .env.local/.vercel의 Git 제외를 확인했다. CLI가 덧붙인 중복 ignore 규칙은 .env.example 허용을 덮지 않도록 제거했다. 계정 인증 토큰과 키 값은 출력하거나 문서에 기록하지 않았다.

OpenAI 정적 검사는 키 누락(MISSING), 실제 API 호출은 미실행이다. 앱 코드와 DB seed는 아직 없으며 배포·제품 테스트·전체 preflight를 완료하지 않았다. 이번 설정 안내와 진행 기록은 미커밋이며 commit/push하지 않았다.

설정 후 env ls에서 두 일반 설정의 대상 환경을 확인했다. 문서 정적 검사는 Markdown 73개·로컬 링크 339개·D45/CORE26/AC32와 코드 블록 검사를 통과했고 git diff --check도 통과했다. 첫 문서 수정 스크립트는 stdin 인코딩 오류로 실행되지 않아 명시적 Python 3와 UTF-8 선언으로 재실행했다. 앱 테스트 결과로 집계하지 않는다.

## Vercel GitHub 연결 재확인

2026-09-21 사용자의 계정 연결 완료 후 git connect를 재실행해 Connected를 확인했다. 최초 재시도는 세션 네트워크 제한으로 fetch failed가 발생했고 필요한 접근 권한을 받은 뒤 성공했다. Vercel 프로젝트 API의 필요한 필드만 조회해 Git provider=github, org=Woo-Dong, repo=wanna-gs, productionBranch=main을 확인했다. Next.js·Node 22.x 설정도 유지됐다.

원격 환경변수 이름은 OPENAI_MODEL·LLM_MODE이며 OPENAI_API_KEY는 아직 등록되지 않았다. 프로젝트 응답의 latestDeployments는 비어 있었고 이번 작업에서 배포를 실행하지 않았다. Git 연결 성공은 빌드·Preview 접근·실제 모델·E2E 성공과 구분한다. GitHub 연동 차단은 해소됐으며 키 주입·남은 preflight·앱 구현과 배포 검증이 남아 있다. 인증 토큰과 비밀값은 출력하지 않았고 commit/push하지 않았다.
