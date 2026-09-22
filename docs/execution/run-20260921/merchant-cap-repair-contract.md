# 경영주 현재안 수량 상한 누락 복구 계약

권한 근거는 원래 GOAL/AGENTS의 필수 결함 수정·독립 검증 지시다. D47을 경영주 변경 승인으로 확장하지 않는다. 별도 필수 버그 복구이며 D47의 고객 자연어 후보 C7와 구분한다. C7 prompt/model/schema/search/catalog 및 평가 정답·실패·후보 수는 변경하지 않는다. 기존 ADR005의 이번안 maxQuantity→proposal.maxQuantities, CORE05/06/07/25·AC07/08/31의 명시 상한 보존을 구현한다. 새 경영주 자연어 후보·정책 추가가 아니다.

독립 상태 감사자가 실제 seed/메모리 SQLite로 수요5→예산0으로 보류→예산50000/최대2 수정 시 maxQuantities가 비어 line5→명시 승인 order5를 재현했다. 현재 merchant adapter가 current.lines만 매핑해 deferred SKU가 빠진다. 실패 이력은 유지한다.

작성자 preflight_builder: 격리 worktree의 src/components/merchant/model.ts와 tests/merchant/model.test.ts, 필요한 tests/domain/merchant-cap-regression.mts 및 자체보고만 소유. root는 contracts/context/gates/Git. 독립 검증자 holdout_revision_review는 발견 반례와 실제 SQL 및 정상/인접 기능을 재검증한다. 공유 schema/lockfile/prompt/provider/catalog/도메인 서비스 수정은 하지 않는다. 모델·장부 호출0.

실제 명시 상한을 현재 검토의 실행·보류 SKU에 일관되게 반영하고, 원수요/예산/MOQ/배수·재검토/stale·명시승인은 기존 도메인 서비스가 유지하게 한다. 현재 line수량이 작은 것을 상한 의미와 혼동하지 않는다. 상한이 올라가도 실제 수요를 넘는 발주는 금지한다. 기존 다른 조건/undo·미지정 필드 보존과 미래 정책 copy의 상한을 회귀 확인한다. 기존 테스트의 가정이 정책과 다르면 근거/원래실패를 남기고 독립검토하며 합격선 완화로 처리하지 않는다.

이 수정은 격리 브랜치에서 검증하고 별도 PR/CI로 통합한다. C7 개발 평가의 source63614f9/원본은 그대로 남긴다. 최종 runtime이 바뀌면 이후 전체 validation/holdout/UX/G5/G6를 변경된 정확 source에 새로 결속한다. 과거 runtime 성공을 새 runtime PASS로 바꿔 쓰지 않는다. 고객 후보 실패 시 최종제품 배포는 여전히 불가하며 추가 NL후보를 자동 만들지 않는다.
