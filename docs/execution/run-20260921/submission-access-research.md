# G6 제출 접근 사전 조사 — 읽기 전용

- 작성/확인일: 2026-09-21, 담당 preflight_builder. 현 프로젝트 보호 설정 GET 및 공식 문서 조사만 수행했다.
- 목적 보존: CORE-13 제출 URL 실제 앱·모델·DB 브라우저 검증, CORE-23 사용자 OpenAI 키 서버 전용, ADR003 Preview 보호·비용 한도, D44 한 PC SQLite·D45 OpenAI 단일 경로를 유지한다. 이 문서는 공개 전환 승인이나 G6 PASS가 아니다.
- 변경/배포/secret URL 생성/유료구매/외부 DB 생성/실제 모델 호출은 모두0. 환경변수 API는 호출하지 않았으며 토큰·환경값·bypass 값은 출력/파일 저장하지 않았다.

## 현재 확인된 설정

Vercel CLI59.23.2의 GET `/v9/projects/prj_T6x8XA3XyaNTgjMmvp7p9CgGCsks`를 팀 `beatrain-4635s-projects` scope로 호출했다. 전체 JSON은 subprocess 메모리에서 읽고 아래 허용 필드만 출력했다. 팀 GET `/v2/teams/team_LQu4hJD51rPgRDt3ExiYHBhf`도 plan/slug만 출력했다. 두 요청 exit0.

```json
{
  "project": "wanna-gs",
  "plan": "hobby",
  "ssoProtection": {"deploymentType": "all_except_custom_domains"},
  "passwordProtectionConfigured": false,
  "trustedIpsConfigured": false,
  "protectionBypassConfigured": true
}
```

