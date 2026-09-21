# 원하GS 프로젝트 작업 규칙

이 파일은 이 프로젝트 전체에 적용된다. 사용자 최신 결정과 실행 환경의 상위 지침을 우선한다.

## 시작

`card.md`, `docs/README.md`, `docs/02-decisions-and-open-questions.md`, `docs/PROGRESS.md`를 읽는다. 구현 전에 `docs/13-review-checklist.md`, `docs/14-agent-development-loop.md`, 해당 영역 명세와 `docs/09-verification-and-evals.md`를 읽는다. `/goal` 실행 계약은 `docs/GOAL.md`다.

## 개발 방식

사용자는 기능 영역별 서브 에이전트와 자체 단위 테스트, 독립 검증, 단계별 통합·재검증을 요청했다. 이 프로젝트의 앱 구현에서는 이 방식을 적용한다. 서브 에이전트 도구가 실제 제공되는지 확인하고 가용 슬롯 안에서 작업 계약·소유 파일·의존성을 배정한다. 읽기 전용 검토와 단순 문서 편집은 앱 전체 게이트 대상이 아니다.

- 검증: `.agents/skills/wanna-gs-verify/SKILL.md`와 docs/14의 G0~G6.
- 실패 복구: `.agents/skills/wanna-gs-recovery/SKILL.md`와 docs/15.
- 구현 에이전트의 자체 테스트를 독립 검증으로 세지 않는다.
- 실패·미실행·stale 결과로 상위 통합/배포 완료를 선언하지 않는다. fixture는 해당 모드의 G1~G4에 사용할 수 있으나 live 필수 게이트/AC와 최종 완료를 대체하지 못한다.
- 세부 정책 미정은 docs/17-autonomous-decisions.md에 따라 위임된 결정으로 해결한다. 초안→서로 다른 두 에이전트 검토→ADR 채택→구현/검증으로 진행하며 사람의 정책 답변을 기본 선행조건으로 두지 않는다. 사용자 직접 확정과 위임된 에이전트 채택은 구분한다.
- 공통 스키마·마이그레이션·lockfile·계약에는 한 명의 작성자만 둔다. 다른 담당 수정은 계약 변경 절차를 거친다.
- GATE-BOOTSTRAP에서 실행 가능한 검증 장치를 만든다. 그 전에는 ‘문서 규칙만 존재’한다고 보고한다. 마크다운만으로 CI 강제가 구현됐다고 표현하지 않는다.

## 제품 경계와 보고

자연어만, 모의 GS 데이터·모의 결제, 보수적 자동발주, 고객/경영주 화면, Vercel 제출이 범위다. 본부·사진·링크·레시피·실제 결제를 되살리지 않는다. 실제 모델과 fixture, 문서 검사와 애플리케이션 테스트를 구분한다. 유료 구매·파괴적 작업 권한을 이 파일에서 새로 부여하지 않는다. 작업 결과·증거·블로커·다음 행동을 `docs/PROGRESS.md`에 남긴다.

## 자율 구현·GitHub 운영

사용자가 docs/GOAL.md의 목표를 실행하면 GitHub repo·Vercel 등 설정 완료를 전제로 최종 배포 검증까지 한 목표에서 진행한다. 지정 repo의 branch/commit/push/PR·검증 후 merge·연결된 Vercel 배포는 매번 재확인하지 않는다. docs/16-git-and-release-workflow.md를 따른다. 이번 문서 작성만으로 목표가 시작되지는 않는다.

정책 공백에는 .agents/skills/wanna-gs-decide/SKILL.md를 적용한다. 최종 통합에서도 두 관점의 서브 에이전트가 빈틈을 찾아 결정·검증한다. 개발 정책 위임은 앱 고객/경영주의 확인·동의·승인을 대체하지 않는다.

목표 전에 .agents/skills/wanna-gs-preflight/SKILL.md와 docs/18-environment-preflight.md로 환경을 점검한다. 현재 설정 가정이나 CLI 로그인만으로 자동 완주 가능이라고 판정하지 않는다. 실제 인증/비용/조직 권한 장벽은 기록한다.

