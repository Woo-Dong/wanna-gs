# C7 정책·상태 독립 감사

판정: **FAIL — 경영주 수정 어댑터의 명시 수량 상한 누락 1건(P1)**. 고객 C7 prompt의 성능 판정과 별개인 기존 구현 결함이다. 정책의 새 결정을 요구하는 공백으로 분류하지 않는다. 현재 통합 후보의 최종 제품 완료를 차단하며, D47 범위를 확대해 자동 수정하지 않는다.

- reviewer: `holdout_revision_review`; 앱 작성자가 아닌 상태·수량·복구 관점의 독립 검토자. 제품 관점 검토자의 결론을 읽기 전에 이 초기 판정을 확정했다.
- audited source: `63614f9663a607373e0c7e9d43cb7e4616406b34`, branch `codex/n08-customer-recovery`.
- consumed context: `CTX-20260921-N08-v16`, SHA256 `a9048d25ecce920ba8d9e2c38d9fc262381abf10c5612d1b02d64a6b00111bc6`.
- source fingerprint: `15e1ede83a81eb3e21fbbf2a5a7572f58344d3ab6be3ebb0d9185d37ae019c97`.
- 감사 중 HEAD가 `73a364860cb90f9bc9de4e186390411bce9dfd21`로 이동했으나, audited source와 HEAD 사이 `src data public tests/domain tests/merchant` 차이는 0개였다.
- 범위: card/CORE/유효 결정, docs13/17의 처분 규칙, domain/SQLite runtime·schema, 경영주 controls와 기존 시험 근거. `wanna-gs-verify` 적용.
- 금지 준수: 앱·정책·장부 변경 0, 실제 모델 호출 0, 보호 평가 원문 사용/노출 0. 쓰기 산출물은 이 보고서와 조정자가 추가 요청한 최소 재현 파일이다. 재현은 public seed의 메모리 사본이며 IndexedDB/실제 사용자 상태를 변경하지 않았다.

## P1: 보류 상품을 다시 실행 가능하게 만들 때 명시 상한이 누락됨

근거: `src/components/merchant/model.ts:8`은 `maxQuantity`를 **기존 `current.lines`에만** 매핑한다. `MerchantView.tsx`의 `applyAnswer`는 이 결과를 `proposal.revise`에 전달한다. `src/domain/engine.ts:51`은 매핑이 없는 SKU의 이번안 상한을 무제한으로 해석하고 최신 수요·예산으로 다시 계산한다.

재현 결과(실제 함수와 SQL 엔진, 모델 응답은 정상 구조화 값으로 직접 공급):

1. public seed의 정상 조건 상품에 고객 동의 수요 5개를 생성하고 경영주가 검토한다.
2. 이번안 예산을 0원으로 변경한다. 실행 line 0개, 보류 1개가 된다.
3. 정상 수정 해석 `{budgetLimitKrw:50000, maxQuantity:2, scope:current}`에 해당하는 제약을 실제 `proposalChange`에 전달한다.
4. 어댑터 출력의 `maxQuantities`는 `{}`. 도메인 재계산 결과 상품 수량은 **5개**다.
5. 별도의 명시 묶음 승인까지 수행하면 실제 메모리 SQL 주문도 **5개**로 저장된다.

```json
{"before":{"lines":0,"deferred":1,"budget":0},"after":{"lineQuantities":[5],"mappedCapCount":0,"requestedCap":2},"approvedQuantities":[5]}
```

기대값은 CORE-05, AC-07의 정확한 현재 묶음 수정과 ADR-005의 이번안 `maxQuantity`→`maxQuantities` 매핑이다. 새 예산에서 다시 계산한 실행 품목에도 명시 상한 2가 적용되어야 한다. 일반적인 상한 증가 허용 여부를 새 정책으로 추측하지 않고, 명백한 **상한 초과** 반례만 결함으로 확정했다.

고객 동의 수량 5를 초과하거나 사용자 승인 없이 발주한 반례는 아니다. 경영주가 먼저 받은 변경안에는 상품별 최대 2가 표시되지만 반영 후 계산·승인 가능 수량은 5가 되어 명시 조건을 위반한다. 수량·예산을 함께 수정하는 정상 업무에 영향을 준다. 별도 승인 단계와 최종 수량 표시가 존재해도 수정 정확성 실패를 해소하지 않는다.

기존 `tests/merchant/model.test.ts`는 실행 line의 cap 축소와 기존 line 증가 금지를 검사한다. 보류 line의 재진입과 복합 예산+수량 수정은 검사하지 않아 기존 44 PASS와 이번 반례가 양립한다. 모델이 정확한 해석을 반환해도 발생하므로 NL 점수의 실패로 재분류하지 않는다.

