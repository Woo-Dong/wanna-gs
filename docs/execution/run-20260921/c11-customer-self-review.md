# C11 고객 행동 분류 가설 — 작성자 자체 검증

- 작성자: research. 구현자 자체 검증이며 독립 승인이나 실제 고객 QA가 아니다. 이 작성자는 과거 고객 UI도 구현했다.
- 격리 기준: `a7adafc0381e9ad069030b1cd13b181790763e89`, branch `codex/c11-customer-classification`.
- 소비 컨텍스트: `context-n13-v20.json`, SHA `6fffa1419a57a7c12e5b641251a0cec741e31dccad0369fee447f21533ba3e31`; 변경 전 격리 기준의 76개 입력 해시 전부 일치 ACK. root에서 병행 수정 중인 runner를 이 ACK에 포함했다고 주장하지 않는다.
- 신규 root 작업 계약: `c11-recovery-contract.md` SHA `9a51648c6f4057fbedd5cabff1e29f3b486f495ededaffb3b7585a938b5f58ae` 직접 확인. 최종 root 컨텍스트·runner 검증은 별도다.

## 목적 보존과 가설

고객이 알아볼 수 있는 상품을 자연어로 찾고 확인·동의로 이어가는 정상 경로를 유지하며, 모호·미등록·범위밖 요청에서 근거 없이 primary 후보를 선택하는 행동을 줄이는 가설이다. C10 보호 평가에서는 조정자가 전달한 범주별 집계만 소비했다. 보호 질문·정답·ID·생성기를 열지 않았다. C10 공개 성공과 보호 실패는 그대로 보존하며 이 변경으로 실패를 재채점하지 않는다.

현재 프롬프트는 wire의 필수 primary 설명이 의미 판단보다 앞에 있었다. C11은 먼저 요청 범위와 정체성을 판단하고 action을 선택한 다음 해당 wire를 생성하도록 순서를 바꾼다. 기존 wire 문단은 내용 그대로 뒤로 이동했다. 기존 in-scope identity 문단을 범위/노이즈, 구체적으로 지칭한 원상품 미식별, 실제 모호함, 식별된 상품의 조건 불확실성 순서로 명시했다. 새 필드·추가 모델 호출·후처리 보정은 없다.

같은 상품의 별칭·오타·규격·명시적 정정은 식별 가능하다. 알레르기·성분·인증의 미확인은 정체성 미식별이 아니며 confirm/unknownConditions로 남긴다. 모호한 설명을 미등록 상품이라고 단정하지 않는다. 대체를 명시 요청하면 기존 한도 내 alternative를 유지하고, 대체 거절은 실제 원상품의 정상 식별을 막지 않는다. 질문 2회 이후 새 질문은 금지된다. 고객 동의나 거래 실행을 모델이 승인하지 않는다.

## 실제 변경과 불변

앱 변경은 `src/server/prompts.ts`의 CUSTOMER_PROMPT 및 `PROMPT_VERSION=customer-classification-v11`뿐이다. 경영주 export부터 EOF까지 기준 바이트와 같으며 SHA `58b2b314ea7f9630e717136caa0c5bb536134374ac61d8d544c2697d8b9c500d`다. 공통 버전 표기만 바뀌므로 경영주 실행 envelope에도 새 버전이 기록되는 점은 숨기지 않는다.

customer/merchant wire, schema, assistant 검증 본문, C10 크기 증명, provider/model, packing, catalog/retrieval, 데이터와 domain/UI는 수정하지 않았다. 비교 SHA는 격리 worktree `artifacts/private/c11-self/binding.json`에 보존했다.

- prompt SHA: `16e967e7f0adf1cfff7ff16e994a0e82e6ff09cf09ac6cc2e5fc0303f51a6d5a`
- focused test SHA: `1b0464bdcd57a5627c92f6dfd1ce8b6042fd105504a086c598b639204d81b07f`

## 실행한 자체 검사와 한계

- 기존 서버 60개 + 신규 2개 = 62/62 PASS. 신규 테스트는 합성 13경로의 선언된 응답을 provider로 주입하여 허용된 action, 원문·대화 전달, 후보 순서/ID와 uncertainty·alternative 무손실, question limit, usage, 응답 버전을 검사한다. 생성 모델이 그 발화를 올바르게 해석했음을 증명하지 않는다.
- 실제 설치 SDK의 fetch를 가짜 응답으로 대체하여 단일 호출, 정확한 customer instructions, strict decision schema, store=false, output3200, 기존 모델 옵션과 usage를 확인했다. 외부 HTTP·모델 호출은 0이다.
- 첫 전체 실행 후 새 테스트에서 union 타입을 좁히지 않아 TypeScript 오류 1개가 있었다. 원본 `typecheck.log`를 보존하고 `'action' in result`를 확인하도록 테스트만 수정했다. 최종 focused 2/2 및 `tsc --noEmit` PASS. 대체 비교 보존 문장 추가 후 focused도 재실행했다.
- C10 크기·음수/기호·별칭/모호함 fallback, 고객 wire, 경영주 restore/policy/stale/grounding 등 기존 60개 기술 검사가 통과했다. 서로 다른 model 품질을 fixture 성공으로 대체하지 않는다.

독립 의미/기술 검토, root 통합 게이트, 실제 dev·validation 두 반복·새 보호셋·역할 QA·UX·G5/G6는 이 자체 검사로 완료되지 않는다. 프롬프트 길이가 늘고 규칙 간 우선순위를 모델이 실제로 따르는지는 아직 불명확하다. 과도한 거절·질문 증가·정상 대안 누락이 나타나면 그대로 회귀로 판정해야 한다. 구현자는 자기 후보의 출시 품질을 승인하지 않는다.
