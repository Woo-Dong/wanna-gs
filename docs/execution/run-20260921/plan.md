# 실행 계약과 실제 DAG — 20260921

상태: PLAN-READY 독립 판정 PASS (method-audit.md 최종 판정). 루트 작업 공간·private 로그·격리 probe는 보존한다. main에 완제품 전 변경을 직접 게시하지 않는다.

## 관측과 적용 근거

- base 3ef1ee3447ab3943527c4685949da4116bcf0566, 지정 Woo-Dong/wanna-gs와 연결 Vercel 사용.
- P03/P06 sql.js8/type/build/독립 Chrome, P05/P07/P08/P09 실제 Preview source dc81df9·live 모델129tokens 증거는 preflight-independent.md. PR1 최신 config-only head9e0f12f의 CI/임시merge는 ledger로 보강한다.
- 초기 연구 R20260921-v1과 독립 research-independent.md. 200상품/좌표/eval은 후속 데이터 게이트이며 미완료.
- ADR001 최소seed 병행, ADR002 거래, ADR003 평가/지도/UX 경계 채택. D40 팀원자료 미채택 유지.
- preflight 자동 Production 오분류는 deployment-recovery.md로 보존. 잘못된2배포 제거. 이후 preview API target 생략/null 검증, probe code의 git.deploymentEnabled=false로 자동푸시배포 없음 확인. 제품에는 main만 Git배포 허용, 나머지는 정확 gitSource Preview API로 생성하는 config를 검토한다.

## 작업 계약·소유권·의존

모든 작업은 current context hash를 ACK하고 core/AC/ADR 적용, 정상/실패 기대값·actual evidence를 결과로 반환한다. 역할명은 순차 재사용하며 자기 구현의 독립 QA 금지. 개발 모델은 제공 collaboration의 상속 모델(override 없음); 이름 추측 안 함. 중요 정책·거래·검증은 현재 조정자와 독립 최고가용 상속 추론으로 검토하며 모델 선택 실패 시 승격/재배정한다.

| task | 선행 | 구현자/소유 | 독립 검증 | CORE/AC·기대값·게이트 |
|---|---|---|---|---|
| B01 gate/bootstrap | PLAN-READY | root: package/lock, quality, scripts/gates*, CI, 기본 Next shell/config | research(제품기능 구현 전 독립 검토) | CORE16~18/22, stale/0/skip/fixture-live/자기검증/누락 거절·명령실패중단; 초기 G0/G1/G2해당범위 |
| D01 자료정규화 | 연구·자료계약 | preflight_builder→data/dba: data/research만 현재 진행 | method_auditor 표본·provenance/중복/좌표 | CORE14/20/21/24, AC21~24/26; 200SKU/8~12실점포/합성구분 |
| E01 taxonomy/eval | ADR003·초기연구 | method_auditor→nl-evaluator: eval schema/dev/validation + private holdout | research가 taxonomy/분할 metadata만 검토; holdout내용 미열람 | AC24/26/28/29, family 교집합0, 9범주최소·oracle/scorer·최종보호 |
| D02 schema/domain/minseed | B01·ADR002·D01 계약(전체자료와 병행) | data/dba 단일소유 src/domain, src/db, data/schema, seed builder, own tests | method_auditor(비구현자) | CORE4~10/13/17/25/26, AC4~17/20/31/32, 실제SQL rollback·FIFO·수량보존·예산·동의/48h |
| D03 fullseed | D01/D02 | data/dba | method_auditor | CORE14/20/21, AC22~24 seed/catalog/hash 동일·실제SQL·공개자산holdout없음 |
| C01 customer UX/FE | B01 + D02 API contract | research→customer implementer: src/components/customer만 | method_auditor→customer-qa | CORE2~4/9~11/24/25, AC1~5/11~15/30/31. 정상상품·확인동의·대안/미식별·복구 |
| N01 NL API/search | B01 + catalog contract | root: src/server + app/api + eval runner(no holdout내용) | method_auditor nl-evaluator | CORE3/5/11/15/21/23/25, AC1~3/7/8/17/24/26/28/29. 실제SKU허용·구조화응답·불확실실패·키비노출 |
| M01 merchant UX/FE | D02 API + N01 | root: merchant components·shell integration | research→merchant-qa(C01만구현, merchant구현없음) | CORE5~8/24~26, AC6~10/17/30~32. 묶음·정책·드릴다운·입고수령 |
| I01 G3/G4 | D02+C01+N01+M01 | root 통합 단일담당 | method_auditor customerQA + research merchantQA | 고객→경영주→고객 UI/SQL 같은 snapshot, 오류/중복/48h·reset·역할세션 |
| N02 baseline/candidate | D03 + I01 + E01 | root nl-experiment: prompt/search candidate만 | method_auditor scorer/holdout/best승인 | ADR003 336baseline/84holdout·후보한도·paired·mandatory0·usage |
| L01 G5/release | D03/N02/I01·두UXQA·정책감사·운영감사 | root release | research 제품·method_auditor 실패/운영 두감사 | 전체AC(except19pendingG6), latestmain+candidate exactSHA·CI·Preview |
| L02 G6 | 검증PR integration→main merge·해당Production | root 정합/ledger | 서로다른 customerQA/merchantQA | AC19 포함 실제제출URL·live·SQL/reset/예외/48h·키비노출 |

