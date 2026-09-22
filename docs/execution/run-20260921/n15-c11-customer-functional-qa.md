# N15 D50 고객 독립 기능 QA

**고객 실제 브라우저 6/6 PASS, 별도 HTTP fixture 경계 12/12 PASS.** 실제 OpenAI 호출은 3회이고 fixture 단계는 0회다. 검사한 고객 기능 범위에서 미해결 중대 오류는0이다. 이는 D50 기능 출시의 고객 구성요소이며 보호셋 75/84 FAIL·원래 G5 NOT_READY를 PASS로 바꾸지 않는다. 경영주 독립 QA와 최종 main/Production G6는 별도다.

## 결속·독립성

평가자는 `method_auditor`, 제품 구현자는 `root`/`research`/`preflight_builder`로 구분했다. 고객 UI 구현자 research의 자체 검사를 독립 증거로 사용하지 않았다. 실제 Chromium의 fresh profile과 390px 고객 관점에서 UI를 입력·선택하고 한 탭 역할 전환, 새로고침, SQLite/IndexedDB snapshot과 events를 대조했다.

- source `e727b99a640743c744082f8a3cf754260f0d755a`, current/Git source47 및 runtime50 일치. runtime `d49c13dcbe3f5b358b8f7fb80d4316a68fd738c9f83a0e6395ec6f56a5dfbb9d`.
- exact Preview `dpl_HrUL1N35GXdFVfGG95fCgxMBKJRn`, `https://wanna-o08huc5in-beatrain-4635s-projects.vercel.app`, target null/READY. NL holdout의 별도 Production 배포와 같은 앱 source이지만 배포 ID는 다르다.
- model `gpt-4.1-mini-2025-04-14`, prompt `customer-classification-v11`, catalog248/seed 불변. 반환 모델·prompt·catalog와 실제 usage를 검사했다.
- 정상 실행 `c11-customer-qa-02`, approved config SHA `e999ded48152f151305af75750d6b3aab3f09f88f47d1cfe48763a496b1b0378`.
- 경계 실행 `c11-customer-boundaries-01`, cap0 config SHA `807cd79a4c85a7ab70c2a151af3d3b79334896b7e6321341bb320246a2b0287e`. 정상 실행 PASS와 같은 source의 requested/received SQLite 파일 및 metadata SHA를 결속한 후 실행했다.

## 최초 실패와 최소 도구 수리

첫 `c11-customer-qa-01`은 Preview에 삽입된 외부 Vercel feedback script 때문에 경로 guard가 중단됐다. 모델0회, 고정6검사 모두 NOT_RUN, 결과FAIL과 원본을 보존했다. 브라우저 노모델 진단에서 same-origin 앱 자산은200이고 상품 찾기 버튼은 정상임을 확인했다.

고객 전용 private route helper만 정확 `https://vercel.live/_next-live/feedback/feedback.js`의 GET/script/query·hash·userinfo 없음에 한해 네트워크 전에 abort하고 처리 완료로 반환하도록 수정했다. 다른 외부 origin/path/API/method/type 차단과 OSM 처리, 비밀 헤더의 origin 제한은 그대로다. 앱·shared qa-live·경영주/G6 helper는 바꾸지 않았다. 이전 helper bytes를 보존했다. 자체7회귀와 별도 final_ux_state의19경계 독립 검토가 통과한 후 root의 조건부 GO로 새 실행을 시작했다. 실패한 run을 덮거나 단순 재호출하지 않았다.

## 실제 모델·브라우저·SQLite 정상 검사

- PASS — 브랜드·모의·모바일·예시 입력만/복구
- PASS — 실제 모델 정확명→후보·usage SQLite 저장
- PASS — 지도 장애 목록 fallback·명시 동의·수량변경 재확인·연타1접수
- PASS — refresh·한탭 경영주 승인→공급→고객 예약·48h 아직없음
- PASS — 입고 후 알림+48h·고객/경영주 상태 일치·refresh
- PASS — fresh 실제 모호입력·후속정정 history와 사용자 확인 보존

