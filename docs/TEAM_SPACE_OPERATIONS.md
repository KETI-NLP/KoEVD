# Team 가입 후 KoEVD 서버의 현재 상태와 운영 준비

## 최신 기본 복귀 — plan0.54

v0.54에서 별도 승인된 실제 private CPU 유한 종료 시험을 완료했다. 기준9개 보존·새 snapshot3개/396,229바이트로3회/24MiB 한도를 지켰다. 현재 코드에 결합한 parent 종료 로그 뒤 마지막 snapshot이 생겼고 finite worker2회 완료·후속 기동 initialization_inventory_mismatch 거부를 확인했다. 별도 다운로드한3사본 중 두 현재48+48기록 원본/이력이 모두 일치한 digest를 내용으로 선택했다. 고정 복원 후 실제 HF 재로그인의 두 원본·두 이력4파일이 복원 전 native 다운로드와 바이트 일치했고 새 저장/공개 조회 거부·worker OFF·복구 대기를 확인했다. 최신 기본 revision `8e692c88d412d6305879473e3e8e74d46bb7dd2c`의 RUNNING/cpu-basic·66파일 바이트/목록 일치로 복귀했다. Bucket12객체/68,382,317바이트·Secret·public Static을 보존했으며 상시 백업은 꺼져 있다. 이 승인은 시험 종료로 소진됐다. 과거 누락4B 이력이 복구됐다고 주장하거나 과거 횟수 실패를 소급 통과 처리하지 않는다. 실제 HF host restart 이벤트 로그·상시 운영/RPO·현재 Docker 전체 용량·운영자 정책/복구 인수·공개 참조는 미확보다. 실제 GPU/F1/분류 정확도의 새 검증은 아니다. [최신 근거](validation/platform_m6_actual_finite_shutdown_20261012.json). 전체 목표/완료 조건은 유지하며 전체 완료를 선언하지 않는다.

아래 이전 기록은 당시 범위다.

## 최신 운영 상태 — plan0.52

v0.52에서 유한 worker의 마지막 capture 전에 소유한 HTTP 서버를 종료·회수하고 전용 stdin으로 마지막 백업을 허용하는 순서를 구현했다. 현재 새 비편집 설치의 source50·고정 의존성25·pip check와 전체352 CPU검사/146.942초/failures0/errors0/skips0가 통과했다. 현재9개 digest를 metadata-only double로 재현한 실제 소유 로컬 HTTP/worker 통합29.344초에서 두48+48기록 원본/이력의 고정 복원 일치, 마지막 SQLite capture 전 서버 종료, 이후 연결 거부, 새 빈 초기화 거부, 복원 대기와 credential 분리를 확인했다. HF/OAuth는 명시적 double이다. Windows 상태 파일 교체의 일시적 WinError5/32/33에만 최대6회·총0.62초 재시도하며 지속 오류는 전달한다. 관측된 WinError5의 근본 원인은 미확정이다. 기본65·관리형68파일 및 초기1+worker2/24MiB/600초의70파일 제안을 로컬에 준비했고 이번 외부 전송·배포는0회다. 앞서 승인된 v0.51 시험은 종료됐으며 새 제안의 권한으로 재사용하지 않는다. 실제 마지막 기본 revision은 `f65a8b1065b934e649e545043c4ac89b18c2d4a5`, 상시 백업 OFF다. 이전 실제 새4B 이력 누락은 복구됐다고 주장하지 않는다. 실제 HF 두 현재 초안의 종료 보존·현재 Docker 전체 용량·운영 인수·공개 참조는 미완료다. [최신 근거](validation/platform_m6_finite_final_capture_20261012.json). Goal active/원래 범위를 유지한다.

아래 이전 기록은 당시 범위다.

## 최신 운영 상태 — plan0.51

