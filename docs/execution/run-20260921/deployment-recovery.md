# Preflight 배포 경계 복구

- 목적: 제품 구현 전 동일 프로젝트의 **Preview** SQLite/모델 경로 확인. 제품 Production/G6 통과로 간주하지 않는다.
- Git 연결 조회는 productionBranch=main이었으나 codex/preflight-20260921-probe push dc81df9005170cde0f48862fac302ae97b7fd202에 대한 최초 자동 Git 배포 dpl_Hj8RkGhTHbM9EDcUMPigz951gTzh가 target=production으로 생성됐다. 관측 전 기존 배포는 없었다.
- READY/aliasAssigned=true 확인. 취소 호출은 이미 완료라 400, ledger의 이 배포만 vercel remove --yes로 제거 성공. 기존 사용자 서비스/데이터 제거 없음. 잠시 Production 별칭이 점검 화면을 가리킨 사실을 숨기지 않는다.
- 최초 Git 배포의 분류 원인은 아직 미확정. main 설정만으로 자동 Preview를 보장한다고 가정하지 않는다. 추가 push/merge 전 Git 배포 분류를 확인하고 직접 생성 API에 target=preview를 명시한다. 보호 설정 유지, 새 유료 기능 사용 없음.
- Preview API 생성/실제 target/source 확인은 preview-deployment.json 및 후속 P05~09 결과와 연결한다. 원인 확인 전 자동배포만 믿고 제품 통합/릴리스 진행 금지.
- 별도 CLI 복구: branch별 PROBE_TOKEN 추가가 branch_not_found로 실패해 먼저 정확한 기존 HEAD에서 원격 probe branch를 생성한 후 성공했다. 잘못 옮긴 SHA로 base 생성 422가 1회 발생했고 git rev-parse HEAD의 실제값으로 바로잡았다. 공유 이력/기본 branch 변경 없음.

- API에 target 문자열 preview를 넣은 두번째 시도 dpl_7TUDmUeKJ5DNo6HQCT7WzjXJTZNh도 production으로 응답했다. 공식 API 계약의 target은 생략 시 Preview이며 preview 문자열 자체를 지정하는 방식이 아님을 확인했다. 두번째 배포도 이 ledger ID만 제거한다.
- target을 **생략**하고 정확한 gitSource ref/SHA로 만든 dpl_HjgwxK7oQCwRuoG48SUZF7XE9h3t는 target=null(Preview) 확인. 이 검증된 API 경로를 후속 Preview에 사용한다. 앞선 두 배포는 Preview 성공/제품 Production 성공 증거로 사용하지 않는다.

## B01 후속 복구와 확인

- exact source `5cf1ed0` 첫 요청(target 생략)이 `dpl_ChBDNJCMwVjbA5q51dBje2xmSXxG` target production으로 생성돼 즉시 취소·제거했다. 다음 target staging 명시도 `dpl_5vQB6DEZ2pADmhiuypMLRoQesczP` production이어서 같은 실행기에서 즉시 취소했다(취소 exit 0). 이 취소 기록은 유지했다.
- Vercel CLI 59.23.2의 first-deployment 안내와 [공식 환경 문서](https://vercel.com/docs/deployments/environments)를 root와 method_auditor가 대조했다. 첫 배포를 Production으로 지정하는 동작은 공식 문서로 확인했다. 전부 삭제한 뒤 그 상태로 복귀한다는 인과는 관측에 근거한 추론이다.
- 취소 기록을 유지한 상태에서 hasDeployments=true를 직접 확인하고 target 생략 요청을 한 번 수행했다. `dpl_9fTvCGkZoNcB8SYDD456g9iZ1euv`, target=null, source5cf1ed0, READY를 확인했으며 390/1440 실제 Chrome·health·가로 넘침0·pageErrors0 검사 PASS. metadata는 bootstrap-preview.json, 브라우저는 bootstrap-browser.json.
- 향후 배포는 반환 target/source를 즉시 검증하고 예상치 않은 Production은 취소한다. 활성 Preview를 유지해 첫 배포 상태를 반복 만들지 않는다. 정상 제품 Production은 여전히 G5 이후에만 제출한다. 환경 추론/target 생략만으로 안전을 보장한다고 주장하지 않는다.
