# C11 1회 시도·필수 예약 정책 독립 검토

reviewer `final_ux_state`, 2026-09-22. **정책 제안 조건부 PASS**: ADR003의 “최초 포함 최대3회”는 상한이다. 새 실행 전 max_attempts=1을 고정하여 모든 user turn을 최초1회만 실행하고 최초 실패를 그대로 FAIL/incomplete로 보존하는 것은 제품 합격선 완화가 아니다. 현재 코드는 여전히3회로 고정돼 있으므로 구현 완료/기술PASS는 아니다. 과거 C10 두 보호셋 포함 실패를 지우거나 다시 실행할 권한을 주지 않는다.

## 확인한 목적·현재 코드

ADR003 오류처리/반복/전체분모, docs23·25, C10 계약, scripts/run_nl_eval.py의check_inputs/Runner/resume/Budget, scorer 최소·회귀 판정, UXv3/역할QA/G6 준비계획을 읽었다. 현재 runner의range(...,3), remaining*3, retry==2를 함께 바꾸어야 하며 config만 추가해 예약만 줄이면 실제 시도와 불일치하므로 불가하다. src/server/provider.ts의SDK maxRetries:0은 유지한다.

동일 데이터·정답·case/turn분모, customerclear≥95%/uncertain≥90%와 merchant각기준, incomplete/mandatory0, C5 대응정상·핵심범주회귀0, validation 두 독립 run의 동일config와 각각PASS, freshholdout 최초1, UX·역할QA·G5/G6가 그대로여야 한다. 응답 실패를 건너뛰어 성공분모로만 계산하거나 모델오류를 미식별 성공으로 바꾸지 않는다. 첫턴 실패 뒤 불가능해진 후속턴은 미실행 증거로 남고 제품게이트에 그대로 반영해야 한다.

## 호출 산술 및 독립 임시Budget 확인

실장부를 열지 않았으며 root가 제공한 upper1786/$11.0094737을 기준으로 계산했다. 남은 호출614/비용$8.9905263은 이 관측값의 산술이며 이후 실제 직전 장부가 권위다.

| 진입 | 이전upper | 해당stage 최대turn | future예약 | 첫 호출 전체guard |
|---|---:|---:|---:|---:|
| dev |1786|34|372=validation184+holdout92+UX84+QA/G612|2192|
| validation01 |1820|92|280=validation92+holdout92+96|2192|
| validation02 |1912|92|동일280|2284|
| holdout |2004|92|96|2192|

현재 Budget.reserve를 실제 공유장부와 무관한 임시 ledger에 import해 위4개 허용을 직접 확인했다. validation02 이전116추가호출이면2400에서 허용,117추가면2401/CALL_RESERVE_STOP을 확인했다. 비용합계가 정확히20이면COST_SOFT_STOP도 확인했다. 이는 제안1회용 reserve값에 대한 Budget기구 검사이며 아직 미구현 max_attempts 루프 검증이 아니다.

계획전체 신규34+92+92+92+84+12=406, 완료예상upper2192로614중208이 계획 밖에 남는다. 동일validationconfig가 두번째에도 다음validation92를 예약하므로 진입상 여유는116이며,208을 후속실험 자유예산으로 쓸 수는 없다. 새로운 후보·추가QA·장애가 생기면 남은 필수예약과 비용을 다시 계산해야 한다. freshholdout의 실제확정turn수가92인지 실행 전에 검증하고 다르면 계획을 재결속한다.

## 비용 및 UI 필수 호출

96의 후속예약은 UX두arm84 + 고객QA3 + 경영주QA3 + G6 2 =92개의 실제 계획 호출을 포함하고4개 운영여유를 남긴다. 고객별도fixture12와 SQL/반응형/정책/asset감사는 모델호출0으로 설계돼 있다. 따라서 현 고정 계획은96내에 들어간다. 단, QA3/3/G62만으로 실제 여정 전체가 자동PASS가 되는 것은 아니며 실패 뒤 남은4를 자동재실행허가로 사용하지 않는다. 새 여정에 모델호출이 필요하면 미리 예약에 추가한다.

호출한도 통과는 비용보장이 아니다. 각 승인config에 mandatory_cost_reserve_usd를 근거와 함께 명시하고$20·prior50/$2.50·unknown$.05·pending계상은 유지해야 한다. UX/역할QA의 현재cap 잔여를$.05로 예약하는기구도 유지한다. 현 제안에는 미래비용값이 명시되지 않았으므로 가격/실측근거의NL예약과 UI96×$.05=$4.80을 포함한 금액을 root가 확정해야 한다. 모델응답실측/unknown에 따른COST_SOFT_STOP은 override하지 않는다.

## 구현 채택 조건과 위험

1. max_attempts는 최초포함 **turn별 총시도**다. 필드생략은기존3, 명시값은bool을 제외한정수1..3만허용한다.0/음수/4/float/string/null/bool은거절한다. 새C11 dev·두validation·holdout 모두명시1로고정한다. 과거config/장부/결과에기본값을삽입해fingerprint를바꾸지않는다.
2. check_inputs뿐아니라Runner직접진입에서도동일검증하고, retry loop·마지막시도break·현재stageremaining예약을같은effective cap으로계산한다. cap1에서는transient첫실패를journal한뒤retry/sleep/replay없이그case실패로남긴다. auth/quota/source/pending의기존STOP은더이상완화하지않는다.
3. configfingerprint·resume에cap을포함해중간변경을거절한다. validation동일fingerprint외에 **validation→frozenbest→holdout의effective max_attempts도결속**해야한다. 현재CANDIDATE_KEYS에이키가없어두validation만1이고holdout3인변조를별도로막아야한다. 모든cap변경은새source/config바인딩으로명시한다.
4. 기존source/runtime/model/prompt/catalog/평가/coverage/서버비밀/원장/출력보존guard를유지한다. runner hash변경으로옛UX/QA draft의budget source는stale이되므로실행전새draft로재결속하고과거증거를수정하지않는다.
5. 자체시험과별개독립검사에서기본3회유지,cap1/2의최대호출·실패journal·후속턴미실행,잘못된cap거절,resume/holdout cap변조거절,2400/2401·20비용경계및불변제품분모를확인한다. paidcall없는mock/tempBudget으로가능하다.
6. 재시도감소는네트워크일시실패에취약해져필수incomplete0탈락가능성을높인다. 이는선택한엄격한실행조건이지실패면제가아니다. 과거retry가능결과와새1회결과의설정차이를표시하고,retry감소자체를모델정확도/지연개선의인과근거로주장하지않는다.

C10 aggregate76/84·고객uncertain12/20·wrong_action8과기존실패holdout은그대로은퇴보존한다. 이번검토는새holdoutv3의제작·검토·실행승인이아니며보호본문을읽지않았다. 실제앱/평가소스수정0, 실제모델·HTTP0, 공유장부읽기/쓰기0. 임시Budget7검사와이private정책보고만작성했다.
