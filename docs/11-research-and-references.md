# 조사 근거·사례·추가 확인

문서 기준일: 2026-09-20. 아래는 대화 중 열람한 공식 문서와 참가자 회고를 요약한 것이다. 계정 권한·현재 가격·지원 모델은 실행 시 다시 확인한다. 이번 문서화 과정에서 모든 출처를 새로 재검증한 것은 아니다.

## 공식 기술 자료

| 주제 | 출처 | 적용점·한계 |
|---|---|---|
| Goal | [Using Goals in Codex](https://developers.openai.com/cookbook/examples/codex/using_goals_in_codex) | 완료 조건을 실제 증거로 정의. 설치 환경의 지원 여부 별도 확인 |
| Next.js FE/BE | [Backend for Frontend](https://nextjs.org/docs/app/guides/backend-for-frontend) | 화면과 서버 API를 한 프로젝트에서 운영 |
| Vercel 함수 | [Functions](https://vercel.com/docs/functions) | 서버 메모리를 영구 상태로 삼지 않고 DB 사용 |
| 함수 제한 | [Functions limits](https://vercel.com/docs/functions/limitations) | 버전·플랜의 실행 시간·번들 제한 확인 |
| DB 설치 | [Vercel integration CLI](https://vercel.com/docs/cli/integration) | 리소스 생성·연결·환경변수 동기화 |
| Neon 통합 | [Neon skills in Vercel CLI](https://neon.com/blog/neon-skills-landed-in-the-vercel-cli) | Vercel에서 Neon 계정/DB 생성 경로, 실제 권한 별도 |
| Neon 무료 | [Neon Free plan 안내](https://neon.com/blog/how-to-make-the-most-of-neons-free-plan) | 무료 리소스 조건은 실제 연결 계정 기준으로 확인 |
| pgvector | [Neon 확장 안내](https://neon.com/blog/ten-most-popular-postgres-extensions) | PostgreSQL 안에서 관계형 데이터와 벡터 관리 가능 |
| Supabase 비교 | [Pricing](https://supabase.com/pricing) | 대안. 무료 비활성 중지·백업 제한을 비교 |
| Gateway 가격 | [Pricing](https://vercel.com/docs/ai-gateway/pricing) | 조사 시 월 $5·일부 모델·별도 호출 한도. 전체 무료 아님 |
| Gateway 인증 | [Authentication](https://vercel.com/docs/ai-gateway/authentication-and-byok) | 배포 OIDC/로컬 키 등 지원 경로 검증 |
| 임베딩 | [Gateway Embeddings](https://vercel.com/docs/ai-gateway/modalities/embeddings) | 기능 지원과 무료 모델 사용 가능 여부는 다름 |
| Cron | [Usage and Pricing](https://vercel.com/docs/cron-jobs/usage-and-pricing) | 조사 시 Hobby 하루 1회·시간 단위. 48시간 경계는 DB 비교 |
| 배포 | [Deploy from CLI](https://vercel.com/docs/projects/deploy-from-cli) | Preview·Production·환경변수·검증 흐름 |
| 인증 | [Vercel CLI](https://vercel.com/docs/cli) | 계정 존재와 CLI 인증 구분 |
| ChatGPT/API 과금 | [OpenAI billing](https://help.openai.com/en/articles/9039756) | Workspace 권한이 일반 API 무료권을 뜻하지 않음 |
| Enterprise 계약 | [Token-based billing](https://help.openai.com/en/articles/20001520) | 계약별 API 포함 여부는 관리자가 확인 |
| Codex 토큰 | [Access tokens](https://learn.chatgpt.com/docs/enterprise/access-tokens) | Codex 자동화 토큰과 일반 API 키 구분 |
| Workspace Agents | [Trigger runs](https://learn.chatgpt.com/workspace-agents/trigger-runs) | 조사 시 응답 본문 API 조회 미지원. 실시간 추론 기본안 제외 |

가격·모델·서비스 조건은 공식 페이지의 현재 본문을 우선한다. 검색 요약과 페이지 본문이 다르면 오래된 검색 요약에 의존하지 않는다. 무료 한도 소진을 우회하기 위한 다중 계정 생성은 대안으로 삼지 않는다.

## 랄프톤과 장시간 에이전트 사례

### 랄프톤 공개 소개

[Ralphthon](https://ralphthon.org/)은 자율 실행과 사람의 개입, 실행 증거를 강조한다. 다만 회차별 시간·평가·배포·개입 규칙은 해당 행사 안내를 확인해야 한다. 원하GS의 ‘Vercel 제출’은 이번 사용자 제공 조건이다.

### Resend 복제 사례: 성공과 사람 개입을 함께 봐야 함

[참가자 Ashley Ha의 회고](https://ashleyha.com/posts/software-is-becoming-reproducible)는 랄프톤 서울 2위와 이메일 발송 등의 구현을 보고한다. 동시에 약 5시간 뒤 56개 중 약 40개 기능이 끝났고 발표 전 사람이 QA·수정을 했다고 설명한다. 이후 저장소의 개선 결과와 대회 당시 결과를 혼동하지 않는다.

적용: 목표 제품을 관찰해 인수 기준을 만들고 기능별 구현·검증을 반복한다. ‘자율 몇 시간’보다 실제 완성 범위와 수동 개입을 기록한다.

### Writing First 연구 사례: 결과물과 실패 대안을 먼저 설계

[참가자 Byungjun Yoon의 회고](https://byungjunyoon.ai/writing-driven-autoresearch/)는 AI Scientist 트랙 1위를 보고한다. 제출물 구조와 필요한 증거를 먼저 정하고, 초기 가설이 반박됐을 때 근거에 따라 방향을 바꾸는 설계를 설명한다.

적용: 원하GS도 데모·인수 기준을 먼저 정한다. 실험이 실패하면 검색/모델/구조를 수정하고, 가짜 성공 결과를 만들지 않는다. 이 사례는 참가자 보고이며 우리가 재현한 결과가 아니다.

### 장시간 코딩의 실패: 너무 많이 시도하고 일찍 완료 선언

[Anthropic의 long-running harness 연구](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)는 과도한 일괄 구현, 다음 세션에 불명확한 상태 인계, 충분한 검증 없이 완료 선언하는 문제를 설명한다.

적용: 작은 작업, 진행 기록, Git 이력, 실제 브라우저 테스트를 사용한다. 컨텍스트가 길다는 이유만으로 일관된 작업을 보장하지 않는다.

### 화면 존재와 작동은 다름: 비용도 비교

[Anthropic의 앱 개발 harness 실험](https://www.anthropic.com/engineering/harness-design-long-running-apps)은 게임 제작 앱에서 화면은 있지만 게임 입력이 동작하지 않는 사례와 평가 루프의 개선을 비교한다. 해당 비교에서 실행 시간과 비용도 크게 늘었다.

적용: 여러 에이전트를 추가하는 것 자체를 목표로 하지 않는다. 검증 결과와 실행 비용으로 구조를 선택한다. 타사의 비용 수치를 원하GS 예상 비용으로 사용하지 않는다.

### 로컬 검증과 실제 연동은 다름

[ReviewHarness 공개 저장소](https://github.com/procloudkim/Ralphthon-ICML-2026-Track2)는 로컬 완료와 실제 행사/외부 제공자 미검증을 분리한다.

적용: fixture 모드, 실제 DB, 실제 LLM, 최종 URL의 검증 상태를 별도로 기록한다. 로컬 테스트 통과를 전체 배포 성공으로 확장하지 않는다.

## 추가 조사 목록

| 질문 | 필요 시점 | 판단에 쓸 근거 |
|---|---|---|
| 실제 GS의 요청·예약·재고 기능 범위는? | 최종 제안서의 문제 표현 확정 전 | 공식 서비스 안내·실사용·담당자 확인 |
| 행사에서 허용되는 모델·외부 무료 서비스는? | M0 이전 | 주최 측 안내 |
| 제공 Workspace 외 API 크레딧이 있는가? | M0 이전 | 관리자/주최 측 답변 |
| Vercel/Neon 실제 무료 리소스·권한은? | M0 | 계정 내 사용량·플랜 |
| 한국어 후보 검색·경영주 지시 품질은? | M3/M4 | 고정 평가 세트 |
| 벡터 검색이 개선되는가? | 선택 M7 | 동일 사례의 비교 실행 |

## 주장 기록 형식

```text
주장/결정:
출처 또는 실행 증거:
확인일:
확인된 범위:
추정/미확인 범위:
설계에 반영할 내용:
```

## 조사·평가 참고 (2026-09-20 확인)

- [머니투데이: 민음사빵 탐색·품절 사례, 2026-09-08](https://www.mt.co.kr/amp/society/2026/09/08/2026090709475845306): 사용자·점주 사례가 포함된 초기 조사 후보. 여러 점포 탐색, 재고 표시 차이, 무작위 구성품 니즈를 시나리오로 검토한다. 해당 시점 보도이지 현재 점포 재고 증거가 아니다.
- [이투데이: 민음사 빵, 어디 있나요?, 2026-08-26](https://www.etoday.co.kr/news/view/2618139): 상품 구분과 재고 탐색 맥락 참고. 기사 원문을 평가 발화로 복제하지 않는다.
- [OpenAI evaluation best practices](https://developers.openai.com/api/docs/guides/evaluation-best-practices): 목표·데이터·평가·비교를 정의하는 참고. 별도 유료 평가 서비스를 필수로 하지 않는다.
- [Playwright best practices](https://playwright.dev/docs/best-practices): 사용자에게 보이는 동작·격리·안정적인 locator와 assertion 참고.
- [Codex Subagents](https://learn.chatgpt.com/docs/agent-configuration/subagents): 역할/작업에 맞는 모델·추론 설정 참고. 실제 사용 가능한 모델/도구가 우선이다.

이 목록은 출발점이다. goal 실행 때 24번 조사 에이전트가 필요한 최신 근거를 직접 확인하고 채택/기각과 설계·테스트 연결을 기록한다. 유행 사례의 존재는 원하GS가 이미 사용자 효과를 입증했다는 뜻이 아니다.

## 2026-09-21 모델 예비 경로 조사

[25번](25-model-budget-and-fallback.md)에 공식 모델 종료 안내, Gemini 요금·호출 제한, Gateway 잔액 API 근거를 정리했다. 모델·가격 확인과 실제 사용자 계정 접근 검증은 구분한다.
