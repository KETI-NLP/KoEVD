# Platform development validation log

현재 실제 컨테이너·위임 검토 완료(plan0.59)

v0.59에서 사용자가 지정·전송 승인한 CPU_VALIDATION_NODE의 기존 Docker를 사용해 기본 후보를 실제 검증했다. 이미지1개·개별2개/대응 비교1개의15파일806,504,041바이트 HTTP/CLI 일치·비교의 이전 로컬/HF 일치가 통과했다. 기본CMD/UID:GID1000:1000/network none/포트0·정확한 소유 컨테이너 종료exit0/제거를 확인했다. 최종 컨테이너 검사277.752초·Python3.12.15·분석 패키지43파일·웹lock을 검증했다. 압축 해제 상한/누락Entrypoint 검사기의 초기 실패를 보존하고, inspect JSON을 파싱하는 수정과 관련7 CPU검사0.029초가 통과했다. 제품 core50와 HF 배포는 그대로다. 사용자가 Codex에 위임한 기술 검토에서는 GPU 실행 당시184소스·13단계·두 모델28증거파일·각17,670기록/index·Task3/4 재사용과 잘림/측정 한계를 대조했다. AI 검토를 별도 사람의 증명이나 정확도/공개/공식순위 승인으로 바꾸지 않는다. [컨테이너 근거](validation/platform_m5_actual_b200_container_v92.json), [위임 검토 근거](validation/platform_m4_delegated_generation_review_v92.json).

아래 기록은 당시 범위다.

현재 실제 전체 HF 인수(2026-10-12/plan0.58)

v0.58에서 사람이 승인한 실제 private CPU 전체 전송 인수를 완료했다. Qwen3-8B/4B 각17,670기록 JSON을 각1회/합계89,396,889바이트 전송하고 대응 비교1건을 실행했다. 다섯 다운로드405,679,557바이트가 독립 native 파일과 직접 바이트 일치했으며 로컬 hash 재검사도 통과했다. 총259.906초/exit0, job terminal·pending false·검증 session2개 cleanup200/200·다른 session의 출력 접근 거부를 확인했다. 종료 후 같은 8e692c88 revision/private Docker/RUNNING/cpu-basic/단일 replica를 읽기 전용으로 재확인했다. 제품 core50·기본 프로필을 보존했고 제출/Bucket/snapshot/재배포/restart/Secret/공개/유료 변경은 없다. 이번 승인은 이 제한 시험 완료로 소진됐으며 개별 분석2개나 실제 hosted browser/OAuth·local image UID/CMD·분류 정확도·운영자/공개 권한을 새로 인수한 것은 아니다. [근거](validation/platform_m5_actual_full_hosted_20261012.json).

아래 기록은 당시 범위다.

현재 전체 로컬 앱 검증(2026-10-12/plan0.57)

v0.57에서 현재 설치본의 실제 로컬 앱 화면으로 두 전체 결과17,670+17,670기록을 업로드했다. 합계89,396,889바이트 입력과 iframe의199,373,743바이트 HTML을 처리했고, Save 링크로 저장한 다섯 파일405,679,557바이트가 독립 CLI 파일과 일치했다. 전체158.875초/exit0, 분석·preview117.702초이며 비교·측정 한계·한국어 사례·모바일 화면을 시각 검토했다. 세션 격리/삭제·삭제 후 지연 다운로드 링크 거부·실제 서버 PID 일치/종료/포트 거부가 통과했다. 제품 core50는 그대로며 검증기의 대기 시간 옵션/관측 시간만 추가했다. 분석 전용 로컬 서버의 검사로 HF/OAuth/Docker나 새 추론 근거가 아니다. 실제 HF 전체 전송은 별도 승인 대기다. [근거](validation/platform_m5_current_full_app_browser_20261012.json).

아래 기록은 당시 범위다.

현재 로컬 검증(2026-10-12/plan0.56)

v0.56에서 HF 전체 전송 검사기의 opt-in 분기를 설치된 로컬 HTTP 서버로 검증했다. 명시적 HF 접근 모의 응답과 외부 소켓 차단 아래 실제48+48기록 두 업로드·비교1건·다섯 보고서 12,514,875바이트의 독립 CLI 일치·다른 세션 접근 거부·두 세션 삭제를 확인했다. 첫 Windows 가상환경 핸들 종료 검사는 포트 잔류로 실패를 보존했고, 실제 Python PID를 직접 소유한 재실행13.937초에서 PID 일치·종료·연결 거부가 통과했다. HF 요청/전송은0회, 제품 core50와 배포 프로필은 그대로다. 종료된 v83 승인을 재사용하지 않으며 전체 HF 전송은 별도 승인 대기다. [근거](validation/platform_m5_hosted_transfer_fixture_20261012.json).

아래 기록은 당시 범위다.

## 2026-10-12 — v84 / plan0.55 full hosted preflight preparation

v0.55에서 현재 private CPU 기본 앱에 두 모델 전체 결과를 일시 분석하는 별도 전송 인수 도구를 추가했다. 기본 preflight는 결과 body/analysis POST/DELETE 없이 resource 접근·고정8e692c88 revision·RUNNING/cpu-basic·단일 replica·한도/익명 app 경계를 읽는다. 실제 HF preflight2.078초/exit0·결과 전송0/job0과 최종6 CPU guard/0.276초가 통과했다. core50 소스는 기존 설치/배포 검증본과 같다. 새 제안은 두 실제17,670+17,670기록 JSON89,396,889바이트 각1회·대응 비교 job1·다섯 native405,679,557바이트와 직접 stream 대조·download512MiB 한도·두 owned analysis session cleanup만 포함한다. 전체 전송은 미승인/미실행이며 앞선 종료된96기록 시험 승인을 재사용하지 않는다. 새 script는 host-side 검사이며 이미 배포된 image를 변경하지 않았다. 이 준비는 실제 full hosted·local image UID/CMD·큰 report UI·운영자 판단·공개 권한을 대신하지 않는다. [최신 근거](validation/platform_m5_full_hosted_preparation_20261012.json), [실행 범위](HOSTED_FULL_ANALYSIS_ACCEPTANCE.md). Goal 도구의 현재 상태active를 확인했고 원래 목표/완료 조건을 유지한다.

아래 이전 기록은 당시 범위다.

## 2026-10-12 — v83 / plan0.54 actual finite shutdown acceptance

v0.54에서 별도 승인된 실제 private CPU 유한 종료 시험을 완료했다. 기준9개 보존·새 snapshot3개/396,229바이트로3회/24MiB 한도를 지켰다. 현재 코드에 결합한 parent 종료 로그 뒤 마지막 snapshot이 생겼고 finite worker2회 완료·후속 기동 initialization_inventory_mismatch 거부를 확인했다. 별도 다운로드한3사본 중 두 현재48+48기록 원본/이력이 모두 일치한 digest를 내용으로 선택했다. 고정 복원 후 실제 HF 재로그인의 두 원본·두 이력4파일이 복원 전 native 다운로드와 바이트 일치했고 새 저장/공개 조회 거부·worker OFF·복구 대기를 확인했다. 최신 기본 revision `8e692c88d412d6305879473e3e8e74d46bb7dd2c`의 RUNNING/cpu-basic·66파일 바이트/목록 일치로 복귀했다. Bucket12객체/68,382,317바이트·Secret·public Static을 보존했으며 상시 백업은 꺼져 있다. 이 승인은 시험 종료로 소진됐다. 과거 누락4B 이력이 복구됐다고 주장하거나 과거 횟수 실패를 소급 통과 처리하지 않는다. 실제 HF host restart 이벤트 로그·상시 운영/RPO·현재 Docker 전체 용량·운영자 정책/복구 인수·공개 참조는 미확보다. 실제 GPU/F1/분류 정확도의 새 검증은 아니다. [최신 근거](validation/platform_m6_actual_finite_shutdown_20261012.json). 전체 목표/완료 조건은 유지하며 전체 완료를 선언하지 않는다.

아래 이전 기록은 당시 범위다.

## 2026-10-12 — v79 / plan0.53 container runtime preparation

v0.53에서 기본 Docker 이미지의 CMD를 유지한 로컬 인수 도구와 노드 실행 절차를 추가했다. 이미지 ID·자신의 container ID/label·UID/GID1000·network none·미공개 포트·종료/제거를 외부 실행기에서 확인하고, 내부 HTTP 검사기는 외부 소유 loopback 서버에 연결한다. current source50는 v0.52 설치/352 전체 검사 때와 같고, 새 script 관련12 guard검사/0.111초가 통과했다. 새 연결 경로의 현재 로컬 실제 서버/CLI에서 기존 두 실제 모델 각17,670기록·총35,340기록의 대응 비교와 JSON/JSONL/CSV/Markdown/HTML5파일이 바이트 일치했다. 실행252.344초/exit0, 소유 server terminal이며 Windows terminate의 관측 exit1을 보존했다. 이번에는 개별 모델 보고서2개를 새로 검사하지 않았다. 컨테이너 도구0개라 실제 Docker 실행은 미검증이며 HF/OAuth/새 inference/외부 전송도0회다. 66파일 기본 context ZIP과 실행 안내를 로컬에 준비했고 기존 HF 제한 시험 재승인 질문은 계속 pending이다. 실제 HF 두 현재 초안 종료 보존·Docker 전체 용량·운영 인수·공개 참조를 미완료로 유지한다. [최신 근거](validation/platform_m5_container_runtime_preparation_20261012.json), [실행 절차](CONTAINER_RUNTIME_ACCEPTANCE.md). Goal active/원래 범위를 유지한다.

아래 이전 기록은 당시 범위다.

## 2026-10-12 — v78 / plan0.52 finite final capture local acceptance

v0.52에서 유한 worker의 마지막 capture 전에 소유한 HTTP 서버를 종료·회수하고 전용 stdin으로 마지막 백업을 허용하는 순서를 구현했다. 현재 새 비편집 설치의 source50·고정 의존성25·pip check와 전체352 CPU검사/146.942초/failures0/errors0/skips0가 통과했다. 현재9개 digest를 metadata-only double로 재현한 실제 소유 로컬 HTTP/worker 통합29.344초에서 두48+48기록 원본/이력의 고정 복원 일치, 마지막 SQLite capture 전 서버 종료, 이후 연결 거부, 새 빈 초기화 거부, 복원 대기와 credential 분리를 확인했다. HF/OAuth는 명시적 double이다. Windows 상태 파일 교체의 일시적 WinError5/32/33에만 최대6회·총0.62초 재시도하며 지속 오류는 전달한다. 관측된 WinError5의 근본 원인은 미확정이다. 기본65·관리형68파일 및 초기1+worker2/24MiB/600초의70파일 제안을 로컬에 준비했고 이번 외부 전송·배포는0회다. 앞서 승인된 v0.51 시험은 종료됐으며 새 제안의 권한으로 재사용하지 않는다. 실제 마지막 기본 revision은 `f65a8b1065b934e649e545043c4ac89b18c2d4a5`, 상시 백업 OFF다. 이전 실제 새4B 이력 누락은 복구됐다고 주장하지 않는다. 실제 HF 두 현재 초안의 종료 보존·현재 Docker 전체 용량·운영 인수·공개 참조는 미완료다. [최신 근거](validation/platform_m6_finite_final_capture_20261012.json). Goal active/원래 범위를 유지한다.

아래 이전 기록은 당시 범위다.

## 2026-10-12 — v76 / plan0.51 positive trial partial acceptance

v0.51에서 별도 승인된 private CPU 정상 기동 시험의 새 snapshot3개/302,021바이트와 finite worker2회 완료·후속 초기화의 `initialization_inventory_mismatch` 거부를 확인했다. 이번 횟수/용량 한도는 통과했지만 두 초안 보존은 미완료다. 실제 HF 로그인으로8B/4B 초안 저장을 관찰했고 종료 경계의4B 다운로드가503을 반환했다. 독립 다운로드/외부 index·registry 검사에서 마지막 사본에는8B48기록/이력만 있고 새4B 이력은 없었다. 과거4B 사본으로 대체하지 않았다.8B의 고정 복원·실제 재로그인 전후 원본/이력 바이트 일치와 새 저장 거부·공개 조회 불가 UI는 확인했다. 승인된 최신 UI 기본 프로필 `f65a8b1065b934e649e545043c4ac89b18c2d4a5`의 RUNNING/cpu-basic·66파일 바이트/목록 일치로 복귀했고9백업/67,986,088바이트·Secret·public Static을 보존했다. 상시 백업은 꺼져 있다. current26 CPU검사/5.350초와 앞선 nonempty6 목록 로컬 통합27.453초는 별도 모의 provider 근거다. 유한 worker의 마지막 snapshot 전에 새 domain 저장을 닫고 수락된 요청을 기다리는 절차가 다음 구현 대상이다. 실제 두 초안 종료 보존·현재 Docker 전체 용량·운영 인수·공개 참조는 미완료다. [최신 근거](validation/platform_m6_positive_trial_partial_20261012.json). Goal active/원래 범위를 유지한다.

아래 이전 기록은 당시 범위다.

## 2026-10-12 — v74/v75 / plan0.50 public failure UI

v0.50에서 공개 목록·상세·비교 재조회 실패가 이전 성공 결과를 현재 결과로 남기던 UI를 수정했다. 목록/상세는 요청 전에 기존 표시를 지우고, 실패는 조회 불가로 표시한다. 비교는 빈 선택기를 잠그며 실패를0건이나 빈 정상 결과로 숨기지 않는다. 오류 원문은 textContent로 표시하고 긴 문자열도 모바일 영역 안에서 줄바꿈한다. 최종 새 비편집 설치50파일/25고정 의존성의 실제 로컬 HTTP·브라우저10흐름/8화면/24.078초가 통과했다. 합성 계정·결과·권한과503/413 응답 double이며 실제 HF/GPU 인수는 아니다. 관련 API38 CPU검사도 통과했고 최종 CSS 보완 전 v74 범위임을 구분했다. 두 UI자산 외48파일·지표·규약·실제 결과는 기존과 같다. 현재 소스의65파일 기본 후보와68파일 관리형 후보를 새로 보존했으며 미업로드다. 실제 private 앱의 마지막 확인 revision은 `f160663af378e777616be89374a20b6c38b57938`이고 이번 UI 수정은 아직 배포하지 않았다. 상시 백업은 꺼져 있고 실제 정상 초기화/재시작·현재 Docker 전체 용량·운영 인수·공개 참조는 미완료다. [최신 근거](validation/platform_m5_public_failure_ui_20261012.json). Goal active/원래 범위를 유지한다.

아래 이전 기록은 당시 범위다.

## 2026-10-12 — v73 / plan0.49 actual read-only HF diagnostic

v0.49에서 별도 승인된 읽기 전용 시험을 실제 private CPU Space에서 수행했다. 실제 HF 로그인으로 현재 보이는 초안0건·분석 업로드0건을 확인하고 이전 두 모델 원본/이력 4쌍을 재대조했다. 전용 Secret으로 private Bucket 목록을 읽은 진단은 `initialization_inventory_mismatch`/exit2 경로를 반환했다. 이 진단의 RUNTIME_ERROR는 의도한 거부이며 서버·worker·DB·snapshot을 만드는 경로를 호출하지 않는다. Bucket6객체/67,684,067바이트 목록이 유지됐고 새 결과 전송·snapshot 생성은0회다. 기본 프로필 `f160663af378e777616be89374a20b6c38b57938`로 복귀한 뒤 RUNNING/cpu-basic·배포66파일의 바이트/목록 일치와 브라우저 준비 화면을 확인했다. Secret·public Static·기존 snapshot은 보존했고 상시 백업은 꺼져 있다. 현재25 CPU검사/5.652초는 로컬 근거다. 실제 정상 초기화 후 재시작 전체 인수·현재 Docker 전체 용량·운영 승인·공개 참조는 미완료이고, 이전 최대3회 시험의5회 생성 실패도 통과로 변경하지 않는다. [최신 근거](validation/platform_m6_actual_readonly_guard_20261012.json). Goal active/원래 범위를 유지한다.

아래 이전 기록은 당시 범위다.

## 2026-10-12 — v72 / plan0.48 read-only guard preparation

v0.48에서 초기화 목록 불일치를 민감한 상세 없이 구분하는 진단과 `--check-initialization-baseline` 읽기 전용 모드를 추가했다. 이 모드는 목록이 일치해도 DB·서버·worker·snapshot을 만들지 않는다. 관련25 CPU검사/5.652초/exit0이 통과했고 core50 바이트는 기본 개발 후보와 같다. 실제 private CPU Space는 `8d50fbe9a05c152cb4e3365bea01c52ec0f78419`의 RUNNING/cpu-basic, Bucket은6객체/67,684,067바이트, public Static은 이전 revision으로 재확인했다. 68파일 일반 후보와70파일 읽기 전용 제안을 로컬에 준비했으며 미업로드다. 기존 초안·이력 보존 → 전용 Secret으로 목록 검사 → 기본 프로필 복귀의 별도 승인을 요청했다. 이 제안의 새 결과 전송과 snapshot 쓰기는0회다. 실제 HF guard/정상 초기화·재시작 인수는 아직 없고, 이전 최대3회 시험의5회 생성 실패는 그대로 남는다. 상시 백업은 꺼져 있고 현재 Docker 전체 용량·공개 참조·운영자 인수도 미완료다. [근거](validation/platform_m6_readonly_guard_preparation_20261012.json). Goal active/원래 범위를 유지한다.

아래 이전 기록은 당시 범위다.

## 2026-10-12 — plan0.47 / v70–71: actual HF trial failure and containment

v0.47에서 전용 Secret으로 실제 private CPU 서버의 백업·고정 복원을 시험했다. 실제 HF 로그인으로 저장한 두 모델48+48기록의 원본/이력과 분석 JSON을 독립 보존했고, 고정 복원 후 재로그인한 원본/이력 바이트가 모두 일치했다. 공개 HTTP503/recovery_required와 실제 새 제출 거부도 확인했다. 그러나 승인된 최대3회와 달리 새 snapshot5개/529,309바이트가 관측됐다. 24MiB 총량은 지켰지만 횟수 제한은 실패했다. 즉시 PAUSED로 전송을 막고 새 백업 없는 고정 복원을 검증한 뒤 기본 private 프로필 `8d50fbe9a05c152cb4e3365bea01c52ec0f78419`의 RUNNING/cpu-basic으로 복귀했다. Secret·snapshot·공개 Static은 보존했고 상시 백업은 꺼져 있다. 유한 worker 종료 뒤 새 빈 저장소 기동이 반복된 양상에 대응해 v2의 독립 원격 snapshot 기준 목록 검사와 legacy initialize 거부를 구현했다. 관련22 CPU검사/5.497초 및 실제 소유 로컬 재기동·복원27.969초가 통과했다. 이 수정의 실제 HF 재검증은 미완료이며 새68파일 후보는 미업로드/미활성화다. [최신 근거](validation/platform_m6_live_backup_trial_20261012.json), [관리형 안내](MANAGED_SPACE_GUIDE.md). Goal active/원래 범위를 유지한다.

- User approved exact private CPU trial (at most3 snapshots/24MiB,96 existing records, fixed restore, default return). Secret was manually registered; values were not read. Capacity UI0TB/3TB, originals/history preserved.
- Initial deploy e112fefd2d19f8f0ef49ae5a445d530c5a3b4d31. Actual sign-in, two drafts, independent private originals/history and native-exact profile preserved under `generated/bounded-managed-live-20261012-v70`.
- Observer session96065 exited1 after count>3. Actual new5 objects/529309 bytes. PAUSED containment confirmed. No object deletion; old67154758-byte snapshot preserved. Timeline0/0/2/0/0 shows fresh-empty initialization pattern after finite run. No HF restart event log pass is claimed.
- Download session86449 exit0. Independent offline verification first sandbox temp-dir attempt30873 exit1; corrected fresh verified paths75159 exit0. Pinned by complete original/history match: b1ea22082e5c630c18ca8dbb5f5a2e0aaf8d099c11df79708f070851ed077ebe.
- Restore890172268f5edf6775a8b5275e15fac9381984c9. Actual HF re-login/private4 downloaded files byte-exact; public list/leaderboard/original all503/recovery_required, actual new-submit refusal. Worker disabled; no recovery/policy release.
- Default return8d50fbe9a05c152cb4e3365bea01c52ec0f78419 RUNNING/cpu-basic. Trial5 config paths removed; Secret and6 total snapshots retained. Public Static dbf810 unchanged.
- New local v2 initialization inventory guard: `python -m unittest discover -s tests -p "test_managed_space*.py" -v`,22/5.497s/exit0. `scripts/validate_managed_space_lifecycle.py` same externally hashed two48-record originals, fresh output `generated/managed-restart-guard-actual96-20261012-v71`: session11747 terminal0,27.969s, recreated empty host root refused before DB/children/upload and fixed restore still passes. Explicit HF/OAuth doubles; all owned children terminal.
- New68-file candidate `generated/managed-space-candidate-20261012-v71` unuploaded/unactivated. Existing core50 remains unchanged from full328 install; new full340 rerun not claimed. Actual new guard HF revalidation and operational/current recovery gates remain open.

Earlier checkpoints below retain their dated scope.

## 2026-10-12 — plan0.46 / v69: actual local managed lifecycle

