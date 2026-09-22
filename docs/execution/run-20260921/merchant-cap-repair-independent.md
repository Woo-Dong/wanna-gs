# 경영주 상한 복구 독립 검증

판정: **PASS — 기존 P1의 수정과 영향 범위 내 기술 회귀**. 최종 모델 품질·브라우저 QA·G5/G6 완료 판정은 아니다. 원래 P1 FAIL 기록은 변경하지 않았다.

- task: `MERCHANT-CAP-REPAIR`
- reviewer: `holdout_revision_review`; implementers: `preflight_builder`, `root`.
- worktree: `/Users/gsr/Desktop/workspace/2026-ralphton-merchant-cap-repair`; branch `codex/merchant-cap-repair`; base `73a364860cb90f9bc9de4e186390411bce9dfd21`.
- context: `CTX-20260921-MERCHANT-CAP-v17`, SHA256 `b5b15a4eff6c8ead11313ca6908f35f223a8ccbcad11855afa115953789fed42`. 64개 입력 파일 hash를 직접 재계산해 불일치 0개.
- source fingerprint: `70dc053f50bd40ec5bc88ab46047defe13f3f810daa1cda0d3d3236acb517aec`; `scripts/gate_contract.py`의 fingerprint 함수로 독립 재계산해 일치.
- adapter SHA256: `0c33f6e127d127731c1891a42b3c774fc5fb52263ee67f173d4a9870126c1a69`.
- 권한: 원래 GOAL/AGENTS의 필수 결함 복구. D47 고객 후보 추가 승인에 경영주 후보를 포함시키지 않았다. ADR005 의미·정책·모델 prompt·서버/도메인·catalog/schema는 불변이다.

## 결함과 수정의 일치

기존 `current.lines`만 상한을 매핑하던 코드가 실행 line·보류 line·기존 cap key의 합집합을 사용한다. 새 명시 cap은 그 값 그대로 저장하고, cap 생략 시 이전 map을 유지한다. 현재 계산 수량을 명시 상한으로 잘못 저장하던 `Math.min(line.quantity, cap)`도 제거했다. 실제 발주량은 기존 도메인이 수요·coverage·공급·예산·정책 cap·MOQ/배수로 제한한다.

설정 cap10/현재 수요6에서 제약10, 실제 주문6이 정상이다. 기존 단위시험의 cap6 기대는 설정값과 결과량을 혼동했으므로 ADR005 및 수정 전 독립 감사에서 확정한 기대값으로 정정한 것이다. 수량 초과 금지 기준을 낮추지 않았다. 별도 정책 확인/승인도 유지된다. 새 정책 또는 경영주 모델 수정은 필요하지 않다.

## 직접 실행한 증거

### 원본 실패 재현 그대로 실행

명령: `node --import tsx artifacts/private/run-20260921/merchant-cap-repair/repro.mjs`.

이 파일 SHA256은 원본과 같은 `786c657aca39cf81912f873f14177b43059ea216bdf3f74662087e9990726dda`다. 기대값 2를 바꾸지 않았다. 수정 전의 `5 !== 2` FAIL은 원본 감사와 별도 before 로그에 보존되어 있다. 검토자가 수정 후 직접 실행해 exit 0을 확인했다.

```json
{"requestedCap":2,"mappedCapCount":1,"proposalQuantities":[2],"approvedQuantities":[2]}
```

public seed를 메모리 SQL로만 읽어, 수요5 → 예산0 보류 → 예산50000+cap2 → 명시 승인까지 검사했다. 모델·외부 네트워크·IndexedDB 저장을 사용하지 않았다.

### 실제 도메인과 어댑터 회귀 실행

명령: `node --import tsx --test tests/domain/domain.test.mts tests/domain/merchant-cap-regression.mts tests/merchant/model.test.ts`.

검토자가 직접 실행한 결과 **46 tests, 46 PASS, fail/cancelled/skipped/todo 모두 0**, exit 0. 작성자 자체 46 PASS를 독립 실행으로 재표기한 것이 아니다. 기존 도메인36, 추가 실제 SQL5, merchant 단위5의 합계다. 여러 파라미터를 개별 test 수로 부풀리지 않았다.

실제 SQL 회귀는 실행/보류 혼합, 생략 cap 보존, 두 단계 undo, configured10/실제수요6, future-copy 제약10 및 별도 확인한 정책 저장10, MOQ 미달 보류·배수 내림·capacity·예산의 더 작은 한도, 활성 정책 cap의 더 작은 한도, 승인 전 주문0을 통과했다. 원래 도메인의 동의·FIFO·공급·결제 재시도·48시간·reset·역할·저장 rollback 회귀도 함께 통과했다.

### 검토자가 별도로 구성한 SQL 반례·정상 경로

작성자 테스트 기대값을 복제하는 데 그치지 않고, `node --import tsx --input-type=module`의 독립 메모리 SQL probe로 public 조건 3개에 각 수요3을 생성했다. 이 경로는 실제 `DomainEngine`, `proposalChange`, `toModelConstraints`를 호출했다.

- 예산6000/원가1000에서 실행2·보류1 → 예산20000+명시 cap4+한 SKU 제외: 나머지 두 상품이 각각3, 제외 상품은 보류. 세 상품의 설정 cap은4를 유지한다.
- 예산만19000으로 바꾸어도 cap map과 제외 조건이 유지된다. 현재 계산량3을 cap3으로 바꾸지 않는다.
- cap0 수정은 실행0, undo는 cap4와 이전 두 실행 line을 복원한다.
- 고객 미동의 요청 및 경영주 `confirmed:false` 승인은 각각 거절되고 주문0이다.
- 명시 승인 뒤 주문6/원수요9를 유지하며 같은 command 재전송은 추가 주문0이다.
- 재검토 후 조건 변경으로 stale이 된 제안을 승인하면 `STALE_PROPOSAL`, 추가 주문0이다. 최종 도메인 불변식 검사도 통과했다.

```json
{"independentProbe":"PASS","mixedActive":2,"mixedDeferred":1,"configuredCap":4,"actualPerSku":3,"excludedSkuRetained":true,"capZeroUndo":true,"consentAndApprovalRequired":true,"replayAdditionalOrders":0,"staleAdditionalOrders":0,"originalDemand":9,"ordered":6,"modelCalls":0}
```

## 목적 보존과 제한

CORE05/06/07/17/25 및 AC07/08/31의 명시 수정 정확성, 보수적 수량·예산, 별도 승인, 정상 업무 회복을 이 수정 범위에서 확인했다. 앱 코드 변경은 adapter 한 파일이며 작성자의 수정 범위와 동결 hash가 일치한다. 감사자는 앱·정책·장부를 수정하지 않았고 실제 모델 호출0, 보호 원문 접근0이다. 수정 전 실패를 삭제하거나 통과로 덮지 않았다.

이번 독립 검증은 SQL/어댑터 기술 검증이다. 경영주 실제 브라우저의 정책 복사 UX와 최종 제품 동선, 모델 성능, 전체 G5/G6는 아직 완료하지 않았다. C7 고객 dev 성공은 별도 평가 결과이며 이 PASS의 근거로 쓰지 않았다. 최종 runtime이 달라지므로 이후 validation/holdout/UX/두 역할 QA/G5/G6를 변경된 exact source에 결속해야 한다. 조정자의 전체 gate·CI·PR/통합도 별도 증거로 관리한다.
