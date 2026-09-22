# C11-RUNTIME-LINEAGE 독립 준비 검토

- 판정: **PREPARATION_PASS / N15 최종 source·context 결속 대기**. 실제 모델/브라우저 품질 PASS가 아니다.
- reviewer final_ux_state, C11 앱 작성/통합 root·research와 분리. 앱·테스트·실행기 수정0, 모델/HTTP/브라우저/공유 원장/보호 원문 접근0인 작업으로 수행했다. 별도 보호셋 영향 검토는 이 산출물에 포함하지 않는다.
- 기계 판독 근거: [JSON](c11-runtime-lineage-preparation.json), SHA-256 `b1446fe90d38e4ea0678708266d40f39082b3c854fd979dd7ac6f3915325bf75`. JSON은 이 문서를 다시 참조하지 않아 해시 순환이 없다.

## 직접 확인

C11 원본 source `cd29a2bc3be8c80fa00c03c2985f06819bef7255`의 Git 트리, 관측 HEAD `812827ada38b886ad5e364c3b4d2d8c904ef7ff8`의 Git 트리, 현재 작업 파일의 runtime inventory를 각각 비교했다. `app`, `src`, `public`, `data/seed`, `data/schema`와 runtime config/lockfile 전체 **50파일**의 경로와 바이트가 같다. 추가/누락/불일치/symlink는0이다. 이전 n14 C11 UX 준비의 runtimeFiles와도 일치한다.

runtime hash는 `d49c13dcbe3f5b358b8f7fb80d4316a68fd738c9f83a0e6395ec6f56a5dfbb9d`다. 코드뿐 아니라 배포 seed.sqlite·WASM·catalog·schema·lockfile를 포함한다. 앱/runtime 불변을 문서 선언만으로 판단하지 않았다.

기존 `CTX-20260922-N14-v21` 원본 hash `e6512b02cac714b66845dda8be5648094d8967155c624016003b7c6b6ed136b0`의87항목을 cd29 Git 객체에 직접 대조했다. 기존 C11 기술 gate·context·4개 quality review·고객/니즈/평가/보호 자료 독립 보고 총11파일은 현재도 cd29와 byte 동일하다. 기존 gate의8검사와4review가 fingerprint `9a995eeb881b1906c7f746f43d782e5534349326d9d1e314320d3a712f5db0c4`에 일치하는지 확인했다. 보호 자료의 공개 집계 보고만 사용했다.

## 인정 범위와 후속 결속

기존 gate는 contracts/catalog, Python211, server62, domainUI53, UX기구19, type/build의 **당시 기술 실행과 독립 검토**다. 현재 앱이 동일함을 증명하므로 C11 앱 구현 검토의 계보로 사용할 수 있다. 기존 전체 fingerprint를 수정 중인 N15 평가 실행기의 새 PASS로 재사용하지 않는다. ORACLE-V4의 manifest/normalization/derived checker/runner 변경은 새 기술 게이트와 별도 독립 검증 대상이다.

JSON의 `newSourceSha`는 null이다. N15 커밋 후 root는 새 Git runtime50과 원본 cd29의 일치를 다시 확인하고 정확한 Production/Preview deployment metadata의 source를 별도 결속해야 한다. 새 source를 과거 실제 validation이 실행된 source로 바꾸지 않는다. derived checker는 원 실행 source cd29와 새 제출 source를 구별하고 같은 앱 runtime/model/prompt/catalog였음을 검사해야 한다. 기존 actual run ID/fingerprint/FAIL/사용량은 그대로다.

이 준비 자료는 runtime byte 동등성의 앵커이며 신규배포 health·실제 모델 품질·보호 holdout·역할 QA·UX·G5/G6를 대신하지 않는다. runtime50 중 하나라도 바뀌면 이 동등성 경로는 stale이다. 최종 context가 확정되면 변경 영향 범위와 새 실행기 검토 결과를 함께 결속한다.
