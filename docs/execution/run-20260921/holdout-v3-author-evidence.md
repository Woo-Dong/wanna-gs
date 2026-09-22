# 신규 보호 holdout-v3 제작·동결 증거

- 작성자 method_auditor, 독립 데이터 검토자 final_ux_state. 작성자는 C11 후보 프롬프트·앱 코드를 읽지 않았고 평가 원문/정답을 구현자에게 전달하지 않았다.
- revision03 **독립 DATA-REVIEW PASS**, 모델 품질/실행/출시 PASS는 아니다. 실제 모델 호출0, 운영 장부 쓰기0, 신규 dataset claim0.
- 공개 동결 파일: [manifest-v3](../../../evals/manifest-v3.json), SHA-256 `2ad1373a6539b81d569f2fd3a06080c171d8d15fbb6d1ca8fba17347817d2159`. frozenAt `2026-09-22T03:07:11.245383+00:00`.
- 보호 dataset canonical hash `5854b370a954fee49bfedf1834d24427267adc79499cd7ecc5e62925ba75518d`, 파일 hash `3c0ce0039cbbaace6dde8c4052ed46b7578b3c599ac7bce0f9542642210ec6c0`.
- [독립 검토](holdout-v3-independent.md)·[결속 JSON](holdout-v3-independent.json), JSON hash `932d328d5a482707ef732075a97f260706213ca90f79bf058a41483bf8794f1d`.

## 목적·분모·난도 유지

고객60/경영주24, 명확40/15·불확실20/9,18범주,76 단일턴+8 다턴=92 user turn을 유지했다. 경영주 명확 사례의 비기본 제약필드 분포도1필드6·2필드4·3필드5로 보존했다. 원래95/90·불완전0·mandatory0·고정 paired 회귀 기준과 scorer는 바꾸지 않았다.

독립 검토자는 새84행·정답·대화·업무 상태를 읽고 공개 dev/validation·두 은퇴 보호셋·고정 C10 공개 demo/테스트와 의미 family를 대조했다. 난도 동등 판정은 사전 내용·구조 검토이며 실제 모델 결과의 통계적 동등성 주장이 아니다. family hash 교집합0만으로 의미 비중복 PASS를 부여하지 않았다.

revision01은 의미9행·난도8행, 총17행의 문제로 FAIL했다. 해당17행만 보완한 revision02도 공개 테스트에 이미 나온 상품 정체성1건으로 FAIL했다. revision03에서 그1행만 보완하고 나머지83행은 그대로 보존했다. 모든 초안·검토·생성기·보완 이력은 private에 남긴다. 실패 원문을 숨기거나 실제 모델 결과를 보고 사례를 바꾸지 않았다.

## 상태·계보·비공개 경계

실제 SQLite seed에서 합성 요청과 검토 상태를 생성한 경영주 fixture24개를 준비했다. 모델 입력에는 업무 상태만 있고 정답·label·허용 action 목록은 없다. 최종 dataset의24개 identity/group SKU 결속을 재확인했으며 state hash는 `9cbbd15d484820f15b232dfa6514bd7979fb93a714c6301d82b920f5785b7d38`다. 이 오프라인 상태 생성은 실제 모델/브라우저 QA가 아니다.

원래 manifest, manifest-v2, 공개 dev/validation, 은퇴 v1 및 사용한 v2의 원본 바이트를 유지했다. 새 manifest는 v2를 predecessor로 연결하고, 기존 은퇴 기록을 유지한 채 C10 v2 FAIL을 추가해 총168개 은퇴 사례를 추적한다. 재호출 권한은 false다. `worst_attempts=276`은 데이터 메타의 기존 최대3회 상한이고 C11의 사전 `max_attempts=1` 실행 계약은 config와 실행 증거에 별도로 결속한다.

보호 원문·정답·상품/사례 ID·생성기는 공개하지 않는다. 소유 private 경로는 `artifacts/private/run-20260921/holdout-v3/`; root/앱 구현자는 공개 metadata만 사용한다. 이 데이터의 실제 최초 실행은 후보 dev→동일 설정 validation 두 반복 통과와 best 동결, 정확 배포/소스/장부 결속 및 별도 GO 뒤에만 가능하다. C10 holdout76/84 FAIL과 미실행 UX/역할 QA/G5/G6를 새 데이터 PASS로 대체하지 않는다.
