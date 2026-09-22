# C10 규격 인증 독립 기술 검토

판정: **C10-TECH PASS, 최종 root G01 수정본에 한정**. 구현자 preflight_builder/root와 분리한 research가 원문 계약·코드·합성 반례·정상 동작·실제 설치 SDK의 모의 전송을 직접 검증했다. 기술 PASS는 실제 NL 정확도/편의성/역할 QA/G5/G6 PASS가 아니다. 연구 담당의 과거 고객 UI 작성은 이번 서버 변경 검증과 구분하며 독립 고객 UI QA로 세지 않는다.

## 계약과 소스 결속

card, CORE02/03/11/17/18/21/23/25, 유효 ADR과 `c10-size-contract.md`의 목적은 명시한 규격을 보존하면서 정상 모호함·별칭·정정·대체·확인을 유지하는 것이다. 불확실한 입력을 전부 거절하거나 정답 SKU를 특별 취급하는 복구는 허용하지 않는다. C9 validation83/84 최소PASS/채택FAIL·340ml 오류와 동규격 두500ml 항목의 출처 모호성은 그대로다. 이번 변경은 데이터/정답의 모호성을 해결하거나 기존 결과를 재채점하지 않는다.

최종 context `docs/execution/run-20260921/context-n13-v20.json`, SHA256 `6fffa1419a57a7c12e5b641251a0cec741e31dccad0369fee447f21533ba3e31`의76입력 hash를 직접 대조해 ACK했다. 직접 계산한 aggregate fingerprint는 `244d63c5331bf31454d4840067d364ca1bbdf0d3fab5b8082e0f9b7cde8e6216`이다. 처음 builder56c9ae19의6파일 중 helper/test는 독립 결함에 따라 root가 후속 수정했으므로 원래 builder 지문을 최종본으로 재사용하지 않는다. 최종6파일 개별 해시는 private `c10-independent/binding.json`에 있다.

C9 exactsource8b52 대비 provider/model/packing/retrieval/catalog/customer·merchant wire/기존 경계 인증·grounding/domain/UI/merchant cap/seed/공개 scorer·adapter·validation/manifest-v2 바이트가 동일하다. 두 verify 함수 본문과 MERCHANT_PROMPT export 이후 전체 바이트도 동일하다. 경영주 응답 schema는 stale/SKU-only 조합에서 C9와 동일하다. 별도 post-output 치환·중복제거·정답ID 우선 선택을 추가하지 않는다.

## 발견한 결함과 실제 수정 확인

**C10-G01 최초 FAIL:** catalog 이름 비교가 구두점을 제거한 뒤 숫자 regex가 뒤쪽 숫자만 읽어 다른 규격을 긍정 인증했다. 합성 `1,500ml`→500ml, `0,5L`→5L, Unicode 음수 기호도 양수로 인증했다. 실제 현재 catalog의 `간편 블럭 미소된장국 47.5g`을 `47,5g`으로 쓰면5g로 인증해 원래 SKU를 제외했다. 처음 서버59 PASS는 이 반례가 없었던 결과로 보존한다.

첫 root 수정은 쉼표·부호와 숫자 전체를 확인했다. 이후 같은 구두점 소거 문제의 인접 입력 `≠500ml`, `500ml~`, label의 `500ml(?)`가 여전히 명확500ml로 인증되는 반례를 발견해 완료 판정을 보류했다. 최종 root 수정은 subject에 허용된 문자/숫자/공백/점/슬래시만 허용하고, 정확히 한 규격 매칭 외 다른 숫자가 남으면 인증하지 않는다. request 끝의 정상 구두점은 subject 밖이라 기존 정상 문법을 유지한다. 미지원 기호/숫자는 요청을 거절하지 않고 원래 모델·전체허용 enum 경로로 돌아간다.

동일 기대값의 G01 숫자 및 세 인접 반례와 실제47.5g 반례를 최종 source에서 재실행하여 전부 fallback으로 닫혔음을 확인했다. 최초 FAIL을 정상 성공으로 소급 변경하지 않는다. 원형 재현 script·원본 builder 재현 출력·실제 catalog 반례·인접 실패 JSONL은 private에 남아 있다.

## 직접 실행한 최종 검증

- **독립10그룹 PASS**, 실제 설치 SDK fake fetch4회 포함. G01·긍정 단위 등가·NFKC/fullwidth·정상47.5g, 부정/범위/정정/다중용량/별칭 오타/알레르기 문구·임의 prefix·이전 대화의 fallback, 안전 집합/차단 집합 없음, unknown/복합/다른 차원 유지, 모든 candidate kind의 제한과 count2, 기존 schema/merchant 보존을 검사했다.
- SDK가 받는 실제 요청에서 원래248 catalog row와 원문/history/context를 유지하며, 새 hint와 **모든 후보 kind의 ID enum만** 같은 known mismatch 집합을 제외함을 확인했다. 전체 enum1000 미만·strict 구조화 출력·storefalse/output3200/기존model옵션을 유지한다. 올바른 ID는 기존 canonical SKU로 돌아온다.
- 잘못된 규격 ID를 응답으로 주입하면 실제 handler는502/SUPPLIED_CATALOG_SCHEMA와 known usage120token을 반환한다. 응답을 정상으로 고치지 않는다. usage 미확인은 null 오류로 남는다. 이전 대화가 있으면 hint를 만들지 않고 기존 enum/참조 경로를 유지함도 SDK mock으로 확인했다.
- 직접 전체 서버 원본59/59 및 첫 G01 수정후60/60 PASS, fail/cancel/skip0. 마지막 변경은 helper 허용문자와 해당 테스트이므로 최종 영향 suite **7/7 PASS**와 독립10그룹을 다시 실행했다. 변경 없는 다른 그룹을 반복 실행한 것으로 꾸미지 않는다. root 별도 최종 전체 gate의 server60 등 결과는 독립 검사와 별도다.

합성 후보는 상품명/규격만으로 구성했고 고정 평가 정답을 helper로 복사하지 않았다. 소스에는 특정 상품ID/평가case 조건이 없다. label 문법의 어휘 근거 확인은 해당 입력 catalog를 사용하며, 이름 관측과 실제 규격 비교를 분리한다. history/모호한 문법의 인증 부재는 사용자에게 규격 조건이 없다는 의미가 아니므로 기존 모델 판단과 확인을 유지한다.

## 남는 한계와 후속 게이트

인증은 좁은 긍정 문법의 충분조건이며 일반 한국어 이해기가 아니다. unknown/복합 규격이나 질량·부피 간 비교 불가는 enum에서 남으므로 모델이 정체성·불확실성·대안을 제대로 표현하는지는 실제 평가가 필요하다. 동일500ml 두 항목은 모두 남고 packaging 누락/단일정답 모호성도 해결하지 않는다. differences를 전역0으로 만들거나 동일규격이면 무조건 정답으로 승격하지 않는다. 실제 품질 성공이나 회귀 해소를 이 기술 검사로 약속하지 않는다.

필수 미해결 기술 결함0. 실제 모델·외부 HTTP·브라우저·배포·공유장부 접근0, 보호 원문/생성기 접근0. private `c10-independent/`에 재현/최종 script·결과·로그·source binding을 보존했다. 서명 없는 review JSON은 검토 신원의 암호학적 증명이 아니다. 이후 정확한 배포에서 고정 dev→같은 config validation 두 회→freeze/새holdout→고정 UX·두역할 QA·최종정책/G5→main/Production G6가 별도다. 현재 데이터/oracle·품질·분모·예산·실패 기록은 완화하지 않는다.
