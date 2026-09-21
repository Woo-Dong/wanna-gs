---
name: wanna-gs-ux-audit
description: Audit WANNA GS customer and merchant journeys in an actual browser with independent role-specific QA, grounded scenarios, and server-state evidence. Use for Preview, integration, or release UX evaluation; do not treat screenshots, fixtures, or API-only checks as completed browser QA.
---

# 원하GS UX 감사

[UX·자연어 품질 기준](../../../docs/21-ux-and-natural-language-quality.md), [핵심 요구](../../../docs/CORE_REQUIREMENTS.md), [최신 시장 조사](../../../docs/24-market-research-and-scenario-design.md)를 읽고 [조사 시나리오](../../../docs/templates/research-scenario.md)와 [UX 보고서](../../../docs/templates/ux-eval-report.md)에 실제 근거·관측을 남긴다.

1. customer-qa와 merchant-qa를 서로 다른 agent ID로 배정하고 각 대상 기능 구현자와도 분리한다. 슬롯이 적으면 순차 실행한다.
2. 같은 deployment/source SHA를 실제 브라우저의 독립 profile/context에서 검사한다. 고객은 모바일, 경영주는 데스크톱 관점으로 사용자 경로를 직접 입력·선택·새로고침한다. 준비용 로컬 서비스는 seed/clock 설정에만 쓰고 평가 경로를 건너뛰지 않는다.
3. goal 실행 시 최신 시장 조사에서 모든 적용 기능 영역의 현실적 필요·최근 관심·표현·업무 맥락을 골고루 시나리오와 자연어 평가 사례로 만든다. 몇 개의 고정 예시를 전체 UX 근거로 재사용하지 않는다. 출처로 뒷받침된 사실·표현과 합성 persona/발화를 표시하고, 실제 GS 정책·재고·판매 실적으로 과장하지 않는다.
4. 고객의 식별·후보 정정·상품/점포 확인·동의·요청·상태·픽업과 경영주의 상품별 묶음→고객별 요청 상세·미식별·자연어 수정·정책/예산·발주·입고·수령을 각각 정상/경계/실패로 확인한다. 고객 상세에서 상품·수량·가격·동의 여부/시각·접수 순번·발주 연결·확보/배정/결제/예약/픽업 상태를 확인하고, 상품 합계·고객 행 합계·DB/event가 일치하는지 대조한다. 같은 세션의 양쪽 상태 일치, 다른 세션 격리, 권한과 모의 표기도 교차 확인한다.
5. 화면 관측에 console/network와 DB/event 증거를 연결한다. screenshot 한 장, HTTP 200, console 오류 없음, fixture 화면만으로 PASS 처리하지 않는다.
6. 필수 여정 불가, 잘못된 금액·결제·기한·상태, 오류 뒤 다음 행동 부재, 역할/세션 누출은 릴리스 차단으로 기록한다. 수정 뒤 같은 경로를 독립 재검증하며 미실행은 PASS가 아니다.

실제 브라우저 도구·배포·필수 데이터가 없으면 해당 범위를 BLOCKED 또는 not_run으로 남긴다. UX 취향 개선을 필수 결함으로 부풀리지 말고, 필수 G4~G6와 최소 출시 기준을 감사 중단 사유로 면제하지 않는다.

D-44: 각 QA가 한 탭에서 역할을 전환해 전체 흐름을 재현한다. 서로 다른 profile/context는 독립 QA의 초기 상태이며 공유 DB가 아니다. 새로고침 뒤 SQLite 사본 복원·reset과 저장 실패도 관측한다.
