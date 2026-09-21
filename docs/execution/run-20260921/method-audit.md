# 시작 단계 운영 감사 및 preflight P02 독립 정책 검토

- 감사 ID: MA-20260921-01, 검토 1/2.
- 작성자: `/root/method_auditor`; 조정자 `/root`와 별도 agent. 하위 agent 생성 없음.
- 역할: 초기 운영 감사, preflight P02의 첫 독립 정책 검토. 구현·Git·배포 변경 없음.
- consumed_context_hash: `74bf125ebe9c8ed2f7933abb55b08c904400f3a7ba1319c395a2429c32c20679`.
- Context: `CTX-20260921-BOOT-v1`, base `3ef1ee3447ab3943527c4685949da4116bcf0566`, phase `preflight/research/planning`.
- 모델: 실행 환경에서 상속한 모델. 이 작업에서 모델 override 또는 실제 앱 모델 호출을 수행하지 않았다.
- 적용 기준: card, CORE-04/06/10/13~23/25/26, D-40/44/45, ADR-001, GOAL, WORKPLAN, 14/17/18/20/22번 및 orchestration-audit skill.
- 소유 파일: 이 보고서만. 다른 담당 파일·공통 계약·Git 상태를 변경하지 않았다.

## 목적 보존과 실제 관측

고객 자연어 확인·동의에서 수요, 보수적 발주, 공급 확보·모의 결제, 입고 알림 이후 정확히 48시간 수령까지 이어지는 정상 경로를 유지한다. 이번 감사는 그 경로를 구현하는 개발 순서와 증거 계약을 검토하며 제품 동작이 실행됐다는 판정은 하지 않는다.

`shasum -a 256`으로 context.json 자체 hash를 확인했고 Python hashlib 대조로 manifest에 나열된 8개 문서가 전부 MATCH임을 확인했다. 현재 root에는 README.md, docs/18-environment-preflight.md, docs/PROGRESS.md, docs/README.md의 기존 변경과 docs/execution/ 미추적 산출물이 있다. 기존 변경을 삭제하거나 다른 작업의 완료로 집계하지 않는다. 이는 읽기 전용 관측이며 사용자 변경의 내용별 소유권까지 검증한 것은 아니다.

확인한 실행 증거는 문서 읽기·hash 일치·작업 파일 상태뿐이다. 앱 SQL/WASM, 모델 호출, 브라우저, 원격 PR/CI/merge, Preview 및 Production 실행은 이 감사자의 독립 실행 기준으로 모두 `not_run`이다. 조정자나 구현자의 결과는 이후 정확한 revision과 산출물을 받아 별도 검증한다.

## 초기 DAG·역할 감사 판정

**초기 경로 유지에 찬성한다. PLAN-READY 및 제품 게이트는 아직 판정하지 않는다.**