v0.51에서 별도 승인된 private CPU 정상 기동 시험의 새 snapshot3개/302,021바이트와 finite worker2회 완료·후속 초기화의 `initialization_inventory_mismatch` 거부를 확인했다. 이번 횟수/용량 한도는 통과했지만 두 초안 보존은 미완료다. 실제 HF 로그인으로8B/4B 초안 저장을 관찰했고 종료 경계의4B 다운로드가503을 반환했다. 독립 다운로드/외부 index·registry 검사에서 마지막 사본에는8B48기록/이력만 있고 새4B 이력은 없었다. 과거4B 사본으로 대체하지 않았다.8B의 고정 복원·실제 재로그인 전후 원본/이력 바이트 일치와 새 저장 거부·공개 조회 불가 UI는 확인했다. 승인된 최신 UI 기본 프로필 `f65a8b1065b934e649e545043c4ac89b18c2d4a5`의 RUNNING/cpu-basic·66파일 바이트/목록 일치로 복귀했고9백업/67,986,088바이트·Secret·public Static을 보존했다. 상시 백업은 꺼져 있다. current26 CPU검사/5.350초와 앞선 nonempty6 목록 로컬 통합27.453초는 별도 모의 provider 근거다. 유한 worker의 마지막 snapshot 전에 새 domain 저장을 닫고 수락된 요청을 기다리는 절차가 다음 구현 대상이다. 실제 두 초안 종료 보존·현재 Docker 전체 용량·운영 인수·공개 참조는 미완료다. [최신 근거](validation/platform_m6_positive_trial_partial_20261012.json). Goal active/원래 범위를 유지한다.

아래 이전 기록은 당시 범위다.

## 최신 개발 후보 — plan0.50

v0.50에서 공개 목록·상세·비교 재조회 실패가 이전 성공 결과를 현재 결과로 남기던 UI를 수정했다. 목록/상세는 요청 전에 기존 표시를 지우고, 실패는 조회 불가로 표시한다. 비교는 빈 선택기를 잠그며 실패를0건이나 빈 정상 결과로 숨기지 않는다. 오류 원문은 textContent로 표시하고 긴 문자열도 모바일 영역 안에서 줄바꿈한다. 최종 새 비편집 설치50파일/25고정 의존성의 실제 로컬 HTTP·브라우저10흐름/8화면/24.078초가 통과했다. 합성 계정·결과·권한과503/413 응답 double이며 실제 HF/GPU 인수는 아니다. 관련 API38 CPU검사도 통과했고 최종 CSS 보완 전 v74 범위임을 구분했다. 두 UI자산 외48파일·지표·규약·실제 결과는 기존과 같다. 현재 소스의65파일 기본 후보와68파일 관리형 후보를 새로 보존했으며 미업로드다. 실제 private 앱의 마지막 확인 revision은 `f160663af378e777616be89374a20b6c38b57938`이고 이번 UI 수정은 아직 배포하지 않았다. 상시 백업은 꺼져 있고 실제 정상 초기화/재시작·현재 Docker 전체 용량·운영 인수·공개 참조는 미완료다. [최신 근거](validation/platform_m5_public_failure_ui_20261012.json). Goal active/원래 범위를 유지한다.

아래 이전 기록은 당시 범위다.

## 최신 운영 상태 — plan0.49

v0.49에서 별도 승인된 읽기 전용 시험을 실제 private CPU Space에서 수행했다. 실제 HF 로그인으로 현재 보이는 초안0건·분석 업로드0건을 확인하고 이전 두 모델 원본/이력 4쌍을 재대조했다. 전용 Secret으로 private Bucket 목록을 읽은 진단은 `initialization_inventory_mismatch`/exit2 경로를 반환했다. 이 진단의 RUNTIME_ERROR는 의도한 거부이며 서버·worker·DB·snapshot을 만드는 경로를 호출하지 않는다. Bucket6객체/67,684,067바이트 목록이 유지됐고 새 결과 전송·snapshot 생성은0회다. 기본 프로필 `f160663af378e777616be89374a20b6c38b57938`로 복귀한 뒤 RUNNING/cpu-basic·배포66파일의 바이트/목록 일치와 브라우저 준비 화면을 확인했다. Secret·public Static·기존 snapshot은 보존했고 상시 백업은 꺼져 있다. 현재25 CPU검사/5.652초는 로컬 근거다. 실제 정상 초기화 후 재시작 전체 인수·현재 Docker 전체 용량·운영 승인·공개 참조는 미완료이고, 이전 최대3회 시험의5회 생성 실패도 통과로 변경하지 않는다. [최신 근거](validation/platform_m6_actual_readonly_guard_20261012.json). Goal active/원래 범위를 유지한다.

