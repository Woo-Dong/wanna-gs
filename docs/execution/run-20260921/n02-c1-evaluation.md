# N02 C1 공개 dev30 독립 평가

판정: **선별 dev 측정 완료 / C1 채택 불가 / validation 보류 권고**. 동일 공개30사례에서 B0보다통과수는늘었으나7개기존정상사례회귀,응답실패증가와지연악화가있다. full dev252 또는validation84를통과했다는주장이아니다.

## 동결·실행

- source `3984a85be548affea158e28c98db551721e546c0`, immutable Preview dpl_HrbM7qiBR59ooDa4nhnSQBmjCmQT, prompt retrieval-enum-v2, model gpt-5-mini-2025-08-07, catalog248/f2696…. 로컬root aa3406d와필수26파일git source byte동일확인.
- config SHA `b535ac0b7fdd9a41d2648b7aa447dc8e6311f8c54e68f974065e273ea9aa0094`, immutableREADYproof SHA `f288b3d964d7355797601776d33a65a7dc7e7f8a2ea7ea0c9d104e35ecfd49d8`. API자체source attestation한계는기존대로유지한다.
- 사전고정 dev30 dataset SHA `0d394d463679189b082390219e74725e7a310f5173a5613d0bd87b5af85d26c7`. 모든고객범주각2개,경영주각1개+M01/M03/M09추가1개를ID순으로선택하고C1첫호출전에동결. 실행후사례변경0.
- 명시GO는dev30만. run_id `237e33f7-8ff1-4908-aec6-8b810a18808d`, fingerprint `92636e59dae390fe58ce3837f2d2dc665d1e485b28f5bd6c553850d09093bb51`. validation/holdout호출0·holdout본문읽기0.

## 같은30사례의전후비교

| 지표 | B0 저장관측 | C1 실제관측 |
|---|---:|---:|
| 통과/전체 | 17/30 | 22/30 |
| 응답미완료 | 3 | 6 |
| mandatory오류 | 0 | 0 |
| 실제user turn호출 | 34 | 33 |
| P50 HTTP응답(ms) | 2337 | 3138 |
| P95 HTTP응답(ms) | 4483 | 15560 |

개선12개와회귀7개를따로보존했다. 회귀ID는 C02-dev-001,C03-dev-001,C06-dev-002,C08-dev-001,C08-dev-002,C09-dev-001,C09-dev-002. 단순순증5개가핵심범주회귀를상쇄하지않는다. B0비교는기존저장관측만읽었으며재호출하지않았다. 두관측의반복수/설정이다르므로best동일설정validation repeat로세지않는다.

C1계획34턴 중 C06-dev-002 첫턴이실패하여후속1턴은호출하지않았다. 사례전체를실패분모에남겼다. 실제33회모두provider_called/usage확인,재시도0,pending0,stop_code=null. 실제토큰601671,추정비용$0.1744575,평균약$.00528659,최대attempt$.0080855. 전체공유ledger는upper467calls/known417calls/unknown0,누적측정$1.91076225+priorplanning2.5=$4.41076225이다. prior50은실측과구분한다.

## 실패 근거

- 5건은usage output_tokens=1600이며고정출력한도에도달했다. C02-dev-001(input19501),C03-dev-001(19487),C06-dev-002(2871)는보존된Vercel model_incomplete 로그의reason=max_output_tokens와일치하여원인을확인했다. C08-dev-001/C09-dev-002는동일상한관측이지만이보고시점확보로그는앞의3건이므로원인확정범위를구분한다.
- C08-dev-002는안전진단EXACT_WITH_UNKNOWN_CONDITION으로조건미확인후보의정확표시를서버가거절했다. 동의·불확실성검증을제거해복구하면안된다.
- C09-dev-001은정답외primarySKU를추가해incorrect_candidate. M05-dev-001은상충지시를clarify대신modify로제안했다. 이것은단순전송실패와분리된의미오류다.
- 전체실패8개의공개입력/expected/실제응답/attempt는private n02-c1-dev30-analysis/public-failures.json,원전송기록은n02-c1-dev30에보존했다. raw로그에없는세부모델사고를추측하지않는다.

## 다음단계경계

C1은기술검토/strictschema실제수락을거쳤지만품질채택조건은충족하지못했다. 고정validation84를지금사용하기보다새가설의제한된복구후독립기술검토와별도GO를권고한다. 후보기록/실패/개선·회귀를모두유지하고정답·분모·합격선을낮추지않는다. 비용예약$.008/attempt보다관측최댓값이크므로다음후보의input/schema/output상한을반영해필수예약을다시산정하고총2400/$15는유지해야한다. 현재C1 frozenconfig의960/$7.68은소급수정하지않는다.

UX B0 복구는별도과정에서실패해비교NOT_READY로남아있다. C1의NL측정완료가그UX미완료나G5/G6를대신하지않는다.