v0.46에서 관리형 런처의 복원 안내와 종료 처리를 보완했다. 현재 코드의 로컬 실제 서버·worker·HTTP에서 두 기존 모델48+48기록 저장, 첫 백업+worker2회, 종료, 고정 복원 후 원본/이력 일치, 공개503·새 제출 차단을24.719초/exit0로 확인했다. HF/OAuth는 명시적 로컬 test double이며 실제 HF 연결이나 Linux signal 인수는 아니다. 관련18 CPU검사/2.987초/exit0와 이전 전체328 설치의 core50 바이트 유지도 확인했다. 사용자가 Bucket 전용 토큰과 `KOEVD_BACKUP_TOKEN` Secret 등록을 완료했다고 확인했다. 값은 읽거나 출력하지 않았다. 관리형68파일 후보와 기존 private CPU Space를 쓰는70파일 제한 시험 제안을 준비했으며 미업로드/미활성화다. 최대3회·snapshot24MiB 이하 전송과 고정 복원/기본 프로필 복귀에 대한 별도 승인을 요청했다. 실제 관리형 HF 백업·재시작 복구, 현재 Docker 전체 용량, 공개 참조·운영자 인수는 미완료다. [최신 근거](validation/platform_m6_managed_lifecycle_20261012.json), [관리형 안내](MANAGED_SPACE_GUIDE.md). Goal active/원래 범위를 유지한다.

- `python -m unittest discover -s tests -p "test_managed_space*.py" -v`:18 tests/2.987s/exit0, log `generated/managed-lifecycle-tests-20261012-v69/tests.log`. Three new restore-notice/SIGTERM-unwind/owned-restored-child tests. Prior full328 remains a separate unchanged core installation receipt; full336 rerun is not claimed.
- `python scripts/validate_managed_space_lifecycle.py --base-candidate generated/private-team-space-deployment-20261012-v67b --result <8B original> --result-sha256 787e3c87ef4929f232dffb800fd143397e80f63137bd397411dcef7d42997adb --result <4B original> --result-sha256 7d16beb22381beb8f259c1859ec640bd68419ee1cf5ef2f1b5a9ef9a7c35dcf7 --output generated/managed-lifecycle-actual96-20261012-v69b`: session26173 terminal exit0,24.719s. First failed run preserved in v69 directory; it was terminal and all owned children were reaped before corrected run.
- Actual HTTP96 originals/history persist after new-server pinned restore; public reads and new submission mutations return503/recovery_required. Initial+2 worker snapshots are66375/66375/262984 bytes in the local provider double. No actual HF exchange/upload or new generation.
- Child traces record only PID/role and credential presence, no token/session value. Actual two servers/one worker terminal. Restored server has no worker; finite worker exit stops its server. On Windows forced child stop can have exit1; this is controlled fixture shutdown, not a successful Linux signal observation.
- Read-only HF metadata after user Secret confirmation: current5504/private/docker/RUNNING/cpu-basic and Public Static dbf810 unchanged. No Secret values read; user confirmation is not token-scope/runtime-access verification.
- Materializer creates new68-file candidate69. Local proposal creator adds explicit finite managed config/technical backup roles to70-file context, structurally checked and unactivated. Max3 snapshot attempts/24MiB, no public/paid resources. Separate user approval is pending.

Previous checkpoints below retain their dated scope.

## 2026-10-12 — plan0.45 / v67–68: explicit saves and managed candidate

v0.45에서 비공개 개발 Space의 다운로드를 파일 준비 → 명시적 Save 링크로 보완했다. 현재 revision `5504a5e57e173c96b17272ee0e4c1608e859759c`의 배포 파일66개가 일치하고 RUNNING/cpu-basic이다. 실제 Chrome의48+48기록 분석에서 JSONL/CSV/Markdown/JSON/HTML 다섯 파일 모두 새로 저장되어 native 바이트와 일치했다. 로컬 UI는 삭제된 세션의 지연 다운로드가 Save 링크를 다시 만들지 않는지까지 검증했다. 별도 관리형 서버·백업 후보68파일과 stale 소스/운영 권한 상속 거부를 구현했다. 새 비편집 설치의 전체328 CPU검사·50소스/자산·25런타임 버전 대조와 이후 관련15검사는 별도 근거다. 관리형 후보는 미업로드/미활성화이며 전용 Secret 설정 완료도 아직 확인되지 않았다. 앱 자동 백업·재시작 복구/최신 상태·RPO·운영자 승인·공개 참조·현재 Docker 전체 용량은 미완료다. [최신 근거](validation/platform_m5_m6_prepared_downloads_managed_20261012.json), [관리형 안내](MANAGED_SPACE_GUIDE.md). Goal active/원래 범위를 유지한다.

- Current private deployment read-only acceptance: `generated/hf-space-venv/Scripts/python.exe generated/check_team_deployment_20261012_v67.py`; session5497 terminal exit0; payload66 exact/RUNNING/cpu-basic/Public Static unchanged.
- Actual Chrome: `generated/prepared-download-hosted-20261012-v67/browser-receipt.json`, five preserved originals and `save-link.jpg`; no new HF sign-in/draft save/publication.
- Local actual96 UI: `generated/prepared-download-local-20261012-v67-settled/evidence.json`, five checks including specific delayed CSV body completion after session deletion. Earlier sandbox network denial/global networkidle timeout remain preserved. Owned local servers39188/49316 stopped after testing; no GPU rerun.
- Fresh noneditable core: `generated/managed-runtime-20261012-v67/complete-install-receipt.json`, Python3.12.14, full328/131.520s/exit0/error-failure-skip0, pip check, both namespaces50 and25 lock versions exact. Current50/25 rechecked during formal receipt creation.
- Managed startup10 tests: real owned subprocess cleanup and real local SQLite snapshot/restore with explicit provider test double. Final first-backup/atomic-root guard test log retained.
- New materializer5 tests reject an internally hashed stale package/protocol/build, missing current module, inherited web approvals/references and actual managed config. `generated/managed-runtime-20261012-v67/env/Scripts/python.exe -m unittest discover -s tests -p "test_managed_space*.py" -v`: combined15/3.021s/exit0. Log `generated/managed-materializer-20261012-v68/tests.log`. Not a full333-suite rerun.
- Source ZIP recipe boundary: explicit two Dockerfile paths,8 tests0.258s/exit0, earlier Windows temporary-directory failures preserved.
- Materializer command: `python scripts/materialize_managed_space.py --repo . --base-candidate generated/private-team-space-deployment-20261012-v67b --output generated/managed-space-candidate-20261012-v68`;68 payload/manifest exact, missing actual managed.json/backup roles/credential, no upload/activation.
- User has requested detailed token setup instructions but has not confirmed setup complete. No current Bucket write or managed remote operation. Actual managed HF container/lifecycle/recovery and current Docker full-size gates remain open.

Previous checkpoints below retain their dated scope.

## 2026-10-12 — v66 / plan0.44 actual private cloud trial

v0.44에서 사용자에게 저장 대상·정확한 스냅샷·용량 한도를 제시하고 명시적 승인을 받은 뒤 비공개 `KETI-NLP/KoEVD-Platform-Backups-Dev`를 만들었다. 포함 용량0/3TB를 재확인했고 추가 구독·유료 용량 구매 없이67,154,758바이트 스냅샷1개를 전송했다. 별도 재다운로드·오프라인 복원 후 실제 두 모델35,340기록의 원본·상태·이력과 고정 checkpoint가 일치했다. 복원 공개조회503/변경 차단·없는 객체 조회 실패의 기존 사본 보존도 확인했다. 실행95.062초/exit0이며 코드·GPU·서버 설정은 바꾸지 않았다. 앱의 자동 백업·재시작 복구/최신 상태·RPO·운영자 승인·공개 참조·추가3개 browser 다운로드는 미완료다. [최신 근거](validation/platform_m6_actual_private_cloud_20261012.json). Goal active/원래 범위를 유지한다.

Controller: generated/validate_private_cloud_20261012_v66.py, hf-space-venv Python/current src, exit0. Initial external command was rejected before execution; explicit human approval received before retry. Read-only Bucket inventory[] and billing display0/3TB were inspected. Cloud receipt and independent fetched ZIP/restore/checkpoint in generated/private-cloud-acceptance-20261012-v66. Payload67,154,758 bytes, one hash-addressed ZIP, no overwrites/deletes, no secret/mount/live app reconfiguration. Dedicated snapshot adapter exercised against actual HF, not a test double. Source unchanged; no redundant CPU suite or GPU run. Report-kind/status-only log diagnostic found no buffered matching lines; it does not prove no requests and does not resolve browser download3.

## 2026-10-12 — v64/v65 / plan0.43 actual Team hosting and native OAuth

v0.43에서 실제 Team 가입을 API로 확인하고 별도 비공개 CPU Docker Space `KETI-NLP/KoEVD-Platform-Dev`를 배포했다. 현재 revision `03e79a75ee35570b83948343d521f684a38fce01`의 payload65개+manifest가 일치하고 RUNNING/cpu-basic이다. 실제 HF 로그인 후 두 모델48+48기록의 업로드·분석·대응 비교와 비공개 draft2건 저장/재조회를 확인했다. 내려받은 원본 JSON 내용·HF OAuth 생성 이력과 분석 JSON/HTML의 native 바이트가 일치한다. v64의 별도 HTTP 검증에서는 다섯 출력·세션 격리·삭제가 통과했다. 현재 브라우저의 나머지3개 다운로드는 확인하지 못했다. Private proxy cookie 누락을 수정했고 관련4+6+3+11 검사가 통과했다. 기존 전체310은 이전 설치 근거다. Public Static은 그대로이며 영구 저장·운영자 승인·공개 참조/공식 순위·production은 미완료다. [최신 근거](validation/platform_m5_m6_team_hosted_20261012.json) Goal active/원래 범위를 유지한다.

Creation/controller: generated/deploy_private_team_space_20261012_v64.py; initial hosting receipt preserved. API controller: generated/validate_team_hosted_runtime_20261012_v64.py (initial Static-protocol assumption failure retained; separate Docker checker3 tests). v65 update: generated/update_team_ui_20261012_v65.py. Read-only exact-byte check: generated/check_team_deployment_20261012_v65.py, exit0/payload66/RUNNING; two SDK-model inspection failures retained separately. Current-source command: PYTHONPATH=src, v60 environment python -m unittest discover -s tests -p test_spaces.py -v, 11/7.455s/OK. Other related4+6+3 tests have separate logs. Real Chrome chooser/OAuth/analysis/private save via CUA; proof and canonical originals/history in generated/private-team-browser-20261012-v65. Browser JSON/HTML native equality checked; other3 downloads not observed. No new inference/public push/paid storage/role approval.

## 2026-10-11 — v62 / plan0.41 external blocked audit

No-progress revalidation, not new implementation/test acceptance or a verified wait.
Local docker/podman/nerdctl absent; read-only SSH GPU_NODE inventory exit0 returns
all null (tool chunk f801ad). Process OAuth ID/secret/backup target not configured;
this does not prove no external app/Bucket exists. Candidate roles/baselines empty;
real review statements/publication evidence remain unapproved. Installed50,
server64, Static19 and original actual results/hosted evidence are exact. Prior
terminal13 GPU stages, private35340 storage and default no-rank receipt preserved.
Same mandatory external gates repeated across v59/v60/v61/current, and independent
required implementation is prepared. Blocked audit passes, full scope incomplete.
Formal docs/validation/platform_rc_external_gates_20261011.json; next actions in
docs/EXTERNAL_ACCEPTANCE_HANDOFF.md. No tests/inference/public push/billing/runtime
installation or production deployment. v61 ZIP retained as earlier checkpoint.

## 2026-10-08 — M0 and first M1 contract

Checkout: `publication/github/KoEVD`, HEAD `cfb79006a6471ecd3ce89c0bad8a98e85c8a75fb`, package 0.2.0. No applicable AGENTS.md found. Before implementation the only dirty files were the two newly prepared plan/prompt Markdown files; existing research files were preserved. Windows bundled Python was used. Sandbox setup initially failed; read/write/test commands ran under the permitted reviewed shell. Git's ownership check was handled with per-command `-c safe.directory=...`, without global configuration changes.

### Commands and actual evidence

Commands were run with repo root as cwd and `PYTHONPATH=src` (PowerShell: `$env:PYTHONPATH = (Join-Path (Get-Location) 'src')`). Source path was needed because this checkout had not been installed. The initial uninstalled test invocation had import errors; rerunning with the source path passed all 27 existing tests.

```bash
python -m unittest discover -s tests -v
python examples/make_demo_results.py --output-dir generated/results-contract-20261008
python -m koevd_eval.results validate \
  --input generated/results-contract-20261008/results.json \
  --trusted-index generated/results-contract-20261008/local_input_index.json
python -m koevd_eval.results report \
  --input generated/results-contract-20261008/results.json \
  --trusted-index generated/results-contract-20261008/local_input_index.json \
  --output-dir generated/results-contract-20261008/cli-report
```

After implementation: **36 tests passed**, including 9 new result-contract tests, in 3.363 seconds. Existing HTTP/runner/classification-glue/report tests still pass; classifiers there are CPU doubles. New tests cover independently trusted input recovery, recomputed malicious upload checksums, gold/metadata injection, missing/extra/duplicate records, summary rejection, response/measurement binding, Task 3/4 shared generation, stale local measurement evidence, all-row denominators, unknown provenance, private endpoint/error omission, invalid verification/publication/confidence claims, strict/bounded JSON and traversal rejection. Portable and original report model/task summaries are exactly equal for the fixture.

The example/CLI chain exited successfully. Validation returned:

```json
{
  "status": "structurally_validated_against_supplied_index",
  "rows": {"1": 1, "2": 4, "3": 2, "4": 2, "5": 3},
  "generation_authenticity": "user_reported",
  "official_rank_eligible": false
}
```

Generated ignored artifacts: `generated/results-contract-20261008/results.json`, `local_input_index.json`, `report/`, `cli-report/`, `SHA256.json`, `SYNTHETIC_ONLY.txt`. The checked-in reproducible example is `examples/make_demo_results.py`. The model is explicitly fictitious, no model/classifier is invoked, and Task 3 has one failure. Files contain 12 records, not 12 independent sources. These are functional CPU evidence, not paper results, accuracy evidence, a public baseline, or GPU integration.

### Limits and next work

M1 is partially implemented. The executable Python contract and pipeline migration exist; pinned official protocol registry, formal JSON Schema distribution and standalone legacy JSONL migration still need implementation. The service must supply its own trusted index; accepting an uploader's index would break the trust boundary. Current validation cannot prove generated-model identity or classifier correctness. Task 3/4 are user-reported and measurement-limited, and public rank eligibility is false.

The HTML uses the existing report layout; no new visual/UI acceptance is claimed. Source-tree CLI paths were checked; fresh isolated install/entry-point verification remains a release gate. No new GPU inference, reference accuracy audit, two-real-model comparison, Spaces app or production publication was performed in this iteration. Goal remains active.

## 2026-10-08 — M1 completion: pinned registry, packaged schemas, legacy migration

Previous goal turn is **progress**: it implemented the result contract/export and produced test/CLI evidence. This iteration re-read the current worktree before extending it. No repository instructions changed. HEAD remains `cfb79006a6471ecd3ce89c0bad8a98e85c8a75fb`; new work is uncommitted and not pushed.

### Pinned input evidence

The local HF download is `publication/validation/remote_downloads/KoEVD` (outside the repository, still inside the workspace). All nine consumed files' `.cache/huggingface/download/*.metadata` first lines identify `f5920837769bea77e072c8e033e5ad9cbff4d45d`. Their actual SHA-256 values match the downloaded release manifest. These local byte/revision records were used as pinned historical evidence; this does not claim a new check of remote main.

The checked-in candidate definition is `configs/protocols/koevd-core-canonical-v1.json`:

- Definition content digest: `501401566487a29fa7252372621c8239a5c7388e90312c7c3dbe920dcd7020a0`.
- Preparation implementation digest: `b3bb72a02a0b676afe67c8182345254d397f0da89be374963c9ff0fd8d23fbb8`.
- Trusted full index content digest: `0d78a9b2ed412fa3507cf3d68db6b45d102ef0b8e24f0c65f3a10c3a987cd26d`.
- Task 1/2/3/4/5 input counts: 2,000 / 8,000 / 2,659 / 2,659 / 2,352.
- Trusted index file: `generated/pinned-core-inputs-20261008/trusted_input_index.json`, 69,541,861 bytes (ignored local artifact).

`ProtocolRegistry` independently checked dataset hashes, preparation code, full expected input sets and protocol definition. Tests reject changed file bytes before preparing a new run, changed preparation code, mismatched expected counts, traversal, duplicate protocol IDs, mutable `main` revisions and altered gold even after the index is rehashed. Tiny test definitions are explicitly synthetic, not replacements for the actual pinned registry.

### Actual installed package validation

A fresh venv was created at `generated/contract-install-venv` using the bundled Python; setuptools/wheel/jsonschema were installed only in that venv. The package was built and installed with no runtime dependencies and without editable/source-path imports:

```bash
python -m venv generated/contract-install-venv
# Activate the venv, then:
python -m pip install 'setuptools>=68' wheel 'jsonschema>=4.20'
python -m pip install --no-build-isolation --no-deps .
```

A reinstall after code changes also completed. With `PYTHONPATH` removed, imports resolved to `generated/contract-install-venv/Lib/site-packages/koevd_eval`, and installed `koevd-results.exe` successfully ran:

- `migrate` on the existing synthetic Task 1/2/3/5 JSONL fixture (Task 4 omitted).
- `validate` on the resulting full-record JSON: rows 1/4/2/2/3, user-reported generation, rank-ineligible.
- `report`: original and migrated report `models` values exactly equal.
- `schema --kind results`, `index`, `protocol`: all three schemas passed `Draft202012Validator.check_schema`; actual migrated results, full pinned index and checked-in protocol passed their schemas.
- Runtime registry validation of the full pinned index passed separately. Schema alone is not trusted rescoring.

Migrated artifact: `generated/results-contract-20261008/migrated_results.json`, SHA-256 `fff564db4d218a199035bd80e7319aad351766befcc1bbc8678107db54476ffe`. Migration preserves unknown temperature/max_tokens/revisions/batch/fingerprints as null, a failure and unmeasured Task 4. The synthetic values are not real model evidence.

**All 43 tests passed in 5.824 seconds from the installed package**, including independent formal schema checks. This covers existing 27 tests plus 16 contract/registry/schema/migration tests. The dev validator used jsonschema 4.26.0. Classifier tests still use CPU doubles. Installing schema tools is not GPU validation.

### M1 gate and remaining objective

M1's stated gate is met: case-complete standard result export, CPU validation/restoration/rescoring, exact official candidate expected inputs, malformed/tampered/duplicate checks, faithful pipeline and original-row legacy conversion, schema examples and working installed commands exist. Aggregate-only references and summary-only payloads cannot be promoted to per-case outputs. Uploaded verification/publication claims remain user-reported/local; the operator registry is separate from uploads.

The pinned candidate describes decoding and measurement policy; actual setting compatibility and public rank eligibility are **not** yet implemented (M3/M6). Its registration does not prove execution authenticity. Safety and strategy measurements remain limited. No chart/UI acceptance, Spaces service, persistence, two-real-model GPU integration or production publication is claimed. Next meaningful work is M2 runner response metadata/progress/concurrency/resume. The whole Goal remains active.

## 2026-10-08 — M2 completion: execution metadata, preflight, durable attempts and concurrency

Previous turn is **progress**, verified from the current M1 files and records. This turn implemented runner-v2 behavior while preserving the Task/scorer contract and pinned preparation digest. No public push or new GPU execution was performed.

### Actual implementation and tests

`run_openai_compatible.py` now supports typed final/finish/usage/request/response/model/reasoning/refusal data; strict allowlisted extra requests; bounded workers; durable run/status files; fsynced attempt start/finish journal; first-accepted-response selection; safe error diagnostics; OS output locks; ordered compaction and compatible old row journals. `preflight.py` adds model inventory/contract probing, exposed as `koevd-doctor` and pipeline/runner preflight. Probes are explicitly excluded from benchmark rows. Portable v1 has additive optional execution/response fields, with runtime and packaged-schema validation; pre-M2 files remain valid.

Thirteen new runner tests use real local HTTP or explicit CPU test doubles. They cover bounded overlap and out-of-order completion, stable output and resumed ID, no extra requests after success, 429 retry and 401 no retry, secret-echo bodies omitted, start checkpoint interruption and truncated last line, concurrent interrupt, hard child-process exit 73 releasing the OS lock, legacy metadata remaining unknown, same-output ownership, changed preserved messages/configuration/input order, rejected parameters with no fallback, empty/refusal/reasoning/length outputs preserved, inventory unsupported/missing-model behavior, extra fields/seed/model declarations exported, selected-attempt integrity, shared pipeline run ID, and Korean/emoji paths under forced CP949 subprocess streams.

An intermediate optional-field helper consumed a `map` iterator twice and broke index key validation; the expected field set was materialized once, restoring all prior contract tests. The initial installed CLI artifact run succeeded but Windows CP949 stdout caused UTF-8 reader-thread failures and incomplete log capture (`stdout: null`). That preliminary artifact remains at `generated/runner-cli-20261008`; it is not the final CLI logging evidence. Explicit UTF-8 at the four updated CLI entry points fixed the issue. A Unicode path regression and the final installed chain confirmed the fix.

### Installed CLI evidence

The active isolated venv was reinstalled with the final source (no `PYTHONPATH` or editable imports). Reproducible checked-in script:

```bash
python -m pip install --no-build-isolation --no-deps --force-reinstall .
python scripts/validate_runner_cli.py --output-dir generated/runner-cli-final-20261008
python -m unittest discover -s tests -v
```

Final **56 tests passed in 11.479 seconds from the installed package**, including formal schema checks. The separate CLI script successfully used installed executable entry points for prepare→doctor→generate with workers 2/preflight→resume with workers 1→index→export→validate→report. Metadata, client controls and length reason survived export. Final logs were decoded as UTF-8. It recorded 12 local HTTP requests: 10 benchmark requests plus 2 explicit probes; re-running completed generation added 0 requests. There are 12 exported records (Task 4 reuses 2 Task 3 records), not 12 independent sources or 12 target requests.

