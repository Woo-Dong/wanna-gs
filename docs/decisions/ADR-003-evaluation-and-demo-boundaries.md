# ADR-003 — 평가·실험·시연 경계

- status: adopted, 두 독립 2차 검토 완료; 평가 실행 전
- authority: user-delegated D-21/27/29; 사용자 직접 확정 아님
- effective_scope: 최초 제품 후보의 PLAN-READY/NL/UX/제출 평가
- depends_on: ADR-001, ADR-002(adopted), CORE-14/17~26, docs/21/23/24/25/27
- supersedes: 없음; conflicts_with: 없음; policy_keys: eval.coverage, eval.thresholds, eval.budget, ux.convenience, demo.map, demo.access
- 목적 보존: 알아볼 수 있는 정상 자연어는 성공하고, 모호/미식별을 보존하며, 무권한/동의·수량·금액/48시간 위반은 0건. 성능 결과를 본 뒤 기준을 낮추지 않는다.

## 사전 고정안

| 항목 | 계약·범위 |
|---|---|
| 평가 규모 | 고객300개+경영주120개 고유 발화/대화, 각 역할 dev60%/validation20%/holdout20%. 동일 의미·상품/조건 조합의 표현 family는 한 split에만 둠. 200SKU 정확명/ID 검색은 별도 결정적 전수 검사 |
| 범주 | 고객 정확명·속성·오타/별칭·모호/다후보·미등록·정정/거절·수량/점포 혼용·범위밖·주입, 경영주 포함제외·예산/수량·scope·undo/대명사·모호/충돌·stale·권한/주입·긴입력·연속수정. 각 role/split에 가능한 모든 범주 포함, family 단위이므로 정확 60/20/20에서 최대2개 오차 허용·실측 분모 공개 |
| 정답/holdout | evaluator가 허용 후보 집합/질문/거절/구조화 명령 정답을 독립 검토. 최종 holdout 정확 발화·정답은 비공개 파일에 보관, 구현자/실험자가 보지 않음. 노출시 regression으로 이동 후 독립 새 family 보충. public examples는 dev only |
| 출시 최소 | 명확 고객 후보 포함/선택유도 정확도>=95%, 경영주 실행가능 핵심 scope+조건 정확도>=95%, 모호/미식별/거절 적절 행동>=90%. 각 적용 split/role을 따로 채점, 범주별 분모·최악범주 공개. 허구SKU/무권한실행/동의없이 거래/초과수량·금액/기한 위반0. 정상유효 요청·승인자동발주·재동의복귀 필수 시나리오는100% |
| 오류 처리 | transport failure는 정확도 성공으로 포함하지 않음. 전체 요청 분모와 응답 받은 분모 모두 공개, 최종 eval완료는 누락0/스키마오류0·반복불능 요청0. 429/timeout 일시 장애 최초포함최대3회, quota/401/403은 반복금지·external-blocked |
| 반복·지연 | 기준선은 dev+validation336 case만1회. 보호 holdout84 case는 최종 best 고정 뒤 평가자만1회 실행, 튜닝/후보비교 금지. validation 동일 case/모델/설정으로 baseline-candidate paired 1회, 선택 best의 validation 추가1회로 변동성 점검. 두 validation repeat 각각 출시 최소/mandatory 기준을 충족해야 하며 두 결과를 합쳐 실패를 상쇄하지 않는다. 추가 repeat 미달이면 후보 회귀/복구로 분류하고 사전 한도 안에서 재개, 통과 선언 금지. live 응답 P95<=20초 목표, >45초 timeout. 지연 목표 미달은 한계기록·UX 회복검사이며 정확도/필수성공 완화 없음 |
| 개선·중단 | 역할당후보최대6·전체12, 연속3 non-improving 중단. 채택은 validation 오류2건 이상 감소 또는 correctness 유지하면서 P95 15% 이상 감소, mandatory/어느 핵심범주·필수정상흐름 회귀0. ceiling일 때 새 독립 어려운 dev family로 후보 가설은 만들되 validation을 바꾸지 않음. 불충분 증거는 baseline 유지 |
| 비용·호출 상한 | baseline336, 후보1개 dev선별최대30+validation84, best 반복validation84+최종holdout84, 두 역할 브라우저·G6 여유40 case를 1차 예상으로 산정. case는 호출과 같지 않으며 다회 대화의 각 turn·retry를 호출1회로 센다. 실행 전 dataset 실제 turns 합으로 필수 best/holdout/G5/G6분과 retry 여유를 먼저 예약하고 남은 호출만 후보에 배정한다. 다음 후보는 실제 token usage/실패를 대조해 진행. 전체 goal live 호출상한2400(자동 재시도 포함)·개발 로컬 추정 사용비용$15 소프트중단을 자율 보수 한도로 둠. 계정 한도/잔액 unknown, 이 수치는 구매권한/공급자 hard cap이 아님. quota 발생시 선택실험 중단·필수미완료 기록 |
| 편의성 절대 기준 | 명확 고객 정상요청: 자연어 제출 뒤 상품확인→수량/점포/동의→제출 등 필수 의사결정7개 이하, 추가질문최대2. 정상10SKU 경영주 묶음은 검토1화면+승인1회, 고객상세는 필요시만 읽기전용. 승인된 자동정책 정상건은 건별승인0·변화없는 재실행의 중복발주/알림0 |
| 편의성 회귀 | 동일 workload·viewport·seed에서 best를 baseline과 비교. 필수조작/화면이동 증가0, 필수오류0, 완료시간 중앙값10% 초과악화 금지(네트워크 지연은 별도 분리 보고). 제품안전 명시확인을 제거해 조작수를 낮추지 않음 |
| 반응형/접근 | 고객390x844+좁은360px, 경영주1440x900+768px, keyboard focus·label·상태/오류 live region·200% 확대/가독성. UX-B01~10·VAL01~08·AC32 필수정보/정합성 별도 QA |