`deploymentProtection` 별도 응답 키는 null/미존재였지만 이것은 보호 꺼짐을 뜻하지 않는다. 유효 설정은 위 ssoProtection이다. bypass는 존재 여부만 확인했으며 공유 가능한 제출 URL로 전환하지 않았다. alias 목록/Production revision/실제 익명 접근은 이번 제한된 조회에서 확인하지 않았으므로 특정 URL이 지금 공개라는 주장은 하지 않는다. 프로젝트 GET의 공식 경로는 [Find a project](https://vercel.com/docs/rest-api/projects/find-a-project-by-id-or-name), 보호 설정을 변경하는 별도 동작은 [Update a project](https://vercel.com/docs/rest-api/projects/update-an-existing-project)에 문서화되어 있다.

## 공식 문서와 날짜 차이

검색 색인의 2026-01-07 overview에는 Hobby에서 production 보호가 유료처럼 남아 있었다. **2026-09-09 공식 변경 공지와 2026-09-15 가격표를 우선**한다. 최신 기준 Hobby도 Vercel Authentication의 Standard/All Deployments, Preview domain exceptions, automation bypass를 추가 보호 요금 없이 사용할 수 있다. Password Protection은 Hobby 미지원, Pro는 프로젝트별 월$20이며 Trusted IPs/Passport는 Enterprise 범위다. Hobby shareable link는 계정당1개 제한이다. 이 기능 요금이 없다는 것이 앱/모델 호출 비용 면제는 아니다. [공식 변경 공지](https://vercel.com/changelog/protect-production-deployments-for-free-on-every-plan), [최신 기능별 가격표](https://vercel.com/docs/deployment-protection/usage-and-pricing)

Standard Protection은 production domain을 제외한 preview/generated deployment URL에 보호를 유지하는 옵션이다. 현재 API의 `all_except_custom_domains`는 이 목적과 부합하는 구성 후보이며 그대로 보존하는 것이 우선이다. 단, 9월15일 Authentication 문서의 API 예시에는 `prod_deployment_urls_and_all_previews`를 Standard로 표기하고 현재 응답값을 생략하는 문서 불일치가 있다. 이 조사만으로 두 enum의 모든 alias 동작이 같다고 단정하거나 API PATCH로 임의 변환하면 안 된다. 적용 전 Dashboard의 현재 범위 이름 및 실제 anonymous URL별 동작으로 확인해야 한다. [보호 범위 설명](https://vercel.com/docs/deployment-protection), [Authentication API 예시](https://vercel.com/docs/deployment-protection/methods-to-protect-deployments/vercel-authentication)

## 구체 대안과 권고

| 대안 | 필요한 후속 작업 | 목적/제약 |
|---|---|---|
| A. 현 보호 설정 유지 + 정상 Production project domain/alias를 제출 | 두 관점 ADR 검토로 공개 제출 범위를 채택한 뒤 exact release의 Production 배포·도메인 연결, 익명 브라우저 검증 | 우선 권고. 보호 전체off/bypass공유/요금제 변경 없이 Preview 보호와 일반 접근을 함께 달성 가능한 공식 경로. generated immutable URL을 production domain으로 혼동하지 않는다. 현 실제 alias는 별도 확인 필요 |
| B. All Deployments 유지 + Vercel 인증 기반 심사자 접근 | 심사자의 Vercel 접근 권한·절차 검증 | 보호는 강하지만 로그인 없는 공개 제출 목표와 다르다. 신규 심사자 로그인/권한을 이미 있다고 가정하지 않는다 |
| C. 특정 Preview domain exception | 별도 정책 채택 후 명시 domain만 공개 | 이제 Hobby도 지원하지만 해당 Preview 보호를 해제하므로 ADR003의 Preview 보호 유지 기본안과 다르다. Production domain 공개용 기능도 아니어서 이번 우선 대안이 아니다 |
| D. Shareable Link | 별도 승인·비밀 취급·접근 검증 | 일반 공개 alias가 아닌 전달 가능한 접근 권한이고 Hobby 계정당1개 제한. 현재 생성/노출하지 않았다 |

Preview exception은 지정 domain의 기존·미래 배포 모두 공개로 바뀌고 제거 시 다시 보호된다. 따라서 한 배포에만 한시적으로 적용되는 보호 우회로 취급하지 않는다. [공식 exceptions 범위](https://vercel.com/docs/deployment-protection/methods-to-bypass-deployment-protection/deployment-protection-exceptions)

A를 채택해도 공개 모델 endpoint 비용은 별도 제약이다. root 서버의 현재 provider.ts에는 instance call 상한과 maxRetries0/45초 timeout이 존재한다. 서버리스 instance 메모리를 계정 전체 비용 hard cap으로 해석하지 않는다. 최종 공개 범위/운영기간/서버의 실행 가능한 요청 제한을 두 관점 정책 검토로 다뤄야 하며, 로컬 eval ledger2400/$15가 외부 심사자 HTTP를 자동 차감한다고 주장하지 않는다. 본 보고서는 이를 이유로 유료 서비스나 외부 DB를 요구하지 않는다.

## G6 실제 검증 절차 (아직 미실행)

1. 독립 두 관점 검토에서 A의 공개 제출 경계·호출 비용 한계·복구 방법을 채택하고 최종 코드 SHA/CI PASS/source fingerprint를 고정한다. 보호 해제 자동승인으로 ADR003을 해석하지 않는다.
2. 승인된 release의 Production deployment ID·target·git SHA와 제출 production domain/alias 연결을 읽기 확인한다. Preview/generated URL과 제출 domain을 각각 적는다. API 보호 필드는 배포 전후 비교하고 Preview 보호 유지 여부를 별도로 확인한다.
3. Vercel 로그인 쿠키·automation bypass header/query가 전혀 없는 새 브라우저 context에서 제출 주소 직접 열기→인증화면 없이 앱 표시→새로고침·직접 재방문을 확인한다. 루트 HTML200만으로 PASS하지 않고 WASM/seed/JS·모델 API 동일 origin 요청을 확인한다.
4. 최종 두 역할 실제 모델 E2E를 예산에 예약해 실행한다. 고객 식별→최종 상품/점포/수량/동의→모의 요청, 경영주 자연어→검토/승인·정책, 정상/모호·오류·복구를 각각 확인한다. usage/model/requestId와 실패 분모를 보존한다.
5. 같은 탭 SQLite/IndexedDB 저장·새로고침·역할 전환·reset·48시간 직전/정각/직후 및 수량/동의/중복 방지를 실제 제출 origin에서 확인한다. 새 origin의 빈 IndexedDB 정상 초기화도 확인한다.
6. public bundle/응답/브라우저 저장소에 서버 키나 bypass 비밀이 없는지 값 노출 없이 검사한다. 보호된 Preview는 익명 접근 차단, 자동QA는 공식 same-origin header 경로로 별도 검증한다.
7. 제출 URL·검증 시각·배포 ID/SHA·모드·실제 호출수·각 정상/예외 증거·남은 한계를 기록한다. 하나라도 실패/미실행이면 G6 완료를 선언하지 않고 수정 후 영향 범위 재검증한다.

## 결론과 남은 확인

추가 유료 상품 없이 **Preview 보호를 유지하면서 Production project domain으로 일반 접근을 제공하는 대안 A가 가장 작은 변경 범위**다. 현재 설정이 이미 그 목적의 후보이므로 우선 설정 변경0으로 배포/alias 동작을 확인한다. 이번에 실제 판정한 것은 Hobby/보호 설정 조회와 공식 지원 옵션뿐이며, 공개 여부·심사자 접근·비용 보호·실제 제출 URL 제품 성공은 후속 ADR 및 G6 실검증 대상이다.
