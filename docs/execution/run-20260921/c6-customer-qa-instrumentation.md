# 고객 QA 준비 장치 독립 검토

판정: **준비 장치 PASS**, 실제 고객 QA·C6 모델 품질·G5/G6는 별도다. 작성자는 preflight_builder, 독립 장치 검토자는 research다. research가 고객 UI 작성자이므로 이 검토를 독립 고객 역할 QA로 세지 않는다. 실제 역할 실행·판정은 method_auditor 소관이다.

실제 브라우저/모델/외부 네트워크/공유 goal 장부 읽기·쓰기0, 비밀 환경값/보호 평가 원문 접근0으로 검토했다. 승인 전 config는 false이며 source/Preview/모델의 최종 값은 실행 전에 새로 결속해야 한다. C6 실제 dev 실패 이후 이 준비물의 PASS를 C6 live QA 실행 근거로 쓰지 않는다. 다른 승인 후보로 바꾸면 identity/source/config 및 변경 영향의 별도 검토가 필요하다.

## 검증 범위와 결과

준비 장치는 live 정상6개/최대3모델 호출과 별도 fixture 경계12개를 분리한다. live는 원문·실제 응답 history, 명시 상품 확인/동의, 요청 중복 방지, 공급·모의결제·입고/48시간과 SQLite/IndexedDB 상태를 확인하도록 구성되어 있다. fixture는 동일 source의 성공 live snapshot을 결속하고 모델 호출 없이 오류·늦은 응답·저장 실패·재동의·기한을 검사한다. 실제 실행 전의 스크립트/locator/상태 단언 검토이며 화면 검사를 대신하지 않는다.

최초 작성자 시험14개를 직접 실행했으나, 별도 반례에서 두 누락을 발견했다. 외부 POST의 경로가 /api/로 시작하지 않으면 모델 회계 없이 통과하는 경우와, 새 evals/manifest-v2.json의 source 결속 누락 허용이었다. 원본과 실패 근거를 남긴 뒤 작성자가 이 private 장치만 보완했다.

최종 변경은 필요한 OpenStreetMap 숫자형 tile image GET만 외부 허용하고 그 외 요청/리다이렉트를 차단하며, 민감 헤더 제거·재시도0·STOP/NOT_RUN 분모를 유지한다. 새 평가 manifest도 필수 source에 포함했다. 일반 앱/공통 실행 helper/UX 비교 장치는 변경하지 않았다.

- 수정 후 작성자 시험19개 독립 재실행 PASS, fail/skip/cancel0.
- 추가 독립 route callback 모의16개 PASS: 외부 API 차단, STOP 후 전송0, 정상 타일/같은 origin 정적파일 유지, 잘못된 host/method/query/resource type/redirect 차단과 헤더 제거.
- 추가 임시 binding10개 PASS: 정상 및 source/manifest/예산 실행기/runtime/승인/출력 경로/호출 상한/필수 helper 반례.
- 추가 실패 분모 모의2개 PASS: 현재 live FAIL+후속5 NOT_RUN=6, fixture STOP 현재FAIL+후속11 NOT_RUN=12. 실제 브라우저를 띄우지 않았다.

최종 private 준비 inventory SHA `34d06b7207464cb0a3b4831183aa273a294f8337c8534d1857871249767b9dae`의10파일을 대조했다. 독립 상세 보고서 SHA `5c4246daa7c67ca01182af542f7191bf26ff2b0a6cb852a76ab74d4f96f231e1`; 준비물과 최초/보완 로그는 해당 작업 공간 private 영역에 보존한다. 독립 VM 검사 첫 실행의 Buffer 누락은 검사 코드의 setup 오류로 구분·보존했고 실제 판정에 사용하지 않았다.

검토 미해결0이지만 실행 승인은 아니다. 최종 후보 선정, exact 배포·전체 runtime/source/plan/helper/config 결속, 예약을 포함한 예산 확인과 직렬 GO 후 실제 브라우저로 수행해야 고객 역할 QA 증거가 된다. fixture 응답이나 모의 전송을 실제 모델 성공으로 바꿔 표시하지 않는다.
