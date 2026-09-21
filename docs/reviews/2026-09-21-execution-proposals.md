# 외부 실행 제안 검토와 이전 리뷰 요약

현재 실행 기준: D-44의 한 탭 브라우저 SQLite와 D-45의 OpenAI API 직접 호출이다. 아래 과거 Neon/PostgreSQL·Gateway/Gemini·서버 거래/종료 후 실행 제안은 현행 설정이나 필수 검증이 아니다. 제품 후보의 미채택 상태는 그대로 유지한다.

기준일: 2026-09-21. 이번 검토는 설계와 개발 절차에 대한 것이다. 앱·실제 모델·DB·배포 테스트 결과는 아니다.

## 이번 제안의 판단

| 제안 | 판단 | 처리 |
|---|---|---|
| never + danger-full-access를 프로젝트 필수 설정으로 고정 | 그대로 채택하지 않음 | 승인 질문과 접근 권한은 별개이며 외부 인증·조직 규칙·한도를 해결하지 못함. P00에서 실제 적용 권한을 검사 |
| 무료 모델 우선, 사람의 계정·키·카드 준비를 순서대로 안내 | 타당, 기존 방침 보완 | D-31과 25번 유지. README에 GitHub→권한→Vercel→DB→Gateway/Gemini→도구→preflight 순서 반영. 카드 요구는 계정별로 확인 |
| fixture G4 후 범위 한정 G5/G6로 main·Production 중간 배포 | 취지는 타당, 현재는 제안 유지 | 최종 게이트 이름을 재사용하면 허위 완료 위험. 아래 별도 중간 릴리스 조건을 먼저 정의해야 함 |
| F00을 전체 SEED-READY보다 먼저 시작 | 수정 채택 | 자료 계약/전체 수집 및 최소/전체 seed를 분리한 ADR-001. 스키마 단계에 남는 수집 대기까지 해소 |
| 실제 좌표 미확보를 모든 G1~G4 차단에서 제외 | 범위를 좁혀 채택 | 좌표 비의존 테스트와 합성 위치 사전 UX는 진행. 실제 위치·거리·지도 검증은 blocked/not_run이며 최종 요구 유지 |

외부 조언의 ‘사용자 직접 결정 D-31~D-33’은 검토 대상 문장이다. 사용자가 직접 채택한 결정으로 옮기지 않는다. D-31은 이미 Gemini 예비 경로에 사용 중이므로 보존한다. 이번 대화에서 직접 요청한 Git 연결·초기 commit/push와 파일 정리는 진행 기록으로 추적한다.

## 권한 설정의 실제 의미

