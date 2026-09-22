# N16 기능 릴리스 검사기 독립 기술 검토

검토자 final_ux_state, 구현자 research. 판정: 검사기 기술 범위 PASS. 실제 기능 출시, 원래 G5 또는 최종 G6 PASS를 뜻하지 않는다.

D50 사용자 직접 결정과 검사기·템플릿을 대조했다. C11의 고정 source/runtime50, 모델·prompt·catalog, 원래 보호 평가75/84 FAIL, 정량 UX 미실행, 원래 품질 NOT_READY를 검증하며 기존 G5 검사기나 평가 결과를 변경하지 않는다. 고객 live6·fixture12, 경영주 live11 및 각각 실제 호출3을 요구한다. 독립 역할 QA 두 개와 서로 다른 두 정책 관점의 중대 문제0을 요구하고, 성공 시에도 최종 G6는 pending이다.

초안에서 고정 호출3을1~3으로 허용하던 공백을 지적했고, 구현자가 정확 정수3과1/2/4/bool 거절로 수정했다. 고객 fixture12의 별도 분모·미실행0·실패0·실제 호출0도 확인했다. 최종 자체18시험을 직접 실행하여 PASS를 확인했고, 독립25개 정상/변조 사례에서 호출·분모·자료형·fixture·역할 누락·정책 신원·기존 실패/UX 은폐 경계가 예상대로 동작했다. 실제 runtime50과 pinned 문서·실패 보고서 해시가 일치하며 미완성 템플릿은 NOT_READY로 거절된다. 모델·브라우저·HTTP·공유 장부·보호 원문 접근0이다.

최종 소스 SHA-256:
- scripts/check_functional_release.py: cb211cddae9a0491cd85a17cc1781687c9266cca3ac45f58ad492ce9b80290e3
- tests/release/test_functional_release.py: 71cdc10cc147fb99d1b4448c2f617c60dc58aaa32217b4122079901ea2e3ddb7

검사기는 제출된 증거의 일관성을 검사한다. 실제 실행 여부와 검토자 신원은 서명되지 않은 JSON만으로 증명되지 않는다. 실제 두 역할 QA, 실제 증거에 근거한 두 정책 검토, 현재 전체 기술 게이트/CI 및 정확한 main Production의 최종 익명 검증은 별도로 완료해야 한다. 독립 상세 결과는 private n16-functional-checker-independent.json SHA-256 d4a514acb206fe36e9fa1cee54a771e02258a9145c3a1c4e3160360d4f1025c6에 보존했다.