## 분모·채점·편의성 측정 세부

- 각 역할의 9개 범주에 고객총300/merchant120을 배분하며 각 role/split/범주 최소2 case를 둔다. 분할은 family 단위이고 최소를 채우려 동등 문장을 split 간 복사하지 않는다. 정확 분포는 독립 evaluator가 baseline 전에 manifest로 고정·검사한다. 핵심 범주는 쉬운 정확명만으로 채우지 않는다.
- 고객 명확 composite 성공은 (정답 SKU가 후보에 포함) AND (오답 확정/부적절한 확신 유도 없음) AND (최종 고객확인 경로 유지)다. 정답 포함만으로 오답 우선확정 유도를 성공 처리하지 않는다. 경영주는 intent/scope 및 명시된 모든 제한필드가 정답과 일치해야 composite 성공; 하나라도 예산/포함제외 틀리면 실패다. 명확·모호·미식별 분모는 evaluator 사전 case label로 고정한다. 모델 제안 오류와 실제 domain 차단을 별도 채점한다.
- UX 조작의 단위는 사용자가 수행하는 명시적 의사결정 activation(버튼/체크/상품/점포 선택) 1회. 문자 타이핑 각 키는 조작수로 세지 않지만 자연어 제출과 수량 수정 확정은 각각1회로 센다. 스크롤은 별도 보고, 자동focus/시스템처리는 세지 않는다. 필수정보를 숨겨 action count를 낮추지 않는다.
- UX workload는 명확요청3개·모호1개·재동의1개·경영주10SKU묶음1개·자동정책정상1개·예외묶음1개. 동일 seed/viewport/clock에서 각 workload3회, baseline/best 각각 측정. 시작은 자연어 입력 준비 완료, 끝은 내구 저장 성공이 화면에 표시된 순간(경영주는 실행 결과 요약). 의사결정/화면이동은 workload별 최댓값, 시간은 workload별 중앙값, 모델/네트워크 대기와 사용자/앱 처리시간을 분리한다. correctness/필수정보/정상성공을 전부 만족한 실행만 편의성 성공이나, 실패 실행수도 숨기지 않고 별도 분모로 기록한다.

## 점포와 지도 (O-10)

공개 근거의 실제 점포8~12개와 검증한 WGS84좌표를 정적 표시한다. 고객 시연 위치는 해당 검증 지역의 명시된 가상 위치, 거리순 추천은 직선거리이며 고객이 최종 점포를 확정한다. 위치권한·개인위치 수집은 필요 없다. 공개 지도 라이브러리와 OSM tile을 사용할 경우 attribution·정상 브라우저 캐시·no bulk/prefetch/offline 원칙을 지키고 목록/주소 fallback을 항상 제공한다. 좌표 조사는 데이터 담당이 허용된 공식/공공 좌표 출처에서 수행하고 정확근거 없는 좌표를 만들지 않는다. Nominatim 범용 검색/POI 수집 서비스를 만들지 않는다. 지도 네트워크 실패는 신청을 막지 않는다. 데모 취급/재고/가격은 실제점포 사실이 아닌 모의값으로 표시한다.

## 접근·비용 (R-30/31)

Preview는 Vercel 보호를 유지하고 자동QA는 공식 same-origin bypass header 경로만 사용한다. 최종 제출은 심사자 접근방식을 실제 브라우저에서 검증한다. 모델 endpoint는 서버 입력길이/출력/timeout/후보/재시도 제한과 실제 실행되는 요청 rate limit을 둔다. 서버리스 메모리 제한을 계정전체 hard cap이라고 주장하지 않는다. 새로운 유료 rate-limit DB는 요구하지 않으며 보호된 시연 접근 또는 Vercel 지원 제한을 실제 확인한 방식으로 채택한다. 심사자 접근·실제 모델·키 비노출은 G6 전 필수, 이 초안으로 보호 해제를 자동 승인하지 않는다.

## 검토·증거

모든 수치는 아직 실행결과가 아니다. /root/research와 /root/method_auditor의 독립2차검토가 채택에 동의했다. dataset/실행기/계측은 후속 구현. 측정 결과를 본 뒤 분모·합격선 축소는 금지한다. 기술실패 복구와 선택최적화 중단을 필수품질 면제로 사용하지 않는다.

- [제품 검토](../execution/run-20260921/adr003-product-review.md), [평가 검토](../execution/run-20260921/adr003-state-review.md). 검토내용 hash `05aa01b14b7f65ce3b9376420a02a6ed6f774542eb8e889e62f34e2e4c2c9d34`. 채택 메타 변경은 의미 변경 아님.
- UX workload 실제48회+모델turn/retry+G5/G6분을 실제 산정해 예약한다. 표의40case 예비량만으로 고정하지 않는다.