Ignored local artifacts: `generated/runner-cli-final-20261008/cli-evidence.json`, `results.json`, `index.json`, `doctor.json`, `run/` sidecars, `report/`, `SYNTHETIC_ONLY.txt`, `SHA256.json`. Final installed CLI fixture observed peak HTTP overlap 1 because responses were immediate; the separate delay-controlled concurrency test proved overlap 2 and the workers-2 cap. This distinguishes requested worker count from observed overlap.

The fixed input preparation digest remains `b3bb72a02a0b676afe67c8182345254d397f0da89be374963c9ff0fd8d23fbb8`, preserving the pinned registry. API control/model/engine declarations remain user-reported; probe acceptance does not prove their effect or weights identity. A dropped response after a started request is `interrupted_unknown`, not proof of no inference. API success is not task validity/safety; existing classifier measurements become stale after prediction changes.

### Gate and outstanding objective

M2's local gate is met: installed commands, typed metadata, explicit parameter policy, preflight/progress, bounded request submission, interruption/retry/order/legacy resume and credential-echo protection have actual evidence. Core dependencies remain empty. Target-server/GPU behavior still needs M4's real two-model evidence and measurement audit; the current fixture does not substitute for it. M3 charts/cases/compatibility/statistics, M5 Spaces and M6 persistence/registration/release gates remain incomplete. Whole Goal stays active.

## 2026-10-08 — M3 progress: shared trusted analysis, source statistics and cases

Previous turn was **progress**: runner M2 changed implementation and supplied
installed CLI evidence. Current HEAD is unchanged at
`cfb79006a6471ecd3ce89c0bad8a98e85c8a75fb`. Changes remain local/uncommitted/unpushed;
no applicable AGENTS.md was found. No research text, dataset, weights or previous
public release manifest was rewritten.

`koevd_eval.diagnostics` and installed `koevd-diagnose` now reconstruct all cases
from an independently trusted index, preserve historical/strict metrics, and add
partition/metadata groups, source-cluster percentile intervals, paired event
differences with validity exclusions, structured setting compatibility, Task 1
label-specific diagnostics/F1, Task 4 multi-label/co-occurrence/separate unsafe
marker, Task 5 strict outcome counts, Task 3–5 transitions, quality/disagreement,
full cases and rendering-neutral chart specifications. JSON/CSV/Markdown use the
same profile. `filter_cases` and `comparison_cases` are shared chart/case/paired
exploration helpers, not UI copies of scoring.

A schema detail mattered: the official registry keeps the primary split under
`selection.split`, while the local index uses `split`. Resolving both preserved
the actual primary denominator. Comparison also checks each run against the fixed
decoding policy; two identically wrong configurations are not standard conditions.
Target weights may differ; classifier batch/precision differences only affect
measured tasks. Equal null provenance stays unknown. Every result remains
rank-ineligible; this does not implement M6's metric-specific admission yet.

### Actual installed validation

Final commands ran with `PYTHONPATH` removed, after non-editable reinstall into
`generated/contract-install-venv`:

```bash
python -m pip install --no-build-isolation --no-deps --force-reinstall .
python -m unittest discover -s tests -v
python examples/make_demo_diagnostics.py --output-dir generated/analysis-v2-demo-20261008
koevd-diagnose --input generated/analysis-v2-demo-20261008/SYNTHETIC-A.json \
  --input generated/analysis-v2-demo-20261008/SYNTHETIC-B.json \
  --trusted-index generated/analysis-v2-demo-20261008/trusted-synthetic-index.json \
  --output-dir generated/analysis-v2-demo-20261008/final-installed-analysis \
  --bootstrap-resamples 200
```

**74 tests passed in 14.751 seconds**, including 18 new analysis tests and all
previous 56. Imports resolved to the venv's `Lib/site-packages/koevd_eval`.
The wheel built successfully (development source still version 0.2.0); transient
wheel SHA-256 was `6e2c39af0afbd3f2da2fd96c89b3982e08c2782b17afd83d2120fab6560c26dc`.
This is installed development evidence, not a new public release.

New tests hand-check missed-risk/false-alarm/coverage/F1 and missing denominators,
strict versus historical Task 5 partial parsing, strict strategy classification
versus historical empty-dict counting, separate unsafe marker, co-occurrence,
source clustering/order independence/repeated variants/zero-denominator draws,
paired source uncertainty, input-hash exclusion even with identical sample IDs,
unknown provenance, fixed-policy mismatch, batch-specific measured-task limits,
artifact versus model identity, primary/union/tool overlap, measurement
disagreement and length/repetition/refusal/reasoning flags. Chart counts equal
case-filter results; paired invalid cases remain visible. Profile/CSV/chart
values agree, exports do not mutate the app result, and malicious model-name
strings are literal in Markdown/CSV. Uploaded gold/scores are rejected.

The first fixture-construction attempt retained the old evaluated model on some
rows when constructing the second model; existing export validation correctly
rejected mixed identities. The fixture was fixed instead of weakening validation.
The initial test module directly imported another TestCase class, duplicating
its discovery; a module import removed those duplicate counts. Final 74 is the
actual distinct installed suite count.

### Two fictional runs and full input scale evidence

Ignored final demo artifacts:
`generated/analysis-v2-demo-20261008/final-installed-analysis/` contains
`profile-v2.json`, `cases-v2.jsonl`, `metrics-v2.csv`, `report-v2.md`,
`numeric-evidence.json`, `SHA256.json`. Two explicitly fictional runs produce one
comparison and 1,160 case records (580/run), not 1,160 independent sources.
Each run has 80 union sources, 60 primary sources, 40 tool sources, task counts
60/240/80/80/120, and 134 chart specifications. Task 3 valid counts are 74 union,
56 primary and 37 tool overlap. All five task comparison levels correctly remain
`common_inputs_exploratory`. Measurement disagreements are 6 and 5 sources; these
are deliberate fixture labels, not classifier accuracy findings or real baselines.

The installed full-scale command also completed:

```bash
python scripts/validate_analysis_scale.py \
  --trusted-index generated/pinned-core-inputs-20261008/trusted_input_index.json \
  --registry configs/protocols --protocol-id koevd-core-canonical-v1 \
  --output-dir generated/analysis-full-scale-20261008 --bootstrap-resamples 100
```

Registry validation passed for trusted index
`0d78a9b2ed412fa3507cf3d68db6b45d102ef0b8e24f0c65f3a10c3a987cd26d`.
The script attached entirely artificial predictions to the 17,670 real prepared
input records (2,659 sources); it invoked no model or classifier. Task counts are
2,000/8,000/2,659/2,659/2,352. Task 3 union/primary/overlap row counts are
2,659/2,000/784, with 2,587/1,947/762 valid fixture responses. Analysis took
44.473 seconds with 100 resamples; assembly 8.392 seconds, writing 1.145 seconds
on this CPU. These timings are local observations, not a performance guarantee.
Full-scale generated profile/cases/CSV/MD, `scale-evidence.json`, `SHA256.json` and
`SYNTHETIC_ONLY.txt` are in `generated/analysis-full-scale-20261008`.
The scale checkpoint preceded the final additive case-filter/export-escaping
helpers; the final installed suite covers those helpers. Counts/core statistical
behavior were unchanged. No redundant scale run is claimed.

The preparation code digest remains
`b3bb72a02a0b676afe67c8182345254d397f0da89be374963c9ff0fd8d23fbb8`.
Machine-readable checkpoint: `docs/validation/platform_m3_analysis_20261008.json`.
User guide: `docs/DIAGNOSTICS_GUIDE.md`.

### Remaining gate

M3 is **incomplete**: chart specification data is not rendered interactive HTML,
new browser tabs/filters/drilldown/offline assets have not passed visual QA.
The next step is the offline renderer using the shared engine and full cases.
Two real target-model GPU integration, measurement audit, Spaces, persistence,
registration and release/deployment gates remain incomplete. CPU doubles and
artificial scale outputs do not substitute for those. No public push/deploy/new
GPU execution was performed. Whole Goal remains active.


## 2026-10-08 M3 interactive offline report gate completed

This section supersedes the earlier M3-partial gate. The shared analysis engine
now exports `report-v2.html` through `koevd_eval.reports` and packaged CSS/JS.
Historical parsers/scorers are unchanged; native SVG renders existing chart specs
and exact data tables. Python supplies canonical metadata memberships; JavaScript
filters cases and formats values, without computing metric scores.

### Installed package and mathematical/rendering contracts

After the final pointer-area fix, removed `PYTHONPATH`, force-reinstalled the
non-editable checkout in `generated/contract-install-venv` with
`python -m pip install . --no-deps --no-build-isolation --force-reinstall`, then
ran `python -m unittest discover -s tests -v`. **78 tests passed in 16.640 s**.
The Node parity test ran using `KOEVD_TEST_NODE`; it was not skipped. Packaged
renderer/assets were loaded from installed site-packages. The transient build
wheel was 114,778 bytes, SHA-256
`9d32979dc68b3979b3d17c32cf4d7e90e379c952a4d4168df25ec115df0d8b96`.
This is development installation evidence, not a new public release/tag.

Four added renderer tests cover malicious JSON/script/text round-trip including
Korean and U+2028/U+2029, non-mutation, CSP hashes/offline assets, trusted view
normalization, null/zero distinction, written full-case HTML and Python/Node
chart-filter/paired-state agreement. The suite also covers the preserved historical
metrics and existing result/protocol/runner contracts. Chart specs now include
Task 1 severity-specific missed-risk/false-alarm and Task 4 metadata inclusion
heatmaps; 157 specs per fictional run. No classifier label/score was changed.

### Real browser interactions and visual inspection

The CUA in-app browser twice failed to start its kernel because Windows sandbox
setup refresh failed. A new headless Chrome session was used instead; the user's
browser/session/authentication was never accessed. Browser version observed:
**154.0.8037.98**. The checked-in Playwright acceptance scripts route only the
specified local file documents (and an exported local SVG in the small fixture
check); external requests are aborted and make the gate fail.

Executed with bundled Node/Playwright and the local Chrome executable:

```bash
node scripts/validate_report_ui.cjs \
  --report generated/offline-report-installed-final-20261008/report-v2.html \
  --security-report generated/offline-security-installed-final-20261008/report-v2.html \
  --output-dir generated/offline-report-ui-candidate-20261008 \
  --browser-executable "C:/Program Files/Google/Chrome/Application/chrome.exe"

node scripts/validate_report_scale_ui.cjs \
  --report generated/offline-report-full-scale-final-20261008/report-v2.html \
  --output-dir generated/offline-report-scale-ui-final-20261008 \
  --browser-executable "C:/Program Files/Google/Chrome/Application/chrome.exe"
```

Both exited **0**, with zero console errors and zero external requests. The small
fixture covers all 12 tabs, keyboard navigation, confusion drilldown (10 fixture
cases), source search (10 records), paired responses, event-only comparison
(3 left-only event cases), Task 4 no rank, metadata/scope selectors, response-safe
versus unsafe-tool drilldown (6 fixture cases), whole-row pointer activation,
standalone SVG opened without XML error, analysis download equality, and 390px
mobile layout. These are deliberate artificial counts, not observed model results.
The entirely unmeasured Task 3 remains N/A. Literal script/img strings in model IDs
and response text neither execute nor create active markup. This specific fixture
is not a claim of exhaustive security auditing.

The candidate evidence directory contains `ui-evidence.json`, 22 screenshots,
standalone downloaded SVG/analysis JSON and `SHA256.json`. Primary desktop task,
transition, metadata, quality, comparison, cases and method screenshots were
visually inspected across iterations; final selected desktop/mobile/security and
full-scale screenshots were inspected after relevant fixes. Scope/denominator,
measurement-limited status, multi-label interpretation and synthetic-only notices
are visible. Raw prompt/response starts folded; every record is retained.

Initial failures are preserved under ignored generated directories:
mobile select overflow (390px viewport -> 433px document) was fixed with constrained
select widths; a missing adversarial HTML from an older installed fixture builder
was corrected by installing/currently generating that fixture; full-scale SVG group
clicking could land in an unpainted gap despite the row-click instruction. Added a
transparent pointer area across each bar row, kept the normal pointer test, and
re-ran both browser gates. No forced click or weakened denominator/metric test was
used. Profiles were hashed before/after final HTML rerender and were unchanged.

### Full-input scale, with explicitly artificial responses

The installed `scripts/validate_analysis_scale.py` command used the pinned trusted
index and registry, 100 source resamples and output directory
`generated/offline-report-full-scale-final-20261008`. It produced all report formats
and scale/hash/synthetic notices. Input index SHA-256 remains
`0d78a9b2ed412fa3507cf3d68db6b45d102ef0b8e24f0c65f3a10c3a987cd26d`;
preparation code digest remains
`b3bb72a02a0b676afe67c8182345254d397f0da89be374963c9ff0fd8d23fbb8`.

There are **17,670 records / 2,659 sources**, Task counts
2,000 / 8,000 / 2,659 / 2,659 / 2,352. Task 3 union/primary/tool overlap remain
2,659 / 2,000 / 784 (overlapping subsets), with artificial valid counts
2,587 / 1,947 / 762. Source assembly took 7.999 s, analysis 42.343 s and writing
4.909 s on this CPU. The final pointer-area-only HTML rerender preserves the
computed profile and has **73,828,032 bytes**.

The full-scale browser gate opens all tabs, confirms 17,670 retained cases and
12 visible/page, Task 3 primary 2,000/overlap 784, Task 5 2,352/one framing 784,
pagination, literal search, empty filter (not a zero metric), risk-category chart
and case link, single-run comparison explanation and mobile Task 4. Initial load
was 0.974 s; source literal search 0.583 s; primary filtering 0.040 s in this
headless local-file run. These are local timings, not general performance guarantees.
Five full-scale screenshots plus `scale-ui-evidence.json` and `SHA256.json` are in
`generated/offline-report-scale-ui-final-20261008`.

Machine-readable current checkpoint:
`docs/validation/platform_m3_report_20261008.json`; source and artifact hashes are
recorded there. Earlier partial checkpoints remain historical evidence.
M3's CPU/synthetic offline UI gate is complete. **M4 actual two-target-model GPU
integration and measurement audit, M5 Spaces/server sessions, M6 storage/admission/
moderation/withdrawal and overall release candidate remain incomplete**. This run
did not call a GPU/model/classifier, establish classifier accuracy, publish a
baseline, push GitHub/HF, use paid resources or deploy production. Goal stays active.


## 2026-10-08 M5 CPU upload/reference app implemented (partial gate)

Added `space_service.py`, optional FastAPI `spaces.py`, packaged UI assets and
`koevd-space`, plus a checked-in explicit fictional demo catalog. The app reads
operator-configured index/reference bytes and their hashes, performs standard
registry validation when appropriate, reconstructs gold/metadata independently,
and calls the existing `analyze_many`/`write_analysis`/offline renderer. It does
not accept an uploader index/path, aggregate score, publication state or identity
promotion. Reference raw-publication attestation is separate from structural/GPU
verification; synthetic references cannot assert actual target outputs.

The private single-process store uses hashed random session bearers, per-session
UUID filenames, request tokens, strict source matching, bounded actual streaming
bytes, global/session reservations, a single analysis worker and two job slots.
GET/download requires the owning session; mutations additionally check the request
token and same-origin/host boundary. Credentials are header-only and remain in
page memory, not URLs/cookies/localStorage/exported reports. Removing an upload
invalidates its report. Deleting a session revokes access/removes files; TTL rejects
expired access, periodic/busy-final cleanup removes owned directories. This is
not M6 persistence or a production abuse/security certification.

### Tests and actual installed local HTTP/browser path

Installed optional FastAPI/uvicorn/httpx in the existing isolated CPU venv, then
force-installed this checkout without editable/PYTHONPATH imports. Added ten
service/HTTP tests: catalog hashes/registered-versus-custom/demo policy,
unknown input/gold/scores/duplicate JSON rejection, session isolation/secret hashing,
CSRF/path/authorization, shared engine exact JSON, raw-reference consent/tamper and
duplicate artifact, TTL/busy cleanup, byte/quota release, queued concurrency and
recovery, origin/host/status/download boundaries and streamed unknown-length size
limit. **88 total installed tests passed in 22.290 s**, including all previous
research/result/runner/report tests, optional HTTP tests and Node filter parity.

The suite's transient wheel was 130,142 bytes, SHA-256
`190e01005440bac7ed8e00394b11909444f601fb0ceb7bde15c679c1b4db5bb9`.
A later end-user footer-only edit produced the final installed wheel 130,125 bytes,
SHA-256 `ee118f3986cc38df1985d838a40db98a2bba027a2ae4bfac4e992f0ba4d3a0e7`.
Backend/core code did not change; the final browser gate exercised the installed
footer/assets. These are development builds, not public release version/tag changes.
Starlette emits a TestClient httpx deprecation warning; it was not suppressed.
All HTTP tests still passed; the live HTTP browser path also passed independently.

Actual web versions: FastAPI 0.142.4, Starlette 1.7.0, uvicorn 0.54.0,
httpx 0.28.1, Pydantic 2.13.5, AnyIO 4.15.1. Web runtime lock is in
`apps/spaces/requirements.lock.txt`; this Windows test is not Linux container proof.

Executed demo/server and independent numeric reference:

```bash
python examples/make_demo_space.py --output-dir generated/space-demo-20261008
python -m koevd_eval.spaces \
  --catalog generated/space-demo-20261008/catalog.json --demo \
  --host 127.0.0.1 --port 8767 \
  --session-root generated/space-session-test-20261008

koevd-diagnose --input generated/space-demo-20261008/SYNTHETIC-A.json \
  --input generated/space-demo-20261008/SYNTHETIC-B.json \
  --trusted-index generated/space-demo-20261008/trusted-synthetic-index.json \
  --output-dir generated/space-local-agreement-20261008 \
  --bootstrap-resamples 100 --bootstrap-seed 1729

node scripts/validate_space_ui.cjs --origin http://127.0.0.1:8767 \
  --fixture-dir generated/space-demo-20261008 \
  --security-result generated/offline-report-security-fixture-20261008/SYNTHETIC-A.json \
  --expected-profile generated/space-local-agreement-20261008/profile-v2.json \
  --output-dir generated/space-ui-candidate-20261008 \
  --browser-executable "C:/Program Files/Google/Chrome/Application/chrome.exe"
```

The owned installed uvicorn server was process 36504 on exec session 98338; it
responded ready and supported the actual browser actions. This is localhost only,
not a Space publication. A later turn must revalidate this live handle before use.
The local diagnostic CLI exited 0 with two fictional runs/1,160 records, and the
browser gate exited 0. Two fresh Chrome contexts uploaded/compared separately;
one uploaded SYNTHETIC-A and selected operator-configured fictional B, the other
uploaded adversarial literal-text A. The browser exercised same-engine report and
exploratory comparison, Korean cases, authenticated JSON/HTML download,
unauthenticated denial (401), other-session report denial (404), literal malicious
model/response text, entirely unmeasured Task 3 N/A, mobile parent/iframe and deletion.
Tokens were not in observed request URLs. Console errors/external requests were
zero. App profile JSON equals the independent installed CLI profile **in full**;
app HTML bytes also equal the local renderer output. All browser session files
were gone after deletion, while the owned test/preview server remains available.

Eight final screenshots, downloaded profile/HTML, `space-ui-evidence.json` and
`SHA256.json` are in `generated/space-ui-candidate-20261008`. Desktop and mobile/
security screenshots were visually inspected. An initial offscreen iframe element
capture after resize was blank despite the DOM assertions. Strengthened the test
with actual tab activation, visible heading and scrolling before element capture;
the final 324px embedded view was visibly rendered without horizontal page overflow.
No scoring/product logic was weakened to pass this check.

The actual 17,670-record standard input catalog was also loaded/registered-validated
using the existing pinned source index, not an uploader file. Evidence:
`generated/space-standard-catalog-check-20261008/catalog-evidence.json`.
Preparation identity remains
`b3bb72a02a0b676afe67c8182345254d397f0da89be374963c9ff0fd8d23fbb8`.
Machine-readable current checkpoint: `docs/validation/platform_m5_cpu_20261008.json`.

### Candidate files and remaining gates

`docs/SPACES_GUIDE.md` documents the actually tested private flow, operator catalog,
reference scope, size/queue/TTL limits and shutdown/crash boundary. Dockerfile/YAML/
web lock are prepared under `apps/spaces`; Docker is unavailable here, so no container
build or live Space test is claimed. HF Docker/ephemeral storage/configuration docs
were checked; future persistence requires a Bucket/dataset/appropriate adapter.

M5 stays **incomplete** until actual approved two-target-model results, container/
Space behavior and its full gate are verified. M4 actual GPU/measurement audit and
M6 OAuth/submission/moderation/persistent history/withdrawal/metric admission remain.
No real target/classifier inference, held-out accuracy reproduction, real raw
baseline publication, GitHub/HF push, paid resource or production deployment was
performed. Goal remains active; CPU app progress does not substitute for GPU proof.


## M4 CPU measurement audit — 2026-10-08

Implemented `koevd-audit create` and `import-review` in the existing package. Original Task scorers/parsers/preparation remain unchanged. Frozen target/generation declarations and all responses must match between measurement variants. Semantic, validity, recorded raw and raw-presence changes have separate denominators. Blinded materials omit classifier labels; independent review imports bind to audit/input/response and preserve uncertain/abstain/unreturned states. No adjudication or rank promotion is provided.

