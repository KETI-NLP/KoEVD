# HF 로그인과 웹 제출 후보

현재 공개 서비스(2026-10-15): 운영 Space에서 실제 HF 로그인, 소유자 등록,
수치 요약 공유·철회, 서버 재시작 후 재로그인 및 원본·이력 복원을 검증했다.
최신 사용법은 [사용자 안내](PLATFORM_USER_GUIDE.md), 정확한 소스·배포 버전과
검증 범위는 [현재 인수 결과](PUBLIC_SERVICE_ACCEPTANCE.md)를 따른다.
아래 개발 단계의 미완료·미검증 표시는 해당 날짜의 과거 기록이다.

현재 상태(2026-10-12/plan0.43): v0.43에서 실제 Team 가입을 API로 확인하고 별도 비공개 CPU Docker Space `KETI-NLP/KoEVD-Platform-Dev`를 배포했다. 현재 revision `03e79a75ee35570b83948343d521f684a38fce01`의 payload65개+manifest가 일치하고 RUNNING/cpu-basic이다. 실제 HF 로그인 후 두 모델48+48기록의 업로드·분석·대응 비교와 비공개 draft2건 저장/재조회를 확인했다. 내려받은 원본 JSON 내용·HF OAuth 생성 이력과 분석 JSON/HTML의 native 바이트가 일치한다. v64의 별도 HTTP 검증에서는 다섯 출력·세션 격리·삭제가 통과했다. 현재 브라우저의 나머지3개 다운로드는 확인하지 못했다. Private proxy cookie 누락을 수정했고 관련4+6+3+11 검사가 통과했다. 기존 전체310은 이전 설치 근거다. Public Static은 그대로이며 영구 저장·운영자 승인·공개 참조/공식 순위·production은 미완료다. [최신 근거](validation/platform_m5_m6_team_hosted_20261012.json) Goal active/원래 범위를 유지한다.

아래 이전 검증의 범위·수치는 당시 근거다. [운영 준비](TEAM_SPACE_OPERATIONS.md).

2026-10-11. `oauth.py`, `submission_web.py`와 기존 서버 앱의 opt-in 확장이다. 비공개 Static 분석 Space와 실제 두 모델 GPU 검증은 별도로 완료했지만, KoEVD 제출자 OAuth 앱과 실제 계정 로그인은 미검증이다. 이 문서는 실제 로그인 또는 production 배포 완료 보고가 아니다. Static 후보에는 아래 서버 제출 경로가 연결되지 않았다.

## 사용자가 거치는 흐름

1. 기존처럼 결과 JSON을 임시 분석 세션에 올리고 리포트를 확인한다. 익명 업로드만으로 원본이 제출 저장소에 보존되거나 공개되지는 않는다.
2. HF로 로그인하고, 검증된 업로드 중 하나를 선택해 별도의 private submission을 저장한다. 제출 원본·revision·이벤트는 로컬 저장소에 보존되며 분석 세션 삭제와 분리된다.
3. summary 또는 responses 공개 범위와 권한 설명을 선택해 명시적으로 review를 신청한다.
4. 독립적인 운영자 reviewer가 permission review를 수행하고, 별도 admin이 승인된 revision을 게시한다. 검토와 게시 권한은 서버 설정에서만 읽는다.
5. 게시된 후보에서 지표·분자/분모·coverage와 제외 사유를 확인한다. responses 범위의 원본만 자신의 임시 분석에 다시 가져와 다른 실행과 같은 공통 엔진으로 비교할 수 있다.
6. 제출자 또는 admin이 철회하면 공개 목록·요약·원문에 새로 접근할 수 없다. private 원본·이력은 감사 목적으로 유지된다. 이미 다운로드된 외부 복제본 삭제는 보장하지 않는다.

로그인·permission review·게시 승인으로 모델 생성 진위나 classifier 정확도가 승격되지 않는다. 현재는 candidate 정책이고 공식 순위를 활성화하지 않는다. 기존 분석에는 대응 비교와 source bootstrap을 제공하며 임의 종합 윤리 점수와 Task 4 품질 순위는 없다.

## 운영자가 준비할 설정