아래 이전 기록은 당시 범위다.

## 최신 운영 상태 — plan0.48

v0.48에서 초기화 목록 불일치를 민감한 상세 없이 구분하는 진단과 `--check-initialization-baseline` 읽기 전용 모드를 추가했다. 이 모드는 목록이 일치해도 DB·서버·worker·snapshot을 만들지 않는다. 관련25 CPU검사/5.652초/exit0이 통과했고 core50 바이트는 기본 개발 후보와 같다. 실제 private CPU Space는 `8d50fbe9a05c152cb4e3365bea01c52ec0f78419`의 RUNNING/cpu-basic, Bucket은6객체/67,684,067바이트, public Static은 이전 revision으로 재확인했다. 68파일 일반 후보와70파일 읽기 전용 제안을 로컬에 준비했으며 미업로드다. 기존 초안·이력 보존 → 전용 Secret으로 목록 검사 → 기본 프로필 복귀의 별도 승인을 요청했다. 이 제안의 새 결과 전송과 snapshot 쓰기는0회다. 실제 HF guard/정상 초기화·재시작 인수는 아직 없고, 이전 최대3회 시험의5회 생성 실패는 그대로 남는다. 상시 백업은 꺼져 있고 현재 Docker 전체 용량·공개 참조·운영자 인수도 미완료다. [근거](validation/platform_m6_readonly_guard_preparation_20261012.json). Goal active/원래 범위를 유지한다.

아래 이전 기록은 당시 범위다.

현재 상태(2026-10-12/plan0.47): v0.47에서 전용 Secret으로 실제 private CPU 서버의 백업·고정 복원을 시험했다. 실제 HF 로그인으로 저장한 두 모델48+48기록의 원본/이력과 분석 JSON을 독립 보존했고, 고정 복원 후 재로그인한 원본/이력 바이트가 모두 일치했다. 공개 HTTP503/recovery_required와 실제 새 제출 거부도 확인했다. 그러나 승인된 최대3회와 달리 새 snapshot5개/529,309바이트가 관측됐다. 24MiB 총량은 지켰지만 횟수 제한은 실패했다. 즉시 PAUSED로 전송을 막고 새 백업 없는 고정 복원을 검증한 뒤 기본 private 프로필 `8d50fbe9a05c152cb4e3365bea01c52ec0f78419`의 RUNNING/cpu-basic으로 복귀했다. Secret·snapshot·공개 Static은 보존했고 상시 백업은 꺼져 있다. 유한 worker 종료 뒤 새 빈 저장소 기동이 반복된 양상에 대응해 v2의 독립 원격 snapshot 기준 목록 검사와 legacy initialize 거부를 구현했다. 관련22 CPU검사/5.497초 및 실제 소유 로컬 재기동·복원27.969초가 통과했다. 이 수정의 실제 HF 재검증은 미완료이며 새68파일 후보는 미업로드/미활성화다. [최신 근거](validation/platform_m6_live_backup_trial_20261012.json), [관리형 안내](MANAGED_SPACE_GUIDE.md). Goal active/원래 범위를 유지한다.

아래 이전 checkpoint는 당시 범위다.

현재 상태(2026-10-12/plan0.46): v0.46에서 관리형 런처의 복원 안내와 종료 처리를 보완했다. 현재 코드의 로컬 실제 서버·worker·HTTP에서 두 기존 모델48+48기록 저장, 첫 백업+worker2회, 종료, 고정 복원 후 원본/이력 일치, 공개503·새 제출 차단을24.719초/exit0로 확인했다. HF/OAuth는 명시적 로컬 test double이며 실제 HF 연결이나 Linux signal 인수는 아니다. 관련18 CPU검사/2.987초/exit0와 이전 전체328 설치의 core50 바이트 유지도 확인했다. 사용자가 Bucket 전용 토큰과 `KOEVD_BACKUP_TOKEN` Secret 등록을 완료했다고 확인했다. 값은 읽거나 출력하지 않았다. 관리형68파일 후보와 기존 private CPU Space를 쓰는70파일 제한 시험 제안을 준비했으며 미업로드/미활성화다. 최대3회·snapshot24MiB 이하 전송과 고정 복원/기본 프로필 복귀에 대한 별도 승인을 요청했다. 실제 관리형 HF 백업·재시작 복구, 현재 Docker 전체 용량, 공개 참조·운영자 인수는 미완료다. [최신 근거](validation/platform_m6_managed_lifecycle_20261012.json), [관리형 안내](MANAGED_SPACE_GUIDE.md). Goal active/원래 범위를 유지한다.