1. docs-only → 격리 preflight → 실제 Preview shell → 초기 조사·구체 DAG → PLAN-READY → GATE-BOOTSTRAP 순서는 순환이 없다. 최초 PLAN-READY에 아직 없는 gate runner를 요구하거나 초기 scaffold에 완제품 G5/G6를 요구하지 않는다. 반대로 scaffold의 단위/build 통과를 제품 게이트로 승격하지 않는다.
2. preflight P02(에이전트 동작 검사)와 WORKPLAN WP-P02(실제 Preview shell)는 다른 작업이다. ledger와 보고서에 전체 ID를 사용해 성공 범위를 혼동하지 않는다.
3. ADR-001의 D01/D02A → D03 → D04A와 P04 → F00 경로를 유지한다. 최소 seed가 F00 앱 API를 기다리거나 전체 seed가 완성된 UX를 기다리는 역의존을 만들지 않는다. 정식 QA·NL baseline·G5에는 D05 전체 seed가 필요하다.
4. 4개 슬롯은 역할 4개 제한이 아니다. 현재 coordinator/research/preflight-builder/method-auditor 배치는 적합하다. 구현 완료 후 순차 재배정으로 제안자 외 두 정책 검토자, 독립 코드 검증자, 서로 다른 customer/merchant QA를 확보할 수 있다. 살아 있는 worker가 종료·인계하기 전에 동일 소유 파일 작업을 중복 발행하지 않는다.
5. 현재 manifest는 초기 역할과 버전을 명시하나 task별 branch/worktree·AC·독립 reviewer·모델 위험도/선택 이유·eval/holdout 소유자는 미확정이다. 이는 아직 설계 전이므로 현재 preflight 읽기 작업을 막지 않는다. WP-P03 전에 실제 task 계약과 파일 소유권 표로 채워야 하며 현재 manifest만으로 PLAN-READY를 통과시킬 수 없다.
6. GATE-BOOTSTRAP의 책임은 조정자가 단일 작성자에게 배정해야 한다. 결과 0개/skip/stale/누락 자식/fixture-only live/같은 구현·검증자/잘못된 SHA/목적 보존 증거 누락 반례를 실제 실행해야 한다. 현재 상태는 규칙 문서화 완료·자동 강제 미구현이다.
7. NL 평가 기준은 baseline 결과 전에 고정하고 grouped holdout은 평가자가 관리한다. 구현자에게 holdout 정답을 넘기지 않는 파일/접근 계약이 필요하다. 구현자 자신이 candidate 품질을 독립 승인하거나 후보 한도 도달을 필수 기준 통과로 기록하면 실패다.
8. 발주 마감·동의 유효기간·알림 생성 후 48시간은 서로 다른 값과 사건이다. 향후 G0/ADR에 정상·직전·정각·직후와 snapshot 복원·역할 전환 후 동작을 포함한다. 새 SKU/점포/가격/수량을 원래 동의에 붙이거나 모집 목표를 신청 상한으로 사용하는 정책은 이 운영 간소화에서 파생될 수 없다.
9. Production 불변은 preflight 범위다. 최종 G5 이후 main 병합→연결된 Production 배포→G6는 이미 사용자와 GOAL이 승인한 후속 경로다. 임시 preflight base merge가 실제 보호 branch merge 권한을 증명하지 않는다.

위 항목은 새 제품 게이트나 추가 관리 계층을 만들지 않는다. 현재 실제 재작업/실패를 관측하지 않았으므로 역할 수 확대나 전체 문서 재작성 실험은 제안하지 않는다. 소유권·증거 집계의 미확정 부분은 원래 WP-P03/P04 작업에 배정한다.

## preflight P02: 첫 독립 정책 반례 검토

검토 대상 초안: “기존 사용자 변경을 root에 보존하고 preflight 별도 worktree와 로그를 보존하되 Production은 변경하지 않는다.”

**판정: 찬성 — 아래 범위가 포함된 제한 시험에 적합하다.** 이 결과는 첫 번째 독립 검토이며 두 번째 검토나 조정자의 ADR 채택을 대신하지 않는다. 제품 정책에 관한 사용자 직접 확정으로 표현하지 않는다.

- authority: user-delegated. 작업 공간 보존은 이번 사용자의 명시적 요청에도 부합한다.
- policy_key 제안: `preflight.workspace_retention`.
- effective_scope: `run-20260921`의 preflight 실행·시험 리소스 보존. 후속 제품 구현 및 G5 후 정식 Production 배포 금지로 확대하지 않는다.
- depends_on: D-32/34/44/45, docs/18의 임시 ledger·격리·보존 규칙.
- supersedes: 없음. 기본 cleanup을 사용자 요청에 따라 소유·영향·정리 방법이 있는 의도적 보존으로 처리한다.
- conflicts_with: 위 scope에서는 없음. 전 목표에서 Production을 영구 금지하면 GOAL/CORE-13과 충돌하므로 그 해석은 기각한다.

