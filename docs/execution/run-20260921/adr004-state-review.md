# ADR-004 독립 상태·수량 검토

- reviewer: `/root/method_auditor`; proposer root와 별도. 다른 검토자 결론을 읽지 않았다.
- consumed_context_hash: `e8d6eb6ffef8765544e3aeeeb9c27b1e98f0c7cb5131202712ec4d32d806ea99` + ADR-004 SHA-256 `b63cfe76a23630648b2dd603cbf5eb06f6f53d183a7a6553efac04c33c421418`.
- 관련: CORE-06/07/08/25, ADR-002의 보존·link/coverage·멱등성·실패복구, D-44 한 탭 SQLite.
- 독립 상태정책 검토1회. 코드/실제 SQLite/브라우저 검사 `not_run`.

## 판정

**채택에 동의한다.** availableOrderQty를 이미 확보한 재고와 구별되는 “추가 주문 접수 capacity”로 정의하고 승인 때만 소비하면 정상 발주가 가능하면서 자동 부족 재시도량이 유한해진다. 공급부족 고객을 취소하지 않고, 새로운 모의 공급 가능 조건을 명시 변경한 뒤 정상 복귀하는 경로를 보존한다. capacity를 올렸다는 이유만으로 이미 발주한 coverage를 다시 발주할 수는 없으며 ADR-002가 계속 우선한다.

| 반례 | 기대 결과·정책 대조 |
|---|---|
| 수요8/capacity10 승인 후 동일 command replay | 최초 capacity2, replay도2. 주문/예산/연결 증가0. ADR-002 fingerprint 및 durable 결과 적용 |
| 8주문→3확보→부족5, 자동 재검토 | capacity2 유지. 기존 source pool3을 수요와 중복 계산하지 않고 MOQ·예산·미확정 coverage 고려한 최대2만 추가 접수 가능. 그 주문도 부족이면 capacity는0으로 수렴하며 같은 한도를 반복 재사용하지 않음 |
| 공급부족 직후 capacity를0으로 바꾼다 | 부족 수요는 pending 보존, 공급조건 보류 이유 표시. 대기 요청 삭제·자동 취소 없음 |
| 미확정 주문8이 남은 상태에서 capacity10으로 명시 재설정 | 공급 접수능력은10이지만 신규 유효 미연결 수요가 없다면 신규 주문0. 기존 주문 coverage를 차감하므로10을 추가 발주하지 않음 |
| stale proposal에서 capacity 충분해도 가격/MOQ/revision이 바뀐다 | 해당 실행 묶음 전체 거절. capacity·예산·order/link 모두 불변 |
| 10개 line 중 마지막 line 예산 부족 | 전체 SQLite transaction rollback, 앞 line capacity 감소도 복구 |
| SQL commit 뒤 IndexedDB persist 실패 | 직전 내구 snapshot 복구, capacity/예산/order/link가 동일 기준으로 되돌아감. UI 성공 금지. 재시도는 복원된 상태에서 한 번 승인 |
| 자동 정책 off에서 capacity만 재설정 | 조건 revision만 갱신. 정책 승인 없는 자동 주문 없음 |
| 기존 고객 결제·예약 물량이 있다 | capacity 갱신은 미결제 동의나 기존 예약·입고·48시간에 영향0. source 확보량을 capacity와 합산하지 않음 |

이 정책의 “무한발주 방지”는 공급 capacity만으로 보장하는 것이 아니다. 수요·pool·미확정 coverage·예산·멱등 command를 함께 재검증한다는 기존 계약이 필수다. 자동화가 실수로 capacity를 다시10으로 쓰는 구현은 새 명시 확인 없이 supplier 조건을 갱신하므로 이 정책 위반이다.

채택 기록에서 authority=user-delegated, policy_key=`ordering.supplier_capacity`, effective_scope=최초 앱 구현 후보, depends_on=ADR-002/D-44, supersedes/conflicts_with=없음을 명시하고 소비자 context를 갱신하면 된다. 기존 본문의 CORE-6 표기는 CORE-06으로 정리할 수 있는 형식 문제이며 새로운 정책 공백은 아니다.

다음은 위 정상/replay/부족/명시갱신/stale/묶음rollback/저장실패를 domain 및 실제 SQLite 테스트에 연결하는 것이다. 본 동의는 구현 또는 G1/G2 PASS가 아니다.