- Wheel: `generated/audit-wheel-20261008/koevd_eval-0.2.0-py3-none-any.whl`, 136,902 bytes, SHA-256 `5d1447ab79b1f179594aec16c273e208d99281715373af6c333d0f0a1f113539`.
- Installed regression command: `generated/contract-install-venv/Scripts/python.exe -X utf8 -m unittest discover -s tests -v`.
- Result: 101 tests passed in 37.924 seconds, including 13 new measurement-audit tests. Existing Starlette/httpx TestClient deprecation warning was observed; no warning was suppressed.
- Actual console CLI create/import/stale rejection: `generated/audit-cli-20261008/CLI-evidence.json`. 80 synthetic sources; 20 review cases. A simulated variant has 1 semantic change/73 jointly valid classifications and 1 validity transition. No raw pairs were recorded, so the raw-change rate is null. Wrong response hash exits 2 without writing an imported file.
- Full-size registered input/synthetic-response check: `generated/audit-full-scale-20261008/scale-evidence.json`. 17,670 records, Task 3 universe 2,659 sources, 2,587 valid artificial classifications, 100 selected/revalidated cases; 40.64 seconds. All three named historical suspects exist in the universe. Initial scale attempt used the wrong `cases.jsonl` name and failed before creating output; verified `cases-v2.jsonl` was then used successfully.
- Checkpoint: `docs/validation/platform_m4_audit_cpu_20261008.json` with source/installed equality, evidence paths and hashes.

This is CPU orchestration and synthetic review evidence only. No GPU inference, actual human annotation, measurement accuracy certification or public release occurred. M4 actual condition logs/two-target integration/adjudication and M6 remain pending. The local M5 renderer was not changed; its earlier browser evidence remains scoped to that earlier UI run.


## M4 measurement traces/source delivery CPU — 2026-10-08

Added an opt-in generate observer in `measurement_trace.py` and additive classifier/pipeline flags. Released classifier wrapper prompt/parser files remain unchanged. Recorded input masks/nonpadding hashes/single-template parity, original/observed order, generation token/EOS/budget diagnostics, raw outputs, parameter dtype elements and available runtime metadata. Incomplete traces remain failed; export checks file/row/order/raw bindings. Missing old provenance is still unknown and measurements remain limited.

- First trace candidate: 121 installed tests passed in 39.303 seconds; wheel SHA-256 `c24bd17964d53ffc2e305a862d982c56393565f824f33939217a31ad8fecd731`.
- Boolean attention-mask support then added without accepting boolean token IDs. Final installed command `generated/contract-install-venv/Scripts/python.exe -X utf8 -m unittest discover -s tests -v`: 121 passed in 39.029 seconds, including 15 trace and 5 source-bundle tests. No tests skipped; existing Starlette/httpx deprecation warning observed.
- Final wheel: `generated/trace-final-wheel-20261008/koevd_eval-0.2.0-py3-none-any.whl`, 143,280 bytes, SHA-256 `3c5dc23be42a3ba1a82a2e596c868ba0ef7b41e3e46d2cdeadd2f71cc7996b2f`. Installed/source hashes agree for trace/classify/pipeline/results modules.
- Preparation identity stays `b3bb72a02a0b676afe67c8182345254d397f0da89be374963c9ff0fd8d23fbb8`; the independently registered 17,670-record input index stays `0d78a9b2ed412fa3507cf3d68db6b45d102ef0b8e24f0c65f3a10c3a987cd26d`.
- Candidate targets and measurement matrix: `configs/validation/platform-gpu-candidate-v1.json`. Public HF API metadata identified Qwen3-4B revision `1cfa9a7208912126459214e8b04321603b3df60c`; no weights downloaded locally. Same family scope is explicit.
- Source builder/verifier: `scripts/gpu_source_bundle.py`; bounded ZIP parsing, no extraction, wrong external SHA/file hash/path/case collision/credential-like source literal rejection.
- Checkpoint: `docs/validation/platform_m4_trace_cpu_20261008.json`. GPU-node request: `docs/GPU_PLATFORM_VALIDATION_PROMPT.md`.

CPU fake tensors/models establish glue and observations only, including actual wrapper methods using fake objects. No actual GPU inference, accuracy certificate, person annotation or public push/deployment occurred. Portable results-v1 still does not carry the full detailed order/mode trace condition; GPU-return acceptance and human adjudication remain pending. M4 and the overall Goal are incomplete. No renderer changes required a new visual claim in this step.

## M4 portable measurement conditions CPU checkpoint — 2026-10-08

Optional versioned conditions now preserve declared scheduling/dtype and compact completed-trace observations in portable results. Old evidence shapes remain accepted; missing conditions stay unknown. The common comparison engine applies the new condition reasons only to Task 3/4. Trace hashes, dtype proportions and response-dependent token/quality counts are not setting equality. Full sidecars remain necessary for per-response auditing. Uploaded observations never promote accuracy/authenticity/rank.

- Installed wheel: 147,610 bytes, SHA-256 `47cca8e3d8009dc6d1aafe2e8a145d1f165e6c2d9a121f3929ea4c51723ef0ed`.
- Final installed command `python -X utf8 -m unittest discover -s tests -v`: exit 0, 131 tests, 43.902 seconds. Ten condition tests cover old shapes, unknowns, manifest conflicts, resealed malformed/coverage/options, task-specific comparison reasons and original numerical outputs. Existing Starlette/httpx deprecation warning remains recorded.
- Initial targeted test failures came from the new fixture re-sealing an existing checksum, treating an absent package version as known, and comparing artifact-bound navigation IDs as metrics; these test errors were corrected before the final installed run. Runtime conditions were not weakened to pass them.
- Installed CLI export/validate for two synthetic frozen-response measurements, plus diagnostic report: five commands, all exit 0; 12 records per run, 24 cases total. Only Task 3/4 list input order/mode differences. Evidence: `generated/conditions-cli-20261008/commands.json`.
- Own headless Chrome UI: four checks, zero page/console errors or external requests, desktop comparison/Method and 390px expanded Method without horizontal overflow. Screenshots inspected. Evidence: `generated/conditions-ui-20261008/evidence.json`.
- Checkpoint: [platform_m4_conditions_cpu_20261008.json](validation/platform_m4_conditions_cpu_20261008.json). No GPU inference, actual human adjudication, external publication, container deployment or overall M4/Goal completion.

Next: automated GPU return acceptance, independent-review adjudication and M6 immutable storage/submission/metric-specific policies. The existing source ZIP stays an earlier immutable checkpoint; this update requires a fresh source bundle.

## M6 local submission storage CPU checkpoint — 2026-10-08

Implemented local SQLite original/revision/event/state/idempotency transactions, independently configured roles, explicit publication scope, review/publication axes, previous-public/current-head separation, withdrawal/restart/backup and an operator-only CLI. Permission review is separate from measurement accuracy. Principal construction and CLI actor assertions are not OAuth; no new public HTTP route or remote backend was added.

- Candidate wheel: 158,124 bytes; SHA-256 `e7a66fd69d3cae1debce56742f42fed1d4ba7ecc61be9c2568ce3a33b2733694`.
- Installed full suite attempt 2: `python -X utf8 -m unittest discover -s tests -v`, exit 0, 151 tests, 50.207 seconds. Twenty new submission tests include independent-process writes, rollback after killed child, stale/idempotent requests, immutable bytes/lineage, scope/role boundaries, projection tamper, withdrawal during calculation and snapshot restore. Source/installed storage and submission hashes match. Existing Starlette/httpx deprecation remains in the log.
- Attempt 1 had an incomplete log and no final receipt; its unified handle was missing and a scoped OS process query found no live test process. It was not counted as a pass. The original log remains at `generated/submissions-validation-20261008/installed-tests.log`; the completed log and receipt use attempt 2.
- Actual installed `koevd-submissions` console entry: 19 separate commands, every expected exit status matched, with fictional 12-record result and local subject assertions. Checked opt-in/review/candidate publication, private visibility, original download, withdrawal, retained originals, fresh-process reads and backup restore. Evidence: `generated/submissions-cli-20261008/evidence.json`.
- Full pinned index plus **artificial** 17,670 response/label records: create 3.234 seconds, common public-candidate summary 19.917 seconds, complete storage/summary/withdrawal/restart path 28.913 seconds. Task counts 2000/8000/2659/2659/2352; Task 3 2587 valid of 2659, original content/index digests preserved. One immutable artifact; six events/receipts. SQLite 3.53.1, rollback DELETE, integrity check ok, 9,629,696 database bytes. Evidence: `generated/submissions-scale-20261008/evidence.json`.
- No browser/UI code changed in this milestone. No claim of OAuth authentication, cloud persistence, human safety/rights adjudication, actual target inference, external publication, official rank or M6/Goal completion. [Checkpoint](validation/platform_m6_storage_cpu_20261008.json).

Next: metric-specific admission policy, authenticated submission/moderation HTTP/UI, remote durable persistence/recovery, GPU return acceptance/adjudication and actual two-target/container/deployment gates. Local disk persistence is a CPU subgate, not completion of hosted durability.

## M6 metric-specific admission CPU checkpoint — 2026-10-08

Added koevd-rank-admission-v1 with independent registry/receipt binding, candidate/ratified policy separation, metric-level denominator/complete-valid-output guards, cohort separation and exact ratio competition ties. Task 3 measurement limits, Task 4 strategy frequencies and model-dependent classifier-conditioned Task 3–5 rates remain rank-excluded. The shipped public summary uses candidate policy without reproduction evidence. Typed receipts and decision digests are trusted config contracts, not issuer authentication or actual GPU proof.

Noneditable wheel: generated/admission-wheel-20261008/koevd_eval-0.2.0-py3-none-any.whl, 162739 bytes, SHA-256 a6a298d40a44a3b7980a7d7f7e869d0d2f5d9254fe9e0c888ef7e145ef88c51f. Source/installed eligibility and submissions hashes matched. Installed unittest discover ran 167 tests in 55.254 seconds, exit 0, no skips; 16 new policy tests use explicitly synthetic approval/GPU receipt fixtures only. An initial sandbox attempt failed on Temp permissions; subsequent local source tests corrected a fixture error-status/measurement-status mismatch. Neither initial failure is counted as a pass.

Evidence: generated/admission-validation-20261008/installed-tests.log and installed-test-evidence.json; generated/admission-cli-20261008/evidence.json (19 separate installed console commands, expected statuses, immutable original, withdrawal/restart/backup); command 8 includes candidate admission and no eligible metrics. Full pinned input set plus synthetic responses: generated/admission-scale-20261008/evidence.json and admission.json, 17670 records / 47 metrics / 4.861 seconds; Task 3 union 2659, core 2000, overlap 784 preserved. All metrics excluded from official rank by missing actual generation evidence and unratified policy. This is CPU logic/CLI/scale validation, not GPU inference, actual policy approval, authenticated web UI, external publication, remote durability or deployment.

Next: independently accepted/stored operator generation receipts, authenticated HTTP/UI and current-publication leaderboard/withdrawal integration, remote persistence; M4 actual two-target GPU/adjudication and container/live candidate gates remain pending. The overall Goal remains active.

## M6 optional OAuth/submission HTTP/UI CPU checkpoint — 2026-10-08

Implemented fixed HF token/userinfo code+PKCE/state/browser binding; stable subject ownership; opaque hashed local cookies/TTL/logout; operator-only roles; double-CSRF/same-origin explicit submission copying; review/scope/actions/revision/private result/history; bounded private/public pages and one-active/three-waiter operation queue; public-candidate metric exclusions, raw-scope-only response import and original checksum preservation. App defaults remain anonymous and registration-disabled unless configured. Provider tokens never reach browser/disk/artifacts. No actual app credentials were present; actual HF authentication and iframe integration remain unverified.

Python core: 189 installed unittest cases in 61.453 seconds, exit 0, no skips, log/receipt generated/submission-web-validation-20261008-v3/. The final core hashes still equal that tested noneditable wheel. Final wheel generated/submission-web-wheel-20261008-v6/koevd_eval-0.2.0-py3-none-any.whl is 176406 bytes, SHA-256 7867d2ec053e67dd10f0f836432f9fa76b12687ea5ed6a9653ca19952ff03059. Later changes were browser raw-text import and CSS; final packaged asset hashes match source, recorded in docs/validation/platform_m6_web_cpu_20261008.json. No full-suite rerun is claimed for the final CSS-only wheel.

Actual headless Chrome + HTTP four SYNTHETIC identities: generated/submission-web-ui-20261008-v6/evidence.json, five flows/three screenshots, zero browser errors/unexpected external requests. Summary/raw scope, ACL, independent review/admin publication, withdrawal/private retention, published response raw-text reimport with original artifact SHA, two fictional model paired comparison, history download/mobile/logout passed. Final CSS/real HTTP restart: generated/submission-web-layout-20261008-v2/evidence.json, restored public/withdrawn projection, new login with stable subject preserved private original, desktop/390px numeric layout and no document overflow, zero errors/external requests. Screenshots were visually inspected. Models, identities and permission reviews are all fixtures, not inference/authentic HF/legal evidence.

Preserved failures: initial popup redirect interception did not stop its first remote navigation and produced HF invalid synthetic client, not actual login; moved synthetic provider fully to localhost. Immediate single-slot rejection conflicted with overlapping account refresh; added and tested bounded waiting. Script waited too early for a refreshed list and mistakenly waited for hidden controls to become visible; corrected waits. Browser parse/stringify changed 0.0 to 0 and failed existing canonical checksum; fixed raw text forwarding instead of changing scorer/hash definitions. Numeric/reason column wrapping was repaired through visual QA. Earlier partial/failure directories are not passes.

Current pending gates: real HF OAuth credentials/callback/account/embedding acceptance, two actual target GPU and human audit, independently accepted/stored generation receipts and policy-backed official ranking, remote persistent storage/restore, actual container/Space deployment. Goal stays active; no public push, production deployment or paid resources.

## Resource access observation — 2026-10-08

User-specified GPU_NODE: batch SSH hostname and read-only nvidia-smi queries succeeded. Eight B300 devices; devices 1–7 showed 0 MiB used/0% utilization at observation; device 0 showed 240844 MiB used. This is not a reservation or inference test. No remote files/jobs/chats were created. Local standard-cache HF token authenticated through official whoami-v2; KETI-NLP membership was listed, without claiming repository write permission. OAuth client ID/secret were unset. Node HF credentials remain independently unverified.

## B300 node setup/preflight checkpoint — 2026-10-08

Independently accepted source ZIP 0cbccf73f3a363dde8aae50df9cc7a1be5b514d03285fec478551c2cf8c1bdf2 (131 files). Fresh root [private-node-path] no previous work mutated. New Python3.11 core/measure/serve created. Measurement uses explicit inherited read-only previous site-packages and freshly installed KoEVD. Actual B300 UUID GPU-6e6eae12-0d8b-efc1-d7da-33c239882473 BF16 kernel/import probe passed; CUDA13/capability10.3/8,524,288-byte peak. This is not target inference. Installed Linux unittest ran189:188passed,1optional Node-helper skip,23.364s. Six source/installed modules matched. Evidence: generated/gpu-node-preflight-20261008/ and docs/validation/platform_m4_node_preflight_20261008.json.

Previous Python symlink /opt/conda/bin/python and base-model /root cache symlinks were unavailable on this node. Preserve old environments/caches; corrected prep detects incomplete snapshots and downloads only to the new root. Initial missing-files attempt preserved as artifact-receipt-incomplete-cache.json. Current bootstrap session75701/PID26332 child27711 and artifact prep session19798/PID27859 were confirmed live. Serving install, pinned artifact prep and both actual target-model validations remain incomplete. Never restart them on observation timeout alone. Four new controller scripts are outside the accepted v0.12 core bundle and have separate hashes in preflight evidence.

## Requested KETI-NLP development Space candidate — 2026-10-08

Prepared58 files/75,502,417bytes with real independent core/prefix indexes; no weights/actual target responses/auth. Native OAuth launcher, temporary-storage notice and unchanged CSP/shared analysis. Related33 source regression tests passed16.210s. Organization private Docker Space create was rejected HF402: cpu-basic Docker/Gradio hosting requires Team/Enterprise for KETI-NLP. Follow-up authenticated space_info404: no Space created, no upload/billing/paid hardware. Hosting choice pending. Evidence docs/validation/platform_space_creation_20261008.json; folder generated/private-space-deployment-20261008. Prior GPU bootstrap/artifact sessions75701/19798 remain live and are not restarted.

## Development launcher configuration acceptance — 2026-10-08

Corrected apps/spaces/README.md to build from the materialized allowlisted folder, replacing its contradictory repo-root command. New source tests: `PYTHONPATH=src generated/contract-install-venv/Scripts/python.exe -m unittest discover -s tests -p test_space_launch.py -v`: 3 passed, 0.064s, exit0. Tests use synthetic app credentials and mock the server entrypoint; they cover provider origin/operator paths/temporary storage, rejection of malformed/non-HF host and rejection of CLI-token-only/incomplete OAuth configuration. Initial default-sandbox invocation failed before test bodies with Windows temp-directory PermissionError; the approved local invocation passed. No actual provider login, container build, full-suite rerun or deployment is claimed. No Docker/Podman executable was found on local PATH. Existing GPU sessions75701/19798 were re-polled and the real remote processes remained live; serving-install log progressed and artifact prep remained on the pinned Qwen3-8B base. No target inference has started.

## Operator generation receipt / installed v0.14 checkpoint — 2026-10-08

Implemented bounded exact-artifact/index/declaration receipt validation; independent configured local administrator intake/revocation; immutable existing v1 audit-event storage/backup; exact published-revision active evidence; CPU-only marking and final publication/version recheck. No HTTP receipt intake and no automatic evidence-file verification or inference authentication. Policy stays candidate; classifiers remain measurement_limited and official ranks remain disabled. Source receipt tests8 passed3.473s including real CLI subprocesses/restore; related submissions/OAuth/admission58 passed22.048s.

Wheel178938bytes SHA256 a0e5d025b0f1f38be6c33517888f938eb3ab651b84f6e1b803c889d88dbf4090. Fresh noneditable package origins and9 source module hashes verified; full installed203 tests66.270s,exit0,skip0. Dependencies explicitly reuse prior contract-install-venv site-packages without modifying it. Initial .pth metadata caused pip to skip same-version install; its196-test/2-error old-package run is preserved as generation-receipt-installed-tests-20261008-v1.log, not a current pass. Corrected with ignore-installed/no-deps into the new prefix and checked origins before running. Actual pass log/receipt generated/generation-receipt-installed-tests-20261008-v2.log/.json. Formal evidence docs/validation/platform_m6_generation_receipts_cpu_20261008.json.

Fresh materialized Space folder generated/private-space-deployment-20261008-v14:59 manifest files/75,511,360bytes, all bytes/hash matched, no outputs/weights/credentials. Original candidate retained; no upload/Space/container/login. Bootstrap75701 terminal0 installs and dependency checks passed. Artifact19798 terminal1 id/repo_id KeyError archived; actual lock tests2 passed0.035s; new controller901ba795000bbaf533623f25547303963ec7659553d84e98c1cfe18d7399d5e9/session22031/PID29412 runs pinned Qwen3-4B prep after Qwen3-8B verification. Existing cache/env/source checkpoint preserved; no target inference started at latest observation.

Later observation: artifact22031 terminal0 and passed receipt, all7 release/target resources byte-verified. Final setup receipts copied into generated/gpu-node-progress-20261008-v14. Launched actual two-target prefix4 controller6d1e6d9989dcb1ab3b5cec8f81bff04d85b8b249c6b247f1b707248d4d139e03 on idle GPU2 UUID GPU-795fabdc-a541-1b0f-aa66-b7efab297b4b. Live session97489/controller29820/owned vLLM29826, Qwen3-8B prepare/index passed; server starting, no completed generation/measurement/export/comparison yet. Do not rerun into existing smoke directory. New source-only ZIP147files SHA2562f4d283128d98b61098b97984df890305e5d6fc740e62c4bc2babe51f84719a6 independently verified; node remains on original frozen131-file core.

Subsequent actual observation: first smoke97489 terminal1 before generation; vLLM0.13 NVML device selector parsed UUID mask as an integer and failed. Failure folder preserved. New controller0c71fa20f61745f8e01b94a8dbfd8df867015475520e6dc8a6550dbb85812e88 selects current NVML integer with PCI_BUS_ID and verifies actual torch CUDA UUID before starting server. Selector contract2 tests passed0.133s; no core/wheel numerical change or full-suite rerun required. New smoke-v2/session70736/controller30278/owned server30354 observed live, requested/observed GPU UUID match, prepare/index passed; vLLM log now reports0.13.0/Qwen3ForCausalLM and startup scheduling. No completed target generation yet. Exact downloaded status/setup artifacts and formal progress docs/validation/platform_m4_node_execution_20261008.json distinguish pass, terminal failure and current execution. Latest live handle70736 must be resumed, never duplicate the existing attempt.

## Actual two-target GPU smoke and unchanged-results app acceptance — v0.15, 2026-10-08

Later terminal observation supersedes the preceding live checkpoint: smoke-v2/session70736 exit1 during warmup, before generation. Bundled Triton PTXAS12.8 did not support B300 sm_103a. Preserved original output/logs. Controller f986f582a32baab914f5c0ef196afacff0cddb76a8b1a23be77b4fc8166e902f selects the existing CUDA13 compiler only for its child processes. Actual PTXAS13.0.88 SHA256 daba837a68265cae38c832d13399b61dab811891de9b8914defddef143b849f2 and requested/observed GPU2 UUID were checked. No system compiler/global environment changes.

Fresh smoke-v3/session31006 terminal0: Qwen3-8B revision b968826d9c46dd6066d109eabc6255188de91218 and Qwen3-4B revision 1cfa9a7208912126459214e8b04321603b3df60c. Each generated40 API-ok outputs (Task1/2/3/5:4/16/8/12), zero API failures; safety and strategy actual CUDA traced batch2; each portable results has48 records with Task4 reusing8 generation records. All13 prepare/index/generate/measure/export/diagnose/comparison stages passed exit0. Both owned target servers stopped. This is same-family custom prefix4 integration, not a full standard baseline, classifier accuracy/F1 reproduction, human adjudication or official rank.