| 반례 | 기대 동작·조건 | 이번 검증 |
|---|---|---|
| root 변경이 새 worktree에 자동 복사됐다고 가정하고 오래된 계약으로 구현 | 현재 base와 소비 문서 hash를 확인하고 필요한 계약을 명시적으로 전달. 사용자 변경은 root에 보존 | manifest 8개 hash 일치 확인, worktree 계약 전달 `not_run` |
| “보존”을 모든 임시 remote·무제한 probe까지 방치하는 의미로 해석 | worktree/로그와 PR/branch/deployment/browser namespace를 구분해 ledger에 정확한 ID·소유·영향·정리 명령 기록. 공개 비용 소진 endpoint는 허용하지 않음 | 리소스 생성·서버 제한 검사 `not_run` |
| 로그 보존이 .env·인증 응답·키 값까지 복제 | 명령·원본 오류의 비밀값을 정제하고 값은 서버 secret에 유지. 로그는 재현 정보·결과·ID만 보존 | 비밀값 정제 실행 검사 `not_run` |
| Preview branch가 실수로 Production branch와 같음 | 배포 전에 연결된 project/productionBranch/source SHA 대조. preflight는 임시 base/probe와 비 Production만 사용 | 원격 mapping 조회 `not_run` |
| 첫 시험 성공 후 worktree 삭제로 다음 세션 재개 불가 | 사용자 요청에 따라 공간 유지. root→worktree 경로·branch·SHA·명령·증거 포인터로 재개 가능해야 함 | 보존·재개 실행 검사 `not_run` |
| preflight Production 불변 규칙 때문에 최종 배포를 다시 사용자에게 확인 | scope를 preflight로 제한. G5/최종 정책 감사와 보호 규칙을 통과하면 승인된 릴리스 경로 진행 | 문서 계약 확인, 릴리스 `not_run` |
| 임시 CI/Preview가 PASS이므로 필수 고객 동의/48시간도 PASS로 집계 | preflight P00~P11와 제품 G0~G6를 분리. 핵심 시간·수량·동의는 도메인·실제 SQLite·브라우저에서 후속 실행 | 문서 분리 확인, 제품 검사 `not_run` |

## 제한 운영 시험 기록

- 실험 ID/상태: METHOD-20260921-PREFLIGHT-RETENTION / proposed, 첫 검토 완료.
- 제안자·조정자: `/root`; 첫 독립 검토자: `/root/method_auditor`; 두 번째 검토자: 조정자 배정 필요.
- trigger: 사용자 작업 공간·로그 보존 요청 및 현재 root 기존 변경. 실제 삭제 사고·재작업 관측 없음.
- 기준선: root에서 기존 변경 4개 파일, 미추적 실행 디렉터리 관측. 속도/재작업률 측정값 없음.
- 최소 변경: 기본 임시 작업 정리에서 명시적 worktree/정제 로그 보존으로 전환하고 ledger로 추적.
- 시작 전 성공 조건: root 기존 변경 보존, 별도 worktree 소유·경로·SHA 기록, ledger 누락 0, preflight Production 변경 0, 비밀값 노출 0, 제품 PASS 오표시 0.
- 관찰 구간: 현재 run-id의 preflight P00~P11 한 번. 초안+보완 최대 2회 검토.
- 부작용·실패 조건: 다른 사용자 자원 삭제, 저장소 공유 branch 동시 전환, 무제한 model probe, 검증하지 않은 비용/보안 영향, Production 변경, 민감정보 로그 기록.
- 복구: 작업을 확대하지 않고 실제 생성 ledger의 대상 상태를 재조회한다. root 사용자 변경은 건드리지 않는다. 필요하면 시험 endpoint를 비활성화하고 정제 로그·worktree를 남긴다. 삭제 범위 확장은 하지 않는다.
- 실제 실행 revision/결과: `not_run`. 정책 의미 검토와 context hash 검증만 수행했다.
- 처분: 현행 격리 구조 유지 + 보존 정책 제한 시험 권고. ADR/계약/CI 변경은 이 작성자가 수행하지 않았다.
- 종료 이유: 초기 계획의 중대한 순환은 발견되지 않았다. 남은 실행 검증은 원래 P02/P10/P11 및 WP-P03/P04로 연결된다. 새 실패나 context 변경이 없으면 같은 감사 의견을 반복하지 않는다.

## 인계

