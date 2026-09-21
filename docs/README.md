# 원하GS (WANNA GS): 설계 문서

기준일: 2026-09-21 · 최초 구현 기준 · 상태: goal 구현·검증 진행 중

## 프로젝트 한 문장

고객의 자연어 상품 요청을 점포별 수요로 모으고, 경영주의 일괄 판단과 보수적인 자동발주를 거쳐, 확보된 물량을 모의 자동 결제·픽업 예약으로 연결하는 랄프톤 프로토타입.

이 문서 묶음은 지금까지의 사용자 논의를 실행 가능한 설계로 정리한 것이다. 실제 GS 서비스·상품·재고·발주·결제 시스템과 연결하지 않는다. Vercel 프로젝트 생성·로컬 연결과 기본 설정은 마쳤다. 고객/경영주 앱·248상품 SQLite seed·실제 LLM 경로와 CI를 구현했다. 자연어 품질 개선과 최종 배포 검증은 진행 중이며 현재 상태와 실패 증거는 [PROGRESS](PROGRESS.md)에서 관리한다.

## 가장 먼저 알아야 하는 결정

- 고객 입력은 자연어만 구현한다. 사진·링크·레시피·여러 상품 묶음은 제외한다.
- 고객이 상품을 확인한 뒤 수량·점포·가격·자동 구매 조건을 확인하고 요청한다.
- 물량 확보 후 접수 순서로 배정하고 모의 자동 결제한다. 이전의 ‘픽업할게요를 눌러 구매 확정’ 흐름은 폐기했다.
- 픽업 가능 알림 생성 시각부터 정확히 48시간 안에 수령한다. 발주일이나 예약일 기준이 아니다.
- 경영주는 건별 검토 대신 요약·그룹·자연어 지시로 관리한다.
- 자동발주는 사전 승인된 규칙 안에서만 실행하고, 고객 요청 수량을 초과하지 않는다.
- 본부용 화면·기능은 구현하지 않는다. 향후 사업 가치로만 설명한다.
- 배포 목적지는 Vercel이다. 권장 기준선은 Next.js + 브라우저 SQLite + OpenAI API 직접 호출이다. 사용자 키는 서버에만 둔다.
- Vector RAG는 검색 품질을 비교할 선택 실험이다. 핵심 완료 조건에 자동으로 포함하지 않는다.

## 읽는 순서

| 순서 | 문서 | 용도 |
|---|---|---|
| 1 | [01-product-scope.md](01-product-scope.md) | 문제 가설·제품 목적·필수 및 제외 범위 |
| 2 | [02-decisions-and-open-questions.md](02-decisions-and-open-questions.md) | 확정·제안·미정·폐기 결정 구분 |
| 3 | [03-user-journeys-and-states.md](03-user-journeys-and-states.md) | 고객·경영주 흐름과 상태 전환 |
| 4 | [04-business-rules.md](04-business-rules.md) | 발주·배정·금액·기한·중복 방지 규칙 |
| 5 | [05-agents-and-search.md](05-agents-and-search.md) | 두 에이전트의 역할·도구·검색·RAG |
| 6 | [06-system-architecture.md](06-system-architecture.md) | FE/BE/DB/LLM 실행 경계 |
| 7 | [07-data-and-api.md](07-data-and-api.md) | 데이터 모델·API 계약 초안 |
| 8 | [08-environment-and-deployment.md](08-environment-and-deployment.md) | 계정·권한·DB·배포 운영 준비 |
| 9 | [09-verification-and-evals.md](09-verification-and-evals.md) | 인수 기준·단위/통합/E2E·LLM 평가 |
| 10 | [10-implementation-plan.md](10-implementation-plan.md) | 의존성별 구현 단계 |
| 11 | [GOAL.md](GOAL.md) | 준비 단계·본 구현 `/goal` 예문과 완료 계약 |
| 12 | [11-research-and-references.md](11-research-and-references.md) | 외부 사례·공식 출처·자료 한계 |
| 13 | [12-demo-and-copy.md](12-demo-and-copy.md) | 데모·카피·향후 가치 |
| 14 | [13-review-checklist.md](13-review-checklist.md) | 56개 검토 항목·담당·우선순위·권장안 |
| 15 | [14-agent-development-loop.md](14-agent-development-loop.md) | 영역별 서브 에이전트·G0~G6 검증·자동 검증 장치 설계 |
| 16 | [15-failure-recovery.md](15-failure-recovery.md) | 오류 분류·재현·제한 재시도·복구·회귀 검사 |
| 17 | [16-git-and-release-workflow.md](16-git-and-release-workflow.md) | GitHub branch·commit/push·PR·CI·배포 |
| 18 | [17-autonomous-decisions.md](17-autonomous-decisions.md) | 위임 정책·복수 검토·최종 빈틈 감사 |
| 19 | [18-environment-preflight.md](18-environment-preflight.md) | goal 전 사전 설정·연동 테스트·결과 판정 |
| 수시 | [PROGRESS.md](PROGRESS.md) | 작업 상태·검증 증거·다음 단계 |

