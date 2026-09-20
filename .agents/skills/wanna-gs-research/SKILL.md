---
name: wanna-gs-research
description: Research current user needs, trends, product facts, UX, technical integrations and test approaches for WANNA GS at goal start or a feature design gate, then trace evidence into scoped design, seed data and evaluation cases.
---

# 실행 시점 조사와 설계 연결

[24번 조사 계약](../../../docs/24-market-research-and-scenario-design.md), [핵심 요구](../../../docs/CORE_REQUIREMENTS.md), [현재 결정](../../../docs/DECISION_INDEX.md)을 읽는다. 이 스킬은 개발용 조사다. 앱에 실시간 웹검색·자동 상품 등록을 새 기능으로 추가하는 지시가 아니다.

1. 시작 시 조정자/영역 담당과 연구 질문·영향 기능·필요 근거·조사 종료 조건을 정한다. 과거 대화의 상품/상황은 후보이며 실행 당시 최신 자료를 직접 확인한다.
2. 고객 검색/요청/대기/수령, 경영주 수요/발주/예외 처리, UX·데이터·API/배포·테스트 중 해당 영역을 조사한다. 상품/기술 사실은 공식 문서를 우선하고 사용자 행동은 독립 보도·관찰 근거를 구분해 읽는다. 검색 스니펫이나 같은 기사의 재전송을 여러 독립 근거로 세지 않는다.
3. 출처 URL·게시/사건/확인일·지원하는 주장·한계·상충 근거를 기록한다. 커뮤니티를 대표 수요 통계로 일반화하지 않는다. 자료를 확보하지 못하면 가설/미검증으로 표시하고 대체 출처를 찾는다. 개인정보·원문 전체를 테스트 데이터에 복제하지 않는다.
4. [연구 시나리오 양식](../../../docs/templates/research-scenario.md)에 니즈·상황·상품/업무 구분·기대 행동·금지 결과·기능 계약·test case를 연결한다. 생성한 발화는 synthetic으로 표시한다. 실제 사용자에게 받은 발화라고 주장하지 않는다.
5. 데이터 담당·UX/도메인·독립 평가자가 근거와 시나리오를 검토한다. 변경할 사용자 고정 요구가 아니라 위임된 설계 선택이면 [17번](../../../docs/17-autonomous-decisions.md)의 ADR로 결정한다. 범위 밖 기능은 근거와 후속 과제로 남긴다.
6. [19번 seed](../../../docs/19-data-research-and-seeding.md), [21번 평가](../../../docs/21-ux-and-natural-language-quality.md)에 연구 ID/버전을 전달한다. 개발 사례는 단계별 회귀에 재사용하되 최종 holdout은 평가자가 독립 보관하고 상품 alias/few-shot으로 유출하지 않는다.
7. 근거의 최신성·충분성·누락 범주와 다음 갱신 조건을 남긴다. 날짜/모델/API 변경, 미검증 가설, 설명하지 못한 테스트 실패가 있을 때 관련 조사만 갱신한다. 같은 검색의 무한 반복이나 조사 명목의 범위 확장을 하지 않는다.

초기 조사 완료는 앱·DB·평가 통과와 별개다. 실제 source를 열지 않았거나 도구/접근이 막혔다면 해당 주장을 확인했다고 보고하지 않는다.