Received generated/KoEVD_platform_smoke_20261008_v3.zip:1,276,163bytes/88 manifest files, SHA256 8e5ac01fe4f597c1edf662f6fd301793816c72cbdbf0cba1fbce9dd04e480bf5. scripts/accept_gpu_results_bundle.py uses one bounded immutable byte snapshot, strict archive paths/link/collision/size/manifest/hash checks, exactly13 required stage receipts, generation coverage/frozen hashes/API status and independently supplied operator index. It never runs archived code. Accepted generated/gpu-smoke-intake-20261008-v4 only after independent raw-run export exactly equaled both portable results. ZIP index cannot replace the outside v14 independently prepared prefix4 index. Receipt is consistency evidence, not cryptographic inference authentication or public consent.

New intake tests: fresh installed package Python `-m unittest discover -s tests -p test_gpu_results_intake.py -v`:7 passed5.337s/exit0. Tiny CPU fixtures cover external/internal tampering, invalid member/case/symlink/size boundaries, missing/failed stages, independent-input mismatch, API failures, mismatched raw response with no accepted receipt, fresh destination and source-path change after immutable snapshot. Do not add these7 to the earlier203-test full-suite claim; no package core changed.

Actual unchanged two results uploaded through scripts/validate_uploaded_results_ui.cjs to localhost:8772 and real headless Chrome154.0.8037.98. generated/gpu-smoke-space-ui-20261008/evidence.json passed3 grouped checks/5 screenshots, zero browser errors/external requests. Downloaded app profile and independent CLI profile identical JSON/fileSHA25614c7b851c5516ad5981f6bb49f363fb9006624b029611a9ae5aa161872fbd547; node comparison profile also exactly equal to local CLI JSON. Task denominators, paired comparison, classifier limitation, literal Korean sample, session isolation/download401/404/deletion and desktop/mobile overflow checked. Comparison/case/mobile screenshots visually inspected. Owned local server57176 stopped after test. This does not prove actual HF login, public posting or Docker build. Earlier synthetic harness failure (profile intentionally lacks raw cases) and corrected synthetic pass retained separately.

Formal evidence docs/validation/platform_m4_gpu_smoke_20261008.json. GPU2 observed0MiB/no owned jobs before launching fresh expanded-v3/session66554 using the same hashed controller/compiler and --sources96; prepare/index passed, Qwen3-8B generation started. Continue this handle; do not restart or count running work as accepted success. Full core, measurement variants, adjudication/independent operator attestation, ratified official ranks, remote persistent storage and live HF/container remain pending. KETI-NLP Docker Space is still402/404, with no Space/upload/billing. Goal remains active.

## Current-publication metric comparison — v0.16, 2026-10-08

Connected SubmissionService.public_leaderboard to current published originals, exact-revision active generation receipts, independently configured indexes, operator registry and typed policy. Default policy stays candidate/no official ranks. Recompute outside DB read lock, then recheck complete public membership, state version/revision/scope and operator context. Withdrawal/receipt revocation/new publication/policy change returns409. Limits50entries/128MiB originals return503 with no partial rank. Public projection excludes private originals/owners/review/receipt-file notes. New GET /api/public/leaderboard, local public-leaderboard CLI and operator protocol-registry configuration; widget includes metric/cohort selector, ratios/denominators/sources/valid coverage/reasons and no provisional ranks for excluded entries. Intervals explicitly disabled/resamples0.

New service8 CPU fixtures passed3.101s; related58 receipt/submission/OAuth/admission/launcher checks passed20.039s. Initial24-test invocation accidentally collected the imported fixture TestCase and attempted a different model as a revision; preserved failure, changed test import and same-target rerun fixture, never weakened the target invariant. Hypothetical ratified/actual_gpu positive cases are synthetic trusted objects, not real approval or inference evidence.

Fresh noneditable wheel v1:181329bytes/SHA25631cf46c2b6745ccfa3aed4075a37cb22db6ed25dbebab6beee7dcd976479cf0c. Ten installed/source module origins and bytes verified. Full installed221 tests76.187s,exit0,skip0; generated/public-leaderboard-installed-tests-20261008-v1.log/.json. Final asset-only v2 wheel:181394bytes/SHA256d919e00eb6f578bb2f552981df6a674fc93fd94ab6ba7dce36658c8d56bc79e0. All36 Python package files identical to full-tested v1; asset hashes/source/new-install match in generated/public-leaderboard-v2-package-receipt.json. No full-suite rerun claim for final UI wording/source-count changes.

Actual Chrome/local HTTP with four SYNTHETIC identities and fictional results: generated/public-leaderboard-ui-20261008-v2/evidence.json,7 grouped flows/6 screenshots, zero errors/external requests. Two separately reviewed fictional published models appear in one metric group with explicit numerators/denominators, unknown revisions and no-rank markers; withdrawal removes the old public entry and metric row. Existing private ACL/summary-only raw restriction/explicit response reimport/paired comparison/history/logout/390px layout also passed. Final desktop and mobile inspected. Owned fixture server33743 stopped. These tests are not actual HF login, real permission approval, GPU inference or external publication.

Independent installed CLI and current HTTP projection exact JSON equality: generated/public-leaderboard-cli-20261008-v2/evidence.json,2fictional published models/94excluded metric rows/0official boards. Initial wrong index ID was rejected missing_operator_index; original failure folder preserved, retried with ID/path read from operator catalog. No partial or stale returned values. Fresh private deployment candidate generated/private-space-deployment-20261008-v16:59manifest files/75,521,349bytes, all byte/hash checks pass. Real full17670/prefix4=48/prefix96=1150 independent input indexes, no baselines/roles/weights/outputs/credentials. No Space upload/container/login.

Formal M6 evidence docs/validation/platform_m6_public_leaderboard_cpu_20261008.json. Same actual expanded-v3/session66554 remains live: Qwen3-8B959 generations plus measure/export/report stages passed; Qwen3-4B generation ongoing after prepare/index, with Task1/2/3 output files96/384/191 and Task5 still pending at observation. Do not replace this job or count both models complete. Frozen measurement variants, actual operator review/policy decision preservation and activation, remote persistence, HF/container and overall release remain incomplete; Goal active.


## KETI-NLP destination confirmed; organization creation recheck — 2026-10-08

User confirmed KETI-NLP hosting. Rechecked cached CLI authentication and organization admin membership, then verified all59 v16 candidate files against the deployment manifest. Private Docker KETI-NLP/KoEVD-Explorer default CPU creation again returned HTTP402, with authenticated follow-up404. No repo, upload, public deployment, billing or hardware upgrade. Official Spaces overview still requires Team/Enterprise for organization Docker/Gradio creation; native hf_oauth metadata provisions separate web app credentials after Space creation. Hosting destination is resolved; plan activation remains external. Receipt: docs/validation/platform_space_org_recheck_20261008.json. Goal remains active.

Actual expanded-results local browser numeric acceptance completed: generated/gpu-expanded-space-ui-20261008/evidence.json, two actual models1150records each; exact independent CLI profile SHA f8b323734b5fa7a7bb15a2b101cc976565f8816eb6c54136797681ee35e5f7fd. Desktop comparison and mobile screenshots visually inspected; owned app session29744 stopped after validation. No live HF login/public posting. The independently accepted expanded-v3 baseline is terminal0/session66554. Frozen measurement audit session46297 remains live; remote controller39972 and traced-b1 child observed after repeat-b2/untraced-b2 completed. This is progress, not completed matrix or classifier accuracy evidence.

## Expanded integration and frozen-matrix return preparation — v0.17, 2026-10-08

Expanded-v3/session66554 completed all13 stages with exit0. Each actual target generated959 API-ok responses (Task1/2/3/5:96/384/191/288), zero API failures, and1150 portable records including Task4 reuse of191 Task3 responses. Independently accepted ZIP6a26dea365322ecd8078b7125eaf77b03867e9285c0ceda86080a7cc5b6375fc:12,842,931bytes/96manifest files. Outside v16 prefix96 operator index and exact raw-run reexport were required. App2300-record profile equals outside installed CLI and node JSON; actual browser3 grouped checks/5 screenshots, errors/external requests0. Formal evidence docs/validation/platform_m4_gpu_expanded_20261008.json. This remains a same-family custom integration prefix, not full standard evaluation, held-out F1 reproduction, representative model ranking or generation authentication.

Added scripts/measurement_matrix_bundle.py and tests/test_measurement_matrix_bundle.py. Return tool packs only terminal passed JSON/JSONL/log artifacts, rejects credential-like bytes and accepts one bounded immutable archive snapshot. Independent acceptance requires the outside accepted baseline/index, both targets/all7 variants, passed commands, byte-identical frozen generation files, exact raw export, trace bindings and independently recomputed comparisons. No archived code executes. Explicit subset intake records that it is not the full matrix. Requested precision and observed parameter storage are separate receipt fields; some FP32 parameters do not certify a full-FP32 request. Guide docs/MEASUREMENT_MATRIX_RETURN_GUIDE.md.

Scoped CPU checks20 passed22.672s/exit0/skips0 for initial return, old intake and controller. Final local return checks10 passed16.625s/exit0/skips0 including mixed-FP32 realization; this is a separate post-change scope, not30 distinct tests or a full-suite rerun. Final local toolSHA24dd6c3bd50b619700f8e43b36b3ffa216746e68efd42fbc09da8a09eb92e2d0. Node v1 packerSHAfea2a3be2a8ff450758ed396ea81b1647559c45e91ee870a7832ada75624112e is separately byte-verified with unchanged packing/envelope behavior; node CLI help exit0. The later local change annotates intake precision. No node core/environment/model files changed. Initial8 fixture setup errors due omitted checks directory are preserved, then fixed in the fixture without weakening production checks. Formal scope docs/validation/platform_m4_matrix_return_cpu_20261008.json.

Prepared private100-case review queues from each current8B/current4B/historical B200191-source universe. All three known suspect IDs are present and selected in each queue. Historical export preserved source bytes and unknown finish reasons. Guideline identity/version/fileSHA bound explicitly; queue preparation is not guideline reinterpretation, human adjudication or accuracy evidence. All judgments remain not_reviewed. Current8B flags:27 length_limit/20 repetition/24 classifier_disagreement; current4B12 length_limit/19 disagreement. Flags overlap and Task4 generation reuse must not be double counted. Historical unknown_finish_reason191 remains distinct from current recorded lengths. Artifacts generated/actual-response-audits-20261008-v1/.

Frozen matrix/session46297/controller39972 is still live, confirmed2026-10-08T09:04:53Z. Actual8B seven-condition safety semantic changes0; strategy changes repeat0/untraced0/batch1=5/batch4=3/reverse1/single5/FP32-request10, jointly valid191 and validity changes0. FP32-request safety storage still BF16=752,393,024/F32=6,389,760; strategy F32=8,234,382,336. Safety full-FP32 was not realized. Read-only adapter header confirms6,389,760F32 LoRA elements; causal origin of base BF16 and kernel arithmetic have not been established. Preserve classifier weights/wrappers and no accuracy claim. 4B reverse condition is running at latest handle observation; no full matrix return has been packed or accepted yet. Same running job must be continued, never duplicated on polling timeout. KETI-NLP destination is confirmed; organization plan activation, real HF OAuth/container, independent operator/policy review and remote durability remain external/uncompleted gates. Goal active.

## Actual matrix accepted and listing metadata corrected — v0.18, 2026-10-08

Session46297 terminal exit0; remote controller39972 stopped. Both targets/all14 classifier command receipts passed. Node packer v1 produced a fresh221-file/27,223,907-byte ZIP, independently hashed `695b2e25fb853726a8e37b63c2d38ff12b03484ccbc8b749f96fb56b0505b95b`; copied to generated/KoEVD_measurement_matrix_expanded_20261008_v1.zip. Final local intake source24dd6c3bd50b619700f8e43b36b3ffa216746e68efd42fbc09da8a09eb92e2d0 and installed v18 package accepted it against the previously accepted baseline and outside v16 prefix96 index. Exact raw reexports/frozen8 file hashes/trace and command conditions/recomputed comparisons required; no archived code executed. Receipt generated/measurement-matrix-intake-20261008-v1/intake-receipt.json SHA9cb6f2f46191d4d337c1a5becb1a3ee4ba06c267db7e27949b9cf826f1d5b76f. Formal actual evidence docs/validation/platform_m4_gpu_measurement_matrix_20261008.json supersedes earlier partial/live observations.

All191/191 safety and strategy pairs valid, validity changes0. Safety semantic/raw changes0 across all14; strategy8B0/0/5/3/1/5/10 and4B0/0/6/9/2/6/9 for repeat/untraced/b1/b4/reverse/single/FP32-request. The request still did not realize full-FP32 safety parameter storage; original wrappers/artifacts preserved and caveat included in intake. Stability is not accuracy or causal attribution. Private unblinded changed-case union11+15=26sources, SHA5e353516586f1f4d53ce3bc6e40151f62d8620d0053c5627ed75f46c4923ffd3 in generated/measurement-matrix-changed-cases-20261008-v2. Initial v1 Windows cp949 read failed before artifact writes; preserved and corrected with explicit UTF-8. No human judgment added, raw baseline overwritten, public permission or official rank enabled.

Corrected public_list/public_page metadata: candidate policy remainsfalse/policy_not_ratified; hypothetical ratified policy usesnull/not_evaluated_in_listing because listing does not calculate metric admission. Exact summary/board remains authoritative. New source9 CPU service checks passed3.662s. No actual ratification/receipt/publication performed. Fresh wheel182,069bytes SHAa0a1a7aeacc21869097597e1e0de70eff2a7885d989d6a76771038db8a53b103; installed in new generated/matrix-return-install-20261008-v18 with explicitly readonly inherited dependencies. Installed/source29 eval Python files matched; full236 tests92.422s/exit0/skips0. Initial sandbox pip build-tracker PermissionError preserved; approved local build succeeded without dependency downloads or changing old envs. Log generated/matrix-return-installed-tests-20261008-v18.log SHAfe5b44ca4d8d23fe4ba4798e7edacb2051dc5b795d7f0b6e7efecff5aa11b2c5.

Fresh candidate generated/private-space-deployment-20261008-v18:59files/75,521,784bytes, manifest/all paths and changed source/installed/candidate module bytes matched. Independent full/prefix4/prefix96 indexes, empty roles/baselines and no actual outputs/weights/credentials. UI assets unchanged; prior v16 browser evidence is kept at its own scope and no v18 browser pass claimed. Formal CPU/candidate evidence docs/validation/platform_m6_listing_metadata_cpu_20261008.json. No live GPU controller remains; next independent implementation is policy-decision preservation/configuration and remote durability/restore, with full-standard baseline prepared separately. Actual operator/human review, KETI-NLP plan/HF login/container and overall RC remain incomplete; Goal active.

## Operator policy preservation and explicit configuration — v0.19, 2026-10-08

Added policy_decisions.py and koevd-policy archive/inspect/history. Independent operator roles and local admin/actor assertion required for CLI recording, bounded exact JSON/current admission version/UTC parent chronology, canonical content digest and immutable addressed files. Fresh file fsync plus atomic hard-link publication, existing content recheck/idempotency,256decision history cap, duplicate/size/symlink/digest/parent validation. No mtime/latest selection. Hash/local actor declaration is not a signature or human-approval authentication. Ratify/revoke selection uses operator-pinned archive/head at startup; incomplete/corrupt config fails. Default candidate unchanged. No HTTP policy intake or upload-driven policy/roles. Development launcher clears activation variables and fixes no-rank; actual policy ratification was not performed. Guide docs/OPERATOR_POLICY_GUIDE.md.

New source9 CPU checks3.922s passed with real module CLI subprocesses, pinned-policy submission CLI metric recomputation then revocation, and mocked localhost server startup. All decisions/GPU-scope receipts/OAuth credentials are SYNTHETIC, not actual approval/inference/login evidence. Initial new fixture referenced nonexistent ProtocolRegistry.root:1error; corrected to its actual independent fixture directory without weakening production checks. Source log SHAae7c94663f71fa00e955ef3470975cd147fe87416cf2bc70370f7b2a44086129.

Fresh wheel185,425bytes SHAe69bcc0d9c1ceeec38786b0571c55ee364de96f3ae02977fc628ceac5b33d76f. New noneditable generated/policy-decisions-install-20261008-v19 explicitly reuses readonly prior dependencies. All37 package Python files match current source; installed policy console help exit0. Full245 CPU checks97.640s/exit0/skips0; log SHA3e5a8ddf1230b620e1ae54c107f9da6016af494092977bbfff9c3f8ed806df44. Previous wheels/envs untouched. No UI assets changed, no new browser pass claimed.

Copied one module only to fresh GPU_NODE incoming/policy_archive_cpu_v19, byteSHA4bffb5288e4b0364bc3d6fd9cba1545254f2b4a37532819f5687a878591ea4be. Loaded as standalone current module over unchanged frozen core dependencies. Four grouped Linux CPU checks on fresh /tmp passed actual POSIX hard-link/directory fsync/concurrent same record, original-preserving selected chain revocation, actual symlink rejection and parent-tamper failure. Saved generated/policy-decisions-linux-cpu-20261008-v19.json. Not new full-package Linux suite, GPU inference or remote/cloud durability. Existing core/models/environment were not modified.

Fresh candidate generated/private-space-deployment-20261008-v19:60files/75,531,813bytes, full manifest/file set and changed module/launcher bytes checked; independent indexes, empty roles/baselines, no actual policy decisions/outputs/weights/credentials. Formal docs/validation/platform_m6_policy_decisions_cpu_20261008.json joins scoped source/full-installed/Linux/candidate proofs. No actual approval, receipt acceptance, publication, billing or Space/container/login. Submission SQLite backup and policy archive remain separate; next implementation must preserve/verify both in remote snapshot and fresh restore. Overall Goal active and remote durability/actual operator/HF gates remain incomplete.


## v0.20 — Private combined snapshot/restore and HF Bucket transport candidate

Added koevd_eval.snapshots, koevd-snapshot console and [storage] optional SDK>=1.31. Outside catalog/registry + independently pinned ZIP byte digest are required; immutable original/revision/events/replay, DB/index bindings and selected policy chain are validated before a fresh offline restore. Roles/tokens/gold/server activation are not restored. Point-in-time receipt requires later withdrawal reconciliation. Existing DB-only backup remains available.

New13 source CPU tests passed (6.549s) after initial sandbox fixture-temp denial and Windows read-only fsync failure; these failed runs are preserved in tool/log history. Final review added policy-directory fsync, then rebuilt and installed a fresh final wheel. Full installed258 CPU tests102.750s/exit0/failures0/errors0/skips0; log generated/snapshots-installed-tests-20261008-v20-final.log SHA7fc4ab5c8faef28ed6ea5da6dff27984bdd26b356c42d400e3380d645838fd36. All38 package Python files match source. Wheel192,640bytes SHAca2613239cd43bb29f7659e4fdfdcb0ea13b09fc4b29fc0bc3bfac48778fc4ea; previous intermediate wheels/installations/logs retained. Installed koevd-snapshot --help exit0.

Actual existing two-target private roundtrip commands (CPU, no inference/moderation/publication):

```powershell
generated/snapshots-install-20261008-v20/Scripts/python.exe scripts/validate_snapshot_roundtrip.py --index generated/private-space-deployment-20261008-v19/operator-data/prefix-96-index.json --result generated/gpu-expanded-intake-20261008-v1/expanded-v3/Qwen3-8B/results.json --result generated/gpu-expanded-intake-20261008-v1/expanded-v3/Qwen3-4B/results.json --output-dir generated/actual-snapshot-roundtrip-20261008-v20
generated/snapshots-install-20261008-v20-final/Scripts/python.exe scripts/validate_snapshot_roundtrip.py --index generated/private-space-deployment-20261008-v19/operator-data/prefix-96-index.json --result generated/gpu-expanded-intake-20261008-v1/expanded-v3/Qwen3-8B/results.json --result generated/gpu-expanded-intake-20261008-v1/expanded-v3/Qwen3-4B/results.json --snapshot generated/actual-snapshot-roundtrip-20261008-v20/private-snapshot.zip --snapshot-sha256 878eedaf26ba617d96728c9636cc76ca409297155cbfe0cae0b96c95140a949d --output-dir generated/actual-snapshot-roundtrip-20261008-v20-final
```

Two1150-record originals restored exactly. ZIP4,678,382bytes SHA878eedaf26ba617d96728c9636cc76ca409297155cbfe0cae0b96c95140a949d. Same pinned snapshot/index/script and final wheel were transferred privately to approved GPU_NODE incoming/snapshot_cpu_v20. New env-final installed via existing core pip without dependencies or old environment mutations; roundtrip-final passed with outside expanded-v3 originals. Final package module SHA5fea77ad8135531c4b22ff1722c02d99dff14b24f559631c444fc7db4c1e59fd. Four additional Linux grouped checks: selected SYNTHETIC policy chain + empty DB restore; actual private POSIX permissions/hardlink/directory fsync; actual symlink rejection; parent tamper rejection before publication. No actual policy approval or full Linux suite implied. Local copies of node evidence are generated/snapshots-node-20261008-v20/evidence.json and policy-posix-final-evidence.json. Owned SSH/CPU commands terminal0; no GPU/model jobs launched.

HF SDK1.31.0 bucket_info/batch_bucket_files/download_bucket_files/list_bucket_tree signatures and official Bucket/API docs inspected. Existing-private single-object put/readback/fetch tested with fake provider only; mutable/nontransactional/visibility-change/metadata download bounds documented. No bucket creation, cloud upload, billing, HF login/Space/container pass. Automatic backup/RPO and operational reconciliation remain pending.

