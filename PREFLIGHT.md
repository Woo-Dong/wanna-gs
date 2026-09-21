# 사전점검 20260921

격리 임시 branch의 최소 연결 검사이며 상품·요청·발주 기능이 아니다.

- 기준: 3ef1ee3447ab3943527c4685949da4116bcf0566
- 소비한 context hash: 74bf125ebe9c8ed2f7933abb55b08c904400f3a7ba1319c395a2429c32c20679
- 목적 보존: CORE-08/13/17/19, D-44 브라우저 SQL·한 탭 역할 전환·내구성 저장 경계를 제품 구현 전에 검사한다.
- 소유: preflight_builder는 package/lockfile, seed, worker/core, 최소 UI, SQL 테스트, preflight CI. 모델 probe API는 조정자.
- API 모델·제품 G1~G6·배포 성공은 이 scaffold의 로컬 테스트로 입증되지 않는다.

## 실행

Node 22에서 `npm ci`, `npm run check`, `npm start`. 개발은 `npm run dev`.

`npm run seed`가 같은 소스로 실제 `public/probe/seed.sqlite`, WASM, JS 및 manifest를 생성한다. 브라우저는 Worker 한 개에서 SQL을 실행하고 `wanna-gs-preflight-20260921` IndexedDB의 `snapshots/current`에 바이트와 버전을 한 트랜잭션으로 저장한다. 역할 전환은 같은 DB를 사용한다. SQLite 변경 후 snapshot 저장이 성공해야 화면이 완료를 표시한다. 실패 시 마지막 성공 바이트를 다시 열고 외래 키를 재활성화한다. 초기 저장 실패는 쓰기를 잠그며 초기화 재시도로 회복할 수 있다. 손상/버전 불일치는 자동 덮어쓰기 없이 초기화를 안내한다.

## 브라우저 점검

1. 최초 0개, 외래 키 켜짐 확인.
2. 고객 메모 저장 → 경영주 전환 후 같은 메모 → 새로고침 후 같은 메모.
3. 두 번째 메모 입력 → 다음 저장 실패 시험 → 오류와 기존 메모 개수 유지.
4. 다시 일반 저장 → 성공하고 두 개.
5. 초기화 → 0개, 세대 증가 → 새로고침에도 0개.
6. 정확한 Preview에서도 동일 검사. UI 상태만 보지 말고 seed/manifest 및 IndexedDB 바이트를 함께 확인.

실패 주입은 probe 전용 버튼이며 모델·제품 fixture가 아니다. Worker는 허용된 고정 명령만 받고 임의 SQL 실행 인터페이스를 공개하지 않는다. 비밀값은 이 작업트리에 복사하지 않는다. 로컬 서버 인증·실결제·다중 기기 동기화를 주장하지 않는다.

## 보존과 정리

사용자 요청에 따라 작업트리와 로그를 보존한다. 로컬 산출물은 이 경로에만 생성된다. 정확한 Preview origin의 `wanna-gs-preflight-20260921` namespace만 정리 대상이며 다른 앱 데이터는 삭제하지 않는다. 외부 PR/CI/Preview 생성·정리는 조정자의 ledger로 추적한다.

모델 폼은 서버 route 응답의 `mode=live`, `result.ok=true`, `message` 1~80자를 검사하고 기존 Worker `add`로 저장한다. API 오류는 저장하지 않는다. fetch 시작 시 generation 및 요청 번호를 기억하고 초기화 후 늦은 응답을 폐기한다. 접근 토큰은 password input과 React 메모리만 사용하고 SQLite/IndexedDB/localStorage에 기록하지 않는다. 요청 timeout은 55초다. 저장 실패 시험은 실제 IndexedDB readwrite transaction을 abort해 마지막 SQLite snapshot 복원을 검사한다.