처분: **기존 정책 구현 결함, 별도 복구 작업 필요**. D47 고객 후보 안에서 경영주/거래 동작을 몰래 바꾸지 않는다. 복구할 경우 작성자와 독립 검증자를 분리하고, 복합 수정·보류 재진입·기존 정상 묶음/undo·정책 상한 회귀를 검사한 뒤 영향을 받는 통합 증거를 갱신해야 한다. 기준 완화나 제외로 닫지 않는다.

새 정책이나 경영주 모델 prompt 변경은 이 반례를 고치는 데 필요하지 않다. 입력 구조화 제약의 예산·상한·scope는 이미 정확하며, ADR005가 상한의 단위/적용을 정했다. 손실 지점은 UI→domain 어댑터다. 별도 복구가 계약 표현을 바꾸어야 한다면 단일 소유자 계약 절차로 다루되 의미/문턱 변경으로 우회하지 않는다.

조정자의 후속 요청에 따라 `artifacts/private/run-20260921/c7-policy-state-audit/repro.mjs`를 남겼다. 저장소 루트에서 `node --import tsx artifacts/private/run-20260921/c7-policy-state-audit/repro.mjs`를 실행하면 현재 구현은 실제 승인량 `5 !== 2`로 exit 1이다. 구현자가 정상 기대값을 낮추지 않고 수정한 뒤 같은 명령이 exit 0이어야 한다. 이 파일에는 protected 평가 사례가 없다.

후속 정상/인접 회귀 대상: (1) 이미 실행 가능한 line의 예산+cap 축소, (2) 실행 line과 보류 line이 섞인 묶음에서 같은 cap 보존, (3) 예산만 수정할 때 기존 명시 cap 유지, (4) undo로 이전 정확 제약 복원, (5) cap 아래 MOQ이면 과잉 보충 없이 보류, (6) 지속 정책 cap·scope와 이번안 수정 구분, (7) 수요·capacity·예산의 더 작은 한도 및 명시 승인/동의 유지. 이 추가 목록은 현재 실행 완료 주장에 포함하지 않는다.

격리 worktree `/Users/gsr/Desktop/workspace/2026-ralphton-merchant-cap-repair`의 `merchant-cap-repair-contract.md` 초안도 읽었다. **복구 범위 타당**: 계산된 현재 line 수량과 경영주가 명시한 상한은 구분해야 한다. 예를 들어 현재 수요 6/명시 상한 10이면 실제 발주량 6을 유지하면서 제약은 10으로 보존해야 하며, 이후 정책 copy에서 임의로 6으로 축소하면 안 된다. 실행·보류 SKU에 동일 명시 상한을 보존하고 실제 실행량은 기존 도메인의 min(수요, 공급, 예산, 상한)·MOQ/배수 검사에 맡기는 것은 ADR005 의미의 복원이다. 미래 copy는 여전히 별도 정책 확인/승인을 거쳐야 한다. 기존 `Math.min(line.quantity, maxQuantity)`를 정답으로 고정한 시험은 이 두 값을 혼동하므로, 실패 원본/근거를 보존한 기대값 정정은 정책 추가나 문턱 완화가 아니다. 이것은 **초안 범위 검토**이며 아직 수정 구현·독립 재검증 PASS가 아니다.

## 나머지 고정 체크리스트 결과

아래는 코드와 기존 시험 근거의 일치 판정이다. 새 전체 브라우저 검증 PASS를 뜻하지 않는다.