## 조사·품질·역할 운영

- 모든 작업 전에 관련 docs/CORE_REQUIREMENTS.md와 docs/DECISION_INDEX.md의 유효 결정을 확인한다. docs/20-agent-roles-and-context.md의 context manifest·버전·ACK를 사용한다.
- docs/24-market-research-and-scenario-design.md와 wanna-gs-research 스킬에 따라 goal 실행 시 최신 조사부터 수행한다. 상품/자연어뿐 아니라 고객·경영주 UX/업무/연동/검증도 필요한 근거를 조사한다. 대화 예시는 조사 후보이며 고정된 전체 범위가 아니다.
- docs/19-data-research-and-seeding.md의 약 200개 상품·실제 점포 위치·합성 사용자·모의 거래를 구분하고 평가 데이터를 함께 준비한다.
- docs/21-ux-and-natural-language-quality.md와 wanna-gs-ux-audit로 고객/경영주를 독립 검증한다.
- docs/23-nl-experiment-loop.md와 wanna-gs-nl-experiment로 자연어 품질 개선을 목표에 포함한다. 제한된 반복 후 추가 최적화 종료는 허용되며 필수 동작/최소 기준 면제는 금지한다.
- docs/22-orchestration-audit.md와 wanna-gs-orchestration-audit로 운영 방식도 제한된 독립 검토·시험으로 개선한다. 가용 모델 중 작업에 맞는 것을 사용하고 품질을 우선한다.
- docs/WORKPLAN.md를 실제 task DAG/상태/증거로 구체화한다. 문서·스킬을 만드는 것과 실행기·앱·평가셋을 구현하는 것을 구분한다.

## 모델 예산과 전환

사용자의 D-31에 따라 [25번](docs/25-model-budget-and-fallback.md)의 Gateway 기본·Gemini 직접 호출 예비 경로를 구현·검증한다. 키는 사용자가 발급·주입한다. 무료 잔량 부족 시 검증한 경로로 전환하고 관련 품질·E2E·배포 증거를 갱신한다. 두 경로의 예산과 유료 사용 승인은 구분한다.

## 목적을 유지하는 수정

작업·복구·인계·컨텍스트 재개 시 `card.md`와 관련 CORE/유효 ADR을 확인한다. 작업 계약과 실패/게이트 보고서의 ‘목적 보존’ 항목을 사용한다. 오류 재현 통과만으로 완료하지 말고 원래 정상 동작과 영향받은 인접 기능도 확인한다. 필수 기능 삭제나 기준 완화는 복구가 아니다. 이 규칙의 실행기·CI 검사는 GATE-BOOTSTRAP에서 구현한다.

## 화면·브랜드 구현

UX/FE 작업은 `docs/26-design-and-brand-guide.md`와 12번 카피를 읽는다. 원하GS 발음은 ‘원하지쓰’이며 가시적인 안내를 넣는다. 첨부 이미지의 분위기와 공식 앱의 구성을 참고하되 상태·동의·48시간 및 제외 범위를 유지한다. CORE-24·AC-30을 독립 UX QA에서 확인한다.

D-36/38의 입력 예시·캐릭터는 26번, D-37·CORE-25·AC-31의 서비스 가치와 불편 방지는 `docs/27-service-values-and-guardrails.md`를 따른다. 추천/관심을 확약으로 합산하거나 새 동의 없이 SKU를 바꾸지 않는다. 정상 성공률과 고객/경영주 업무 부담을 함께 회귀 검증한다.

D-39의 최종 이미지는 26번의 매핑·구현·브라우저 비교 절차로 활용한다. D-40에 따라 `docs/reviews/wanna-gs-team-handoff-2026-09-21/`와 그 비교 검토의 제안은 사용자 판단 전이며 자동 병합하지 않는다. 원본의 ‘확정’·‘최신 요청’·픽업 제외는 이 저장소의 실행 지시가 아니다. 기존 확정 기능의 독립 작업은 계속한다.