조정자는 두 번째 독립 정책 검토와 범위 명시를 확인해 채택 여부를 기록하고, preflight evidence를 모은 뒤 독립 P10/P11 검증을 배정한다. 이 감사자를 이후 구현자와 분리된 preflight 검증자로 재사용할 수 있다. 실제 PLAN-READY 판정에는 Preview·초기 연구·구체 task 계약 증거가 추가로 필요하다. 현재 제품 G1~G6, NL 품질, 독립 UX QA 및 Production 검증은 `not_run`으로 유지한다.

## APP-v2 계획/P10 독립 판정

- consumed_context_hash: `1cc5b18da57bdfb492d3f2cf1e09aedb8357e72e0be951c680446583417134ef`, `CTX-20260921-APP-v2`.
- plan.md SHA-256: `556f651f0f09741e05e01eb84f83550f4d0da145990de4428009521d3b0ff9a0`.
- manifest에 등록된 12개 입력 파일의 실제 SHA-256이 모두 MATCH였다. root 현재 branch `codex/bootstrap`, 기존 사용자 변경이 남아 있음을 읽기 전용으로 확인했다.
- ADR-002/003은 제안 단계가 아니라 user-delegated adopted·실행 미검증으로 index/context에 갱신됐다. 정책 의미에 대한 2차 독립 검토는 각각 별도 보고서에 있다.

**실행 계획 내용에 대한 독립 검토는 PASS다.** B01 초기 gate runner를 만드는 데 완제품 검사를 선행시키는 순환이 없고, 최소/전체 seed와 평가 계약의 선행조건이 분리됐다. root는 package/lock/CI·통합 단일 작성자, data/dba는 schema/domain/seed 단일 작성자다. 계약 변경은 root 통합·소비자 ACK 경로가 있다. 기능별 G0와 실제 실행 증거는 후속 작업이며 앱 미구현은 이 계획의 결함이 아니다.

E01 평가자는 candidate/prompt/search 구현자가 아니며 private holdout을 소유한다. 연구 담당은 taxonomy/분할 metadata만 독립 검토한다. customer QA는 customer 구현자가 아닌 method_auditor, merchant QA는 merchant 구현자가 아닌 research로 분리되어 둘의 agent ID도 다르다. method-auditor가 이후 evaluator를 맡더라도 같은 후보를 구현하거나 자기 구현을 독립 승인하지 않는다. 관리 깊이는1로 유지한다. 4개 슬롯 안에서 역할을 순차 전환하며 해당 소유 작업이 끝나기 전에 중복 배정하지 않는다.

초기 연구는 R20260921-v1의 source·시나리오·미확인 항목과 preflight_builder의 별도 원문 검토/기술 brief를 확인했다. 200개 상품/실제 좌표/전체 eval이 아직 없다는 사실은 후속 D03/N02의 gate 조건으로 유지된다. 현재 조사 보고서를 전체 seed 완료나 제품 테스트로 세지 않는다. 전체 CORE/AC 검증은 표의 역할별 매핑과 L01 전체AC/L02 AC19 추가·GOAL 완료 계약으로 이어진다.

**P10 및 전체 PLAN-READY 최종 상태는 원격 P04 merge와 P11 cleanup/보존 영향 증거가 확정될 때 집계한다.** 이 감사 시점에서는 coordinator가 CI 2회 PASS와 임시 PR merge 진행 중임을 전달했으나 이 작성자가 remote merge/cleanup의 최종 SHA/ID를 재조회하지 않았다. preflight 독립 보고서의 로컬/Preview/실제 모델 증거는 유효하다. 계획 내용 PASS와 실행 전체 READY를 구별하며 B01의 계약/runner 준비와 독립 E01 계획은 계속할 수 있다.

Production 경계 사건은 지우지 않는다. deployment-recovery.md에는 Git 및 잘못 지정한 API target으로 생성된 두 Production 분류 배포와 후속 제거/Preview 경로 수정이 기록돼 있다. 따라서 “preflight 동안 Production 변경0”이라는 초기 성공 조건은 달성하지 못했으며 이를 성공으로 바꾸지 않는다. 정상 target=null Preview를 실측했고 runtime P07/P09가 통과했다는 사실과 과거 경계 실패/복구를 병기한다. 최종 P11에는 잘못된 두 ID의 제거, probe token·Preview 제거 또는 소유/비용영향이 검증된 보존, root/worktree/로그 보존 내역을 정확히 연결해야 한다. 이후 제품 Preview 배포도 실제 target/source를 확인하며 Production 오분류가 재발하면 릴리스를 진행하지 않는다.