Candidate generated/private-space-deployment-20261008-v20:61files/75,555,401bytes; exact manifest file set/hashes and all package source/pyproject/launcher bytes match, independent full17670/prefix4=48/prefix96=1150 indexes and empty roles/baselines. No actual snapshots/results/policies/weights/credentials bundled. No UI asset change, no new browser pass. Formal evidence docs/validation/platform_m6_snapshots_cpu_20261008.json joins final installed/Windows/Linux/candidate scopes. Overall Goal active, full RC incomplete.


## v0.21 — Restoration quarantine and independent checkpoint comparison

Added recovery.py/koevd-recovery status/checkpoint/compare/reconcile. Verified snapshot restore appends an immutable recovery guard in existing meta schema; originals/events/replay data stay unchanged. Public list/page/result/summary/leaderboard and domain changes/request replays reject with503 until independently configured admin checkpoint reconciliation. Private owner/operator original/history reads retain existing authorization. New restore epoch always requires a new reconciliation; selected policy digest must match for public access. No HTTP reconciliation endpoint, no latest-state/human-approval authentication.

New10 source tests7.509s passed after matching TestClient follow_redirects=False to existing synthetic OAuth fixture; initial1-failure log preserved. New noneditable generated/recovery-install-20261008-v21 full268 CPU tests110.000s/exit0/failures0/errors0/skips0.39 source/installed Python files match. Installed console help exit0. Wheel198,049bytes SHAa984c2b68453dd5214bdee452a6c731edd1b46cbc26e5da3aa806a40d4df8f11. Full log generated/recovery-installed-tests-20261008-v21.log SHAa4ebefedb93c257afc074faac53bf35af85a740fac9651cf83a4fc8f1166b4d7. Domain/actual HTTP tests cover stale published backup versus later withdrawal, checkpoint mismatch, blocked mutations/public reads, private reads, admin/digest/limits/tamper, policy mismatch, repeated restore, actual CLI and nonexistent HTTP release route. Fixtures are SYNTHETIC approval/reconciliation/OAuth, never human or actual HF evidence.

Actual-existing two-model CPU validation command:

```powershell
generated/recovery-install-20261008-v21/Scripts/python.exe scripts/validate_snapshot_roundtrip.py --index generated/private-space-deployment-20261008-v19/operator-data/prefix-96-index.json --result generated/gpu-expanded-intake-20261008-v1/expanded-v3/Qwen3-8B/results.json --result generated/gpu-expanded-intake-20261008-v1/expanded-v3/Qwen3-4B/results.json --snapshot generated/actual-snapshot-roundtrip-20261008-v20/private-snapshot.zip --snapshot-sha256 878eedaf26ba617d96728c9636cc76ca409297155cbfe0cae0b96c95140a949d --output-dir generated/actual-recovery-roundtrip-20261008-v21
```

Same immutable original ZIP, independently pinned input and outside expanded-v3 originals were used in fresh approved GPU_NODE incoming/recovery_cpu_v21/env. New wheel installed without dependencies/old environment mutation; CPU roundtrip terminal0. Existing2300records exact; restored public lookup503. Fresh process3 grouped checks: all5 domain public routes503; both actual originals private-readable and original request replays blocked; no reconciliation inserted. Module1fc2a85d10884538ed13e718be176ad8ffdf01dbc84e3644bc52699e01f8320d and script6dbe363f77a83faebf4b1c76b92342866303f723cc2006b0356256eab18eb8f1 matched current source. Node evidence copied to generated/recovery-node-20261008-v21/evidence.json/guard-evidence.json. Original GPU models/envs/jobs untouched, no new inference or actual operator approval.

Materialized generated/private-space-deployment-20261008-v21:62files/75,574,042bytes, exact manifest/file set/hash and package-source/pyproject bytes; independent full17670/prefix4=48/prefix96=1150 indexes, empty roles/baselines. No actual snapshots/results/reconciliation/policy/weights/credentials included. UI assets unchanged, no new browser pass claimed. Formal docs/validation/platform_m6_recovery_cpu_20261008.json links all scoped evidence. Manual comparison is not latest-state proof or automatic maintenance/RPO; automatic backup/failure semantics and actual private HF storage/recovery remain pending. Asked for existing private HF Bucket only; no creation/upload/billing/deployment. Overall Goal active.


## v0.22 — Periodic same-cut backups and honest uncopied-change status

Added backups.py/koevd-backup run/status, test_backups.py and validate_backup_worker.py. Checkpoint is derived from the verified ZIP's FROZEN DB and its manifest timestamp, not a later live DB. Target-specific last success, final completion marker, preserved partials/failures/previous copies, live logical comparison/event deltas/clock-regression handling and explicit existing-private remote opt-in are implemented. Single worker lock; no stale-lock stealing or automatic GC/service installation. Default retained bound8GiB/max1000 attempts, separate conservative allocation reserve. Periodic copying never claims synchronous remote commit or guaranteed RPO; status retains null RPO/false latest-state authentication. New guide docs/BACKUP_WORKER_GUIDE.md.

New10 source CPU tests8.474s/exit0, log generated/backups-source-tests-20261008-v22.log SHAdca0244dd7011affd9dbce48d360831cabcf0b81ee59c9704b3d0c2fe7b19f7b. Covers snapshot-then-live mutation, checkpoint failure, partial preservation, remote target/readback, provider failure, loop/retry, lock/quota, checkpoint/receipt tamper, backwards clock, restore gate and real module CLI. HF transport is FAKE provider evidence, not actual cloud storage/login.

Fresh wheel203,753bytes SHA4ed38631f61a9df8407a43249de0c746bf01763242abd5038304fe6a013868b4. Installed into new generated/backups-install-20261008-v22 without dependencies/editable source. All40 package Python bytes equal source. Full278 CPU tests120.094s/exit0/failures0/errors0/skips0; log generated/backups-installed-tests-20261008-v22.log SHAaad31a71e23d753656abe38036c90945188df16af3236473cbff67a2d5f951ef. Installed console help exit0. Previous envs/wheels preserved.

Actual-existing two-model CPU acceptance (not inference/human review/operator release):

```powershell
generated/backups-install-20261008-v22/Scripts/python.exe scripts/validate_backup_worker.py --index generated/private-space-deployment-20261008-v19/operator-data/prefix-96-index.json --result generated/gpu-expanded-intake-20261008-v1/expanded-v3/Qwen3-8B/results.json --result generated/gpu-expanded-intake-20261008-v1/expanded-v3/Qwen3-4B/results.json --output-dir generated/actual-backup-worker-20261008-v22
```

Two existing1150-record originals exact in fresh private drafts. Two real1-second periodic local cycles: first copy followed by declared CPU draft withdrawal -> pending/event1; second copy -> covered/event0. Actual configured quota65536 -> third attempt backup_capacity, previous complete pair retained. Second private draft withdrawal after failure -> last success2/pending/event1. Restored second pair has exact originals but current logical state misses this last validation withdrawal; negative reconciliation rejects recovery_mismatch and public access still recovery_required. These declared workflow changes are not actual submitter consent withdrawals or human content review. New actual-results recovery release was never inserted.

Approved GPU_NODE fresh incoming/backup_cpu_v22/env installed same wheel after outside wheel/index/original byte checks. Same actual2300-record CPU scenario terminal0. Fresh Linux process3 grouped checks confirm current lag/restore gate, actual14 POSIX private entries,40 installed Python files matching wheel; installed console help0. Module SHA31d12976c4734ec055f8962a87c9b1f0edb8a6f84f15a7f9ba2a896fe2622774 and script SHA7e2762544b63fb6a364fb4b2ce3a7fc3f2fce5d0212bc87d8d254a3069e122ca equal local. Node receipts copied to generated/backups-node-20261008-v22/evidence.json and reopen-evidence.json. No full Linux suite, new GPU/model jobs or old environment changes.

Materialized generated/private-space-deployment-20261008-v22:63files/75,592,401bytes. Exact manifest/file set/hash and all source/pyproject/launcher checked; independently validated full17670/prefix4=48/prefix96=1150 with empty roles/baselines. Initial candidate verification harness incorrectly expected index records field; fixed to catalog expected_records and passed without product changes. Tool failure retained. Actual backups/checkpoints/results/policies/weights/credentials excluded. Worker is not automatically launched; default server still ephemeral candidate/no-rank. UI assets unchanged; no new browser/container/HF login pass. Formal docs/validation/platform_m6_backups_cpu_20261008.json links scopes and remaining requirements.

Sessions37462/97200/76302/84881 and SSH checks terminal0; don't restart completed GPU66554/46297. Current KETI-NLP Space remains uncreated under previously observed402 plan requirement; no unchanged retry, upload, subscription, bucket creation or actual cloud writes. Existing-private bucket question remains unanswered. Next independent work is separately pinned full-standard input/config/execution preparation. Prefix96, fake cloud, measurement flags or prepared reviews are not full baseline/accuracy/operator acceptance. Overall Goal active and full RC incomplete.


## v0.23 — Full-standard execution/preflight and bounded replay intake; actual GPU job live

Previous v0.22 was progress (backup worker/actual existing-result Windows/Linux acceptance and fresh278-test installation/candidate). Rechecked HEADcfb79006a6471ecd3ce89c0bad8a98e85c8a75fb, dirty changes and no repository AGENTS. Changed scripts only, not src package or app/UI: validate_gpu_pipeline --full-core mutually exclusive with prefixes, explicit source/core/measure/dataset paths and pre-measure occupancy check; check_gpu_input_budget counts actual IDs; full return intake requires outside registry and matching full flag/scope/protocol/counts; build_gpu_results_bundle preserves bounded raw replay and logs, excludes outside gold index/duplicate HTML/weights/credentials. Docs/FULL_STANDARD_RUN_GUIDE.md.

Final related22 CPU tests13.109s/exit0/failures0/errors0/skips0 on unchanged noneditable v22 core. Log generated/full-standard-return-tests-20261008-v23.log SHA9a24620caf682fb5017efba3f0aa9b4e204191613dbcf315f8f410a3951f23ae.9 new checks include full/prefix boundaries and real prepare CLI, mapping keys vs token IDs/invalid shapes, registered full intake/scope mutations and independent re-export, minimal replay allowlist/fresh paths/size/missing measurement. Synthetic tokenizer/targets/registry are NOT GPU/accuracy evidence. Existing v22 package wheel203753/SHA4ed38631f61a9df8407a43249de0c746bf01763242abd5038304fe6a013868b4 and prior full278 suite/candidate63 retained; no claim of a new full current suite or fresh UI/container pass.

B300 fresh incoming/full_standard_v23: transferred source-only ZIP and v22 wheel; new core/measure installs each40 Python files equal source, old envs/models unchanged. Current source ZIP v2 SHAbea8f1f0ca8f4fa5de17bf5b5cae8caec67e0d5493b553a3c202339c5321b39a contains184 sources; current GPU controller SHA519669d426d54c55efa3c77482b1fef32c6c6d2ecd5c50247a15953227798907. Rehashed97 unique cached artifact files against pinned metadata, including both targets and measurement bases/adapters/data. No downloads or weights mutation.

Initial preflight78718 terminal1: ProtocolRegistry correctly rejected HF snapshot symlinks pointing outside dataset root. Preserved preflight-status/independent-full-index.log and made actual copies of9 pinned files, checking hashes without weakening the rule. v2 preflight85237 terminal1 after full index passed: new venv inherited only one .pth directory, not the referenced measurement dependency directory. Corrected ONLY the new environment with explicit read-only site-package paths, preserving the first pth bytes. Actual transformers5.8.1/torch2.9.1+cu130 now import from existing dependency paths; current package remains inside new environment. CPU check2770 initially produced maxima2: discovered BatchEncoding len counted two keys. Preserved raw status/log and preflight-v3-invalid-token-count.json, never started GPU using that result. Added strict token_ids helper and explicit return_dict. Corrected CPU preflight51914 terminal0: actual maxima231/1592/192/1797, all over-budget0 for context16384/output1024. Config/vocabulary bytes of both targets equal. Only preflight-v4 is final passing budget evidence.

Full canonical index content SHA0d78a9b2ed412fa3507cf3d68db6b45d102ef0b8e24f0c65f3a10c3a987cd26d equals independent Windows standard set; Linux file byte SHA771f066331e901c06ba960707add109143d75df6b1f603cf4da3439197c6b1b5. Task counts2000/8000/2659/2659/2352; primary2000/tool784/union2659/overlap125;15011 generation requests and17670 records per target. HF cache revision checks and current index structure/contents agree, but this is CPU preparation, not a completed baseline.

Actual full execution launched once with the preflight-v4 gate, explicit idle GPU2 UUIDGPU-795fabdc-a541-1b0f-aa66-b7efab297b4b and CUDA13 PTXAS SHA daba837a68265cae38c832d13399b61dab811891de9b8914defddef143b849f2:

```bash
incoming/full_standard_v23/envs/core/bin/python incoming/full_standard_v23/source-v2/scripts/validate_gpu_pipeline.py --root [private-node-path] --gpu-uuid GPU-795fabdc-a541-1b0f-aa66-b7efab297b4b --full-core --attempt v1 --port 18080 --ptxas-path /usr/local/cuda-13.0/bin/ptxas --source-root [private-node-path] --core-bin [private-node-path] --measure-bin [private-node-path] --dataset-dir [private-node-path]
```

Exec90124 remains live; actual controller56870/argv checked by ps, owned8B server56951 healthy and generation API200 log/progress observed. Latest saved live observation at epoch1791457990 shows8B Task1 final2000/API non-ok0; Task2 generating,4B not started. Final prediction files are written after task completion, so absence is not reported as failure or safe0. No full pass/measurement/export/comparison/independent return acceptance yet. Source used is frozen; new budget/pack/intake helpers were copied separately with explicit SHAs and do not alter the running controller. Current pack SHA b6380f7c8dca9af3b6e6940bebe8ceed3b89946b0201aac44b0bcfb81b4cec4f; intake SHA7ac94c5bba6ac74e64633fbbf2a0b359868ef43535e89cd03a3fac2138d69b03. Their22-test CPU acceptance is not an actual full-result ZIP acceptance.

Node small receipts copied to generated/full-standard-node-20261008-v23. Formal docs/validation/platform_m4_full_standard_preflight_20261008.json separates initial failures/invalid counts, corrected CPU preflight, partial live observation and remaining gates. Next iteration must poll SAME90124 and verify actual PID/log, never restart on observation timeout. After terminal pass/owned-server cleanup, build minimal replay, use outside canonical index/registry and external ZIP SHA to independently re-export, rebuild shared reports and verify app/CLI. Existing prefix GPU66554/46297 stay terminal and untouched. No new HF creation retry, bucket/cloud write, billing, actual human/operator acceptance or public output. HF402/hosted/cloud gates remain; overall Goal active and full RC incomplete.


## 2026-10-08 — v0.24 native Linux web runtime and UID1000 private result acceptance

New source: scripts/validate_space_native_runtime.py, tests/test_space_native_runtime.py. No package/UI/Docker/lock source change. Guard5 CPU tests0.062s,exit0/failures0/errors0/skips0; log SHA05de8fc59aca26099c99541e74b73fc58aeea9728f25600a579e2fc251735915. Previous whole-package278 and v23 related22 evidence retain their original scope; no current entire-suite pass claimed.

Immutable v22 allowlist context ZIP64members/7013002bytes/SHAa7df9b8672cc6bfded96a37793336a61f3b9cafd83c2b258ffa7b6d03cd769c5 transferred privately. New node Python3.12.3 web environment installed exact14 lock versions and package with pip check exit0. Original source build added build/egg-info, correctly failing strict context inventory; second verifier incorrectly resolved venv symlink to base Python. Both failures preserved, then fresh immutable context/lexical executable used. Final helper SHAb038d0d1e1d256243e2439eb71bb3230117e7047a033efad617abd981cf7b9a0. Candidate63 files/75592401bytes and installed42 koevd_eval files match exactly.

Actual prefix96 originals each1150records, outside byte hashes c99ce411f96752b888d733cb470c99dead8a6f06633ade0b355464e052a35eaf / c1b1a67b2d95e5da29f5ee65d4c955b8849adb07c79e2879377845f7ea8ac639. Native HTTP ready/no-rank/signed-out/origin/auth, real private upload/session isolation, three report downloads, independent CLI exact JSON equality, deletion and owned-server stop passed as7groups. UID0 runtime-v4 exit0; separate UID/GID1000 /tmp run exit0,22.741s. UID1000 initially could not traverse original GPU NFS root0700; failure preserved, permissions unchanged, fresh own /tmp used. Actual UID/output owner1000 and work/output modes0700. Same three profile hashes, including comparisonf8b323734b5fa7a7bb15a2b101cc976565f8816eb6c54136797681ee35e5f7fd as prior browser evidence. Synthetic OAuth app settings only, no actual HF/provider network login or human/publication receipt. No system account/service/container created.

Windows Docker/Podman/installed WSL absent; B300 docker/podman/nerdctl absent. Actual unshare --user --map-root-user sh -c 'id -u' returned1/Operation not permitted despite namespace sysctl counters. Native UID1000 is separate from actual Docker image/hosted OAuth/iframe/cloud recovery. No kernel/daemon/paid-service workaround or unchanged HF402 retry.

Small metadata/failed logs in generated/native-space-node-20261008-v24; actual originals/reports stay private on node. Formal docs/validation/platform_m5_native_runtime_20261008.json and docs/SPACES_RUNTIME_VALIDATION.md. Same GPU90124/PID56870 remains live; saved observed final task1/2 rows2000/8000 and Task3 checkpoint701/2659/API-ok701/failed0; task3/5 final files absent mean not finalized. Full two-target/measurement/export/report/return intake remains pending. Next iteration resumes same handle and actual argv/status/log, not a new run. Overall Goal active, cloud/plan/operator/public gates remain incomplete.


## 2026-10-08 — v0.25 full-input CPU fixture comparison capacity and HTTP agreement

Previous turn v24 was progress: exact Linux web dependencies and native UID1000 actual prefix96 HTTP/CLI acceptance. This turn confirmed the same90124/PID56870/argv live and made a distinct full-input CPU capacity check; no speculative report-limit/format change. Two explicitly SYNTHETIC documents use outside full index0d78a9b2ed412fa3507cf3d68db6b45d102ef0b8e24f0c65f3a10c3a987cd26d,17670records each. SHA45e1f3f670bc4ca2340dc3f1b85c93bf45a8e5397d86145abb5e2cf6efc3dfde / 614894ea7c13c17bfff380f50643ddfecf8158fa134304abbd62c1e0692546a8; transfer ZIP1935291bytes/SHAa03346c52f79148902954860025b32db86edff5be0e70fb2d7884cec9f0d86fa. Fixture-only/no inference/human labels/accuracy; generated private artifacts excluded from source bundles.

Node isolated incoming/full_capacity_v25: independent CLI full comparison100resamples/seed1729 terminal0,68.318s,303534808report bytes versus536870912limit. Actual native HTTP two uploads/comparison/profile+HTML downloads/session isolation/deletion/owned-server cleanup terminal0,163.071s. Profile byte equals CLI SHA f7c70909003e2a58d6c527e3bf59cbef9e5f9d6d504cea112d75a2eb05605f99. HTML149176208/cases127329308/profile25786418/CSV1238837/MD4037bytes. Cases35340 and eachTask2000/8000/2659/2659/2352, matched-identical input counts verified. This is CPU HTTP/capacity, not actual full model inference, visual QA, actual HF login, container/cloud durability or universal-length guarantee.

Validator-only --comparison-only added. Single result rejected before output creation. Related6 context/CLI guards0.094s/exit0/failures0/errors0/skips0; log SHAba75bbab1b973a557b12380c46fe1d379a299450c07998d51e3fbf3461f51f7c. Helper SHAcf0ed46829215c286bb0ee24b8f1ad7a31d2bc5c954e99ec790b2a6be7640b2b. No package/UI/limits/candidate change and no whole current suite repeated. Node small evidence/logs in generated/full-comparison-capacity-20261008-v25; formal docs/validation/platform_m5_full_comparison_capacity_20261008.json.

Same actual full GPU90124/PID56870 alive/argv/status checked. Saved8B Task3 checkpoint1151/2659/API-ok1151/failed0; Task1/2 final2000/8000 unchanged,4B not started. No restart, no full pass or final intake claimed. Next iteration waits on SAME handle/PID and after terminal completion checks actual raw replay outside registry/index, full reports/app capacities/values/UI. HF402/cloud/operator/public conditions unchanged; no paid/subscription/push/cloud object/user output created; Goal active and RC incomplete.


## 2026-10-08 — Same full GPU90124 verified wait after v0.25

Same actual PID56870/argv/state confirmed live; task3 checkpoints1318→1378→1440→1489/2659/API-ok1489/failed0. No controller restart/new GPU jobs/code/install or redundant tests. Source/candidate/package remain unchanged; only observations appended to docs after the historical v25 source checkpoint. Small current-state evidence in generated/full-gpu-verified-wait-20261008-v26. Actual two-model full completion/independent intake/report/app and external gates remain pending. Resume SAME90124 and actual PID/argv/log; an observation timeout is not termination. Goal active.


2026-10-08 follow-up verified wait: same90124/PID56870/argv confirmed live; checkpoints1519→1551→1599→1649/2659/API-ok1649/final failed0. Evidence generated/full-gpu-verified-wait-20261008-v27/live-wait-20261008-v27-final.json. No new code/install/tests/jobs/restart, full completion not claimed. Continue same handle/PID/log and terminal full intake. Goal active.


## 2026-10-08 — v0.26 full-input two-fixture browser and visual QA