아래 이전 checkpoint는 당시 범위다.

현재 상태(2026-10-12/plan0.45): v0.45에서 비공개 개발 Space의 다운로드를 파일 준비 → 명시적 Save 링크로 보완했다. 현재 revision `5504a5e57e173c96b17272ee0e4c1608e859759c`의 배포 파일66개가 일치하고 RUNNING/cpu-basic이다. 실제 Chrome의48+48기록 분석에서 JSONL/CSV/Markdown/JSON/HTML 다섯 파일 모두 새로 저장되어 native 바이트와 일치했다. 로컬 UI는 삭제된 세션의 지연 다운로드가 Save 링크를 다시 만들지 않는지까지 검증했다. 별도 관리형 서버·백업 후보68파일과 stale 소스/운영 권한 상속 거부를 구현했다. 새 비편집 설치의 전체328 CPU검사·50소스/자산·25런타임 버전 대조와 이후 관련15검사는 별도 근거다. 관리형 후보는 미업로드/미활성화이며 전용 Secret 설정 완료도 아직 확인되지 않았다. 앱 자동 백업·재시작 복구/최신 상태·RPO·운영자 승인·공개 참조·현재 Docker 전체 용량은 미완료다. [최신 근거](validation/platform_m5_m6_prepared_downloads_managed_20261012.json), [관리형 안내](MANAGED_SPACE_GUIDE.md). Goal active/원래 범위를 유지한다.

아래 이전 checkpoint는 당시 기록이다. [연결 준비](TEAM_BACKUP_CONNECTION.md).