비차단 manifest 설명 정리: `versions.model`의 “gpt-5-mini configured, access unverified”는 preflight live 접근 증거와 다르다. 다음 context 갱신에서 “preflight access verified; product prompt/quality not_run”처럼 범위를 분리한다. 모델·schema·seed·평가셋 자체의 제품 미검증 상태는 유지한다. 이 설명 수정만으로 기존 runtime 검사를 전부 반복할 필요는 없다.

다음 감사 시점은 첫 G3/G4 또는 새 실제 실패, 그리고 G5 직전이다. 실제 반례 없이 같은 PLAN 의견을 다시 열지 않는다. E01 taxonomy/scorer 계획은 evaluator로 진행하며 protected holdout 정확 발화/정답은 구현자에게 전달하지 않는다.

### P04/P11 증거 수신 후 최종 집계 — PLAN-READY / P10 PASS

후속으로 cleanup.json, resource-ledger.json, preflight-report.md, deployment-recovery.md의 최종 상태를 읽고 GitHub API를 독립 재조회했다.

```text
PR #1: merged=true, state=closed
base: codex/preflight-20260921-base
head: codex/preflight-20260921-probe
merge SHA: 33b7c7f62fc0d49aa570f30af6432780c88821e0
Actions 35579564243: merge SHA exact, completed/success
Actions 35579372364: head 9e0f12f4eaf6bd7813cd2514e3422bea6f8764b5 exact, completed/success
Actions 35579375086: same head exact, completed/success
삭제된 Preview의 /api/health: HTTP404
```

인증은 기존 Git credential을 gh subprocess 환경에만 전달했고 값은 출력하지 않았다. main 병합으로 오인하지 않도록 실제 PR base를 확인했다. cleanup/ledger에는 생성한 세 배포 ID 제거, 현재 배포목록0, branch PROBE_TOKEN 제거, 사용자 요청에 따른 root/worktree/branch/PR/CI/정제 로그 보존, 후속 제품 QA용 기존 API secret과 named bypass의 제한된 보존이 연결돼 있다. 배포 목록0와 환경변수 제거는 coordinator가 수행한 정리 증거를 검토했으며 이 작성자가 같은 원격 삭제를 반복 실행하지 않았다. 정상 Preview URL이 더 이상 살아 있지 않은 것은 HTTP404로 별도 확인했다.

**현재 환경의 P10 준비 집계 PASS, ready_for_goal=true, 실행 계획 PLAN-READY로 판정한다. B01 gate/bootstrap 구현을 시작할 수 있다.** 앞 절의 대기 항목이 충족됐으므로 형식 문구나 앱 미구현을 이유로 독립 구현을 더 대기시키지 않는다. 최초 plan에 runner 존재를 요구하지 않으며 B01이 구현한 runner로 나중에 계획 manifest를 재검사한다.

이는 복구 후의 준비 판정이다. 두 번의 Production 오분류/일시 배포가 있었다는 실패 이력은 그대로 남고 “Production 변경0”으로 고쳐 쓰지 않는다. 검증된 target 생략→Preview 경로, probe Git 자동배포 비활성화, 해당 리소스 제거로 알려진 잔여 실행 위험을 닫은 것이다. `production_execution_verified=false`, 제품 G0~G6 및 전체 seed/NL/독립 UX QA 미실행 상태는 유지된다. 제출 main 보호/실제 Production 접근·G6는 릴리스 단계에 별도로 검증한다.

원장 일부에 남은 “independent pending”, “merge CI 후속”, “독립 집계 대기” 표현은 위 exact SHA 결과로 갱신할 수 있다. 해당 문구 정리는 이미 실행된 증거를 갱신하는 작업이며 새로운 검증 게이트가 아니다.