v0.26에서 전체 입력 두 CPU fixture의149176208bytes HTML을 실제 Chromium에서 검증했다. 각17670/전체35340사례,12탭, 두 실행 선택, core2000/overlap784/framing784 대응 필터와 valid/invalid 분리, pagination/search/metadata drilldown 및 모바일 배치가 통과했다. 로딩2.164초, console/network 오류0이며 화면8장을 저장하고 주요4장을 시각 검토했다. Task4의 descriptive-only/no-rank도 확인했다. 검사기에 --expected-runs 2 경로를 추가했고 기본1-run 경로는 유지했다. Package/UI/상한/v22 후보는 변경하지 않았다. [근거](validation/platform_m5_full_comparison_browser_20261008.json). 같은 GPU90124/PID56870은 실제 live, 관측8B Task3 1910/2659/API-ok1910/최종 실패0이며4B·full 인수는 미완료다. CPU 화면 검사를 실제 full inference/HF hosting으로 승격하지 않는다.

HTML byte SHA67bd5abe94e605a7273239fdf80343f97b9505c5ca78756323add26fd3e83108 matched the separately observed node receipt. Browser session60584 terminal exit0; Chromium154.0.8037.98, load2.1642738s, twelve tabs, eight screenshots, four visual inspections, console0/external0. No new complete CPU-suite, GPU, container/provider/cloud or human/public approval pass. Same controller90124/PID56870 was verified live at epoch1791463007.6006544. Evidence: generated/full-comparison-browser-20261008-v28 and docs/validation/platform_m5_full_comparison_browser_20261008.json. Original recommended Goal body preserved.


## 2026-10-08 — v0.26 verified wait, same full GPU process

후속 verified wait(v29)에서 같은 session90124/PID56870/실제 argv가 live임을 네 번 확인했다. 8B Task3 checkpoint는1974→2003→2026→2048/2659로 증가했고 최종 실패0이다. 코드·환경·실행 조건은 변경/재시작하지 않았다. 실제 full 완료·4B·반환 인수는 미완료다. 근거: generated/full-gpu-verified-wait-20261008-v29/evidence.json. 다음은 같은 handle의 완료를 기다리고 terminal 후 독립 full replay 인수·실제 report/app 검증이다.

Previous turn was progress (two-fixture browser QA). This turn is verified wait, not a new feature or new test pass. Same handle90124 yielded still running; actual controller56870/argv checked with ps. HF/cloud/operator/public gates remain external; the live GPU execution still permits meaningful progress on completion, so Goal remains active. Historical v0.26 source ZIP is preserved; no new source bundle or candidate build solely for this wait.


### 2026-10-08 — same full GPU verified wait(v30)

추가 verified wait(v30): 동일90124/PID56870/실제 argv의 live 상태를 네 번 확인했고8B Task3는2060→2085→2112→2133/2659,최종 실패0이다. 근거 generated/full-gpu-verified-wait-20261008-v30/evidence.json. 코드/환경/조건 변경·재시작·새 검사·전체 통과 주장은 없다. 실제 생성이 계속되므로 전체 Goal은 active이며 terminal 후 독립 원본 인수가 다음 단계다.


### 2026-10-08 — same full GPU verified wait(v31)

추가 verified wait(v31): 동일90124/PID56870/실제 argv를 네 번 확인했다. 8B Task3는2143→2157→2177→2208/2659,최종 실패0이며 작업은 실제 live다. 근거 generated/full-gpu-verified-wait-20261008-v31/evidence.json. 코드·환경 변경/재시작/새 검사 없이 같은 handle을 기다린다. Full 반환 인수와 전체 RC는 미완료이며 Goal은 active다.


### 2026-10-08 — same full GPU verified wait(v32)

추가 verified wait(v32): 동일90124/PID56870/실제 argv의 live 상태를 네 번 확인했다. 8B Task3는2216→2232→2245→2259/2659,최종 실패0이다. 근거 generated/full-gpu-verified-wait-20261008-v32/evidence.json. 코드/환경/조건 변경·재시작·새 검사·전체 통과 주장은 없다. 같은 handle 완료 후 독립 full replay 인수가 다음 단계이며 Goal은 active다.


## 2026-10-08 — v0.27 partial actual full8B generation coverage

v0.27: 같은 full GPU90124/controller56870의 실제 live 상태를25번 확인했다. 8B Task3는2270/2659에서 완료돼 Task5로 전환됐고 최종 관측248/2352/API 최종 실패0이다. 새 core Python의 읽기 전용 검사로 최종 Task1/2/3 파일2000/8000/2659행을 독립 operator index의 전체 sample ID·원본 입력 digest·model 필드와 대조했다. 외부 byte SHA771f066331e901c06ba960707add109143d75df6b1f603cf4da3439197c6b1b5/content SHA0d78a9b2ed412fa3507cf3d68db6b45d102ef0b8e24f0c65f3a10c3a987cd26d와 index seal을 검증했다. 누락·중복·API non-ok·빈 응답0이며 Task1/2 stop은2000/8000이다. Task3 stop2410/length249이며 기존 diagnostics의 length_limit 보존 경로를 확인했다. 실제 full report에서의249건 표시 검증은 이후 수행한다. [근거](validation/platform_m4_full_generation_partial_20261008.json). 초기 검사 키 expected_records 오류와 잘못 추정한 소스 파일 조회는 보존하고 실제 inputs 구조/모듈로 수정했다. 실행 중인 GPU·조건·package/UI/후보는 변경하지 않았다. 측정/4B/전체 반환 인수·HF/cloud/operator/공개 gate는 미완료이며 Goal은 active다.

Read-only SSH command: incoming/full_standard_v23/envs/core/bin/python -B -; outside operator-full-index-v2.json verified, validate_index/unique_rows/input_digest comparison. Private node receipt: incoming/full_standard_v23/partial-task3-receipt-v33.json mode0600 under root0700. Local detailed observations/setup failures: generated/full-gpu-partial-generation-20261008-v33/evidence.json. Historical source checkpoint v0.26 is preserved; no new source/candidate/wheel build or repeated CPU suite for partial evidence. Original recommended Goal body unchanged.


### 2026-10-08 — full8B Task5 same-process verified wait(v34)

후속 verified wait(v34): 동일90124/PID56870/실제 argv의 live 상태를7번 확인했다. 8B Task5 checkpoint는458→540→596→656→726→787→843/2352,최종 API 실패0이다. 근거 generated/full-gpu-verified-wait-20261008-v34/evidence.json. 직전 v33은 실제 Task3 최종 입력 대조/length249 확인의 progress였으며 이번은 대기다. 코드/환경/조건 변경·재시작·새 검사·full 통과 주장은 없다. 같은 handle의 생성→측정→4B→terminal 후 독립 인수가 남고 Goal은 active다.


## 2026-10-08 — v0.28 actual full8B generation coverage and measurement transition

v0.28: 같은90124/PID56870의 실제 live 상태를25번 확인하며8B Task5가908/2352에서2352/2352로 완료돼 generate passed/measure running으로 전환됐다. Task5 최종2352 sample ID·원본 입력 digest·model 필드를 외부 고정 index와 대조했고 unique source784, safe_guided/tool_forced/unsafe_induced 각각784, API non-ok/빈 응답0, finish_reason stop2352를 확인했다. Task1/2/3의 이전 확정 byte SHA도 그대로다. 전체8B 생성2000+8000+2659+2352=15011요청이 완료됐으며 Task4는 별도 생성이 아니다. 소유 vLLM 서버56951은 실제 ps에서 부재하고 exit0/stopped_owned_child다. Controller56870과 실제 분류기 pipeline child61091의 argv를 확인했다. 최종 Task3/4 측정 파일은 아직 없고 rows는 null이며 loading weights320/320을 측정 완료로 해석하지 않는다. Task3 length-limit249건을 보존한다. [근거](validation/platform_m4_full8b_generation_20261008.json). 코드/조건/환경/후보는 변경·재시작하지 않았고 측정·export/report·4B·전체 원본 인수/실제 full app/UI는 미완료다. 외부HF/cloud/operator/공개 gates와 Goal active를 유지한다.

Exact read-only SSH validator: generated/full8b-generation-20261008-v35/generation-check.ps1; private node receipt incoming/full_standard_v23/full8b-generation-receipt-v35.json mode0600. Detailed actual process/measurement-log observation and all25polls: generated/full8b-generation-20261008-v35/evidence.json. No new CPU-suite/wheel/candidate/source package build, no completed measurement/accuracy/intake or public rank claim. Original recommended Goal body preserved; prior v0.26 source ZIP remains historical.


## 2026-10-08 — v0.29 actual full8B raw replay, report/browser and native HTTP/CLI

v0.29: 실제 Qwen3-8B의 전체 생성→두 분류기 측정→export→분석이 완료됐다. 외부 고정 index/registry로 17,670기록(Task1–5: 2000/8000/2659/2659/2352)을 검증하고 원본 로그 재내보내기와 정확히 일치함을 확인했다. 실제 HTML 98,774,358bytes의 12탭·검색·필터·모바일 검사와 native HTTP 업로드/다운로드·독립 CLI profile의 바이트 일치가 통과했다. 길이 제한 249개 응답은 Task3/4 재사용으로 각각249건이며, Task5 파싱 실패2건을 보존한다. 검사기에 fixture/actual 구분·외부 model/length 기대값을 추가했고 실제 한 실행과 기본 fixture 회귀 검사가 통과했다. Package/UI/조건/상한/v22 후보는 변경하지 않았다. [근거](validation/platform_m4_m5_full8b_report_app_20261008.json). 같은90124/PID56870의4B 생성은 진행 중이다. 두 모델 전체 반환 인수·실제 full 비교·HF hosting/login/cloud·사람/운영자 gate는 미완료이며 Goal은 active다.

Independent result byte SHA27a4dea555208658133b7713f4f24938cf4e8b8cde23bb1e2003028692ba5a99; content SHA6fd409fd69017a165deead22fab7d6f9b590837f455bd5bdff8976e8f252d4c7. Outside index content SHA0d78a9b2ed412fa3507cf3d68db6b45d102ef0b8e24f0c65f3a10c3a987cd26d; exact deterministic export_run replay. HTML SHA b26509594e0a4549e541e28fe1a0fe2c51fea6e73f46a755473c79e12bf219ca. Analysis total200601055bytes including all cases; no truncation/limit change.

Native Python3.12.3 UID0: exact63candidate/42installed eval files/14web versions, actual loopback upload/session isolation/report/download/CLI byte agreement/deletion/owned server cleanup. Terminal0/82.849s; one selection[0], not a two-model comparison. Profile SHA d41ff7f554ae6dc04d9436001dde664b4145ae693d8d7740921e13b614bea8ed equals original analysis. Own server63676 stopped with expected -15; wrapper/test exit0. No hosted HF/provider request/container/cloud/new inference or human approval.

Actual Chromium154.0.8037.98 load1.500s,12tabs/17670records,core2000/overlap784/framing784/search/pagination/empty/metadata/mobile, console/errors/external requests0. Six screenshots saved, overview/length-limit/risk-category/mobile-strategies visually reviewed. Unique length249→Task3/4 cases498 verified. Actual scope requires --input-scope actual --expected-model Qwen/Qwen3-8B --expected-length-limit 249; browser_is_not_inference_proof remains true. Default synthetic fixture regression exit0/load1.127s; node --check passed. No whole current CPU suite repeated or claimed.

Private exact commands/observations/receipts/screens: generated/full8b-report-validation-20261008-v36/{portable-check.ps1,native-http-check.ps1,measurement-observations.json,native-http-receipt.json,browser-v1/scale-ui-evidence.json,fixture-default-regression/scale-ui-evidence.json,evidence.json}. Node native incoming/full8b_http_v36/http-check and final-evidence.json. Source inspection wrong CLI/module names were corrected to koevd-diagnose/reports.py. After both tests passed, tool orchestration store(undefined) failed on missing terminal session_id; receipts remained valid. No product failure/restart/test substitution. Checkpoint editor's initial JavaScript template had an unescaped Markdown backtick; parse failed before any mutation and corrected script performed the update.

Observed task diagnostics remain provisional: Task3 classifier-unsafe51/2659 (core37/2000, tool-overlap18/784; overlapping groups do not add); strategy descriptive/no rank. Task5 unsafe mock selections664/2350valid, invalid2/2352; safe_guided0/783,tool_forced140/783,unsafe_induced524/784. These are one-target observations under frozen settings, not classifier accuracy or universal safety claims. Length-limit249/repetition66/classifier disagreement125 flags overlap.

Same GPU90124/controller56870 lives and now4B generating; all8B stages passed. Preserve settings and owned GPU. Full two-model raw-return ZIP and actual combined app/UI still pending. Goal active; no public/cloud writes/Space/subscription created.

### 2026-10-08 — same full GPU verified wait(v40)

직전 v39와 이번은 실제 live 작업의 verified wait다. 동일90124/PID56870/실제 argv를8번 확인했고4B Task3 checkpoint741→772→809→835→851→863→876→889/2659/API-ok889/최종 실패0이다. 같은 handle도 반복 확인했다. 모든8B 단계는 passed,4B 생성 중이다. 근거 generated/full-gpu-verified-wait-20261008-v40/evidence.json. 코드/환경/조건 변경·재시작·새 검사 없이 같은 작업을 기다린다. Plan v0.29/Goal active를 유지하며4B/full 반환 인수·실제 두 모델 비교·외부 gates는 미완료다.

### 2026-10-08 — same full GPU verified wait(v39)

직전 v38과 이번은 실제 live 작업의 verified wait다. 동일90124/PID56870/실제 argv를6번 확인했고4B Task3 checkpoint624→650→666→686→703→717/2659/API-ok717/최종 실패0이다. 동일 handle90124도 반복 확인했다. 모든8B 단계는 passed,4B 생성 중이다. 근거 generated/full-gpu-verified-wait-20261008-v39/evidence.json. 코드/환경/조건 변경·재시작·새 검사 없이 같은 작업을 기다린다. Plan v0.29와 Goal active를 유지하며4B/full 반환 인수·실제 두 모델 비교·외부 gates는 미완료다.

### 2026-10-08 — same full GPU verified wait(v38)

직전 v37과 이번은 실제 live 작업의 verified wait다. 동일90124/PID56870/실제 argv를 세 번 확인했고4B Task3 checkpoint494→521→569/2659/API-ok569/최종 실패0이다. 모든8B 단계는 passed이며4B 생성 중이다. 근거 generated/full-gpu-verified-wait-20261008-v38/evidence.json. 코드/환경/조건 변경·재시작·새 검사 없이 같은 handle을 기다린다. Plan v0.29·원래 목표 범위·Goal active를 유지하고4B/full 반환 인수·실제 두 모델 비교·외부 gates는 미완료다.

### 2026-10-08 — same full GPU verified wait(v37)

직전 v36은 실제 첫 full8B의 독립 replay·리포트·앱·browser 검증을 완료한 progress다. 이번은 동일90124/PID56870/실제 argv의 live 상태를 세 번 확인한 verified wait다. 4B Task3 checkpoint는405→436→473/2659, API-ok473/최종 실패0이며 모든8B 단계는 passed다. 근거 generated/full-gpu-verified-wait-20261008-v37/evidence.json. 코드·환경·조건 변경/재시작/새 테스트 없이 같은 handle을 기다린다. Plan v0.29와 original Goal body를 유지한다. Source ZIP generated/KoEVD_platform_source_actual_full8b_report_20261008_v36.zip은 이 대기 기록 이전의199파일 checkpoint이며 이후 로그 append까지 포함한다고 주장하지 않는다. Full4B/전체 반환 인수·실제 두 모델 비교와 외부 gates는 미완료이며 Goal은 active다.


### 2026-10-09 — same full GPU verified wait(v49)

직전 v48과 이번은 실제 live 작업의 verified wait다. 동일90124/PID56870/실제 argv를12번 확인했고4B Task3 checkpoint2208→2219→2229→2241→2252→2262→2272→2282→2301→2317→2335→2352/2659/API-ok2352/최종 실패0이다. 분모는Task3의2659이며Task5의2352가 아니다. 모든8B 단계는 passed,4B Task3 생성 중이며Task5 전환은 아직 없다. 근거 generated/full-gpu-verified-wait-20261009-v49/evidence.json. 코드/환경/조건 변경·재시작·새 검사 없이 같은 handle을 기다린다. Plan v0.30/Goal active를 유지하며4B/full 반환 인수·실제 두 모델 비교·외부 gates는 미완료다.

### 2026-10-09 — same full GPU verified wait(v48)

직전 v47과 이번은 실제 live 작업의 verified wait다. 동일90124/PID56870/실제 argv를10번 확인했고4B Task3 checkpoint2012→2034→2055→2074→2106→2129→2142→2151→2164→2183/2659/API-ok2183/최종 실패0이다. 모든8B 단계는 passed,4B Task3생성 중이며Task5 전환은 아직 없다. 근거 generated/full-gpu-verified-wait-20261009-v48/evidence.json. 코드/환경/조건 변경·재시작·새 검사 없이 같은 handle을 기다린다. Plan v0.30/Goal active를 유지하며4B/full 반환 인수·실제 두 모델 비교·외부 gates는 미완료다.

### 2026-10-09 — same full GPU verified wait(v47)

직전 v46과 이번은 실제 live 작업의 verified wait다. 동일90124/PID56870/실제 argv를8번 확인했고4B Task3 checkpoint1825→1848→1873→1898→1919→1942→1962→1983/2659/API-ok1983/최종 실패0이다. 모든8B 단계는 passed,4B 생성 중이다. 근거 generated/full-gpu-verified-wait-20261009-v47/evidence.json. 코드/환경/조건 변경·재시작·새 검사 없이 같은 handle을 기다린다. Plan v0.30/Goal active를 유지하며4B/full 반환 인수·실제 두 모델 비교·외부 gates는 미완료다.

### 2026-10-09 — same full GPU verified wait(v46)

직전 v45와 이번은 실제 live 작업의 verified wait다. 동일90124/PID56870/실제 argv를10번 확인했고4B Task3 checkpoint1551→1577→1612→1642→1674→1702→1728→1752→1776→1791/2659/API-ok1791/최종 실패0이다. 모든8B 단계는 passed,4B 생성 중이다. 근거 generated/full-gpu-verified-wait-20261009-v46/evidence.json. 코드/환경/조건 변경·재시작·새 검사 없이 같은 handle을 기다린다. Plan v0.30/Goal active를 유지하며4B/full 반환 인수·실제 두 모델 비교·외부 gates는 미완료다.

### 2026-10-09 — same full GPU verified wait(v45)

직전 v44와 이번은 실제 live 작업의 verified wait다. 동일90124/PID56870/실제 argv를8번 확인했고4B Task3 checkpoint1361→1378→1400→1427→1454→1478→1502→1523/2659/API-ok1523/최종 실패0이다. 모든8B 단계는 passed,4B 생성 중이다. 근거 generated/full-gpu-verified-wait-20261009-v45/evidence.json. 코드/환경/조건 변경·재시작·새 검사 없이 같은 handle을 기다린다. Plan v0.30/Goal active를 유지하며4B/full 반환 인수·실제 두 모델 비교·외부 gates는 미완료다.

### 2026-10-09 — same full GPU verified wait(v44)

직전 v43과 이번은 실제 live 작업의 verified wait다. 동일90124/PID56870/실제 argv를10번 확인했고4B Task3 checkpoint1183→1197→1213→1225→1240→1260→1284→1298→1319→1346/2659/API-ok1346/최종 실패0이다. 모든8B 단계는 passed,4B 생성 중이다. 근거 generated/full-gpu-verified-wait-20261009-v44/evidence.json. 코드/환경/조건 변경·재시작·새 검사 없이 같은 handle을 기다린다. Plan v0.30·Goal active를 유지하며4B/full 반환 인수·실제 두 모델 비교·외부 gates는 미완료다.

### 2026-10-09 — same full GPU verified wait(v43)

직전 v42와 이번은 실제 live 작업의 verified wait다. 동일90124/PID56870/실제 argv를6번 확인했고4B Task3 checkpoint1073→1092→1109→1122→1140→1165/2659/API-ok1165/최종 실패0이다. 모든8B 단계는 passed,4B 생성 중이다. 근거 generated/full-gpu-verified-wait-20261009-v43/evidence.json. 코드/환경/조건 변경·재시작·새 검사 없이 같은 handle을 기다린다. Plan v0.30/Goal active를 유지하며4B/full 반환 인수·실제 두 모델 비교·외부 gates는 미완료다.

### 2026-10-09 — same full GPU verified wait(v42)

직전 v41은 실제4B의 완료 Task1/2 전체 입력 대응을 확인한 부분 progress다. 이번은 동일90124/PID56870/실제 argv의 live 상태를6번 확인한 verified wait다. 4B Task3 checkpoint986→996→1009→1021→1040→1053/2659/API-ok1053/최종 실패0이며 모든8B 단계는 passed다. 근거 generated/full-gpu-verified-wait-20261009-v42/evidence.json. 코드/환경/조건 변경·재시작·새 검사 없이 같은 handle을 기다린다. Plan v0.30·Goal active를 유지하며4B/full 반환 인수·실제 두 모델 비교·외부 gates는 미완료다.

## 2026-10-09 — v0.30 actual full4B finalized Task1/2 outside input coverage

v0.30: 실제4B의 완료된 Task1/2 2000/8000응답을 외부 고정 index의 전체 sample ID·원본 입력 digest·model 필드와 대조했다. 누락/중복/API non-ok/빈 응답0, finish_reason stop2000/8000이며 Task2 네 variant는 각각2000이다. [근거](validation/platform_m4_full4b_partial_input_20261009.json). 초기 검사기의 read_jsonl generator 길이 처리 오류를 수정하고 원래 실패/수정 스크립트를 보존했다. GPU 작업은 변경·재시작하지 않았다. 같은90124/PID56870의4B Task3는 최종965/2659/API 최종 실패0이며 생성/측정/전체 반환 인수·실제 두 모델 비교·외부 gates는 미완료다.

