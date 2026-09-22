# ADR008 public oracle v4 독립 기술 검토

판정: **PASS — 평가 도구·파생 증거 무결성 범위만**. 작성자는 method_auditor/root, 검토자는 final_ux_state이며 검토자의 앱·평가 코드 작성은 0이다. 실제 모델·공유 비용 장부 접근·이번 기술 검토에서 보호 원문 접근은 0이다.

## 전수 재현과 목적 보존

공개 실행23개를 독립적으로 찾아 dev30의11개가 수정 슬롯과 무관하고, B0와 모든 대상 후보의12개 실제 실행이 새 oracle로 대칭 재채점됨을 확인했다. 총1260개 행에 대해 변경하지 않은 scorer로 원본 관측과 공개 정규화본의 old/new 전체 결과(개별 결과·이유·필수 오류·완료·토큰/횟수 집계 포함)를 독립 재현했다. 도구의 normalize/materialize/score 함수를 재사용해 동등성을 선언하지 않았다.

점수 변화는 3개 실행의 각1개 사례뿐이며 나머지 결과는 그대로다. C11 두 번째 원본은83/84 FAIL로 보존되고 새 파생 oracle 판정만84/84이다. 340ml 오답은 계속 FAIL이다. 기준95/90, 필수 오류0, 기존 사례/발화/분모, 앱 입력과 runtime50은 변경하지 않았다. 원본29개와 runtime50의 현재 바이트·cd29 Git 객체를 직접 대조했다.

## 공개 범위와 실행 차단

정규화는 허용한 enum/boolean/SKU/명령/수치/usage와 질문의 존재·공백 여부만 남긴다. 원문 발화·질문·diagnostic·code 문자열은 공개하지 않는다. 전용 경로 허용, 경로 탈출·부모 symlink·보호/비공개 dataset 거절을 읽기 이전 단계에서 확인했다. 이는 익명화나 암호학적 실행/검토자 신원 보장이 아니다.

초기 검토에서 자유문자열 타입, 경로 선검사, 전체 실행 목록 검증의 공백을 지적했고 수정 후 직접18개 반례 그룹이 PASS했다. 최종 freeze 경로에서 pending 원본을 받아들이는 반례를 추가로 재현해 보존했다. 작성자는 기존 Checker.nl(original, best=False)와 완결된92turn/unknown0/사용량·비용 합계 검증을 추가했다. 최종15개 독립 그룹은 정상 파생 두 회를 허용하면서 pending, 횟수·usage·비용 불일치, 미완료, 중복 실행, cap 불일치 및 새 source 계보 누락을 모두 차단한다. 원본83 품질 FAIL은 원본의 실행 무결성과 구분한다.

## 실행 검증과 최종 연결

revision02에서 release121·runner35를 독립 실행해 PASS했고, 최종 수정 후 관련 oracle33개를 다시 독립 실행해 PASS했다. revision04의12개 normalized·raw 바이트는 기존 전수 재현 시점과 같고 old/new report 객체도 전부 같다. 재생성된 일부 report의 JSON 키 순서만 달라졌으며 새 경로·도구 SHA·참조 hash를 차등 검증했다. 초기 반례와 이전 판정 파일은 보존했다.

최종 source: rescore `cb1583a1b90a39699a338d9ea4ff85a662cde5209f10f269cf075d764b2e5797`, checker `af7744bceaa8634a5396a2a0ce95e0c992244ff0cb4e3821a68f4f35441e9a98`, runner `c819eb21e6511bf7a6fc41e081a635bbd95b93aed8fa8ac87eecd799f0ab2de3`.

최종 cohort는 `quality/release/evidence/oracle-v4/revision-04/inventory.json` / `4a8f468ca279de1dc0296a2d2653e8380ff809b3b2ae5512607b367ae0134f17`. 12개 derivation과 private 전수 재현/차등 증거 hash는 `oracle-v4-independent-audit.json`에 결속했다. 보호 v3 영향 검토는 기존 독립 attestation을 참조하며 보호 입력을 이번 기술 검토에 다시 사용하지 않았다.

CTX-20260922-N15-v22의102개 현재 hash를 직접 ACK했다. context SHA `95596d129dc5f891bcabe66a00913f5382555852625901150481de710c07c042`, 기술 gate fingerprint `44ea1287ea5bc4736300200b8b3553246270a2f2dc7a6fa281211e52a7c1b3a4`.

## 남은 실제 검증

새 source commit·배포가 생성된 뒤 exact runtime50 계보를 별도로 결속해야 한다. 이 보고서는 새 deployment의 live 품질, fresh holdout, 역할별 브라우저 QA, 정량 UX 비교, G5/G6 또는 최종 출시 PASS를 선언하지 않는다.