2026-10-12. KETI-NLP의 실제 Team 요금제와 로그인 계정의 조직 관리자 권한을 API로 확인했다. 별도 **비공개 CPU Docker 개발 Space** [KoEVD-Platform-Dev](https://huggingface.co/spaces/KETI-NLP/KoEVD-Platform-Dev)를 배포했다. 기존 [공개 Static 분석 앱](https://huggingface.co/spaces/KETI-NLP/KoEVD-Explorer)은 유지한다. [실제 검증 근거](validation/platform_m5_m6_team_hosted_20261012.json).

| 경로 | 현재 기능 | 데이터 보관 |
|---|---|---|
| Public Static Explorer | 브라우저 내부 분석·두 결과 비교·오프라인 보고서 | 선택한 결과가 분석 서버로 전송되지 않음. 공동 제출 저장 없음 |
| Private Docker Platform-Dev | CPU 서버 분석·native HF 로그인·본인 비공개 초안 저장 | 분석 세션과 별도 SQLite 제출 저장. 모두 개발 Space 임시 disk이며 재시작/재빌드 후 보존 보장 없음 |

현재 Docker는 `cpu-basic`이며 GPU·유료 하드웨어·유료 storage를 활성화하지 않았다. 실제48+48기록 웹 분석/비공개 초안2건과 HF OAuth 생성 이력을 검증했다. 현재 v67의 실제 Chrome 다섯 파일 다운로드는 native와 바이트까지 같다. 보고서 버튼으로 준비한 뒤 표시되는 Save 링크를 눌러 저장한다. v65의 HF 로그인/초안2건 검증과 v67의 분석/다운로드 검증은 별도이며, rebuild 후 이전 ephemeral 초안 보존을 주장하지 않는다. 이전 전체 GPU·Static 용량 검증을 현재 Docker 전체 용량 검증으로 바꾸어 보고하지 않는다.

## 개발 서버에서 직접 확인하는 순서

1. 조직 계정으로 private Space에 접근한다. 이는 HF resource 접근이며 KoEVD 제출자 로그인과 별개다.
2. **Open workspace in its own tab**으로 앱 자체 탭을 연다. Hub iframe에서는 브라우저 cookie 제약으로 로그인이 반영되지 않을 수 있다.
3. **Sign in with Hugging Face**로 로그인한다. 요청은 공개 profile 확인이며 repo 쓰기나 모델 inference 권한을 요구하지 않는다.
4. portable `results.json` 두 개를 선택하고 **Validate and add results** → **Build analysis and comparison**을 실행한다.
5. 저장하려면 **Refresh uploaded results**를 누르고 대상을 선택해 **Save private submission**을 누른다. `draft / unpublished`가 되어야 한다. 분석 업로드와 비공개 저장은 공개 요청이 아니다.
6. 원본·revision/event 이력을 내려받고, 원하는 보고서 버튼을 누른 뒤 표시되는 **Save 파일명** 링크를 눌러 로컬에 보존한다. 새 보고서를 준비하면 이전 Save 링크는 폐기된다. 비공개 저장 JSON은 canonical 직렬화되며 업로드 JSON 내용 전체가 유지된다.

개발 서버의 `reviewers`·`admins`와 공개 기준 모델 목록은 비어 있다. 조직 관리자라고 앱 게시 권한을 자동 부여하지 않는다. 공개 동의문·사람 검토·정책 승인·공식 순위 기록을 검증 목적으로 만들어 넣지 않는다.

## 영구 보관을 연결하기 위한 구체적인 준비

Team 가입으로 Docker hosting 조건은 해결됐지만 제출 원본의 영구 보관이 자동 구성되는 것은 아니다. 현재 launcher는 `/tmp/koevd-development-submissions`를 사용하며 백업 worker는 켜져 있지 않다.

현재 구현된 원격 전송 후보는 **기존 비공개 HF Bucket에 스냅샷을 보내고 다시 읽어 대조하는 방식**이다. [스냅샷](PRIVATE_SNAPSHOT_GUIDE.md), [주기 백업](BACKUP_WORKER_GUIDE.md), [복구 대기](RECOVERY_GUIDE.md)를 따른다. 다른 버전 저장소를 선택할 수도 있지만 별도 adapter와 동시 쓰기·복구 검증이 필요하다. Bucket이 모든 Static 분석의 필수 조건은 아니다.

라이브 연결에 필요한 것은 다음과 같다.

- 조직이 선택한 비공개 저장 대상 ID와 테스트 원본 전송 범위. 현재 비공개 Bucket은 생성·단일 snapshot 전송까지 검증했고, 관리형 앱 연결은 [별도 후보](MANAGED_SPACE_GUIDE.md)다.
- 해당 대상만 읽고 쓸 수 있는 전용 credential. 조직 전체 관리자 CLI 토큰을 앱에 복사하지 않는다. credential은 실행 환경/Space secret에 설정하고 채팅·Git·문서·산출물에 넣지 않는다.
- 앱과 별도로 지정한 backup/recovery 운영자의 역할. 사용자 이름을 추정해서 reviewer/admin 파일에 넣지 않는다.
- 원격 readback 후 별도 새 저장소 복원, 독립 catalog/registry 및 현재 기준 checkpoint 대조, 저장 실패 시 이전 성공본 유지, 복구 대기 동안 공개 차단의 실제 근거.

**살아 있는 SQLite DB를 Bucket/NFS mount에 직접 놓지 않는다.** 로컬 DB와 검증한 스냅샷 전송을 분리한다. 주기 백업만으로 동기 remote commit이나 손실 시간 보장을 주장하지 않는다. 재시작 시험은 먼저 원본/이력의 독립 사본을 확보한 뒤, disposable 개발 데이터로 수행한다.

## 공개 플랫폼으로 전환하기 전에

영구 저장/복구 인수, 실제 운영자 권한·공개 범위 심사, 공개 가능 기준 결과와 provenance 검토, 지표별 정책/측정 제한, 현재 Docker 서버 전체 용량 인수를 마친다. 이후 공개할 Docker 대상과 Static 연결 방법을 구체적으로 제시한다. 현재 개발 서버의 공개 visibility나 production 교체는 수행하지 않았다. GitHub 공개 main과 이 미커밋 개발 후보를 같은 버전으로 표현하지 않는다.