프로젝트 전체 개발 규칙은 [루트 AGENTS.md](../AGENTS.md), 문서 세부 규칙은 [docs/AGENTS.md](AGENTS.md)에 있다. `/goal`에서는 이 README와 GOAL 문서를 명시적으로 읽도록 한다. 검증·복구 프로젝트 스킬은 [.agents/skills](../.agents/skills/wanna-gs-verify/SKILL.md)에 있다. 자동 실행기와 CI의 현재 실행 범위는 PROGRESS와 quality/gates.json에서 확인한다.

## 확정 여부와 문서 우선순위

1. 사용자의 최신 명시적 결정.
2. 결정 기록의 확정 항목.
3. 제품 범위·업무 규칙·인수 기준.
4. 기술 기준선과 구현 제안.
5. 참고 사례·외부 문서.

`사용자 확정`은 직접 지시, `에이전트 채택`은 위임된 ADR·복수 검토를 거친 정책, `기술 기준선`은 추천안, `제안`은 채택 전 기본값이다. `미정`은 실행 시 자율 결정할 항목이며 사람 답변 대기를 뜻하지 않는다. 문서의 구체적인 필드·API 이름은 사용자 요구를 충족하기 위한 구현 초안이지 모두 별도로 승인된 사항은 아니다.

## 운영 방법

- 사용자 추가 정의는 02에 기록한다. 위임 정책은 기존 CORE/DECISION_INDEX 확인→proposed ADR→두 독립 검토→채택→index·명세·테스트 동기화 순서로 관리한다.
- 영향을 받는 업무 규칙·상태·API·테스트를 함께 수정한다.
- 완료 표시에는 실행 증거를 연결한다.
- 외부 요금·무료 모델·계정 권한은 계정 연결 시 재확인한다.
- 이 저장소가 앞으로의 설계 기준이다. 채팅 기억이나 다른 폴더의 초안을 우선하지 않는다.
- 작업 경로는 현재 clone 또는 worktree의 루트다. `git rev-parse --show-toplevel`로 확인하며 특정 사용자 홈 경로나 폴더 이름을 가정하지 않는다. 명령의 상대 경로는 모두 그 루트를 기준으로 한다.

## 현재 다음 단계

사전 설정 → preflight 스킬로 실제 연동 점검 → 단일 goal → 필요한 정책 자율 채택 → 구현·테스트·단계별 commit/push/PR·통합 → 최종 감사·배포 검증. 이번 문서 작성은 목표 실행이 아니며 유료 구매는 포함하지 않는다.

## 검토와 개발 방식

사용자 요청에 따라 영역별 구현·자체 단위 테스트 → 독립 검증 → 단계적 통합·재검증을 개발 규칙으로 추가했다. 단계별 자동 검사와 코드 지문·독립 리뷰 검사를 구현했다. 현재 통과한 단계가 최종 G5/G6 통과를 뜻하지 않는다. 제품 정책 검토는 13번, 역할·게이트는 14번, 실패 복구는 15번을 읽는다. [작업 계약](templates/task-contract.md), [게이트 보고서](templates/gate-report.md), [실패 보고서](templates/failure-report.md)를 재사용한다.

이 기준에서는 위 항목을 사람 의논 대기 대신 에이전트 정책 결정·검증 작업으로 처리한다. 이전 권장안은 출발점이며 채택 여부는 ADR로 추적한다.

## 사전 설정과 스킬 사용

빠른 시작은 [루트 README](../README.md), 상세 설정·실제 시험 범위는 [18번](18-environment-preflight.md)이다. `$wanna-gs-preflight`의 inspect는 로컬/인증 관찰, live는 임시 GitHub·CI·Preview·DB·모델·브라우저·에이전트 시험이다. 부족한 설정을 한 번에 보고한 뒤 GOAL의 단일 실행 문장으로 개발한다. 실제 Production은 기본 사전점검에서 변경하지 않으며 미검증 릴리스 조건을 보고서에 남긴다.

## 실행 중심 문서

처음에는 [핵심 요구](CORE_REQUIREMENTS.md), [현재 유효한 결정](DECISION_INDEX.md), [작업 계획](WORKPLAN.md)을 함께 읽는다.

