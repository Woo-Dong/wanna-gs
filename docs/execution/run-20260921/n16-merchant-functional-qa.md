# D50 경영주 실제 기능 QA

판정: **현재 경영주 기능 범위 PASS**, reviewer research; 앱 경영주/공통 구현자 root·preflight_builder와 독립. 고객UI/C11prompt/need는 본인 작성이므로 고객 독립검증으로 세지 않는다. 대상 exact e727b99a640743c744082f8a3cf754260f0d755a, Preview dpl_HrUL1N35GXdFVfGG95fCgxMBKJRn, C11/runtime d49c…bb9d, gpt-4.1-mini-2025-04-14/customer-classification-v11.

독립 profile 한 탭 실제 브라우저 11/11·모델3/3 PASS, console/runtime 오류0. 실제 SQL/IDB 사본 checkpoint 전부 bytes hash·integrity/FK 대조. 경영주 명시 변경 예산50000+SKU1제외+상품당cap2, 9개상품 각2개·미승인주문0; 미래조건 복사 후 정책 미체크/저장0; undo 예산0·10보류 복원 및 refresh 동일. 별도 사전고정2×10 seed에서 한묶음 승인1·수량20/27700원·연타추가0. 상세 readonly·점포전환 격리 확인. 공급/부족coverage·자동정책중복0, 실패예약 payment_failed/수령불가→요청 상세에서 명시retry→동일예약confirmed, 입고후172800000ms·마감수령거절·reset/refresh, 최소수량보류 보존을 확인했다.

360/390/768/1280/1440 및 실제 computed-font200%·키보드 focus를 검사했다. batch detail/미승인정책/360px200% 스크린샷을 직접 열어 확인했다. 좁은 화면에서는 세로 스크롤을 쓰며 새 사용자 연구나 모든 접근성 표준 준수를 주장하지 않는다.

원본 run01은7PASS/1FAIL/3NOT_RUN, 모델3회성공을 보존한다. 실패는 목록에서 요청상세를 열지 않고 retry 버튼을 찾은 검사기 경로 오류였다. 원본 caller/screenshot/결과 보존→UI 상세 클릭1개 추가→독립 final_ux_state 역diff/경로 검토 PASS→root 승인으로 새 run02 전체11 재검증했다. 앱·기준·assertion·plan 변경0, 출력모델 치환0, 자동 retry0. 두 run 합계 실제6call이며 run02만의3call을 전체 사용량으로 숨기지 않는다. root ledger 최종 upper2105/$12.7993473, pendingfalse; 실제 관측 prior가 아니라 보수예약50 포함이다. 후속 모델 writer 권한은 반납했다.

기존 보호평가75/84 FAIL·UX 비교 미실행·원래 전체G5 NOT_READY는 유지한다. 이 결과는 D50 실제 주요 기능 검증이며 최종 main/Production G6 완료가 아니다. raw HTTP·SQL·이미지는 private 보존, 공개 JSON은 요약과 원본 해시만 포함한다.
