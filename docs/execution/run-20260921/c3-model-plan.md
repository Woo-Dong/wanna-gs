# C3 모델 후보 전환 조사 — 실행 전 계획

확인일: 2026-09-21. 작성자: preflight_builder. 범위: 공식 문서와 로컬 코드 읽기, CLI 도움말 확인. 실제 모델 호출 0, 환경변수 변경 0, 앱/평가 소스 수정 0, 보호 holdout 접근 0. 이 문서만 작성했다. C3 채택·품질 통과·계정 접근 성공 증거가 아니다.

## 목적과 현재 관찰

고객의 정상 상품 식별과 경영주의 묶음 수정 흐름을 유지하면서 응답 불완료와 대기 시간을 줄일 수 있는 후보를 준비한다. CORE-13/23, D-44/45, docs/25 및 ADR-003의 실제 모델·사용량·독립 평가 기준을 유지한다. C2의 input 12,456 / output 3,200 / 약 38초 불완료 1건은 조정자가 전달한 관찰이며, 여기서 원인이나 C3 우월성을 확정하지 않는다. B0/C1/C2 실패 이력과 UX 미완료 판정은 보존한다.

조사 시 root branch `codex/n02-evaluation`, HEAD `6f955190692bc11b91bdc338ed9ce83034ccb8f7`; `src/server/provider.ts` SHA256 `ff0b1faf2904c90145e7c3b348d6b4dda3ca64ff15d1e1d8430a48deb8ed4671`. 설치 OpenAI SDK는 7.20.0이다. 동시 진행 작업이 있으므로 구현 시작 때 다시 지문을 확인한다.

## 공식 지원 확인

