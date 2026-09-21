# 제출 URL 접근 준비 — 미배포

2026-09-21 조회. G5/G6는 아직 미완료이며 아래는 최종 배포 준비다.

프로젝트 prj_T6x8XA3XyaNTgjMmvp7p9CgGCsks의 productionBranch는 main, 등록·검증된 기본 production domain은 `wanna-gs-sepia.vercel.app`이다. 현재 ssoProtection.deploymentType은 `all_except_custom_domains`이며 이번 조회에서 설정을 변경하지 않았다. 현재 Preview의 자동화 보호 헤더를 최종 심사자 URL에 포함하지 않는다.

[Vercel Authentication 공식 문서](https://vercel.com/docs/deployment-protection/methods-to-protect-deployments/vercel-authentication)(2026-09-15 갱신, 2026-09-21 확인)는 Standard Protection API 값 `prod_deployment_urls_and_all_previews`와 전체/Preview 보호를 구분한다. [Vercel 공식 설명](https://domains.vercel.com/academy/optimize-your-vercel-account/deployment-protection)은 production domain과 긴 생성 deployment URL을 구분한다. 계정에서 관측된 과거 enum과 현재 문서 enum은 다르므로 이름만으로 익명 접근 성공을 가정하지 않는다.

G5 통과 뒤 exact main source/Production deployment와 기본 domain의 연결을 확인하고, 쿠키·인증·보호 헤더 없는 새 브라우저에서 해당 domain의 앱·API·WASM·seed 접근을 실제 확인한다. 보호 설정 조정이 필요하면 Preview 보호를 유지하면서 production domain 공개를 지원하는 공식 설정만 적용한다. 이 절차는 사용자가 요청한 최종 제출 배포 범위이며 모든 배포의 보호를 끄는 방식을 기본값으로 삼지 않는다. 현재 익명 접근·최종 모델·SQLite/reset/48시간은 not_run이다.