단일 요청은 상품·한 점포·수량2·가격·미리 체크되지 않은 명시 동의를 확인한 뒤 만들어졌다. 수량 변경은 동의를 해제했고 연타는 요청1/동의1만 생성했다. 사용자 최종 선택 전에는 거래 요청0이었다. 공급·모의 결제 성공 후 예약은 confirmed였지만 입고 전48h deadline은 null이었다. 입고 뒤 pickup_ready 알림1과 정확172800000ms가 생성됐고 refresh 및 수령 완료 상태가 SQLite와 일치했다.

실제 지도 타일 장애를 주입하여 점포 목록 fallback을 확인했다. 이는 정상 지도 제공자의 가용성 증거가 아니다. 서로 다른 fresh profile의 모호한 입력→후속 정정에서 이전 실제 응답 JSON/history와 clarificationCount를 보존했고 동의 없는 요청/예약은0이었다. 390/768/1440px overflow와 focus를 검사했다. brand/pronunciation·모의 표기·픽업 화면 및 360px/200% 글자 스크린샷을 독립적으로 확인했다.

## 별도 fixture 경계 검사

이 단계의 모델 응답은 HTTP fixture이며 실제 모델 품질 증거로 합산하지 않는다. 실제 브라우저·SQLite/IndexedDB 저장, UI 동작과 도메인 전이는 그대로 실행했다.

- PASS — HTTP 실패는 니즈가 아님·입력 보존·fixture 정상복구
- PASS — 모호 질문의 실제 history/count·2회 한도 보존
- PASS — 미식별 명시 니즈 저장·확약 오염0
- PASS — 허구 SKU 응답 거절·거래0·오류후 정상회복
- PASS — 늦은 응답 input revision/역할 변경 차단
- PASS — 대체 후보 거절/전환 취소는 원요청·동의 유지
- PASS — 모의 결제 2회 실패→풀해제→재동의 정상복귀·새발주0
- PASS — 다른 합성고객 내역 격리·360px/200% 글자 핵심조작
- PASS — 손상 snapshot 유지→명시확인 복구·generation 증가
- PASS — 실제 IndexedDB write abort·요청 미생성·동일화면 정상재시도
- PASS — 고객 48h 정각 종료·명시 reset 후 refresh 보존
- PASS — 후속 정정에 실제 후보 SKU·순서·차이 history 보존

14개의 모의 HTTP 응답, 실제 모델0, 예상 밖 outbound 차단0, 오류0이었다. fixture 실행 전후 공유 모델 장부 bytes가 같았다. 원래12개 검사 분모와 요구를 줄이지 않았다.

## 비용·증거·종료

실제3회 HTTP200, 총23,739 tokens, 추정비용 $0.0098844. 후속9회/$0.45 예약 및 prior50/unknown $.05/총2400회·$20을 유지했다. 고객 단계 종료 upper2099회/$12.7664421, known2049회/$10.2164421, pending0/unknownprovider0이다. 장부 SHA `e8c8d7b31879b7f4ec3604d3e6e33ef3699da0563faffd31ebd05b1028036e5e`는 고객 인계 시점 값이며 이후 경영주 검증이 진행되면 최신 장부는 달라질 수 있다. 단일 writer를 root에 반납했고 이 평가자의 추가 유료 호출은0이다.

공개 `quality/release/evidence/c11-customer-functional/`의 qa.json은 기존 Checker.qa와 호환되는 G5 구성요소 형식을 사용하며 별도 `D50-functional-release/customer-component`, `original_full_g5_pass:false`를 명시한다. live/fixture 보고서·SQL 집계·첫 setup FAIL을 각각 hash로 연결했고 Checker.qa 구성요소 검사는 PASS다. private 원본 화면·SQLite·응답·실패 로그는 작업 공간에 남겨뒀다.

알려진 자연어 한계인 잘못된 후보·불필요한 질문·미식별 행동·이전 대화·되돌리기 제안 오류는 [보호 평가](n15-c11-holdout-evaluation.md)에 그대로 남는다. 이번 성공한 정상 경로가 모든 자연어 입력의 정확성을 뜻하지 않는다. 고객 확인·동의 및 경영주 승인 경계를 유지하며, 남은 기능 출시 조건은 root가 경영주 독립 QA와 최종 main/Production 증거로 확인한다.