앱 구현은 branch/worktree로 분리한다. 공통 schema·migration·seed는 dba, package/lock/CI는 root. 소유 변경은 root가 메시지/기록으로 이전하고 같은 파일 동시수정 금지. API 계약 파일은 dba 제안→root 통합→소비자ACK. shared root를 변경하는 read-only 보고서는 각 고유 파일에만 쓴다.

각 작업 branch는 codex/<task-id>-<name>, 누적통합 codex/integration, 제출 main. 초기 root 사용자변경·계약 기록은 bootstrap branch에서 관련 문서만 commit하며 원본을 제거하지 않는다. 기존 probe branch/PR은 제품 통합에 merge하지 않고 참조한 shell 코드만 검토 후 도입한다.

## 목적 보존과 완료

고객이 정상 상품을 확인·동의하면 수요로 남고, 경영주가 최신수요/예산을 한 번 판단하여 모의 공급→자동결제→입고후48시간 수령으로 이어져야 한다. stale/위조/과잉을 막는 코드가 정상성공을 없애면 FAIL. GATE-BOOTSTRAP에서 과거PASS/누락/자기검증을 기계거절하되 의미상 품질은 독립검토/브라우저로 확인한다.

현재 미실행 task를 후속계획이라는 이유로 면제하지 않는다. 사전점검과 제품 게이트는 별도다. 최종 완료는 docs/GOAL 전체와 L02 증거 후만 선언한다. 실제 외부 권한/비용장벽은 공개하고 독립작업 계속. optional 최적화는 ADR003 한도에서 끝내지만 mandatory/최소기준은 남는다.

## 2026-09-22 C11 복구·최종 의존성

C10 공개 dev30 및 validation84 두 회 PASS 뒤 보호 v2 76/84 FAIL로 출시 채택을 보류했다. D48/D49와 [C11 계약](c11-recovery-contract.md)을 현재 추가 DAG로 적용한다.

| 작업 | 선행 | 소유/독립 검토 | 현재 상태·증거 |
|---|---|---|---|
| C11-CUSTOMER | C10 오류 집계 | research prompt-only / final_ux_state | 구현·자체 서버62/type PASS, 독립 검토 대기 |
| C11-NEED | 제품 감사의 저장 누락 재현 | research customer/model·saveNeed / final_ux_state | 기존 필드에 모델근거/차이/미확인 보존, 자체 고객7·실제SQL roundtrip PASS, 독립 대기 |
| C11-EVAL | 두 자원 검토 | root runner/checker / final_ux_state | 자체35+89·독립17그룹 PASS, 최종 context 결속 대기 |
| C11-HOLDOUT | v1/v2 은퇴 보존 | method_auditor private 데이터 / final_ux_state | 보호 v3 84/92 작성·독립 검토 중, 모델0 |
| C11-NL | 위4개 기술 통합·CI·정확 배포 | method_auditor 평가 / root 단계 GO | max1 고정 dev→validation 동일2회→freeze→새holdout 최초1, 아직0 |
| C11-QA/UX | 적격 NL best | customer method / merchant research / UX final_ux_state | 새 runtime/source 결속 필요, 실제0 |
| C11-G5/G6 | 실제 QA/UX·두 정책관점·증거 감사 | root 통합 / 독립 검토자 | main 전 G5, 정확 main Production 후 익명 G6; 아직 미완료 |

C10 Production READY를 유지하며 새 source CI 후 Production을 갱신한다. 미실행을 PASS로 바꾸지 않고 현재 상한 $20/2400·실패 이력·작업공간을 보존한다.
