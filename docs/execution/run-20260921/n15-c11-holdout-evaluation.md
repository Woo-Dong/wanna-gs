# N15 C11 보호 holdout-v3 최초 1회 독립 평가

**75/84 FAIL.** 고객 명확 36/40(90%), 고객 불확실 17/20(85%), 경영주 명확 13/15(86.67%)가 각각 95%/90%/95% 최소에 미달했다. 경영주 불확실은 9/9로 통과했다. incomplete 0·mandatory 0이며 전체 성공률로 역할별 미달을 상쇄하지 않는다. 후속 고객/경영주 QA·UX·G5·G6 실제 호출은 시작하지 않았다.

## 목적과 독립성

목적은 공개 oracle-v4 수리 이후 동일 C11 앱의 미노출 보호셋 품질을 실제 모델로 확인하는 것이다. ADR008의 공개 2개 oracle slot 수리는 보호 원문·정답·분모를 바꾸지 않았다. 기존 C11 validation의 원래 84/84·83/84와 파생 84/84·84/84, 앞선 C5/C10 holdout FAIL도 그대로 보존한다. 이번 FAIL을 공개 oracle 수리나 과거 성공으로 덮지 않는다.

평가자 `method_auditor`는 앱 구현자 `root`/`research`와 다르다. 자신이 작성한 scorer/runner/rescore 장치를 자기 독립 검증으로 세지 않으며, 기존 research/builder 및 final_ux_state의 별도 장치 검토를 근거로 구분한다. 보호셋은 evaluator가 작성한 뒤 다른 검토자가 전수 검토했고 revision01/02 FAIL 및 revision03 DATA-REVIEW PASS 이력을 보존했다. 데이터 검토 PASS는 실제 모델 품질 PASS를 뜻하지 않는다.

## 정확 결속과 실행

- 현재 source `e727b99a640743c744082f8a3cf754260f0d755a`, source 47개 current/Git 동일. 원래 C11 source `cd29a2bc3be8c80fa00c03c2985f06819bef7255`에서 앱 runtime 50개가 동일하며 runtime hash `d49c13dcbe3f5b358b8f7fb80d4316a68fd738c9f83a0e6395ec6f56a5dfbb9d`다. 실행 종료에도 source/runtime 불변을 재검사했다.
- context `context-n15-v22.json` SHA `95596d129dc5f891bcabe66a00913f5382555852625901150481de710c07c042`, 102개 입력 ACK.
- Production `dpl_38tqWijj9QiCzEHUWQotY85v2phy`, `https://wanna-2lrfh4jpe-beatrain-4635s-projects.vercel.app`, READY/target production/exact source. 이는 Git·배포 artifact 결속이며 응답 자체의 원격 코드 암호학적 증명을 주장하지 않는다.
- model `gpt-4.1-mini-2025-04-14`, prompt `customer-classification-v11`, prompt SHA `16e967e7f0adf1cfff7ff16e994a0e82e6ff09cf09ac6cc2e5fc0303f51a6d5a`, catalog248 hash `f2696abe92521e3ff8f9ab43cb36a1d297a6fd23d272e239605b49fab4343b1e`.
- root freeze `2026-09-22T04:24:34.496707+00:00`, freeze SHA `564d13895f5a01567932565ccc59ff89a4e6db6376f5890d9279f04411144dea`. 두 실제 독립 validation run의 원본/파생 체인과 동일 oracle의 B0/C5/C10 회귀 0을 확인한 동결이다.
- approved config SHA `4a4e39c0ae34d1a61a818fff123f56143dee5e22d11dd144cd5f01fe12092132`; 준비 단계 approved:false 구성 및 과거 초안도 보존했다.
- 보호 dataset `5854b370a954fee49bfedf1834d24427267adc79499cd7ecc5e62925ba75518d`, 84case/92turn, 고객60/경영주24, clear40+15/uncertain20+9. 보호 SQL state SHA `9cbbd15d484820f15b232dfa6514bd7979fb93a714c6301d82b920f5785b7d38`.
- run `a32976ff-e911-448d-b1fc-f798b3a80254`, fingerprint `8b1b72d3071a60b7fba709f35021c7190087fd64912854bb260588532499d052`. 실행 시작 `2026-09-22T04:32:43.124799+00:00`, 종료 `2026-09-22T04:36:20.403319+00:00`. 시각은 원본 파일 birthtime/mtime의 실행 경계 근사이며 provider 시각이 아니다.

명시 GO 후 보호 전용 PLAN_VALID 84/92/96, fresh 장부·pending 0·미사용 dataset claim·source/context·freeze·보호 파일 해시를 확인하고 최초 한 번 실행했다. 이 dataset claim은 해당 run에만 연결된다. 앞선 retired 보호셋을 다시 호출하지 않았고 이번 결과를 보고 재실행하거나 정답을 바꾸지 않았다.

## 역할·범주·관측 실패

