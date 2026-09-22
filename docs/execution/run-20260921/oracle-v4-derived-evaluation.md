# Oracle-v4 파생 평가 — 자체 실행 증거

ADR-008 채택 범위의 공개 정답 두 slot만 교정했다. 모델·앱·runtime·입력·원래 관측·기존 FAIL·기존 manifest1~3은 변경하지 않았다. 실제 신규 모델 호출은0이며 장부는2,004회/$12.1930621 상한, SHA b0a77445a49484e454afa6374b28afea91d70006e7928e4c072d6266d06fb110 그대로다.

## 범위와 원본 보존

고정 공개 실행 register는23개다. 해당 slot이 없는 원래 dev30 실행11개는 dataset hash/ID/영향0을 검사하고 원본 상태를 유지했다. baseline1개와 validation11개, 총12개는 기존 정답으로 원래 보고서를 먼저 재현한 다음 교정 정답으로 전수 재채점했다. 이전 사용자턴·실패·미완료·사용량까지 포함한다. 모든 원관측은 private에 남고, 공개 normalized 파일에는 자연어 질문/설명/코드·진단 원문을 포함하지 않는다. enum/boolean/숫자/SKU/구조화 command/질문 형태값만 남기며 private 원문과 normalized의 원래·새 정답 점수가 전부 같음을 자체 확인했다.

원래 C11 두 번째83/84·핵심 회귀1 FAIL은 원래 report/execution/binding에 그대로 남아 있다. 새 report는 derived_public_oracle_rescore wrapper 안에 있으며 새dataset과실행dataset을섞지않는다. 두 독립 run ID, 실행시각, 실제92턴,비용·지연은원본참조다. 새모델호출또는수정정답을사용한과거실행으로표시하지않는다.

초안01 산출물61파일은 private n15-oracle-v4-draft01/evidence에 전후 SHA가 같은 상태로 이동 보존했다. 공개 검토 대상은 quality/release/evidence/oracle-v4/revision-02다. 실제 과거 실행 bundle은 이동·수정하지 않았다.

## 실제 파생 결과

| 원래 실행 | 원래 통과 | 파생 통과 | 변화 |
|---|---:|---:|---|
| B0 전체 공개336 | 227 | 228 | C02 정답 집합 교정1 |
| C8 validation01 | 79 | 80 | C06 이전턴 정답 집합 교정1 |
| C11 validation02 | 83 | 84 | C02 정답 집합 교정1 |
| 나머지9개 baseline/validation 대상 | 원래 값 | 동일 | 0 |

C9의340ml 오류는83/84 FAIL로 남는다. 교정slot밖의판정·필수오류·완료여부는변하지않았다.

C11 두 반복을 모두 동일한 새 validation84 정답으로 비교하면 각84/84, 고객40/40·20/20 및 경영주15/15·9/9, incomplete/mandatory0이다. 새 정답으로 재채점한 B0 validation59/84 대비 두 반복 각각25개 개선·회귀0이다. C5 대응 첫 반복84/84 대비0개 개선·회귀0, 둘째83/84 대비1개 개선·회귀0이다. C10 대응 반복은둘다84/84로동일하다. 원래 점수와 새 점수를 섞어 개선폭을 계산하지 않았다.

## 구현 및 자체 검사

신규 rescore_public_oracle.py는 정확 patch·공개 경로·typed normalized·원본 재현·전run cohort·독립 감사·앱 source/runtime 결속을 검사한다. check_release_evidence.py는 새kind에서만 명시적인 파생 점수를 허용하며 기존 live 경로의 기준은 유지한다. run_nl_eval.py는 새 frozen-best 증거를 위한 분기만 추가했으며 호출·retry·reserve 경로를 바꾸지 않았다.

자체 release121개(기존89+신규32), runner35개 PASS. 신규 시험에는 질문/진단 비노출, 임의 string을 boolean/enum/수치에 넣는 우회, 거절 경로 read0, 두slot외 변경, 원본 실행과 새 점수의 분리, 실행 누락, 감사 누락·자기 감사, 원본binding 교체, 무관source 변경, 다른모델·재시도한도·중복validation freeze 거절, 인접 정상 derived checker/동결 경로가 포함된다. 보호 원문 없이 합성 freeze fixture로 시험했다.

## 독립 검증과 후속

본인은 평가기구 구현자이므로 위 자체 시험을 독립 검증으로 세지 않는다. final_ux_state의 별도 기술반례/전수 private audit, 정확 revision/cohort/derivation 해시의 독립 attestation, 최종 배포 source의동일runtime 계보가 필요하다. 현재 bundle.review-pending에는독립감사ref가없어출시경로에서자동통과하지않는다.

보호v3의새공개정답영향은별도독립검토에서 dataset/state/난도/의미독립성불변PASS를받았으며 원문은이작업에서읽지않았다. 실제보호평가최초1회·역할QA·UX·G5/G6는아직미실행이다. 이 문서는자체파생재현결과이며제품완료또는최종채택선언이아니다.

## 독립 반례 후 좁은 보완

final_ux_state는23run/12derived의1,260행을 별도로 전수 재현해 데이터 대칭성과 원본 보존을 확인했다. 별개로 보호 평가 직전 경로에서 원 execution의 pending_attempts=1을 거절하지 않는 반례를 찾았다. 이는 원본 실행의 실제 pending이 발생했다는 뜻이 아니라 합성 변조를 거절하는 검사가 빠졌다는 의미다.

verify_holdout_freeze가 기존 Checker.nl(original,best=False)를 재사용하도록 수리했다. 원래83/84 FAIL 점수는 그대로 인정하되 원 실행의 pending/전체분모/provider/시각/정합성을 검사한다. runner_complete, 실제92턴, unknown0, 원관측 attempt/사용량/비용 합계도 대조한다. pending1·사례누락·음수token·unknownprovider·미완료·턴누락·음수비용·unknownusage의8변형 모두 거절하는 자체 시험과 정상 인접 경로가 통과했다. 신규 시험은33개다.

코드 해시 갱신에 따라 revision02와 중간03을 보존하고 revision04에 동일23run 결과를 새로 산출했다. 새 정답/원본 관측/실제 호출은 바뀌지 않았으며 점수 변화도0이다. 최종 독립 검토 대상은 `quality/release/evidence/oracle-v4/revision-04`와 private `n15-oracle-v4-local-audit-revision-04.json`이다. 독립 재검토와 최종 감사ref 발급은 여전히 선행조건이다.

## 독립 검증 완료

정식 `oracle-v4-independent-audit.json`(SHA6378b27c97b42c6c711a0f093576c8298c57351fd570fec6aa3f0a6e610cc5b0)이 revision04/cohort23/derivation12와 결속됐다. final_ux_state는1,260행의 원래·새 정답/원관측·normalized 전수 동등성, 신규33시험 및별도freeze15그룹을독립검증해PASS로판정했다. pending반례는차단됐으며정상84/84파생경로와원본84/83분리는유지됐다. 발급된 실제auditref를연결한12bundle전수검사도독립PASS다.

실제원관측·원본29·runtime50·장부불변,추가모델0을유지한다. 이로써파생평가기구기술검토는완료됐으나최종bundle신규발급은새commit/source계보후이며, 최종rootfreeze/미실행보호v3/QA/UX/G5/G6를대체하지않는다.