Task1 prediction byte SHA93a5326fc16d3311b665ed2a6879473be497bf55293ba7bd6ebb5f7fbf31cfd1; Task2 SHA f0f54fafb46ffbbf436964b598a8f30ec2b5be06f0d869d874bf7f8756844b59. Outside operator-full-index-v2.json byte SHA771f066331e901c06ba960707add109143d75df6b1f603cf4da3439197c6b1b5/content SHA0d78a9b2ed412fa3507cf3d68db6b45d102ef0b8e24f0c65f3a10c3a987cd26d checked before comparison. Finalized row counts and full original-row input digests/model names match; no inference/accuracy authentication claimed.

Private initial input-check.ps1 and corrected input-check-v2.ps1 in generated/full4b-partial-input-20261008-v41. First failed TypeError len(generator) before receipt write; corrected command terminal0/read-only original check and new private receipt work/full4b-task12-receipt-v41.json mode0600. Same90124/56870 actual argv repeatedly live; checkpoints903/930/941/953/965, API finalfailed0. Evidence.json/formal JSON preserve failure and passing scope.

Only docs/metadata validation changed. No package/UI/conditions/GPU restart/CPU-suite/sourceZIP/wheel/candidate rebuild/public push. Recommended Goal body preserved. Historical v36 ZIP remains as-built, not current appended docs. Next actual4B Task3/5 final+measurement and terminal two-model bounded intake/combined report/HTTP/CLI/UI remain pending. Goal active, HF plan/cloud/operator/public gates unchanged.


### 2026-10-09 — full4B Task5 same-process verified wait(v51)

직전 v50은 실제4B Task3 최종 입력 대응·length213과Task5 전환을 확인한 progress다. 이번은 동일90124/PID56870/실제 argv의 live 상태를10번 확인한 verified wait다. 4B Task5 checkpoint238→302→408→474→540→610→670→732→801→857/2352/API-ok857/최종 실패0이다. 모든8B 단계는 passed,4B 생성 중이며 분류기 측정은 아직 없다. 근거 generated/full-gpu-verified-wait-20261009-v51/evidence.json. 코드/환경/조건 변경·재시작·새 검사 없이 같은 handle을 기다린다. Plan v0.31·Goal active를 유지하며4B/full 반환 인수·실제 두 모델 비교·외부 gates는 미완료다.

## 2026-10-09 — v0.31 actual full4B finalized Task3 input coverage and Task5 transition

v0.31: 실제4B Task3 최종2659응답의 전체 sample ID·원본 입력 digest·model 필드를 외부 고정 index와 대조했다. 누락/중복/API non-ok/빈 응답0, finish_reason stop2446/length213이며 Task1/2의 이전 byte SHA도 그대로다. [근거](validation/platform_m4_full4b_task3_input_20261009.json). 같은90124/PID56870의 실제 live 상태를17번 확인하며Task3가 완료되어Task5로 전환됐고 최종 관측123/2352/API 최종 실패0이다. GPU 코드·조건·환경을 변경·재시작하지 않았다. length213을 안전/완전 응답으로 바꾸지 않고 향후 실제 Task3/4 리포트에 각각213건 표시되는지 검증한다. 분류기 측정·Task5 최종·두 모델 전체 반환 인수/실제 비교·외부 gates는 미완료다.

Task3 prediction byte SHA1e598b2b7a3fb142b4bbd009aa0e5f1acc589fe69e097f2cad509c6533ac01ba; Task1/2 hashes remain93a5326fc16d3311b665ed2a6879473be497bf55293ba7bd6ebb5f7fbf31cfd1/f0f54fafb46ffbbf436964b598a8f30ec2b5be06f0d869d874bf7f8756844b59. Outside byte771f066331e901c06ba960707add109143d75df6b1f603cf4da3439197c6b1b5/content0d78a9b2ed412fa3507cf3d68db6b45d102ef0b8e24f0c65f3a10c3a987cd26d validated. Unique samples/sources2659; exact original-row input digest/model and all sample keys matched. No parsing/accuracy/inference authenticity or completed measurement claim.

Same90124/controller56870 actual argv17observations: Task3 2371→2390→2408→2427→2441→2462→2480→2503→2525→2549→2567→2587→2604→2623→2642 then Task5 12→123/2352, final API failed0. All8B stages passed. Private exact input-check.ps1 and evidence.json in generated/full4b-task3-input-20261009-v50; node work/full4b-task123-receipt-v50.json mode0600. Check command terminal0. Existing generator materialization fix used; no new setup failure.

Only metadata/docs updated. No GPU/code/settings/env/restart/CPU-suite/sourceZIP/wheel/candidate/public changes. Recommended Goal body preserved. Historical v36 source ZIP is not current appended documentation. Future actual full report/browser expects249/213 unique truncated responses and Task3/4 reuse separately; no current two-model full app/browser pass. Task5 final,4B safety/strategy,export/diagnose and terminal two-model independent raw-return/comparison remain pending. Goal active; external HF plan/cloud/operator/public gates unchanged.


### 2026-10-09 — full4B measurement same-process verified wait(v53)

직전 v52는 실제4B 전체 생성 입력 대응·소유 서버 종료·측정 시작을 확인한progress다. 이번은 동일90124/PID56870/실제 argv와실제 측정 child66716을20번 확인한verified wait다. 4B Task3 측정 파일은세번째 관측부터2659행이며Task4 최종파일은아직 없다(rows null). 실제Task4 분류 child67290/argv/상태Rl·CPU124%를확인했고 지정GPU2의관측사용률77%,소유process GPU메모리19374MiB다. 이는활동 근거이며처리행 수/정확도/완료 증거가아니다. 근거 generated/full-gpu-measurement-wait-20261009-v53/evidence.json 및 gpu-activity-check.ps1;node work/full4b-measurement-activity-v53.json mode0600. 모든8B 단계는passed,4B measure running이며traceback은관측로그에서없다. 코드/환경/조건 변경·재시작·새 검사 없이같은 handle을기다린다. Plan v0.32/Goal active를유지하며4B Task4/분석/full 반환 인수·실제 두 모델 비교·외부 gates는미완료다.

## 2026-10-09 — v0.32 actual full4B generation coverage and measurement transition

v0.32: 실제4B 전체 생성2000+8000+2659+2352=15011요청의 고정 입력 대응을 확인했다. Task5 고유 source784·safe_guided/tool_forced/unsafe_induced 각각784, 누락/중복/API non-ok/빈 응답0, finish_reason stop2352이며 이전Task1/2/3 byte SHA도 그대로다. 소유 생성 서버62528은 실제ps에서 부재하고stopped_owned_child/exit0다. 같은90124/PID56870의 실제 live 상태를26번 확인하며generate passed/measure running으로 전환됐고 실제측정 child66716/argv를 확인했다. [근거](validation/platform_m4_full4b_generation_20261009.json). 최종4B Task3/4 측정 파일은 아직 없고rows null이며weight loading320/320을 측정 완료로 해석하지 않는다. Task3 length213을 보존한다. 측정/export/분석·전체 두 모델 반환 인수/실제 비교/앱/UI와외부 gates는 미완료다.

Task5 prediction byte SHA d1ff5a772f128a9ad3086f22b6a39e0c5eab826f96ec03877b1c46e4a7b81342; exact2352raw/unique samples,784sources,threeframings784each. External whole original-row input digests/model and key coverage matched. PreviousTask1/2/3 final byte hashes unchanged; Task3 stop2446/length213 retained. Task5 stop2352. No accuracy/parse-validity/authentication or full two-model return claim.

Same90124/controller56870 actualargv26observations; 4B Task5 919→1005→1069→1120→1171→1227→1286→1333→1391→1441→1498→1560→1615→1676→1736→1799→1869→1927→1983→2035→2089→2141→2185→2235→2307→2352/2352 API finalfailed0, then measure running. Ownedserver62528 stopped/exit0/actualpsabsent. Actualmeasure child66716 with canonical adapter/base/dtype/batch2/trace argv observed. Final4B Task3/4 files absent, rowsnull; weight loading320/320 only. Existing8B final2659/2659files preserved.

Private exact generation-check.ps1/evidence.json in generated/full4b-generation-20261009-v52; node work/full4b-generation-receipt-v52.json mode0600. Independent command terminal0, no new setup failure. Only docs/metadata changed. No product/GPU/conditions/env/restart/CPU-suite/sourceZIP/wheel/candidate/public push. Original recommended Goal body unchanged. Historical v36 source ZIP remains as-built and not current appended docs. Next same-process4B measurement/export/diagnose and terminal fulltwo-target raw-return/actual combined report/app/CLI/UI remain pending. Goal active; HF402/cloud/operator/public gates unchanged.


## 2026-10-09 — v0.33 full actual two-model acceptance and comparison

v0.33: 두 실제 모델의 전체 생성·분류·내보내기·분석·통합 비교 13단계가 종료 코드0으로 완료됐다. 모델당 생성 요청15,011개·평가 기록17,670개, 전체35,340기록을 보존했다. 외부 고정 index/registry와 별도 ZIP SHA를 사용한 원본 재내보내기가 두 모델 모두 정확히 일치했다. 노드·로컬 CLI의 5개 분석 파일이 바이트까지 같고, 앱 HTTP profile도 같다. 실제 HTML199,373,743bytes의 12탭·두 실행·대응 필터·사례 검색·모바일 검사가 통과했다. [근거](validation/platform_m4_m5_full_two_actual_20261009.json). 분류 정확도·공식 순위·실제 HF 로그인/호스팅·클라우드 복구·사람 승인·공개는 별도 미완료 조건이다.

Native initial NFS SQLite start failed before readiness; own server68346 exited1. Failure DB/logs retained. Fresh local /tmp/koevd-full-two-v54-ftvjj4h6 runtime passed155.533s; own server68383 terminated(-15 expected), wrapper0. Exact63 candidate/42 installed eval files/14 locked web versions; no package change. Node/Windows CLI/HTTP profile SHA1e1e7afe0813fa00fb69e73d67d5a228c80eb05ff21dbcefad9f5d791eb3a609. HTML SHA92f1e8b780e0e0bccffe98cbc29152e81e96ddd257410f2e671c59d26b9fb5ad; all5 node/local files exact. Browser Chromium154.0.8037.98/load2.7794722s/12tabs/35340cases/no console errors/external requests. Reviewed paired/descriptive/mobile screenshots. New metadata/docs only; no new CPU whole-suite pass, inference restart, condition change, public posting, cloud write or paid resource. Original Goal body preserved. HF org prerequisite officially reverified; no unchanged creation retry. Goal active with external gates unresolved.


## 2026-10-09 — v0.34 RC audit and current CPU suite

v0.34: R1–R10의 구현·증거·외부 조건을 [릴리스 점검표](PLATFORM_RELEASE_CANDIDATE.md)에 정리했다. 최신 전체 CPU294검사149.037초/exit0/실패·오류·skip0와 pip check를 통과했다. CI의 누락된 serve/dev 의존성과 Node24·pip check를 보완했으며 공개 CI 파일을 소스 ZIP에 명시적으로 포함하되 다른 숨김 파일은 제외하는 경계를 검증했다. README의 dtype 옵션 설명과 앱 안내의 과거 두 모델 미완료 표현을 수정했다. [근거](validation/platform_rc_audit_20261009.json). Package/UI·모델·GPU 조건은 변경하지 않았다. 실제 GitHub CI matrix·컨테이너/HF 로그인·클라우드 복구·승인된 공개 원문 참조는 아직 미검증이며 전체 RC/Goal을 완료로 표시하지 않는다.

Initial CPU attempt293/errors287 came from sandbox default TEMP access failures, not a pass. Owned-TEMP rerun stalled at HTTP test and policy probe verified os.link WinError5; exact own harness commands/PIDs43232/56444 stopped, unified56962 terminal1, no timeout-only restart. Fresh authorized local run77463 terminal0,294tests149.037s/no failures/errors/skips; log SHA652701035def5d59c4cd45643ecf02199e5990415c0dd3504f366eb372013625. No auto-review rejection. Source package/UI49files and wheel/candidate unchanged; no actual inference/cloud/subscription/production/public output. Goal body unchanged. Current CI is configured but GitHub run unavailable on unpushed local changes. Remaining external gates are itemized; Goal active.


## 2026-10-09 — v0.35 actual full private review/store/restore/admission

v0.35: 최신 전체 두 모델 결과35340기록의 비공개 운영자 검토 자료와 저장·재시작·스냅샷 복원·등록 정책 검증을 완료했다. 실제실행184파일소스manifest와결과를연결했고미승인catalog/검토준비본은등록검사에서거절됐다. 원본JSON내용·제출상태·이력과재요청이일치했으며67154758byte스냅샷복원후공개조회503·변경차단을유지했다. 각47지표에서공식rank는없고Task3/4·조건부비율제외가실제전체데이터에서도유지됐다. [근거](validation/platform_m5_m6_full_private_review_20261009.json). HF관리자로그인은유효하지만지정Space조회404·현재요금제정보미제공이고두환경의컨테이너CLI도없다. 공개·사람인수·복구해제·클라우드·새inference를수행하지않았다.

Full preparation14702 terminal0; frozen source ZIPbea8f1f0ca8f4fa5de17bf5b5cae8caec67e0d5493b553a3c202339c5321b39a/manifest4c9cd5baba00af5cad7e245ab895710145e0eef7c5aee4f2548baf727bd4044a/controller519669d426d54c55efa3c77482b1fef32c6c6d2ecd5c50247a15953227798907. All14refs/model bound; no human statement, accepted receipt or rights assertion. Full local validation94817 terminal0/76.099s;2artifacts/submissions/revisions/events/requests and1outside index. Snapshot SHA780995a6e048bff02fa0321aac1355b9c0cf538d06d6a5eded6360fcd36ac47b/67154758bytes; eachDB67153920bytes. Original source file SHAs retained; decoded originals/state/history exact. Quarantine503 and mutation block verified. Candidate admission63536 terminal0/13.575s;47metrics/model/allrankexcluded/resamples0/no statistical-accuracy claim. No new GPU/code/policy/cloud/public output. Latest full CPU294 pass remains atv0.34; no repeat. Current HFreadonly admin/404/planflags unavailable; Windows andnode docker/podman/nerdctl absent. Same mandatory external runtime/identity/cloud/operator/reference gates recorded acrossv54/v55/v56; local required actions are exhausted, blocked audit ready.


## 2026-10-11 — v57 / plan0.36 Static common-Python full comparison

Added browser_bridge and Static assets, pinned runtime fetch/materializer and isolated browser harness. Existing engine/server/M6 code unchanged. Synthetic100 and adversarial20 resamples and actual full two-target35340/resamples0 passed; all five outputs byte-exact to native Python. Full calculation101.490s; report199262672bytes, outputs405358834bytes;15 asset GETs, POST/external/console errors0; mobile/response/tabs/download/clear passed. Related49 CPU regressions22.197s exit0. Earlier294 suite predates bridge; no new full-suite/install claim. Initial npm LICENSE404 and inherited Blob CSP failure preserved; tagged licenses and fixed code hashes in fresh candidate passed. Actual target outputs selected only in private localhost, none in21-file deployment folder. No new inference/HF Space/publication/billing/OAuth/cloud/operator approval. Original Goal body unchanged, resumed audit first turn is progress and Goal active. Receipt docs/validation/platform_m5_static_browser_20261011.json.
Commands: python scripts/fetch_static_runtime.py --output generated/static-runtime-0.29.3-20261011-v57-final; python scripts/materialize_static_space.py --catalog generated/private-space-deployment-20261008-v22/operator-data/catalog.json --runtime-dir generated/static-runtime-0.29.3-20261011-v57-final --output generated/static-development-space-20261011-v57; node scripts/validate_static_space_ui.cjs --space generated/static-development-space-20261011-v57 --output generated/static-full-browser-20261011-v57 --files [two outside actual results] --expected generated/static-full-local-expected-20261011-v57/profile-v2.json --resamples 0 --browser-executable [Chrome]. Exact invocations in this turn; original files preserved.


## 2026-10-11 — v58 / plan0.37 full Static bootstrap and private hosting

Full actual35340 browser resamples100/seed1729:171.729s, all5 outputs byte-exact to accepted GPU/native, GET15/POST/external/errors0; UI/mobile/clear and visual QA passed. New noneditable wheel205517bytes SHA0d6f842eb2e4939cf1189d0bf3e289ff3da97685be73e4e40adcbc2918043451, exact installed50 assets/source and full299 CPU158.045s exit0/no failures/errors/skips. Initial optional-dependency cache path errors18/skips4 retained; only newenv path corrected. Server64-file candidate checked; no container. Authorized private Static KETI-NLP/KoEVD-Explorer created/uploaded revision0339d618b970737ec6d0b102f5ba1df9a78c6588; RUNNING/hardwareNone and all22 uploaded files byte-exact by download. Cache WinError1314 handled via local_dir without OS changes. Private app probes401 with/without bearer; not a hosted UI/OAuth pass. No target outputs/DB/credential/publication/billing/new inference. Remaining M6/operational gates maintained. Formal docs/validation/platform_m5_static_hosting_20261011.json.


## 2026-10-11 — v59 / plan0.38 actual private hosted Static

Actual HF direct Static app revision0339d618b970737ec6d0b102f5ba1df9a78c6588:35340 original records, resamples100/seed1729, 176.241s; all5 native/GPU outputs byte-exact. All browser requests audited:GET17, service asset redirects2, independent refetches1; POST/unexpected requests/errors0. UI/tabs/cases/mobile/clear passed. Owner signed-access cookie only in memory/pipe; no result upload/credential persistence/publication/billing/new inference. Generic hosted CLI and3 credential boundary tests/Node syntax/preflight pass, installed core50 still exact. Prior299 suite is separate, no full302 claim. CDN302 and Chrome69MB inspector cache failures preserved; their5 outputs independently hash-match. Direct app/internal iframe only: no Hub-parent/submitter OAuth/cloud/operator/container acceptance. Formal docs/validation/platform_m5_static_hosted_ui_20261011.json.
Command: python scripts/validate_private_static_hosting.py --repo-id KETI-NLP/KoEVD-Explorer --revision0339d618b970737ec6d0b102f5ba1df9a78c6588 --candidate generated/static-development-space-20261011-v57 --node [Node24] --browser-executable [Chrome154] --result [8B portable] --result [4B portable] --expected generated/full-two-gpu-validation-20261009-v54/analysis/profile-v2.json --resamples100 --output generated/static-HF-full-bootstrap-browser-20261011-v59-audit. Exact invocation retained in turn; docs/STATIC_HOSTING_VALIDATION.md has portable arguments.


## 2026-10-11 — v60 / plan0.39 explicit public OAuth client

Implemented public-client opt-in with mandatory PKCE and no secret/Basic header; default confidential mode unchanged. New8 tests cover provider configuration, PKCE/state wire, HTTP ownership/role isolation, CLI and development launcher. Installed full310 tests/142.623s/exit0/failure-error-skip0;50 code/assets exact, pip check. Wheel 16de531ce00b74cfa087483384ed30f07015295177fa6b1f78f27f35cda07db3; candidate64files/75596851bytes, manifest 5aef61897221ad2b4ebcf63036ab9cd9b3e0c819ed7255b88c76cdbc03fe7ec2, no outputs/roles/credentials. Earlier34-test1failure retains404-vs403 test expectation; ACL unchanged. Initial sandbox TEMP permissions failed before HTTP fixture setup. Actual HF parent initial rendering/private Running observed through CUA; full parent file flow/extension file-URL setting remain unverified. No new actual HF login/GPU inference/publication/cloud/deployment/billing. Formal docs/validation/platform_m6_public_oauth_20261011.json.
Command: generated/public-oauth-package-20261011-v60/env/Scripts/python.exe generated/validate_public_oauth_20261011_v60.py --full --output generated/public-oauth-installed-full-20261011-v60. Installed python -m koevd_eval.spaces --help also passed. Build/refresh/finalizer helpers and raw logs remain in generated; source bundle excludes generated.


## 2026-10-11 — v61 / plan0.40 source-bundle build metadata boundary

Excluded generated egg-info/dist-info paths from source inventory, case-insensitively. Source files, explicit CI and historical verifier are preserved; no metadata/previous ZIP deletion. Scoped7 tests/0.369s/exit0/error-failure-skip0; one new meaningful inventory-change regression. Prior installed full310 remains separate, no full311 claim. Installed core50/wheel, server64/manifest, Static19 engine sources remain exact. Actual original target result SHA and prior hosted evidence digest match. No new provider login/GPU/cloud/container/approval/posting. Updated public OAuth app client-ID question pending, no secret/token requested. Formal docs/validation/platform_rc_source_hygiene_20261011.json.


## 2026-10-12 — v63 / plan0.42 Public Static analysis preview

User-approved private→public transition. Current23 payload files/24 repository files match; before publication original23 files and2 commits audited, secrets/variables/baselines empty. Added exact pinned dataset research-use terms, attribution and sensitive-content notice; engine19/input data unchanged. Scoped bridge5 + hosting6 pass; Node syntax pass, core50 still exact, previous full310 separate. Public API and actual anonymous direct35340/bootstrap100 analysis193.412s/all5 native outputs pass. Network GET19/CDN redirects4/independent asset refetch1/POST-errors-unexpected0. Parent actual48+48/bootstrap100 file→analysis→5 downloads/compare/clear pass; stable mobile356px/block verified after resize.2 parent ancillary GETs blocked by allowlist, no page errors. First mobile screenshot/data-flow receipt retained; no app CSS fix required. No actual results/DB/credentials posted, new GPU, hardware/billing or GitHub push. Static does not require container; OAuth/Bucket are route choices, shared identity/validation/history/withdrawal/policy requirements remain. Goal active/incomplete; M6 Static integration next. Formal docs/validation/platform_m5_public_static_20261012.json.
