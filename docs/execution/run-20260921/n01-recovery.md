# N01 첫 실제 호출과 회복 기록

구현자 root. 정상 상품 식별·동의 경계를 보존하는 실제 연결 smoke이며 정식 평가가 아니다.

- 첫 catalog220 고객 호출은 provider 응답이 completed/output_text 조건을 만족하지 않아 INVALID_MODEL_RESPONSE로 종료했다. 그 시점 구현이 실패 응답 usage를 기록하지 않아 정확 사용량/상세 incomplete 원인은 unknown이다. 실제 호출 1건으로 예산에 포함하며 삭제하지 않는다. 상품 미식별/니즈로 저장하지 않았다.
- 실패 사용량 누락을 고쳐 응답을 받은 즉시 사용량·model·incomplete reason을 기록하고 오류에도 attempt 정보를 붙였다. SDK 자동 재시도0,45초 timeout,인스턴스 호출/동시6 제한 유지. 이 변경으로 최초 incomplete 자체가 재현/해결됐다고 주장하지 않는다.
- full248 source의 후속 고객/경영주 2호출은 live 구조화 성공, 2.5~4.2초. n01-live-smoke.json의 비용 추정합계0.00896975달러, 첫 호출은 추가 미확정분이다. 모든 실제 품질 기준선·반복·holdout은 아직 not_run.
- 고객 smoke에서 명확한 일반 SKU에 무가당 변형을 primary 후보로 추가했다. 정식 eval 시작 전에 일반적인 exact-name 정밀도 규칙을 보강했다. 실제 회귀/독립 검토를 뒤따른다.
