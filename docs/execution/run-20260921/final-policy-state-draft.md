# 최종 상태·실패 관점 정책 감사 초안

판정: **I01의 검증된 거래 경계는 유지되지만 최종 제출은 NOT_READY**다. 이 문서는 기존 증거의 범위를 확인하는 감사 초안이다. 새 정책·제품 소스·모델 설정을 만들지 않았고 실제 모델 호출과 holdout 본문 접근은 0이다. C3는 별도 기술 검토/배포 준비 중이며 이 초안은 실행 GO나 품질 승격을 부여하지 않는다.

검토자 method_auditor. card, CORE-03~11/17/18/21/23/25/26, DECISION_INDEX의 유효 결정, ADR-002~006, 13번 O/R 점검표를 대조했다. ADR은 사용자 위임에 따른 에이전트 채택이며 사용자 직접 확정으로 바꾸지 않는다. 목적은 고객의 명시 확인·동의부터 경영주의 보수적 묶음 발주와 입고 후 픽업까지 정상 연결하는 것이다. 모든 입력을 거절하는 방식은 이 목적을 만족하지 않는다.

## 현재 소스와 증거의 유효 범위

검토 시 root HEAD는 `6f955190692bc11b91bdc338ed9ce83034ccb8f7`이다. `src/domain`, `src/db`, `src/contracts/domain.ts`, `src/components`, `data/schema`, `public/demo/seed.sqlite`의 추적 파일 19개를 I01 commit `10c00723d0b64ea47a06dcbd00e2b671e7c62daf`의 실제 바이트와 대조해 변경 0을 확인했다. 따라서 아래 거래/UI 증거는 해당 소스 범위에서 유효하다. 이후 모델·서버 변경의 해석 품질이나 최종 배포의 전체 동작으로 자동 확장하지 않는다.

- engine SHA `b9ea21cd344c7467cf6d34fb7fa3abfb21a02c9cbcf3bb46d977cf7ed684cff4`.
- domain contract SHA `fc06aec7bf7b089ebfbf379ad7daf1df9b003f907413aea38818beae8183bd4a`.
- 고객 화면 SHA `50044eaad848a3dc58defcf08df3cc74947096948a4a456d19a909f9d19b2705`, 경영주 화면 SHA `1352bf1ea64bd0f30e5c3acc6352e89a538069427b52c471517544694ac1153f`.
- seed schema-v2/seed-248-v2 SHA `4cb10e899c9706bb0a9278b458bd7b70d3c34bf28f649b62ffae0894794a2b45`; catalog248 SHA `f2696abe92521e3ff8f9ab43cb36a1d297a6fd23d272e239605b49fab4343b1e`.

## 상태 계약과 독립 증거 연결

