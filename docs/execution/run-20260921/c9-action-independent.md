# C9 행동 생성 계약 독립 기술 검증

판정: **C9-TECH PASS — 서버 기술 계약에 한정**. 연구/검증 담당 research가 구현자 root/preflight_builder와 분리해 직접 실행했다. C8 validation79/84 FAIL은 보존하며 C9 실제 모델 품질·현재 두 역할 브라우저·ADR007 UX 연구·G5/G6를 통과 처리하지 않는다. 연구 담당의 과거 고객 UI 작성은 이 서버 변경 검증과 구분하며 독립 고객 UI QA로 계산하지 않는다.

## 입력과 목적 보존

card/CORE02·03·05·11·17·18·21·23·25, 기존 AC/검증·개발 루프, C9 작업 계약 및 최신 D48/D49를 대조했다. 고객은 명확한 SKU를 확인하고 모호함·정정·대체와 미식별을 구분해야 하며, 경영주는 정상 현재 수정/정책 초안/되돌리기를 실행 승인과 구별해야 한다. 이번 수정은 응답 형식의 모순을 생성 단계에서 줄이며, 고객 동의·발주·상품/수량/가격·48시간·평가 정답/합격선을 변경하지 않는다.

- Builder commit `90a4b506bbe70e805fbee69bccce1c9ec462e8ed`의 변경 10파일을 root 통합 바이트와 직접 대조했다.
- 최종 context `context-n12-v19.json` SHA256 `44e82074148e322215f0df95f3358b88e24211f6a8f8cc2dfbc5101a52b3db36`: 72개 입력 hash 전부 일치, ACK.
- 직접 계산한 aggregate fingerprint `9cfb0097b0faf61d60158c037af02a4e316899ead533b88c7d42981da785d61f`.
- `verifyCustomer`/`verifyMerchant` 두 본문 바이트는 C8 sourcebb2와 동일하다. provider/model/packing/retrieval/catalog/customer-wire/경계 인증/merchant grounding/domain/UI/현재 merchant cap mapper/공개 평가 코드와 manifest-v2도 동일함을 확인했다. 보호 평가 원문은 열지 않았다.

## 직접 실행한 검증

1. Builder 동결 worktree에서 서버 전체 **53/53 PASS**, fail/cancel/skip/todo 모두0. 자체53 결과를 독립으로 단순 인용하지 않고 동일 명령을 직접 실행했다.
2. 별도 private 독립 script의 **12개 검사 그룹 PASS**. 수정 전 C8 schema에서 허용되지만 verifier가 거절하는 합성 4건(restore의 policy scope, restore 질문, clarify의 수량 제한, modify 질문)을 재현하고 C9 생성 schema 거절을 확인했다. 이는 실제 M04 원응답 위반 필드를 확정하는 증거가 아니다.
3. 정상 current/policy, budget0·수량0을 포함한 유효 경계, SKU-only/category/mixed, restore/clarify를 독립 검사했다. canonicalMerchant는 decision을 그대로 반환하며 필드를 채우거나 지우거나 재해석하지 않는다. SKU 참조 해제 뒤 기존 검증을 유지한다. empty modify, duplicate ID, 이전 상태 없는 restore도 기존 오류와 알려진 사용량을 유지한다.
4. 실제 설치된 OpenAI SDK를 **fake fetch 6회**로 실행했다. restore·mixed future policy·stale/version mismatch·고객 다후보/대안·실제 handleAssistant 오류 매핑·unknown usage null 보존을 검사했다. 외부 HTTP/실제 모델 호출은0. strict nested object schema, max_output_tokens3200, store=false, GPT4.1-mini reasoning 옵션 없음, ID/history/context 변환과 모델 사용량을 대조했다. 잘못된 wire는502와 SUPPLIED_CATALOG_SCHEMA로 반환되며 사후 정상 출력으로 치환하지 않는다.
5. 고객 schema는 count0/1/2 × 외부범위 true/false × stale true/false 총12 조합에서 C8 JSON schema와 완전히 동일하다. 기존 정상 exact/confirm/미식별·모호함·대체/최대질문 동작은 서버 회귀와 함께 확인했다. full248 고객 enum996, 경영주 enum248+category 수+2로1000 미만이며 모든 object가 strict다.
6. 변경된 기존 fixture 테스트는 merchant wire wrapper와 해당 schema 접근 경로만 바꾸며 canonical 기대값을 완화하지 않는다. 고객 prompt는 additionalCandidates 기본[]와 명시 flavor/size 불일치를 confirm으로 위장하지 않는 규칙을 추가하면서 진짜 다후보 모호함·관련 대안·별칭/오타·최신 정정·알레르기 불확실성을 유지한다. 다만 prompt가 실제 모델의 불필요 후보를 줄이는지는 아직 미검증이다.

원본: private `c9-independent/probes.mts`, `results.json`, `probes-first.log`, `server-53.log`, `binding-budget.py`, `binding.json`, `budget.json`. 새 독립 검사 첫 실행 모두 PASS이며 이전 C8 실평가 실패·builder 수정 전 합성 증거는 삭제/수정하지 않았다.

## 예약 산술 독립 대조

실제 공유장부를 열지 않고 현재 runner Budget을 임시 합성 장부에서 직접 실행했다. upper1476, 남은92turn×3, future672는2424로 CALL_RESERVE_STOP; future648은정확2400으로 허용; upper1477이면648도2401로 STOP. dev 진입1350+34×3+924=2376도 확인했다. 네 경계 모두 기대대로다.

648=다음 validation276+holdout276+UX84+QA/G6·복구12이며, 마지막12=customerQA3+merchantQA3+G6두호출+여유4다. 원래 고정 case/turn/workload 분모나 재시도 상한을 줄이지 않는다. 줄어든24는 미배정 여유다. 같은 validation config가 두 반복 모두 다음 validation276을 예약하므로 dev/첫 validation에서 추가 호출1회만 생겨도 두 번째 진입이 막힐 수 있다. 최악의 재시도 완주, 복구4회 항상 사용 가능 또는 실제 비용 충분을 보장하지 않는다. 실제 호출 직전 동일 장부·비용·pending/unknown/auth guard를 다시 적용해야 한다.

## 범위와 다음 게이트

확인한 기술 범위에 필수 미해결 결함0이다. 실제 모델/외부 HTTP/브라우저/배포/공유장부 접근0, 보호 holdout/생성기 접근0. 서명 없는 review JSON은 검토자 신원의 암호학적 증명이 아니다. D49의 Production 배포 순서 변경은 이번 기술 PASS나 중간 배포를 최종 G5/G6 PASS로 승격하지 않는다. 다음 실제 dev→두 validation→best 고정/새 holdout→고정 UX/두 역할 QA/최종 정책/G5/G6는 별도 증거가 필요하다.
