# C4 제외 범위 prompt 독립 기술 검토

2026-09-21 / research / 1차 판정 **수정 필요 — 좁은 문장 충돌 2건**. 구현자 root와 분리해 읽었다. 실제 모델/보호 holdout0, 제품·정답·소스 수정0이다.

대상은 candidate worktree `codex/n05-scope-candidate`, HEAD `55f92fe107694d0e570135362321d35d47131343`, 최초 prompt SHA `6bb28f5aa3cd89d33d7781405c6058927d0f7f14e2c12242b0dc466997c1dc69`다. git diff의 tracked 변경은 prompts.ts만이며 customer prompt 문자열은 HEAD와 같다. version만 packed-refs-v5, 경영주 field별 제외 범위 문단만 추가했다. 특정 평가 상품/정답 하드코딩은 발견하지 않았다.

## 실행과 한계

Node22에서 `node --import tsx --test tests/server/*.test.ts` 25/25 PASS. 후보 worktree `artifacts/private/run-20260921/c4-independent/server-tests.log`에 보존했다. 기존 schema/검증/참조 복원·실패 처리 회귀는 유지되지만 이 결과는 실제 모델이 새 문단을 정확히 따름을 증명하지 않는다. 입력 그대로 모의 모델의 예상 출력을 돌려주는 테스트를 자연어 성공 증거로 추가하지 않았다.

## 독립 의미 반례

- C4-P01: ‘상품 A는 빼고, 카테고리 B는 전부 제외’는 서로 독립적인 두 제외를 보존해야 한다. 새 문단 앞의 무조건 `excludeCategories must stay []`와 뒤의 mixed command에서 양쪽을 유지하라는 문장이 충돌한다. SKU만 요구한 단일 범위이고 별도 카테고리 요청이 없을 때로 앞 문장을 한정해야 한다.
- C4-P02: currentConstraints에 명시 승인된 category B 제외가 있고 ‘앞으로도 이렇게’라고 요청하면 기존 계약은 해당 제한을 정책 초안으로 복사한다. 새 문단의 category를 실제로 요청해야 한다는 문구 및 다른 상품을 제거하면 category를 삭제하는 최종 점검이 이번 문장에 category 이름이 없다는 이유로 이를 지울 여지가 있다. 기존 명시적 참조 복사는 사용자 요청 근거에 포함됨을 새 문단에서도 연결해야 한다.

SKU metadata만으로 category를 덧붙이지 않는 목적은 기존 계약과 일치한다. 보완은 정상 카테고리 전체 제외, 명시 혼합 명령, 미언급 delta 유지, 명시 미래 복사를 함께 보존하는 좁은 충돌 해소이며 새로운 기능·정책을 요구하지 않는다. 정상 명확 입력을 clarify로 바꿔 실패를 숨기거나 category 기능을 제거하는 수정은 인정하지 않는다.

조정자에게 두 반례를 전달했다. 최종 소스/컨텍스트 v11 및 gate 지문은 아직 발급하지 않았다. C3 품질 개선이나 C4 기술 회귀 통과가 UX 비교 NOT_READY 또는 G5/G6 미완료를 대신하지 않는다.

## 2차 의미 delta — 기술 PASS

최종 prompt SHA `eb1db993100b35785434fef31be7350a11b2849aad5bf0d2fb19e7a4917dbe83`를 직접 재계산했다. 조정자가 C4-P01~02를 보완한 diff를 다시 읽었다.

- SKU-only이고 별도 전체 카테고리 요청이 없는 경우에만 excludeCategories=[]를 요구하므로 명시 카테고리 전체 제외 및 혼합 명령과 충돌하지 않는다. 정확 상품명 안의 일반 식품어를 근거로 범주를 추가하는 경우만 차단한다.
- 알려진 currentConstraints를 미래 정책으로 유지하라는 명시 참조는 category를 포함해 그대로 복사한다고 연결했다. 따라서 이를 새로 추론한 category로 간주해 삭제하지 않는다.
- 다른 명령에서 미언급 예산/상한/제외 필드는 기존 delta 규칙 그대로다. 명확한 SKU 수정은 clarify로 바꾸지 않으며 모순/실행 우회/진짜 stale 및 undo의 기존 우선순위도 보존한다.

초기 두 반례의 문장 충돌은 해소됐다. 새 기능·정답·동의 권한 변경 없이 목적을 유지한 좁은 보강으로 판정한다. 위25개 기존 회귀 실행은 최초 문단에 대한 런타임 검사이며 문장 보완 후 다시 실행했다고 주장하지 않는다. 변경은 prompt 문자열뿐이고 의미 delta를 직접 검토했다. 실제 모델의 정상 카테고리/혼합/참조 지시 준수는 후속 live 평가 전까지 미검증이다. 최종 context-v11/gate 지문 ACK는 별도 대기한다.