| 정책·점검표 | 유지해야 할 의미 | 실행 근거와 현재 경계 |
|---|---|---|
| 7일 동의와 48시간 분리: O-03/07, R-11/16/20 | 미결제 동의는 동의시각+7일 미만. 결제 완료에 소급 만료 없음. 전량 입고·결제 후 최초 픽업 알림부터 48시간, 정각부터 수령 차단. 재입고/새로고침으로 연장 금지 | [D02](d02-independent.md)의 실제 SQL 직전/정각 및 결제 실패 후 정상 복귀 검사, [고객 QA](i01-customer-browser.md)의 입고 전 deadline null·알림0, 입고 후 172800000ms·refresh 불변. 경영주 브라우저의 마감 검사는 정각+1161ms였으므로 수학적 정각 증거는 SQL 검사와 구분한다. |
| 전량 FIFO·출처 보존: O-01, R-01/02/05/06 | 점포/SKU 유효 요청의 앞 순번을 건너뛰지 않음. 회차별 확보 풀은 합산하되 allocation 출처를 유지. 부족 공급은 잔량과 미확보 수요로 남기며 예약/입고를 재고에 중복 합산하지 않음 | D02의 복수 source 합산·선두 전량·수량 불변식 및 [경영주 QA](i01-merchant-browser.md)의 요청3/확보2→예약0/잔여 제안1. 모든 source 입고 전 마감 없음. 부분 배정·부분 수령을 구현된 기능으로 주장하지 않는다. |
| 수요·발주·공급 중복 방지: O-02/12, R-03/04/08/10/24 | pool과 진행 coverage를 뺀 유효 수요만 발주. 같은 command/payload는 저장 결과, 다른 payload 충돌. 공급·입고는 line별 1회; 실행 집합 중 하나라도 stale이면 전체 승인 rollback | D02의 MOQ6/요청13→12+보존1, 멱등성과 snapshot rollback. 실제 고객 연타→요청1, 경영주 연타→order1/10lines/20개와 refresh 불변. 10SKU 정상 묶음 승인1회를 유지했다. |
| 가격·동의·대체: O-04/05, R-07/09/12 | 정수 판매가와 매입 예산 분리, 가격 상승·하락 모두 재동의. 새 SKU/점포는 새 확인·동의. 추천·니즈를 확약으로 합산하지 않음. 결제 성공 후 취소/대체 자동 전환 금지 | D02의 가격/동의 불일치 차단과 재동의 정상 복귀, 고객 QA의 기본 unchecked·수량 변경 시 동의 해제·대체 후보 거절/취소 후 원요청/동의 불변·명시 니즈만 저장. 실제 모델의 의미 정확도는 별도 미달이다. |
| 자동발주·capacity·예산: O-08, R-03/07/10/13, ADR004/005 | 초기 off, 경영주 명시 확인. capacity는 추가 접수 가능량이며 승인 시 소비하고 부족 공급으로 자동 복원하지 않음. 예산은 원 승인 KST일·매입가에 귀속. SKU별 검토 이벤트 상한이며 일일 수량 상한으로 바꾸지 않음 | D02 최신 36 SQL 회귀와 독립 cap 9경계: 수요10/cap3→한 이벤트3, replay0, 새 검토3, 총량10 이내. 공급/입고/clock이 자기 발주 재귀를 만들지 않음. MOQ·예산·capacity 중 작은 제약 적용, 저장 실패 전체 복원. 경영주 QA에서 정책 명시 확인 후 건별 승인0·변화없는 검토의 중복0. 탭 종료 중 상시 자동 실행은 주장하지 않는다. |
| 결제 실패·결과 불확실: O-06, R-24/27 | 알려진 모의 실패와 결과 미확인을 구분. 최초+명시 재시도 총2회, 최대10분 점유. 만료/2회 실패 시 한 번 해제→review_required. 재동의는 새 순번·cycle로 정상 복귀. 결과 미확인은 기존 command 조회부터 | D02 독립 인접 검사와 실제 고객 UI: 2회 실패→풀 해제→재동의→동일 풀 결제 성공, 결제기록3/cycle2/orders1. 외부 실결제나 실제 결제사 불확실성을 시험했다고 주장하지 않는다. |
| 역할·세션·reset·내구 저장: R-17~26 | 한 탭 Worker 큐, actor/store/generation/roleEpoch 검증. reset은 현재 세션 새 generation, 늦은 응답 쓰기 금지. SQLite commit/export와 IDB 저장 완료 뒤 UI 성공, 실패 시 이전 내구 상태 복원 | D02 실제 Chrome Worker/IDB 8경계 및 고객 UI 12경계에서 실제 IDB abort→PERSISTENCE_FAILED→SQL/사본 불변→정상 재시도, 손상 사본 명시 복구, 역할/reset/refresh 및 늦은 응답 차단. 서버 인증·다중 탭/기기 공유·변조 방지 보장은 D-44 밖이다. |
| 검색 실패·미식별·정상 성공: O-11, R-12/26/32/33 | HTTP/스키마 실패를 미등록 니즈로 저장하지 않음. 질문 최대2회, 후보 확인과 새 동의를 보존. 정상 명확 입력에서 불필요한 확인을 늘리지 않음 | 고객 QA의 timeout/허구SKU 주입은 거래·니즈0과 정상 재시도 복구를 확인한 HTTP fixture다. 실제 모델 정상2회와 구분한다. CQA-01 전체 후보 JSON history 보존 및 CQA-02 확대 겹침 수정은 독립 delta PASS. B0/C1/C2 공식 평가에서는 아직 의미·응답 오류가 남아 있다. |