| 역할/입력 | 통과/전체 | 최소 | 결과 |
|---|---:|---:|---|
| 고객 명확 |36/40|95%|FAIL 90%|
| 고객 불확실 |17/20|90%|FAIL 85%|
| 경영주 명확 |13/15|95%|FAIL 86.67%|
| 경영주 불확실 |9/9|90%|PASS 100%|

고객 C01 8/9, C02 8/8, C03 7/8, C04 7/7, C05 3/6, C06 4/6, C07 6/6, C08 5/5, C09 5/5. 경영주 M01/M02/M03/M05/M06 각각3/3, M04 1/3, M07/M08/M09 각각2/2.

실패 9건의 배타적 관측 분류는 잘못된 primary 식별 1건, 명확 입력에 불필요한 질문 1건, 불확실/미식별 입력에 clarify 또는 unidentified 대신 candidates를 반환한 3건, 다턴 이전 응답의 행동 오류 2건, 경영주 복원 명령의 복합 필드 불일치 2건이다. 다턴 2건은 최종 응답만 보면 정답이지만 이전 실제 응답까지 채점하므로 실패다.

경영주 2건의 필드 차이는 intent 1, maxQuantity 1, restorePrevious 1, budgetLimitKrw 1, excludeProductIds 1이며 scope 차이는 0이다. 여러 필드가 한 사례에 함께 나타나는 중복 집계이므로 합계를 실패 사례 수로 사용하지 않는다. 관측·분류 집계는 `n15-c11-holdout-cause-classes.json`에 별도 보존했다.

이 분류는 실제 응답과 고정 oracle의 의미 차이를 설명한다. 검색 단계에서 상품이 제외됐다는 증거나 복수 catalog 항목 때문에 실패했다는 직접 증거, 새 source-grounded oracle 결함은 현재 진단에서 확정하지 않았다. 모델 내부 원인으로 단정하지 않는다. 후속 독립 감사는 실제 의미 오류 7건과 oracle 표현 한계가 있는 2건을 구분했다. 후자의 가능성을 모두 유리하게 보더라도 고객 명확·불확실 및 경영주 명확 최소 미달은 남는다. 별도 [독립 감사](n15-holdout-state-closure.md)의 원시 wire/adapter 대조를 연결하며 자동 재채점이나 PASS 전환을 하지 않는다. 원본 FAIL·기대·분모·점수는 그대로 유지한다. 보호 원문·상품/사례 ID·정답 값은 공개하지 않는다.

## 사용량과 종료

92계획 turn/92실제 HTTP/92 provider 호출, HTTP200 전부, retry 0, usage unknown 0, provider unknown 0, pending 0, stop null이다. 전송·형식상 실행 완료와 품질 FAIL은 구별한다. 토큰 1,372,802, 이번 추정비용 $0.5634956, 최대 attempt $0.0066804, P50 2141ms/P95 3209ms. 비용은 청구 확정액이 아니다.

종료 공유 장부 upper **2096회/$12.7565577** = known2046회/$10.2065577 + prior50/$2.50 + 과거 usage unknown $.05. prior는 실측이 아니다. ledger SHA `f815f4085afad469812a9933bef4b4e21733b33e11b67efad3212b468bd896b7`. max_attempts1·후속96회/$4.80·다음 unknown $.05·총2400회/$20 가드를 그대로 유지했다. 남은 호출 상한은304회이며 예산 잔량만으로 후속 필수 게이트를 통과했다고 간주하지 않는다.

## 증거와 후속 중단

`quality/release/evidence/c11-holdout-v3/`에 원문 없는 report/execution/binding/independent-report/bundle을 발급했다. bundle SHA `5a218251522a597f380d8b94cfa5d92dd9a7a9d9a92bf265fa0ffb36535fb2df`, independent-report status FAIL. 공개 분모·실행 회계·해시 결속을 `Checker.nl(best=False)`로 검증한 구조 검사만 PASS이며, 품질을 요구하는 경로는 `NL_MINIMUM_FAILED`로 실제 거절했다. 원본 실행과 전체 개인별 채점은 private `n15-c11-holdout-01/` 및 `n15-c11-holdout-01-analysis/`에 보존했다.

보호셋 반복·사후 정답/라벨/분모 수정·raw 구현자 제공 0. C11은 파생 validation 선행조건을 충족했으나 최종 보호 품질에서 실패했으므로 출시 가능한 best로 완료 처리하지 않는다. 역할QA/UX/G5/G6 준비물은 미실행이며 추가 실제 호출은 중단했다. 추가 복구 여부는 이 보고서가 승인하지 않는다.

## D50 이후 범위 변경

사용자가 추가 품질 개선을 종료하고 큰 기능 문제가 없으면 배포/main 마무리를 지시한 D50에 따라, 추가 후보·보호평가·UX 최적화를 종료했다. 이 보고서의 품질 FAIL과 원래 G5 NOT_READY는 그대로이며, 독립 기능 QA·최종 배포 검증은 별도 완료 범위다. D50은 이 점수나 원래 품질 기준을 PASS로 바꾸지 않는다.