| 영역 / 관련 처분 | 검토한 실제 장치와 판단 |
|---|---|
| O-01/02, R-01~06: 수량·FIFO·공급 | ADR002/004 채택. 정수 요청 1~20, 활성 요청 중복 제한, 유효 pending에서 미확정 coverage·확정 잔량 차감, 전량 FIFO, 공급 source trace, MOQ/배수 내림, capacity 승인 시 소비. 초과 공급/중복 확정·입고는 차단. 기존 정상·경계 시험과 일치하며 이번 범위에서 추가 필수 결함을 확인하지 못함. |
| O-03~07, R-11/16: 동의·취소·결제 | 기본 미동의·tuple 확인·7일 정각 만료, 결제 성공 뒤 소급 만료/취소 금지. 실패 최초+명시 retry 총2회, 10분 점유, 재동의 새 cycle/순번. `dispatch` 원자 처리와 retry 직전 상태 재검사. 결과 미확인과 알려진 실패를 분리하는 계약 유지. |
| O-08, R-07~10/13: 경영주 예산·정책·묶음 | KST 승인일/원매입가 장부, 사용액 미만 예산 변경 거절, stale fingerprint/version 묶음 전부 차단. 이번안과 지속 정책 별도 확인, 정책 기본 off·동의 재설정, 검토당 상한·이벤트 비재귀 적용. **이번안 상한 어댑터는 위 P1로 FAIL**. |
| R-17~27: 저장·역할·reset·재전송 | D44 한 탭 Worker queue, session/generation/roleEpoch 검사, 같은 command ID·payload replay와 payload conflict 구별. SQL commit/export 후 IndexedDB 완료를 기다리고 저장 실패 시 마지막 내구 사본으로 복구. 명시 reset은 generation 증가, 불일치/손상은 자동 초기화하지 않음. 실제 로그인·다중 기기 보안 보장으로 확대하지 않음. |
| CORE-07/10, AC-12~15: 예약·입고·알림·48시간 | 성공 모의 결제와 예약 생성 원자 처리, 전량 source 입고 뒤 최초 pickup 알림+deadline. deadline=알림시각+172800000ms, 재전송으로 연장하지 않음. 정각 수령 차단·만료 처리. 예약/입고/수령 상태 및 합성 거래를 경영주 화면에서 구분. |
| CORE-25/26, AC-31/32: 니즈·상품→고객 상세 | 니즈/추천은 수요 합계에 넣지 않음. 경영주 자기 점포 요청 상세에 수량·가격·동의·순번·발주연결·확보·결제·예약/기한이 연결됨. 실제 화면 가독성·조작부담·상세 합계 브라우저 QA는 별도 미완료. |

docs13의 원래 질문/권장안을 새 미결정으로 되돌리지 않았다. ADR002/004/005가 위 상태 정책을 구체화한다. O-10 지도/목록 fallback과 R-30/31 접근·호출 제한은 ADR003의 채택 범위이며 최종 배포 실검증이 남는다. D44는 외부 DB/다중 사용자 경합만 제외하고 동의·수량·금액·기한을 유지한다. D45는 OpenAI 단일 경로다. D46은 $20/2400과 ADR007의 실패 보존·UX 비교 기준을 유지한다. D47은 고객 추가 후보 하나이며 경영주 변경 권한이 아니다. D40 미채택 제안을 적용하지 않았다. 이번 감사는 docs13 전체 56개 항목의 최종 출시 처분 완료를 선언하지 않는다.

## 증거와 남은 게이트

기존 `c7-local-gate.json`의 `domain-ui-tests`는 **domain/UI 합계 44개**, failures/errors/skipped 모두 0이다. 감사자가 새로 전체 44개를 실행한 것으로 쓰지 않는다. 이번 독립 재현은 추가 단일 경로이며 `node --import tsx --input-type=module`에서 실제 `DomainEngine`·`proposalChange`와 `public/demo/seed.sqlite`를 사용했다. 첫 모듈 import 시도는 CJS named export 오류로 앱 실행 전에 실패했고, default import로 바로잡은 실행이 위 재현 결과를 냈다. 모델·외부 네트워크·영속 저장은 사용하지 않았다.

| 대상 | SHA256 |
|---|---|
| `docs/execution/run-20260921/c7-local-gate.json` | `533e090e6abff91ccf20d043a0fa9f318a7b864cdb375c800bd16f000a5713ab` |
| `artifacts/raw/domain-ui-tests.json` | `eea23e2b342dfa5834889c27048a320c898a183d91d424ce91ca3c4435e6e39b` |
| `src/components/merchant/model.ts` | `641867ba22c50048601e744d66908b1b262544d3dbd67ce20c00800566262ca4` |
| `src/domain/engine.ts` | `b9ea21cd344c7467cf6d34fb7fa3abfb21a02c9cbcf3bb46d977cf7ed684cff4` |
| `src/db/runtime.ts` | `b567984ecef5504f6d091c30ab518dffbef767e69e06c4c8ee8d7f7ae1ecf631` |

이 보고서의 C7 실제 모델 평가 실행 수는 0. 최종 NL/validation repeat/보호 holdout, 최종 UX·두 역할 실제 브라우저 QA, G5/G6는 **미실행/미완료**를 유지한다. 기술 CI·Preview 준비나 기존 44개 PASS로 승격하지 않는다. 목적 보존 판정은 **아직 충족되지 않음**: 정상 경영주 복합 수정의 명시 상한 위반을 해소하고 독립 재검증해야 한다.
