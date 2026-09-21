# UX baseline 중단 후 복구 측정 — 독립 상태·평가 검토

판정: **동일 B0의 전체24회 추가 측정 1회는 조건부 허용 가능**. 현재 B0 UX는2PASS/1FAIL/21not_run으로 미완료이며, 추가 측정의 허용이 기존 실패의 해결이나 품질 PASS를 뜻하지 않는다. actual recovery repeat는 이 검토에서0이다.

## 확인한 증거

- `artifacts/private/run-20260921/ux-baseline-b0-v2-01/result.json` SHA4989b1053468134ff8a3099b951493ba483687f57fb14de49db48ea4e87b4209. UX-BENCHMARK-v2,8 workload×각3회=24계획, clear-1의3회만실행(2PASS/1FAIL),나머지21회미실행,complete=false.
- 실제3calls는HTTP200/200/502,모두provider_called=true 및usage확인,측정비용$0.013441. stopCode HTTP_MODEL_ERROR_OR_UNKNOWN_USAGE_STOP는포괄코드이고 이실제실패는unknownusage가아니다. 원모델출력/하위검증원인 증거가없으므로일시적네트워크장애로단정하지않는다.
- 실패화면은후보선택대기60초timeout으로표면화됐다. 보고서의failureSnapshot은고객역할/revision1, requests/orders/needs/notifications/proposals모두0이다. 이증거범위에서불확실거래변경이나중복주문복구가아니다. 새독립브라우저세션의측정반복이기존거래를재발행하는상황과구분된다.
- workloadHash613bbb701a155913f02f2de4bf6f45fef793b1d3fa5e61cd5a5211a25e32d71d, seedHash4cb10e899c9706bb0a9278b458bd7b70d3c34bf28f649b62ffae0894794a2b45,clock1789959600000. 기록된제품/UI/domain15개source hash와5개harness hash는추가측정에서도보존해야한다. 서버prompt/model/API도B0임을별도binding으로재확인한다.
- metrics.compare는재직렬화summary를믿지않고각run원자료를재계산하며baseline/best모두각3회정상완료를요구한다. 기존 실패run을그대로비교기에넣으면통과할수없다.

## 계약 해석

ADR003의 ‘기준선 dev+validation336 case만1회’는NL기준선이며,NL B0는이미227/336 FAIL로보존한다. UX는동일8 workload각3회 baseline/best측정과실패분모공개·고정기준을요구한다. docs15는실제실패기록/독립정답/제한복구를허용하지만원인불명실패를통과횟수만으로닫지못하게한다. 따라서UX불완전측정이추가자료확보자체를영구금지하지는않으나,결과가좋을때까지baseline을교체하는해석은허용되지않는다.

다음조건이면기존명세내 bounded 복구측정으로볼수있고새로운합격선ADR은필요하지않다. 기존source/workload/분모/비교판정을변경해야한다면이판정밖이며새독립검토가필요하다.

1. **사전에한번으로고정**: 새run_id의전체24회를딱1회추가한다. 실행전이run을회복측정비교cohort로지정하며성공후더유리한run을선택하지않는다. 중단없이24개를임의강행하도록회로차단을변경하지않고,같은원인재발시다음동일추가실행을자동허용하지않는다.
2. **원본실패영구보존**: 기존2/1/21과새24계획의각PASS/FAIL/not_run을모두공개한다. 총계는계획48,실행3+새실행수,실패1+새실패수,미실행21+새미실행수로기재한다. 기존실패를원인해결·100%성공·삭제된warmup으로바꾸지않는다.
3. **전체동결**: B0제품/서버/model/prompt/catalog/seed/clock/viewport/workload/harness동일,8×3고정. freshprofile과동일seed초기상태만사용한다. baseline호출에는C1또는fixture를사용하지않는다. 이전정상2회를재활용해새22개로완성하거나실패case만재시도하지않는다.
4. **측정과품질분리**: 새cohort가24/24정상일때그cohort의각workload최대조작/이동·중앙처리시간을후속best와비교할수있다. 이때기존B0오류는원인불명으로남고baseline안정성문제도보고한다. 새cohort하나라도실패/누락이면상대편의성게이트는미완료로유지한다. 새로운best는필수정상100%,조작/이동증가0,중앙값10%악화금지·모든필수오류0을그대로충족해야한다.
5. **예산동일장부**: 추가실제모델turn수와실패·retry를global2400/$15 Budget50 ledger에계상하고best/holdout/UX/G5G6필수분을먼저예약한다. unknown이발생하면기존중단/재개계약을그대로적용한다.

## 반례와 거절 경계

- 새run이빨라보이는case만골라기존성공과혼합하면중앙값선택편향이다. 금지한다.
- 첫run의실패를‘baseline은원래나빠도됨’으로간주해비교기complete검사를제거하면필수정상100%·고정분모를훼손한다. 금지한다.
- 새run도502인데세번째·네번째를연속실행하면원인새증거없는반복으로docs15위반이다. 내부작업미완료를유지하고원인진단/별도정책절차로돌아가야한다.
- 새run24PASS가나와도NL227/336실패또는기존UX502가없어진것은아니다. 출시자격은C1/best의독립품질·G5/G6에서별도판정한다.

이 검토는 증거 파일·계측 코드·명세의 독립 읽기 검토이며 새 브라우저/모델 실행은 하지 않았다. 평가 기준 완화, 상품 정책 변경, 동의 생략을 승인하지 않는다.

## ADR-006 proposed 최종 독립 검토

소비 컨텍스트: CTX-N02-v6 `0555063cc1bca9224124b2522d9371bf8ec8178ada49083c9bd306ae0d738a3b` + ADR-006 proposed SHA `4334f594e1e11419da3118cb7253c01b4ab5b6313c444919994360c36899bad7`. 상태/실패 검토자는 초안 작성자와 다르며 다른 제품 검토자의 결론을 읽지 않았다.

판정: **채택 동의**. 초안의 사전 지정 ID `ux-baseline-b0-v2-recovery-01`, 동일 B0·workload·harness, 전체24회 딱1회, no-retry/회로중단 보존, 원본2PASS/1FAIL/21not_run 및 누적48분모 공개, 새실패 시 NOT_READY/세번째실행금지, 동일 Budget50 장부가 앞선 독립 검토의 조건을 모두 만족한다. NL B0 227/336 FAIL 보존과 새cohort24정상일 때만 상대비교를 허용하는 구분도 명확하다. 기존 실패는 원인미확정이며 새정상결과만으로 해결됐다고 표현할 수 없다.

새로운 반례로 검토한 ‘새run에서빠른성공만고르기’, ‘원본2개+새22개혼합’, ‘unknownusage를근거없이실패0처리’, ‘C1모델을B0로라벨교체’, ‘세번째run을새ID로우회’는 규칙1/2/3/5/7에 의해 거절된다. 실제 release checker에서는 지정 ID만이 아니라 원본/추가 artifact hash·source/model/prompt/workload 동일성·분모 연결을 확인해야 하며, 이 문서 동의는 그 실행기 구현이나 실제 측정 PASS를 대신하지 않는다.

추가 모델 호출0, 브라우저 재측정0. 채택 메타 갱신 후 context/ACK 및 release-checker 정상·변조 독립 회귀가 남는다. C1 dev30/validation84 계획은 exactPreview 및 명시실행 GO까지 대기한다.