HF의 [Spaces OAuth 문서](https://huggingface.co/docs/hub/spaces-oauth)는 Space metadata의 `hf_oauth: true`, OAuth 환경변수와 callback 설정을 설명한다. 일반 개발용 앱은 [HF OAuth 안내](https://huggingface.co/docs/hub/oauth)를 따른다. 이 후보는 고정 HF issuer의 authorization-code + S256 PKCE 흐름을 사용한다. 네트워크 endpoint는 [HF discovery metadata](https://huggingface.co/.well-known/openid-configuration)로 확인했으며 upload/환경변수로 다른 provider URL을 선택할 수 없다.

기본 `confidential` 모드에는 `OAUTH_CLIENT_ID`, `OAUTH_CLIENT_SECRET`이 필요하다. secret은 로컬 process 환경 또는 Space secret에만 설정하고 명령줄 인자·소스·로그·결과 JSON에 넣지 않는다. HF CLI의 `hf auth login`은 웹 OAuth 앱 등록을 대신하지 않는다. 요청 scope는 `openid profile`이며 repo 쓰기·추론 권한을 요구하지 않는다.

HF의 [공개 OAuth 앱 안내](https://huggingface.co/docs/hub/oauth#public-oauth-apps-no-secret)에 따라 secret 없는 앱도 사용할 수 있다. 운영자가 해당 앱을 준비한 뒤 `OAUTH_CLIENT_ID`만 설정하고 `--oauth-client-type public` 또는 `KOEVD_OAUTH_CLIENT_TYPE=public`을 명시한다. `OAUTH_CLIENT_SECRET`은 설정하지 않거나 빈 값이어야 한다. 공개 모드에 secret을 함께 설정하거나 기본 모드에서 secret을 빠뜨리면 서버가 시작되지 않는다. 명령줄의 명시적 client type은 환경 설정보다 우선한다. 공개 모드는 앱의 token 인증 방식이며 제출 원문 공개 여부와 무관하다.

두 모드 모두 서버가 고정 HF endpoint에서 authorization code와 S256 PKCE로 token을 교환하고 userinfo를 확인한다. 공개 모드의 token 요청에는 client ID/code/verifier/callback만 포함하며 Basic header와 client secret을 보내지 않는다. provider token은 계속 서버 메모리에만 있고, 브라우저에는 기존 불투명 local session cookie만 발급한다. Static 브라우저 OAuth UI를 추가한 것은 아니다.

등록한 callback은 canonical origin에 `/auth/callback`을 붙인 주소다. localhost에서는 `http://127.0.0.1:7860/auth/callback`, HTTPS에서는 `https://APP_HOST/auth/callback`처럼 실제 설정과 맞춘다. Host header나 upload의 redirect 문자열로 callback을 만들지 않는다.

등록 주소와 host/path가 맞아야 한다. HF는 HTTP loopback에서 port만 달라지는 예외를 허용하지만 `localhost`와 `127.0.0.1`은 다른 host로 취급한다. 위 localhost 예시는 `127.0.0.1` callback을 등록한 앱으로 실행한다. [HF callback 규칙](https://huggingface.co/docs/hub/oauth#redirect-uris).

운영자 roles 파일은 다음 형식이다. subject는 서버의 `/api/identity`가 반환한 stable subject를 사용한다. 본 구현의 subject는 `hf:` 뒤에 verified HF userinfo `sub`의 SHA-256을 붙인다. 사용자명 변경으로 소유권이 바뀌지 않으며 HF 조직 가입만으로 admin 권한을 자동 부여하지 않는다.

```json
{"reviewers": [], "admins": []}
```

실제 필요한 subject를 별도로 설정하기 전에는 누구에게도 운영 권한이 부여되지 않는다.

```bash
# Set OAuth application credentials through the process environment/Space secrets.
# Do not paste the secret into this command or a committed file.
koevd-space --catalog /operator/koevd/catalog.json \
  --session-root /operator/koevd/NEW_PRIVATE_SESSION_DIR \
  --submission-root /operator/koevd/persistent-submissions \
  --roles-file /operator/koevd/roles.json \
  --origin https://APP_HOST --oauth-origin https://APP_HOST \
  --host 0.0.0.0 --port 7860
```

위 명령은 운영자 설정을 설명하는 템플릿이며 실제 Space 배포의 증거가 아니다.

secret 없는 공개 OAuth 앱을 준비한 로컬 개발 예시는 다음과 같다. client ID는 process 환경에 설정하고 secret은 비워둔다. 동일한 server/store/roles 경계를 사용하며 `--submission-root`가 없는 익명 분석에는 공개 OAuth 모드를 지정할 수 없다.

```bash
koevd-space --catalog /operator/koevd/catalog.json \
  --session-root /operator/koevd/NEW_PRIVATE_SESSION_DIR \
  --submission-root /operator/koevd/persistent-submissions \
  --roles-file /operator/koevd/roles.json \
  --origin http://127.0.0.1:7860 --oauth-origin http://127.0.0.1:7860 \
  --oauth-client-type public --host 127.0.0.1 --port 7860
```

이 명령은 사용자별 role을 자동 부여하거나 Space를 생성하지 않는다. Docker 개발 launcher도 명시적 `KOEVD_OAUTH_CLIENT_TYPE=public`과 secret 없는 앱 설정을 검증한다. OAuth client 선택이 조직의 hosting 플랜·저장 옵션을 변경하지는 않는다.

`--submission-root`를 지정하지 않으면 로그인·제출 endpoint와 화면은 비활성이다. 기존 익명 분석은 그대로 동작한다. localhost 개발에서는 `--host 127.0.0.1`과 명시적으로 같은 localhost origin을 사용한다. 앱 종류에 맞는 설정을 준비하고, 가짜 credentials를 실제 HF에 보내 테스트하지 않는다.

## 신원·세션·권한 경계

- code/state는 한 번만 사용하며 state는 해당 브라우저의 별도 HttpOnly binding cookie와 결합한다. state TTL은 5분, pending 최대 128개다.
- token 교환과 userinfo 조회는 서버에서 고정 HTTPS endpoint로 수행한다. HTTP redirect는 거부한다. userinfo의 verified subject를 사용하며 ID-token의 서명되지 않은 payload를 신뢰하거나 해석하지 않는다.
- provider access/refresh/ID token은 브라우저·disk·artifact에 저장하지 않는다. 로그인 후에는 새 불투명 local session cookie를 발급하고 서버에는 그 cookie의 hash만 저장한다.
- HTTPS cookie는 `__Host-` prefix, Secure, HttpOnly, SameSite=Lax, Path=/를 쓴다. localhost HTTP는 테스트를 위해 Secure가 없는 별도 cookie 이름을 쓴다.
- identity session은 최대 256개, 절대 TTL 최대 1시간이며 provider expiry보다 길게 발급하지 않는다. local TTL 동안 HF revocation을 매 요청 재조회하는 구현은 아니다. logout/rotation/restart는 local session을 무효화한다. 재로그인해도 stable subject의 제출 원본은 유지된다.
- cookie 기반 변경 요청은 명시적 same-origin과 별도 identity CSRF header가 필요하다. private upload를 제출로 복사하려면 해당 anonymous analysis Bearer/CSRF도 필요하다. identity·role·gold·index path는 HTTP body에서 받지 않는다.
- 제출과 분석 catalog는 같은 독립 index map이어야 한다. operation body는 16 KiB, private/public 목록 page는 최대 100개다. 무거운 DB/CPU 작업은 한 번에 하나, 대기는 최대 세 개로 제한한다. disconnected 작업의 thread가 끝나기 전에는 처리 slot을 재사용하지 않는다. 변경 요청은 durable idempotency key와 expected version을 사용한다.
- 원문과 이름은 실행하지 않고 textContent로 표시한다. history/original 다운로드와 공개 응답을 private 비교에 가져오기에도 같은 접근 권한·scope 제한이 적용된다.

HF iframe에서 third-party cookie가 차단되면 별도 top-level 탭에서 workspace를 연다. 화면의 로그인 링크와 workspace 링크는 새 탭을 제공한다. 실제 HF embedding·OAuth consent·user 계정 flow는 별도 live gate다.

## HTTP와 보존 범위

`/api/registration`, `/auth/login`, `/auth/callback`, `/api/identity`, identity logout과 `/api/submissions`의 private 목록·create·get·history·result·revisions·actions를 제공한다. `/api/public/submissions`는 현재 승인·게시된 revision의 제한된 목록·요약·명시적 responses 원문을 제공한다. 이 HTTP projection은 로컬 후보이며 외부 저장소에 publish하지 않는다.

`SubmissionService`의 기존 역할·consent·stale-version·immutable 원본·generation-preserving 재측정·이전 공개 revision·철회 검사를 그대로 통과한다. 저장은 [SUBMISSIONS_GUIDE.md](SUBMISSIONS_GUIDE.md)의 local SQLite 계약이다. Space 임시 disk를 영구 저장으로 표현하지 않는다. 현재 로컬 adapter와 저장량 제한은 원격 storage/mount의 transaction·복구 검증을 대체하지 않는다.

현재 process에는 실제 app client ID/secret이 설정되지 않았다. 실제 OAuth 앱 설정, callback 등록·로그인 계정 확인, operator generation receipt 검토, 정책 승인·원격 durability·원래 서버 컨테이너 인수가 남아 있다. 두 target의 전체 GPU 생성·측정·리포트와 비공개 Static 분석은 별도 증거로 완료했다. [릴리스 점검표](PLATFORM_RELEASE_CANDIDATE.md)와 [RANK_ADMISSION_GUIDE.md](RANK_ADMISSION_GUIDE.md)에 범위와 지표별 제한을 설명한다.

## 명시적 로컬 합성 UI 검증

```bash
python scripts/run_submission_ui_fixture.py \
  --catalog generated/space-demo-20261008/catalog.json \
  --root generated/NEW_SYNTHETIC_UI_SERVER --port 8770 --synthetic-fixture
node scripts/validate_submission_ui.cjs \
  --origin http://127.0.0.1:8770 \
  --fixture-dir generated/space-demo-20261008 \
  --output-dir generated/NEW_SYNTHETIC_UI_EVIDENCE
```

선행 fictional demo 생성은 [SPACES_GUIDE.md](SPACES_GUIDE.md)를 따른다. Node test는 Playwright/Chrome 환경을 준비해야 하며 operator가 browser executable을 별도로 지정할 수 있다. synthetic server는 실제 provider 대신 localhost에서 네 가상 계정을 선택한다. synthetic index/reference만 허용하며 실제 app CLI는 이 provider를 로드하지 않는다. fresh evidence directory로 실행하고 이전 실패 로그를 덮어쓰지 않는다. 이 검증 결과를 actual HF login/GPU/permission 또는 외부 publication으로 재사용하지 않는다.