위 PASS는 보고서에 기록된 실제 SQL/Worker/UI 검사 범위다. 이번 감사에서 테스트나 브라우저를 새로 실행한 것이 아니다. 13번 체크리스트 전 항목의 최종 배포 PASS로 확장하지 않는다.

## 독립성의 출처

- 도메인/저장 구현자는 preflight_builder, 고객 화면은 research, 공통 AppShell은 root/builder다. method_auditor의 D02·고객/AppShell 실제 검사는 구현자와 분리된 증거다.
- 경영주 화면 구현자는 root, 독립 브라우저 검증자는 research다. research가 작성한 고객 화면을 자신의 경영주 보고서로 독립 검증했다고 세지 않는다.
- evaluator인 본인이 작성한 scorer·전송 실행기의 자체 테스트는 독립 증거가 아니다. [research의 scorer 반례·복구·248 메타 검토](eval-independent.md), [builder의 E02 독립 11경계](e02-independent.md), [research의 driver 검토](e02-driver-review.md), [builder의 diagnostic 276조합](e02-diagnostic-independent.md)을 연결한다. 최초 실패와 수정 기록을 보존한다.
- [UX 측정기 독립 검토](ux-benchmark-independent.md)와 실제 UX 측정 결과는 서로 다른 증거다. 장치가 동작한다고 제품 품질이 통과한 것은 아니다. root의 Preview 정상 smoke 역시 독립 최종 두 역할 QA를 대신하지 않는다.

## 검증 종료·남은 차단 조건

1. **자연어 최소 기준 미달.** [B0](n02-baseline-report.md)는 227/336, 미완료51을 포함한다. [C1](n02-c1-evaluation.md)은 같은 dev30에서22/30, [C2](n03-c2-evaluation.md)는25/30이나 각각 핵심 회귀가 있어 채택하지 않았다. 후보 통과 수의 순증으로 필수 회귀를 상쇄하지 않는다. C1/C2 validation은 0이며 보호 holdout과 최종 best는 미실행/미선정이다.
2. **UX 비교 NOT_READY.** [ADR006 실제 결과](ux-baseline-recovery-results.md)는 최초2PASS/1FAIL/21미실행, 단일 복구11PASS/1FAIL/12미실행이다. 누적48의 성공 조각을 합쳐 정상24로 재구성할 수 없다. 추가 자동 재측정 권한은 소진됐으며 이번 초안은 세 번째 실행을 허용하지 않는다.
3. **G5/G6 미완료.** 두 validation repeat 각각의 최소 기준, 보호 holdout, 최종 두 역할 live 브라우저, 제출 deployment의 정확 source/model/prompt/catalog와 심사자 접근·키 비노출 증거가 남아 있다. 이전 I01·PR CI·Preview READY로 이 단계를 통과시키지 않는다.
4. **중단 정책 유지.** 역할별 후보 한도 및 연속3 non-improving 규칙은 모델 교체로 초기화되지 않는다. C3 결과를 보고 다음 후보를 이름만 바꿔 무제한 추가하지 않는다. 2,400호출/$15와 prior50 보수 예약, unknown $.05, 필수 후속 예약을 유지한다. 비용 또는 선택 실험 종료가 필수 품질 면제는 아니다.
5. **문서 최신성 주의.** ADR002/004/005/006 본문의 일부 '실행 not_run/검증 전'은 채택 당시 상태이고 현재 실행 증거는 위 보고서와 DECISION_INDEX에 있다. 반대로 현재 INDEX의 'C2 평가 중'은 C2 완료·기각 보고서보다 이전 표기다. 조정자는 최종 인계에서 상태 요약을 정합화하되 채택 원문 의미·이전 실패·동결 실행 config/hash를 소급 변경하지 않아야 한다.

이 감사에서 새 거래 정책 공백을 채택하거나 기존 계약을 완화하지 않았다. 다음 상태 변경은 C3의 정확한 배포/설정 검증과 별도 실행 결과에 따라 기록해야 한다. 워킹디렉터리·분리 작업공간·명령/브라우저/평가 원본 및 실패 로그를 보존한다.
