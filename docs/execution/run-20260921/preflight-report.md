# PREFLIGHT run-20260921

상태: P00–P11·PLAN-READY 독립 최종 PASS. `production_execution_verified=false`.

목적은 지정 GitHub/Vercel·실제 sql.js/browser·서버 OpenAI·독립 agents 경로 확인이며 제품 구현 완료가 아니다. 사용자 작업 공간 보존 지시를 P11에 우선 적용한다.

| 항목 | 실제 증거/결과 |
|---|---|
| P00 | 현재 root/base/remote·Node22/gh/Vercel·기존credential 확인, 기존4문서변경 보존. inspector PARTIAL 자체결과 별도 |
| P01 | Woo-Dong ADMIN, rulesets[], main branch not protected(404), Actions enabled, environment protections[]. Vercel Git main 연결·SSO보호 확인. 계정 정확 잔액 unknown, 실제 소량 OpenAI 호출 성공 |
| P02 | builder와독립method_auditor 다른ID 실행, 연구자와감사자 보존정책2관점 독립반례검토, context hash ACK |
| P03 | 격리Next16.3.5/Node22.22.3/sql.js1.14.2/openai7.20.0, lockfile·type·build·SQL8검사 독립PASS |
| P04 | 임시base/probe만 생성·push, PR1→임시base merge33b7c7f. 9e0f12f exact head의 CI runs35579372364/35579375086 gate PASS. merge결과 exact SHA CI35579564243 SUCCESS 독립재조회확인 |
| P05 | source dc81df9의 dpl_HjgwxK7oQCwRuoG48SUZF7XE9h3t target=null Preview, health200·독립실제브라우저. 원치않은 Production분류2건 복구사건 별도기록 |
| P06 | 실제sql.js insert/read/FK/check/rollback/export/import8개, 생성SQLite seed hash6b1b7139…2f7e |
| P07 | exact Preview Worker/WASM/seed·IDB snapshot·role/refresh/reset·실제IDB abort→직전hash복원/재시도. 독립보고서·private screenshot |
| P08 | local 실제API CONNECTED, 로컬route live131tokens(86+45), Preview live129tokens(87+42); model gpt-5-mini-2025-08-07. unauthorized401/invalid400은 실제모델안호출 |
| P09 | 실제브라우저 한국어입력→서버live구조화응답→Worker검증→SQLite SELECT body 일치→refresh bytes hash 동일. token오류 미저장, pageErrors0 |
| P10 | 독립보고서·ADR002/0032검토·PLAN검토. 환경의 과거성공을 제품성공으로 승격하지 않음 |
| P11 | 테스트Vercel배포3개 모두제거, branch PROBE_TOKEN제거, 배포목록0 확인. 임시PR MERGED, branches/worktree/log는 사용자요청으로 보존. 제품Preview용 기존키와 automation secret만제품QA용보존. ephemeral브라우저context종료 |

세부 원본/정제 증거는 resource-ledger.json, preflight-independent.md, local-model-probe.json, cleanup.json, deployment-recovery.md와 현재Codex tool history에 연결한다. 키/토큰·원문header/trace를 공개로그에 남기지 않는다. private artifact는 .gitignore로 제외한다.

## 사건과 제한

- Git 최초자동배포가 production으로생성됐으며 직접API target문자열preview도 production으로응답했다. 두배포만제거했고 기존서비스배포는 없었다. Production불변시험이 처음부터성공했다고 주장하지 않는다.
- 공식API계약대로 target생략→null Preview를 실제확인. probe vercel.json git.deploymentEnabled=false 추가뒤push·임시merge는 새배포없음. 제품Preview는검증된직접API경로, 최종main은별도릴리스게이트로운영한다. 이복구가제품 G5/G6를대체하지않는다.
- remote required-check protection은현재없음. CI job성공은봤지만현재강제정책존재주장은안함. 제품GATE-BOOTSTRAP에서실행기/단계분기/독립evidence와반례거절을구현한다.
- 계정정확잔액/외부심사접근/제품자연어품질/200SKU/실제점포좌표/제품G1~G6 미검증. 채택ADR의한도·필수reserve·unknown상태를유지한다.

## 보존·재개

root `/Users/gsr/Desktop/workspace/2026-ralphton`, probe `/Users/gsr/Desktop/workspace/2026-ralphton-preflight-20260921`. root `docs/PROGRESS.md`와 context-app-v3.json부터재개한다. private파일·로그는root artifacts/private/run-20260921 및probe preflight-check.log에보존한다. 외부Preview는cleanup으로제거됐으므로현재열리는제출URL이아니다.
