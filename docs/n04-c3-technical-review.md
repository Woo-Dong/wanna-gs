# C3 모델 프로필·좁은 prompt 변경 독립 기술 검토

2026-09-21 / research / **기술 PASS, 실제 모델 수락·품질·채택 not_run**.

작성자 root와 독립인 검토자가 `2026-ralphton-nl-candidate`, `codex/n04-model-candidate`의 변경을 읽고 실행했다. C2 기반 source는 `e056fce800bd1ea225baf9a0d70e85b0a2d0edf3`. 이번 검토는 실제 모델0·holdout 본문/생성기0·키/배포 환경 변경0이다. C3 전체 context/gate fingerprint는 아직 발급하지 않으며 아래 파일 바이트만 판정한다.

| 파일 | SHA-256 |
|---|---|
| src/server/provider.ts | `8a01210b2de8ee634e46866fe5744a5ee5e90ac46ad5247e1c2e941a1c08b46d` |
| src/server/model-profile.ts | `f61a06fd44d0110b283b9c370146a2f489e3e3050e6f2ca7924a860c05251e1c` |
| src/server/prompts.ts | `d48e77fb099eed908e2e67fc32d1b4f657cff7f519b7f339aea32880e4f0ed72` |
| tests/server/model-profile.test.ts | `6bdfe64fb28aa8dad9144fbf4e5776c5e66b088cf2a2a6f300897b2f6a420020` |

## 직접 실행한 결과

Node22 `/opt/homebrew/opt/node@22/bin/node`로 `--import tsx --test tests/server/*.test.ts` **25/25 PASS**, `node_modules/typescript/bin/tsc --noEmit` PASS. 최초 model-profile4개만 Node23에서 실행한 결과도 PASS였으나 최종 회귀는 프로젝트 Node22로 다시 확인했다.

별도 private probe는12검사 묶음, SDK fetch18모의 전송, 실제 외부 전송0으로 모두 PASS했다. 후보 worktree의 `artifacts/private/run-20260921/c3-independent/{probe.mts,probe.log,server-tests.log}`에 재현 자료를 보존했다. 모든 fetch를 고정 모의 응답으로 교체하고 모의 키만 사용했으며 환경은 finally에서 복원했다.

- 4.1-mini 입력/출력 단가0.40/1.60 및5-mini0.25/2.00에 대한 독립10개 연산 벡터. 토큰0은 판명된 비용0이고, 소수/음수/비유한/unsafe integer5개는 null.
- 실제 설치 SDK를 통한4.1 요청에 reasoning 키 자체 없음. store=false, strict=true, additionalProperties=false, max_output_tokens3200 유지. 5-mini에서는 기존 minimal reasoning 유지.
- 요청 모델이4.1이어도 응답 모델이5-mini이면 실제 반환 모델의 비용을 계산한다. 알 수 없는 반환 모델은 알려진 토큰을 보존하고 비용만 null이다. 무료 호출로 바꾸지 않는다.
- usage 누락·합계 불일치·소수·음수는 정상 응답으로 통과하지 않는다. 잘못된 JSON과 incomplete 응답의 이미 알려진 사용량·비용은 오류 attempt에도 남는다.
- HTTP400/401/403/404/429 rate/429 quota/500은 기존 오류 코드로 변환하며 각각 fetch1회, 재시도0. usage는 null이다. 오류 뒤 정상 요청 성공으로 activeCalls 해제를 확인했다.
- 키 없음은 호출 전 실패로 fetch0이다. 소스에서 SDK timeout45000과 maxRetries0가 기존 그대로임을 확인했다. 실제45초 대기/네트워크 timeout 실행은 하지 않았다.

가격 숫자의 공식 최신성·모델의 서버 실제 지원은 builder의 별도 공식 원문 조사/후속 승인된 실제 연결 검사와 구분한다. 이번 검토의 비용 PASS는 위 지정 단가의 계산과 기록 정확성이다. instanceEstimatedUsd는 인스턴스별 추정치이며 unknown 비용이나 전체 goal의 결제 상한을 보장하지 않는다. 기존 동일 goal ledger의 unknown 보수 예약·중단 계약을 그대로 적용해야 한다.

## 추가 prompt 변경과 목적 보존

packed-refs-v4는 알려진 SKU가 들어 있어도 실제 카드 결제·본부 보고·실제 GS 업무 실행 요청을 정상 검색으로 조용히 바꾸지 않는 경계, stale=false와 동일 version을 가진 명확한 제안에 불필요한 버전 재확인을 요구하지 않는 규칙을 추가한다. 특정 평가 사례의 SKU/정답 하드코딩은 없다. 정상 단일상품 식별, 고객 명시 동의, 모의 거래, 실제 stale 시 clarify, 경영주 별도 정책 확인·현재 변경/undo 규칙은 남아 있다.

clarificationCount=2에서 범위 밖 실행 요청이 들어오면 추가 질문이나 show_candidates로 구제하지 않고 unidentified로 끝나야 한다. 정상적인 모의 상품 탐색과 실제 실행 지시를 구별하는 것도 필요하다. 이 두 인접 동작은 정적 prompt 읽기나 모의 SDK 성공으로 실제 달성했다고 주장하지 않으며 기존 범위/질문 제한 회귀에 포함한다.

assistant/schemas/packing/retrieval/catalog5파일은 C2 HEAD와 실제 바이트가 동일하다. 따라서 canonical SKU 복원 뒤 기존 검증, 원문 보존, 승인 권한의 경계는 이 delta로 제거되지 않았다. UI·도메인·데이터·평가 정답은 이번 작업에서 변경하지 않았다.

C3는 모델 변경과 좁은 prompt 보강의 복합 후보다. 향후 성공을 모델 하나의 효과로 분리 주장하지 않는다. 기술 PASS는 실제 API 수락, 자연어 최소 기준, 기존 정상 회귀0, validation2, 보호 holdout, UX 비교 또는 G5/G6 통과를 뜻하지 않는다. B0/C1/C2 실패 자료와 UX NOT_READY는 계속 보존한다.