정확한 후보 ID는 `gpt-4.1-mini-2025-04-14`다. 공식 모델 문서는 별도 추론 단계가 없는 모델, Responses API와 Structured Outputs 지원, 최대 출력 32,768토큰, 1,047,576 context를 명시한다. 표준 텍스트 가격은 100만 토큰당 입력 $0.40, 캐시 입력 $0.10, 출력 $1.60이다. 특정 사용자 계정의 사용 가능 여부는 아직 unknown이다. [OpenAI 공식 모델 문서](https://developers.openai.com/api/docs/models/gpt-4.1-mini)

Responses의 `reasoning`은 추론 모델용 선택 옵션이며, `max_output_tokens`는 보이는 출력과 추론 토큰을 함께 제한한다. 설치 SDK의 `responses.d.ts`도 같은 선택 속성을 정의한다. 따라서 C3는 `reasoning: {effort:'none'}`로 바꾸는 대신 **reasoning 속성 자체를 보내지 않는** 호환성 계획을 채택하는 것이 적절하다. 이는 문서에 근거한 구현 제안이며 실제 요청 성공 판정은 아니다. [Responses 생성 API](https://developers.openai.com/api/reference/cli/resources/responses/methods/create)

## 최소 구현 범위 제안

| 영역 | 필요한 변경 | 보존할 동작 |
|---|---|---|
| `src/server/provider.ts` 요청 | 모델을 한 번 결정하고 정확한 C3 snapshot에서는 reasoning 속성 제외. 기존 GPT-5 mini 경로의 minimal 옵션 유지 | Responses, `store:false`, strict JSON schema, SDK 재시도 0, 45초 timeout, 서버 전용 키, 기존 후속 검증 |
| 출력 상한 | 첫 비교는 현재 `max_output_tokens:3200` 유지. 모델 최대치로 자동 상향하지 않음 | 불완료를 성공으로 변환하지 않고 사용량/사유를 보존하며 기존 오류 반환 |
| 비용 계산 | C3 실제 응답 model ID에 해당하는 가격식을 명시적으로 추가 | 기존 GPT-5 mini 계산 및 알 수 없는 모델/사용량의 null 보존. unknown을 비용 0으로 완료 처리하지 않음 |
| 후보 실행 설정 | 정확한 snapshot, candidate ID, source hash, prompt/catalog/state/dataset binding, 새 run ID 고정 | 현재 장부·시도 분모·불확실 중단/재시도 계약. 과거 실행 binding 덮어쓰기 금지 |
| 검증 | mock 요청에서 C3 reasoning 부재/GPT-5 옵션 유지, 3,200 상한·strict schema·retry0 유지, 비용 정상/unknown, 불완료·400/403/404 인접 회귀 | 실제 연결 검사는 별도 승인된 소량 호출 후 현재 dev→validation→holdout 순서와 최소 기준 적용 |

현 코드에서 환경변수만 바꾸면 reasoning 옵션이 계속 전송되고 C3 비용은 null이 된다. 따라서 환경변수 단독 전환은 준비 완료가 아니다. 현재 계약 `ModelUsage` 필드와 UI/domain/SQLite 스키마 변경은 필요하지 않다. 설치 SDK에 필요한 선택 속성이 있으므로 이번 좁은 변경만으로 SDK/lockfile 교체가 필요하다는 근거는 없다. 비추론 모델이 토큰 소비·대기를 줄일 가능성은 실험 가설이며 한국어 식별·묶음 매핑 정확도 향상을 보장하지 않는다.

## 비용과 기존 예산

보수적 캐시 미적용 추정식은 `(inputTokens * 0.40 + outputTokens * 1.60) / 1_000_000`이다. 캐시 할인을 적용하지 않은 `estimatedCostUsd`이며 실제 청구서 금액이라고 표현하지 않는다. 미래 캐시 사용량을 별도로 검증하지 않고 할인을 예약 예산에서 선차감하지 않는다.

전달받은 12,456 입력/3,200 출력 크기를 그대로 대입하면 $0.0101024다. 입력이 같고 출력 300이면 $0.0054624다. 이 계산은 C3 실제 사용량 예측이나 최대 보장이 아니다. 조정자가 정정한 당시 C2 미래 예약은 960회 × $0.009/attempt = $8.64였으며, $0.008은 이전 값이다. $0.009도 첫 예시보다 작으므로 후보 승인 전에 현재 shared ledger와 남은 필수 호출 수를 사용해 예약을 다시 계산해야 한다. 기존 2,400호출/$15, prior reserve 50, unknown 보수 예약 정책은 확대하지 않는다. 이 문단은 C3 실행 전 비교 기준이며 이후 C3 config의 $0.0105/attempt · $10.08 예약과 혼동하지 않는다. 실제 best UX 준비 시점의 read-only 장부와 계산은 [별도 준비 보고서](c3-best-ux-preparation.md)에 기록한다.

## 특정 Preview 브랜치만 설정하는 방법

Vercel은 Preview 변수에 정확한 Git branch를 지정할 수 있다. 그 브랜치 배포에만 동명 기본 Preview 변수보다 우선 적용되며 다른 Preview 브랜치는 기본값을 사용한다. 키 등 다른 변수를 복제할 필요가 없다. [Vercel 환경별 관리](https://vercel.com/docs/environment-variables/manage-across-environments)

Dashboard에서 프로젝트 `wanna-gs` → Settings → Environment Variables → `OPENAI_MODEL`, 환경 **Preview만**, 조정자가 확정한 후보 branch만 선택하고 값 `gpt-4.1-mini-2025-04-14`를 Config로 설정하는 경로다. Production/Development 선택과 모든 Preview 대상 선택은 하지 않는다. 기존 API key와 배포 보호는 유지한다. 환경변수 변경은 기존 배포에 소급되지 않으므로 이후 해당 branch의 새 Preview가 필요하다. [Vercel 환경변수 적용 범위](https://vercel.com/docs/environment-variables)

설치 Vercel CLI 59.23.2의 `vercel env add --help`를 읽어 아래 플래그를 확인했다. 다음은 **실행하지 않은 계획 템플릿**이며 `<exact-approved-candidate-branch>`는 실제 확정값으로 대체해야 한다.

```sh
vercel env add OPENAI_MODEL preview \
  --git-branch '<exact-approved-candidate-branch>' \
  --project prj_T6x8XA3XyaNTgjMmvp7p9CgGCsks \
  --scope beatrain-4635s-projects \
  --value gpt-4.1-mini-2025-04-14 --no-sensitive --yes
```

동일 branch/key 설정이 이미 있으면 먼저 그 대상만 식별해 update한다. 범위를 모른 채 `--force`나 기본 Preview 전체 update를 쓰지 않는다. 키가 함께 내려올 수 있는 `env pull`은 모델명 확인에 필요하지 않다. [Vercel CLI env 공식 문서](https://vercel.com/docs/cli/env)

후속 담당자는 저장된 변수의 key/target/branch/model명만 확인하고 비밀값을 출력하지 않는다. 새 Preview의 Git branch/SHA와 배포 ID를 후보 source에 연결하고, 승인된 live smoke의 실제 `response.model`이 snapshot과 일치하는지 확인한다. 계정 권한·모델 접근·구조화 응답·사용량·두 역할 정상 흐름은 그때 검증한다. 설정 실패 또는 400/403/404에서 다른 모델로 조용히 fallback하지 않는다. 이 조사에서는 외부 설정 조회/변경·배포·live smoke를 실행하지 않았다.

## 인계 판정

문서/SDK/CLI 수준 구현 준비 완료. 실사용 가능성과 품질은 미검증이다. 다음 단계는 조정자의 후보 계약 및 예산 배정 → 제한된 provider 변경과 mock 회귀 → 별도 branch Preview 설정/배포 → 승인된 실제 연결·후보 평가다. 최종 G5/G6와 기존 미완료 UX를 이 조사 결과로 대체하지 않는다.

## 조정자 후속 예약 결정

위 조사 당시의 $.008은 이전 예비비 추정이다. C2에서는 이미 $.009를 사용했으며, C2 완료 후 장부 upper501/$4.5431865를 확인했다. C3 dev30 준비에서는 미래960회×$.0105=$10.08로 상향했다. 다음 unknown 시도$.05를 포함한 시작합은$14.6731865이며 dev 실행 여유는$0.3268135다. 고출력34회라면 소프트 한도에 먼저 닿을 수 있으므로 완주를 보장하지 않고 기존 시도별 중단을 유지한다.

첫 validation을 실제 실행할 때 현재 실행분276 상한을 미래552에서 빼 후속684회/$7.182로 별도 config를 사전 고정한다. 같은 config로 두 validation run을 진행하며 중간 예약을 변경하지 않는다. method_auditor가 이 계산과 이중 예약 제거를 독립 확인했다. 전체2400/$15·prior50·실패분모·최소기준은 불변이다. 아직 실제 C3 모델 호출0이다.