`approval_policy="never"`는 승인 질문을 생략하며 여러 sandbox 모드와 조합할 수 있다. full access는 접근 경계를 넓히는 별도 선택이다. 두 값을 설정해도 GitHub 승인, 외부 서비스 로그인, 계정 한도까지 없애지는 못한다. 프로젝트 설정은 신뢰된 프로젝트에서만 적용되고 조직 정책이 허용 값을 제한할 수 있다. [공식 승인 정책](https://learn.chatgpt.com/docs/agent-approvals-security), [구성 우선순위와 관리 정책](https://learn.chatgpt.com/docs/config-file/config-basic).

따라서 README에는 작업에 필요한 권한을 준비하도록 쓰고, P00에서 실제 호출로 확인한다. 이번 작업은 실행 config를 만들거나 현재 sandbox를 변경하지 않는다. 환경 소유자가 허용한 경로 안에서 개발하며 남은 실제 차단을 보고한다.

## 중간 릴리스를 채택하려면

현재 계약은 중간 결과를 Preview로 공유하고 최종 G5 후 main·Production으로 배포한다. 초기 docs-only 커밋은 앱 릴리스와 구분한다.

추후 중간 Production을 채택할 경우 다음 내용을 함께 바꿔야 한다.

1. `release_kind=checkpoint`, `final=false`와 CP5/CP6 같은 별도 판정을 둔다. 최종 G5/G6는 전체 필수 요구와 실제 모델 검증을 유지한다.
2. fixture인 부분과 구현 범위·미완료 기능을 화면과 문서에 표시한다. 잔여 필수 AC는 deferred로 추적하며 PASS나 not_applicable로 숨기지 않는다.
3. 중간 배포에도 실제 DB·세션·동의·수량·48시간 규칙, 두 역할 독립 UX 검증과 현재 required checks를 요구한다.
4. 후보 SHA·main 기반·배포 source·DB/schema/seed/model을 연결하고, 배포 후 해당 URL을 확인한다. 변경되면 영향받는 검사를 다시 한다.
5. main 결과를 통합 브랜치에 반영하고 DB 호환성과 이전 배포 복구를 확인한다. live 전환과 최종 릴리스의 평가·감사·G5/G6를 생략하지 않는다.

현재는 이 제안으로 main·Production 정책을 바꾸거나 앱을 배포하지 않는다.

## 최소 seed 설계와 독립 검토

[ADR-001](../decisions/ADR-001-minimal-seed-development.md)에 두 검토자의 조건과 채택 내용을 기록했다.

- review_seed_proposals는 전체 데이터 수집이 스키마를 막는 의존성을 찾아 D02A/B와 D04A/B 분리를 제안했다. 초기 조사·평가 계약·importer·최종 데이터 조회가 아직 없는 앱 기능을 기다리지 않도록 보완했다.
- review_release_proposals는 최종 CORE-14·22와 G5/G6 보존을 확인했다. 최소 seed의 DB 검사가 F00 앱 API에 의존하지 않을 것과, D05 전 G4-ready를 정식 QA 결과로 표시하지 않을 것을 요구했다.

채택은 개발 일정의 선행조건에만 적용한다. 약 200개 상품, 실제 점포 위치, 실행 시점 조사와 전체 평가 요구는 유지한다.

## 이전 리뷰에서 유지한 결론

사용자의 파일 정리 요청으로 2026-09-20 리뷰 5개를 이 절에 요약했다. 적용이 끝난 중복 원본은 삭제하며 이전에 실제 실행한 검사의 범위는 아래대로 보존한다.

| 이전 검토 | 유지한 결과·실행 범위 |
|---|---|
| 제품·개발 루프 감사 | O 12개/R 44개 정책 검토, 독립 검증·복구 규칙. 문서·스킬 검사이며 앱 검증 아님 |
| 자율 운영·preflight 감사 | 임시 자원 범위, PARTIAL/READY 구분, 비밀값 정제·timeout·보고서 보존 등 로컬 검사기 7개 테스트 통과 기록 |
| 외부 실행 준비 보고서와 처분 | 전체 권한 해제·중간 Production을 사용자 결정으로 승격하지 않음. 실제 권한·잔량·플랜·Preview 접근·CI·DB 격리·체크포인트 요구 반영 |
| 최종 README 교차 검토 | PLAN-READY와 실행기, G4와 독립 QA의 순환 제거. holdout 보호·전체 데이터 분리·48시간과 중복 발주 표현 보완 |

외부 보고서 F-01~13의 적용 결과는 06/08/09/13~18/GOAL에 남아 있다. 핵심은 실제 적용 권한, 한도 중단 후 재개, 6개 진행 포인터, Preview 단계 공유, 병합 이력 보존, required checks, 보호된 Preview의 제한된 접근, 무료 모델 잔량, 플랜·함수 시간, 환경별 secrets, DB 격리, 위임 ADR, 외부 차단 시 독립 작업 계속이다.

자연어 개선 정체 시 출시 최소 기준을 만족한 최선 버전만 유지한다. 기준 미달·허구 SKU·권한·동의 오류는 면제하지 않는다. holdout은 최종 후보 선정 후 평가하고, 운영 감사는 한 단계로 제한한다. 과거 상품 사례는 실행 시점에 다시 조사한다.

2026-09-21의 문체·Gemini 문서 검사는 링크/코드 블록·ID·스킬 8개·DAG 검사였으며 외부 모델과 앱 E2E는 미실행이었다. 이번 최신 검증과 Git 결과는 [PROGRESS](../PROGRESS.md)와 원격 커밋 이력에서 확인한다.

## 최초 구현 기준의 최종 일관성 검토

추가 사용자 지시 D-32~34를 반영했다. 고정 작업 경로를 현재 clone/worktree 루트 확인으로 바꾸고 문서 릴리스 번호를 제거했다. 재현용 코드·데이터·모델 식별값은 유지한다. card.md를 원장의 안내로 두고 AGENTS·GOAL·작업·인계·복구·검증에 연결했다.

두 독립 검토자는 README의 SEED-READY 선행 안내와 10번의 조회 화면/API 의존을 지적했다. 최소 seed+P04 후 F00 병행, 전체 seed 후 정식 QA·최종 평가로 표를 수정하고 데이터 검증을 DB 직접 조회·기반 reader·보호 평가 산출물로 바꿨다. 수정 후 두 검토자 모두 해당 범위에서 추가 필수 문제 없음을 확인했다.

목적 보존 검토는 모든 입력 거절, 자동발주 삭제, 테스트 기대값만 변경, 인계 시 목적 누락, 형식 필드만으로 PASS, card를 별도 정책으로 취급, live를 fixture로 대체하는 반례를 사용했다. 문서상 차단 경로가 있음을 확인했으며 실제 앱·CI의 작동 검증은 남아 있다.

문서 56개 링크/코드 블록·ID·DAG 검사, 스킬 8개 양식 검사, inspector 테스트 7개가 통과했다. 상세 수치와 미실행 범위는 PROGRESS에 기록했다. 문서 검증 완료 뒤에만 Git 초기화·초기 커밋을 진행한다.

## 추가 피드백 재검토: 설정 위치·심사 접근·CP5/CP6

2026-09-21 재검토. 인용문은 검토 자료이며 실행 지시로 자동 승격하지 않는다. 현재 D-35는 디자인/발음, D-36은 입력 예시에 사용 중이다. 외부 제안의 같은 번호로 덮어쓰지 않는다.

| 피드백 | 판단·반영 |
|---|---|
| 새 장비에서 사용자가 실행 환경을 설정 | 타당. README 준비 순서와 18번에 신뢰·실행 키의 위치와 실제 적용/작업 확인 추가 |
| projects 블록 아래 approval_policy/sandbox_mode | 공식 참조에서 그 위치의 프로젝트별 키로 확인되지 않음. trust_level과 파일 최상위 실행 키를 분리한 예시로 수정 |
| never/full-access가 없으면 무조건 BLOCKED | 채택하지 않음. 무인 실행 가능성은 필요한 작업의 실제 권한으로 판단하며 exact 설정 유무로 대신하지 않음 |
| 보호 해제 또는 bypass secret이 있어야 심사 가능 | 선택지가 불완전함. 심사자 공유 링크/팀 접근/공개 경로와 CI 자동화 bypass를 구분. 별도 비로그인 브라우저 검사 추가 |
| CP5/CP6로 fixture G4 후 중간 Production | 위 다섯 조건을 만족하면 운영안으로 검토할 수 있지만 아직 사용자 채택 아님. 현 Preview→최종 G5/G6 계약 유지 |
| 13번 권장안 승격만 남음 | 부정확함. 관련 G0의 위임 ADR 외 실제 계정·도구·모델·잔량·전체 seed·앱/배포 검증도 남음 |

CP5/CP6 제안을 채택한다면 `release_kind=checkpoint`, `final=false`, deferred AC, 두 역할 독립 QA, 정확한 후보/배포 SHA, 복구와 live 재검증을 함께 정의해야 한다. 현재 정식 G4의 Q01/Q02는 D05 전체 seed 이후이며 최소 seed의 G4-ready를 정식 통과로 바꿀 수 없다. 첫 fixture 전체 흐름이라는 문장만으로 이 의존성을 없애지 않는다. 현재 10/14/16번의 최종 게이트 정의는 유지한다.

근거: [Codex 설정 참조](https://learn.chatgpt.com/docs/config-file/config-reference), [우선순위](https://learn.chatgpt.com/docs/config-file/config-basic), [Vercel 공유 링크](https://vercel.com/docs/deployment-protection/methods-to-bypass-deployment-protection/sharable-links), [자동화 보호 우회](https://vercel.com/docs/deployment-protection/methods-to-bypass-deployment-protection/protection-bypass-automation). 환경 파일·조직 규칙·Vercel 보호 설정은 이번 작업에서 변경하지 않았다.