| 문서 | 목적 |
|---|---|
| [19 데이터 조사·seed](19-data-research-and-seeding.md) | 200개 이상 상품·실제 점포 위치·합성 사용자·반복 가능한 DB 삽입 |
| [20 역할·공유 컨텍스트](20-agent-roles-and-context.md) | 고객/경영주 UX·FE·BE·DBA·QA 책임, 버전/ACK와 모델 선택 |
| [21 UX·자연어 품질](21-ux-and-natural-language-quality.md) | 별도 사용자 관점 QA, 범주별 eval·독립 holdout |
| [22 에이전트 운영 감사](22-orchestration-audit.md) | 운영 규칙의 모호함/비효율 검증, 제한된 개선 시험 |
| [23 자연어 실험 루프](23-nl-experiment-loop.md) | 기준선→후보→평가→채택, 개선 정체/한도 중단 |
| [24 실행 시점 조사·시나리오](24-market-research-and-scenario-design.md) | 최신 니즈·시장·기능별 근거→설계·데이터·테스트 추적 |

goal 시작과 기능별 설계 시 에이전트가 최신 근거를 조사한다. 대화에 나온 상품은 조사 후보로 다루고, 조사 결과에 따라 데이터와 평가 범위를 정한다. 데이터 생성·실험 실행기·CI 구현은 초기 개발에 포함한다.

추가 스킬: [조사](../.agents/skills/wanna-gs-research/SKILL.md), [독립 UX QA](../.agents/skills/wanna-gs-ux-audit/SKILL.md), [자연어 실험](../.agents/skills/wanna-gs-nl-experiment/SKILL.md), [운영 감사](../.agents/skills/wanna-gs-orchestration-audit/SKILL.md).

[25 OpenAI API 설정·검증·사용량](25-openai-api-and-budget.md): 사용자 키의 로컬/Vercel 입력 위치, dotenv 양식과 실제 연결 검사. D-45·CORE-23·AC-29에 연결한다.

## 문서 기준과 작업 카드

현재 문서 묶음을 최초 구현의 기준으로 사용한다. 문서 릴리스 번호는 붙이지 않으며 Git 이력·사용자 결정·ADR로 변경을 추적한다. 재현에 필요한 schema/seed/model/eval revision·hash는 유지한다. 시작·인계·복구 때 [card.md](../card.md)를 읽고 사용자 목적과 관련 CORE를 작업 계약·검증 증거에 연결한다.

## 디자인과 브랜드

[26 디자인·브랜드 가이드](26-design-and-brand-guide.md)는 사용자 제공 이미지와 우리동네GS 공식 앱 소개 화면을 참고한 구현 기준이다. 이름은 `원하GS`, 발음은 `원하지쓰`이며 화면에 읽는 법을 보이게 한다. 12번 카피와 함께 읽고 D-35·CORE-24·AC-30으로 구현·QA에 연결한다. 첨부 그림은 디자인 참고이며 제외 기능을 추가하는 명세가 아니다.

[27 서비스 가치·불편 방지](27-service-values-and-guardrails.md)는 D-37/43·CORE-25/26·AC-31/32를 구현·회귀 검사에 연결한다. D-36/38의 입력 예시·캐릭터는 26번에 있다. 니즈/추천/거래의 구분, 상품→고객 상세 근거, 경영주 업무 감소, 본부 데이터의 향후 가치를 원장과 함께 유지한다.

## 참고 시안과 팀원 검토 자료

최종 이미지는 26번의 코드 구현 매핑과 브라우저 비교에 사용한다(D-39). [리뷰 목록](reviews/README.md)의 팀원 자료는 실행 명세가 아니다. [경영주 자료 검토](reviews/2026-09-21-merchant-handoff-review.md)의 반영 후보는 D-40에 따라 사용자가 선택하기 전까지 미채택으로 유지한다.

[28 Neon 계정 이후 연결](28-neon-setup-guide.md)은 D-44 이전의 과거 안내다. 현재 goal의 설치·연결 대상이 아니다. [29 브라우저 SQLite 데모](29-browser-sqlite-demo.md)가 현재 데이터 생성·저장·배포·복원·검증 기준이다.

경영주 자료 재검토에서 D-41/42/43은 사용자 직접 결정으로 반영했다. 모집 목표 초과 접수를 유지하고 기한 결합으로 인한 잘못된 자동 구매·입고 전 수령 만료를 금지하며, 상품별 수요에서 고객별 요청 상세로 내려가는 읽기 전용 확인을 제공한다. 나머지 M 후보는 검토 보고서의 권고이며 미채택이다.
