# KoEVD platform release candidate — review checklist

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

현재 준비 상태(2026-10-12/plan0.55)

v0.55에서 현재 private CPU 기본 앱에 두 모델 전체 결과를 일시 분석하는 별도 전송 인수 도구를 추가했다. 기본 preflight는 결과 body/analysis POST/DELETE 없이 resource 접근·고정8e692c88 revision·RUNNING/cpu-basic·단일 replica·한도/익명 app 경계를 읽는다. 실제 HF preflight2.078초/exit0·결과 전송0/job0과 최종6 CPU guard/0.276초가 통과했다. core50 소스는 기존 설치/배포 검증본과 같다. 새 제안은 두 실제17,670+17,670기록 JSON89,396,889바이트 각1회·대응 비교 job1·다섯 native405,679,557바이트와 직접 stream 대조·download512MiB 한도·두 owned analysis session cleanup만 포함한다. 전체 전송은 미승인/미실행이며 앞선 종료된96기록 시험 승인을 재사용하지 않는다. 새 script는 host-side 검사이며 이미 배포된 image를 변경하지 않았다. 이 준비는 실제 full hosted·local image UID/CMD·큰 report UI·운영자 판단·공개 권한을 대신하지 않는다. [최신 근거](validation/platform_m5_full_hosted_preparation_20261012.json), [실행 범위](HOSTED_FULL_ANALYSIS_ACCEPTANCE.md). Goal 도구의 현재 상태active를 확인했고 원래 목표/완료 조건을 유지한다.

아래 이전 기록은 당시 범위다.

현재 상태(2026-10-12/plan0.54)

v0.54에서 별도 승인된 실제 private CPU 유한 종료 시험을 완료했다. 기준9개 보존·새 snapshot3개/396,229바이트로3회/24MiB 한도를 지켰다. 현재 코드에 결합한 parent 종료 로그 뒤 마지막 snapshot이 생겼고 finite worker2회 완료·후속 기동 initialization_inventory_mismatch 거부를 확인했다. 별도 다운로드한3사본 중 두 현재48+48기록 원본/이력이 모두 일치한 digest를 내용으로 선택했다. 고정 복원 후 실제 HF 재로그인의 두 원본·두 이력4파일이 복원 전 native 다운로드와 바이트 일치했고 새 저장/공개 조회 거부·worker OFF·복구 대기를 확인했다. 최신 기본 revision `8e692c88d412d6305879473e3e8e74d46bb7dd2c`의 RUNNING/cpu-basic·66파일 바이트/목록 일치로 복귀했다. Bucket12객체/68,382,317바이트·Secret·public Static을 보존했으며 상시 백업은 꺼져 있다. 이 승인은 시험 종료로 소진됐다. 과거 누락4B 이력이 복구됐다고 주장하거나 과거 횟수 실패를 소급 통과 처리하지 않는다. 실제 HF host restart 이벤트 로그·상시 운영/RPO·현재 Docker 전체 용량·운영자 정책/복구 인수·공개 참조는 미확보다. 실제 GPU/F1/분류 정확도의 새 검증은 아니다. [최신 근거](validation/platform_m6_actual_finite_shutdown_20261012.json). 전체 목표/완료 조건은 유지하며 전체 완료를 선언하지 않는다.

아래 이전 기록은 당시 범위다.

현재 상태(2026-10-12/plan0.53)

v0.53에서 기본 Docker 이미지의 CMD를 유지한 로컬 인수 도구와 노드 실행 절차를 추가했다. 이미지 ID·자신의 container ID/label·UID/GID1000·network none·미공개 포트·종료/제거를 외부 실행기에서 확인하고, 내부 HTTP 검사기는 외부 소유 loopback 서버에 연결한다. current source50는 v0.52 설치/352 전체 검사 때와 같고, 새 script 관련12 guard검사/0.111초가 통과했다. 새 연결 경로의 현재 로컬 실제 서버/CLI에서 기존 두 실제 모델 각17,670기록·총35,340기록의 대응 비교와 JSON/JSONL/CSV/Markdown/HTML5파일이 바이트 일치했다. 실행252.344초/exit0, 소유 server terminal이며 Windows terminate의 관측 exit1을 보존했다. 이번에는 개별 모델 보고서2개를 새로 검사하지 않았다. 컨테이너 도구0개라 실제 Docker 실행은 미검증이며 HF/OAuth/새 inference/외부 전송도0회다. 66파일 기본 context ZIP과 실행 안내를 로컬에 준비했고 기존 HF 제한 시험 재승인 질문은 계속 pending이다. 실제 HF 두 현재 초안 종료 보존·Docker 전체 용량·운영 인수·공개 참조를 미완료로 유지한다. [최신 근거](validation/platform_m5_container_runtime_preparation_20261012.json), [실행 절차](CONTAINER_RUNTIME_ACCEPTANCE.md). Goal active/원래 범위를 유지한다.

아래 이전 기록은 당시 범위다.

현재 상태(2026-10-12/plan0.52)

v0.52에서 유한 worker의 마지막 capture 전에 소유한 HTTP 서버를 종료·회수하고 전용 stdin으로 마지막 백업을 허용하는 순서를 구현했다. 현재 새 비편집 설치의 source50·고정 의존성25·pip check와 전체352 CPU검사/146.942초/failures0/errors0/skips0가 통과했다. 현재9개 digest를 metadata-only double로 재현한 실제 소유 로컬 HTTP/worker 통합29.344초에서 두48+48기록 원본/이력의 고정 복원 일치, 마지막 SQLite capture 전 서버 종료, 이후 연결 거부, 새 빈 초기화 거부, 복원 대기와 credential 분리를 확인했다. HF/OAuth는 명시적 double이다. Windows 상태 파일 교체의 일시적 WinError5/32/33에만 최대6회·총0.62초 재시도하며 지속 오류는 전달한다. 관측된 WinError5의 근본 원인은 미확정이다. 기본65·관리형68파일 및 초기1+worker2/24MiB/600초의70파일 제안을 로컬에 준비했고 이번 외부 전송·배포는0회다. 앞서 승인된 v0.51 시험은 종료됐으며 새 제안의 권한으로 재사용하지 않는다. 실제 마지막 기본 revision은 `f65a8b1065b934e649e545043c4ac89b18c2d4a5`, 상시 백업 OFF다. 이전 실제 새4B 이력 누락은 복구됐다고 주장하지 않는다. 실제 HF 두 현재 초안의 종료 보존·현재 Docker 전체 용량·운영 인수·공개 참조는 미완료다. [최신 근거](validation/platform_m6_finite_final_capture_20261012.json). Goal active/원래 범위를 유지한다.

아래 이전 기록은 당시 범위다.

현재 상태(2026-10-12/plan0.51)

v0.51에서 별도 승인된 private CPU 정상 기동 시험의 새 snapshot3개/302,021바이트와 finite worker2회 완료·후속 초기화의 `initialization_inventory_mismatch` 거부를 확인했다. 이번 횟수/용량 한도는 통과했지만 두 초안 보존은 미완료다. 실제 HF 로그인으로8B/4B 초안 저장을 관찰했고 종료 경계의4B 다운로드가503을 반환했다. 독립 다운로드/외부 index·registry 검사에서 마지막 사본에는8B48기록/이력만 있고 새4B 이력은 없었다. 과거4B 사본으로 대체하지 않았다.8B의 고정 복원·실제 재로그인 전후 원본/이력 바이트 일치와 새 저장 거부·공개 조회 불가 UI는 확인했다. 승인된 최신 UI 기본 프로필 `f65a8b1065b934e649e545043c4ac89b18c2d4a5`의 RUNNING/cpu-basic·66파일 바이트/목록 일치로 복귀했고9백업/67,986,088바이트·Secret·public Static을 보존했다. 상시 백업은 꺼져 있다. current26 CPU검사/5.350초와 앞선 nonempty6 목록 로컬 통합27.453초는 별도 모의 provider 근거다. 유한 worker의 마지막 snapshot 전에 새 domain 저장을 닫고 수락된 요청을 기다리는 절차가 다음 구현 대상이다. 실제 두 초안 종료 보존·현재 Docker 전체 용량·운영 인수·공개 참조는 미완료다. [최신 근거](validation/platform_m6_positive_trial_partial_20261012.json). Goal active/원래 범위를 유지한다.

아래 이전 기록은 당시 범위다.

현재 상태(2026-10-12/plan0.50)

v0.50에서 공개 목록·상세·비교 재조회 실패가 이전 성공 결과를 현재 결과로 남기던 UI를 수정했다. 목록/상세는 요청 전에 기존 표시를 지우고, 실패는 조회 불가로 표시한다. 비교는 빈 선택기를 잠그며 실패를0건이나 빈 정상 결과로 숨기지 않는다. 오류 원문은 textContent로 표시하고 긴 문자열도 모바일 영역 안에서 줄바꿈한다. 최종 새 비편집 설치50파일/25고정 의존성의 실제 로컬 HTTP·브라우저10흐름/8화면/24.078초가 통과했다. 합성 계정·결과·권한과503/413 응답 double이며 실제 HF/GPU 인수는 아니다. 관련 API38 CPU검사도 통과했고 최종 CSS 보완 전 v74 범위임을 구분했다. 두 UI자산 외48파일·지표·규약·실제 결과는 기존과 같다. 현재 소스의65파일 기본 후보와68파일 관리형 후보를 새로 보존했으며 미업로드다. 실제 private 앱의 마지막 확인 revision은 `f160663af378e777616be89374a20b6c38b57938`이고 이번 UI 수정은 아직 배포하지 않았다. 상시 백업은 꺼져 있고 실제 정상 초기화/재시작·현재 Docker 전체 용량·운영 인수·공개 참조는 미완료다. [최신 근거](validation/platform_m5_public_failure_ui_20261012.json). Goal active/원래 범위를 유지한다.

아래 이전 기록은 당시 범위다.

현재 상태(2026-10-12/plan0.49)

v0.49에서 별도 승인된 읽기 전용 시험을 실제 private CPU Space에서 수행했다. 실제 HF 로그인으로 현재 보이는 초안0건·분석 업로드0건을 확인하고 이전 두 모델 원본/이력 4쌍을 재대조했다. 전용 Secret으로 private Bucket 목록을 읽은 진단은 `initialization_inventory_mismatch`/exit2 경로를 반환했다. 이 진단의 RUNTIME_ERROR는 의도한 거부이며 서버·worker·DB·snapshot을 만드는 경로를 호출하지 않는다. Bucket6객체/67,684,067바이트 목록이 유지됐고 새 결과 전송·snapshot 생성은0회다. 기본 프로필 `f160663af378e777616be89374a20b6c38b57938`로 복귀한 뒤 RUNNING/cpu-basic·배포66파일의 바이트/목록 일치와 브라우저 준비 화면을 확인했다. Secret·public Static·기존 snapshot은 보존했고 상시 백업은 꺼져 있다. 현재25 CPU검사/5.652초는 로컬 근거다. 실제 정상 초기화 후 재시작 전체 인수·현재 Docker 전체 용량·운영 승인·공개 참조는 미완료이고, 이전 최대3회 시험의5회 생성 실패도 통과로 변경하지 않는다. [최신 근거](validation/platform_m6_actual_readonly_guard_20261012.json). Goal active/원래 범위를 유지한다.

아래 이전 기록은 당시 범위다.

현재 상태(2026-10-12/plan0.48)

v0.48에서 초기화 목록 불일치를 민감한 상세 없이 구분하는 진단과 `--check-initialization-baseline` 읽기 전용 모드를 추가했다. 이 모드는 목록이 일치해도 DB·서버·worker·snapshot을 만들지 않는다. 관련25 CPU검사/5.652초/exit0이 통과했고 core50 바이트는 기본 개발 후보와 같다. 실제 private CPU Space는 `8d50fbe9a05c152cb4e3365bea01c52ec0f78419`의 RUNNING/cpu-basic, Bucket은6객체/67,684,067바이트, public Static은 이전 revision으로 재확인했다. 68파일 일반 후보와70파일 읽기 전용 제안을 로컬에 준비했으며 미업로드다. 기존 초안·이력 보존 → 전용 Secret으로 목록 검사 → 기본 프로필 복귀의 별도 승인을 요청했다. 이 제안의 새 결과 전송과 snapshot 쓰기는0회다. 실제 HF guard/정상 초기화·재시작 인수는 아직 없고, 이전 최대3회 시험의5회 생성 실패는 그대로 남는다. 상시 백업은 꺼져 있고 현재 Docker 전체 용량·공개 참조·운영자 인수도 미완료다. [근거](validation/platform_m6_readonly_guard_preparation_20261012.json). Goal active/원래 범위를 유지한다.

아래 이전 기록은 당시 범위다.

현재 상태(2026-10-12/plan0.47): v0.47에서 전용 Secret으로 실제 private CPU 서버의 백업·고정 복원을 시험했다. 실제 HF 로그인으로 저장한 두 모델48+48기록의 원본/이력과 분석 JSON을 독립 보존했고, 고정 복원 후 재로그인한 원본/이력 바이트가 모두 일치했다. 공개 HTTP503/recovery_required와 실제 새 제출 거부도 확인했다. 그러나 승인된 최대3회와 달리 새 snapshot5개/529,309바이트가 관측됐다. 24MiB 총량은 지켰지만 횟수 제한은 실패했다. 즉시 PAUSED로 전송을 막고 새 백업 없는 고정 복원을 검증한 뒤 기본 private 프로필 `8d50fbe9a05c152cb4e3365bea01c52ec0f78419`의 RUNNING/cpu-basic으로 복귀했다. Secret·snapshot·공개 Static은 보존했고 상시 백업은 꺼져 있다. 유한 worker 종료 뒤 새 빈 저장소 기동이 반복된 양상에 대응해 v2의 독립 원격 snapshot 기준 목록 검사와 legacy initialize 거부를 구현했다. 관련22 CPU검사/5.497초 및 실제 소유 로컬 재기동·복원27.969초가 통과했다. 이 수정의 실제 HF 재검증은 미완료이며 새68파일 후보는 미업로드/미활성화다. [최신 근거](validation/platform_m6_live_backup_trial_20261012.json), [관리형 안내](MANAGED_SPACE_GUIDE.md). Goal active/원래 범위를 유지한다.

아래 이전 checkpoint는 당시 범위다.

현재 상태(2026-10-12/plan0.46): v0.46에서 관리형 런처의 복원 안내와 종료 처리를 보완했다. 현재 코드의 로컬 실제 서버·worker·HTTP에서 두 기존 모델48+48기록 저장, 첫 백업+worker2회, 종료, 고정 복원 후 원본/이력 일치, 공개503·새 제출 차단을24.719초/exit0로 확인했다. HF/OAuth는 명시적 로컬 test double이며 실제 HF 연결이나 Linux signal 인수는 아니다. 관련18 CPU검사/2.987초/exit0와 이전 전체328 설치의 core50 바이트 유지도 확인했다. 사용자가 Bucket 전용 토큰과 `KOEVD_BACKUP_TOKEN` Secret 등록을 완료했다고 확인했다. 값은 읽거나 출력하지 않았다. 관리형68파일 후보와 기존 private CPU Space를 쓰는70파일 제한 시험 제안을 준비했으며 미업로드/미활성화다. 최대3회·snapshot24MiB 이하 전송과 고정 복원/기본 프로필 복귀에 대한 별도 승인을 요청했다. 실제 관리형 HF 백업·재시작 복구, 현재 Docker 전체 용량, 공개 참조·운영자 인수는 미완료다. [최신 근거](validation/platform_m6_managed_lifecycle_20261012.json), [관리형 안내](MANAGED_SPACE_GUIDE.md). Goal active/원래 범위를 유지한다.

아래 이전 checkpoint는 당시 범위다.

현재 상태(2026-10-12/plan0.45): v0.45에서 비공개 개발 Space의 다운로드를 파일 준비 → 명시적 Save 링크로 보완했다. 현재 revision `5504a5e57e173c96b17272ee0e4c1608e859759c`의 배포 파일66개가 일치하고 RUNNING/cpu-basic이다. 실제 Chrome의48+48기록 분석에서 JSONL/CSV/Markdown/JSON/HTML 다섯 파일 모두 새로 저장되어 native 바이트와 일치했다. 로컬 UI는 삭제된 세션의 지연 다운로드가 Save 링크를 다시 만들지 않는지까지 검증했다. 별도 관리형 서버·백업 후보68파일과 stale 소스/운영 권한 상속 거부를 구현했다. 새 비편집 설치의 전체328 CPU검사·50소스/자산·25런타임 버전 대조와 이후 관련15검사는 별도 근거다. 관리형 후보는 미업로드/미활성화이며 전용 Secret 설정 완료도 아직 확인되지 않았다. 앱 자동 백업·재시작 복구/최신 상태·RPO·운영자 승인·공개 참조·현재 Docker 전체 용량은 미완료다. [최신 근거](validation/platform_m5_m6_prepared_downloads_managed_20261012.json), [관리형 안내](MANAGED_SPACE_GUIDE.md). Goal active/원래 범위를 유지한다.

아래 이전 checkpoint는 당시 범위다.

현재 상태(2026-10-12/plan0.44): v0.44에서 사용자에게 저장 대상·정확한 스냅샷·용량 한도를 제시하고 명시적 승인을 받은 뒤 비공개 `KETI-NLP/KoEVD-Platform-Backups-Dev`를 만들었다. 포함 용량0/3TB를 재확인했고 추가 구독·유료 용량 구매 없이67,154,758바이트 스냅샷1개를 전송했다. 별도 재다운로드·오프라인 복원 후 실제 두 모델35,340기록의 원본·상태·이력과 고정 checkpoint가 일치했다. 복원 공개조회503/변경 차단·없는 객체 조회 실패의 기존 사본 보존도 확인했다. 실행95.062초/exit0이며 코드·GPU·서버 설정은 바꾸지 않았다. 앱의 자동 백업·재시작 복구/최신 상태·RPO·운영자 승인·공개 참조·추가3개 browser 다운로드는 미완료다. [최신 근거](validation/platform_m6_actual_private_cloud_20261012.json). Goal active/원래 범위를 유지한다.

아래 이전 checkpoint는 당시 기록이다. [연결 준비](TEAM_BACKUP_CONNECTION.md).

현재 상태(2026-10-12/plan0.43): v0.43에서 실제 Team 가입을 API로 확인하고 별도 비공개 CPU Docker Space `KETI-NLP/KoEVD-Platform-Dev`를 배포했다. 현재 revision `03e79a75ee35570b83948343d521f684a38fce01`의 payload65개+manifest가 일치하고 RUNNING/cpu-basic이다. 실제 HF 로그인 후 두 모델48+48기록의 업로드·분석·대응 비교와 비공개 draft2건 저장/재조회를 확인했다. 내려받은 원본 JSON 내용·HF OAuth 생성 이력과 분석 JSON/HTML의 native 바이트가 일치한다. v64의 별도 HTTP 검증에서는 다섯 출력·세션 격리·삭제가 통과했다. 현재 브라우저의 나머지3개 다운로드는 확인하지 못했다. Private proxy cookie 누락을 수정했고 관련4+6+3+11 검사가 통과했다. 기존 전체310은 이전 설치 근거다. Public Static은 그대로이며 영구 저장·운영자 승인·공개 참조/공식 순위·production은 미완료다. [최신 근거](validation/platform_m5_m6_team_hosted_20261012.json) Goal active/원래 범위를 유지한다.

아래 이전 검증의 범위·수치는 당시 근거다. [운영 준비](TEAM_SPACE_OPERATIONS.md).

Recorded: 2026-10-12. Local development checkout, package version 0.2.0.
The overall platform remains a release candidate with shared registration incomplete.
The analysis preview is now Public Static under explicit user approval.
[Current receipt](validation/platform_m5_public_static_20261012.json): actual anonymous
35340-record direct analysis/all5 native files and actual96-record Hub-parent
file flow/stable responsive layout pass. Container evidence applies to the server
route; it is not required for this Static route. OAuth/Bucket choices do not replace
identity, validation, versioned storage, consent and withdrawal requirements.
The following private-hosting/blocked checkpoints are historical.

This was a pre-publication development candidate. A private Static Space has been
created and its uploaded bytes/API RUNNING state verified. Full direct hosted
analysis and the internal report iframe pass. Hub-parent initial rendering is now
observed; its complete file flow, actual submitter identity and shared operational
acceptance remain unverified. The full audit is incomplete.

Plan0.41 revalidated the external blockers without rerunning passed tests. Local
and GPU_NODE container inventories are empty; no actual OAuth app ID or approved
cloud validation target has been supplied. Roles/baselines remain empty and real
review/publication preparations are unapproved. Installed50/server64/Static19
sources and original GPU/hosted evidence remain exact. The repeated blocker audit
passes; the goal is incomplete and awaits external conditions.
[Audit](validation/platform_rc_external_gates_20261011.json),
[handoff](EXTERNAL_ACCEPTANCE_HANDOFF.md). The v61 source ZIP is a prior checkpoint
and omits these new audit documents. No new implementation, test pass, browser
acceptance, publication or production deployment is claimed.

## Implemented user workflow

1. Run your target through a vLLM-compatible endpoint using the [own-model guide](OWN_MODEL_GUIDE.md).
2. Preserve generations, measure the frozen responses, and export portable results
   against an independently prepared input index. See the [registered full run](FULL_STANDARD_RUN_GUIDE.md).
3. Build the [offline diagnostic report](DIAGNOSTICS_GUIDE.md), including all cases,
   task/subset/framing denominators, metadata groups and output-quality diagnostics.
4. Upload the same result files to the [local comparison app](SPACES_GUIDE.md).
   Compare two uploads or an operator-approved reference; download the shared analysis.
5. Request publication separately through the [submission workflow](SUBMISSIONS_GUIDE.md).
   Candidate status, operator review, publication and official metric ranking remain
   separate decisions. The default policy grants no official rank.

## Actual integration evidence

Two actual targets, Qwen/Qwen3-8B and Qwen/Qwen3-4B, completed the full GPU workflow.
Each has 15,011 generation requests and 17,670 portable records; the combined report
has 35,340 records. Task 1/2/3/4/5 counts are 2000/8000/2659/2659/2352 per target.
Task 4 reuses Task 3 responses; Task 2 has four variants and Task 5 three framings.

[The full two-model receipt](validation/platform_m4_m5_full_two_actual_20261009.json)
records terminal exit0 for all13 stages, independent raw replay, the outside pinned
registry/index and ZIP checksum, and exact agreement between node analysis, local
CLI and native HTTP analysis. The actual combined HTML is199,373,743bytes.
Browser checks covered12tabs, paired filters, full cases/search and mobile layouts.

Measurement and interpretation limits remain visible:

- Task 3 classifier-unsafe labels:8B51/2659 and4B85/2659; these are classifier outputs,
  not human accuracy or universal safety conclusions.
- Task 5 strict-invalid records:8B2 and4B3; unsafe mock selections664/2350 and909/2349
  use valid denominators, with separate all-record denominators2352.
- Length-limited Task 3 responses:8B249 and4B213. Their reuse in Task4 does not create
  additional unique generated responses.
- The [frozen-response audit](GPU_MEASUREMENT_MATRIX_RESULTS.md) found strategy
  batch/order/precision differences. Safety FP32 requests retained mixed parameter
  dtypes. Neither stability nor hash matching proves classifier accuracy.
- Task4 is descriptive. Label-conditioned Task3→5 groups are diagnostic; their
  membership varies by model. No aggregate ethics score is defined.

## Current CPU and CI checkpoint

The current noneditable package passed328 CPU tests in131.520s with failure/error/skip0; both namespaces (50 source/assets) and25 runtime versions were rechecked. The subsequent materializer/lifecycle15 tests pass in3.021s. This is not a full333-suite rerun. [Current receipt](validation/platform_m5_m6_prepared_downloads_managed_20261012.json). Earlier checkpoints below retain their dated scope.

The v0.40 source-only bundle excludes generated egg-info/dist-info while retaining original files and historical ZIP verification. Seven scoped source-integrity tests pass, including metadata-change inventory stability; the prior installed core310 result is separate. Current installed50 files, server64-file candidate and Static19 engine files remain byte-exact. Original actual two-model result digests and hosted-evidence digest also match. A full311 rerun/new browser/GPU/remote acceptance is not claimed. [Packaging receipt](validation/platform_rc_source_hygiene_20261011.json).

The current v0.39 noneditable wheel passed310 CPU tests in142.623s, failure/error/skip0, pip check and50 exact installed code/assets. Explicit public OAuth requires client ID plus PKCE and forbids a secret; default confidential mode still requires a secret. Synthetic provider/HTTP/CLI evidence does not prove actual HF login. [Current receipt](validation/platform_m6_public_oauth_20261011.json), [configuration](OAUTH_SUBMISSION_GUIDE.md). A new64-file server candidate preserves empty roles/baselines and no-rank. Earlier checkpoints below retain their original scope.

The v0.38 hosted validator has3 passing credential boundary tests plus real owner-access
preflight and Node syntax checks. Installed50 core/assets are unchanged and exact.
The prior299 full-suite result remains separate; a full302 rerun is not claimed.

The v0.37 exact installed candidate passed299 CPU tests in158.045s with failure/error/skip0.
[Current receipt](validation/platform_m5_static_hosting_20261011.json). The earlier294-test CPU suite passed149.037s, exit0, with no failures, errors or skips, using the exact installed candidate runtime and current scripts/tests on Python3.12.14 and Node24.19.0. pip check passed. [Audit receipt](validation/platform_rc_audit_20261009.json). Earlier sandbox temporary-path/hardlink failures were retained; the valid run used a fresh owned path with approved local permissions.

CI now installs the dev/serve extras, Node24 and checks dependencies. The workflow is included in the source bundle; other hidden files remain excluded. This local pass does not prove that the unpublished GitHub Python3.10/3.12 matrix has executed.

The v0.38 [hosted receipt](validation/platform_m5_static_hosted_ui_20261011.json) covers
actual full35340/resamples100 analysis in176.241s, all5 native outputs, GET17,
HF fixed-asset redirects2, separate asset refetches1, POST/unexpected requests/errors0.
Original response files remain in browser memory; no result publication took place.

## Requirement-by-requirement audit

| Requirement | Authoritative evidence and tested scope | Remaining boundary |
|---|---|---|
| M0/R1: versions, input set, install and endpoint | Pinned protocol registry, release lock, independent full index; actual B300 targets and Linux installed native runtime | Current CI matrix execution is not claimed before GitHub runs it |
| M1: schema, legacy/export, tamper and denominators | Current result/protocol tests; both actual raw reexports exactly match portable artifacts | Uploaded model identity remains self-reported |
| M2/R2: interruption, retry, stable output and resume | Local HTTP/subprocess tests in test_runner_v2.py; actual frozen full generations | Fault injection tests are CPU integration evidence, not extra GPU runs |
| M3/R4: analysis, uncertainty and offline cases | Actual full two-model HTML/CLI/CSV/JSON and browser evidence | Interpretation stays observational |
| M4/R3/R6: two targets and measurement audit | Actual full two-target receipt plus independent frozen matrix replay | Human adjudication/classifier accuracy are not established; limited metrics excluded |
| M5/R5/R7: upload, compare, download, isolation and escaping | Full native/Public Static evidence; v67 real Chrome96 records/comparison/all5 fresh native files; local delayed-download deletion race/isolation and66 current deployed bytes exact | Current Docker full-size acceptance and approved public raw references remain unconfirmed |
| M6/R8: publication controls and identity | Actual native HF OAuth login, two private drafts and hf_oauth create events; existing ACL/revision/no-rank contracts | Real operator permission/generation/policy review and public production migration remain incomplete |
| M6/R9: original storage, restart, concurrent requests and recovery | Local SQLite/restart/snapshot evidence; actual private Bucket67MB upload/readback/fresh fetch/offline restore of35340 records, original/state/history/checkpoint equality and recovery quarantine | Default hosted app disk is ephemeral; managed68-file candidate,18 CPU tests and actual local96 HTTP/worker/pinned restore pass (provider doubles); actual HF private snapshot/fixed restoration pass; count bound failed and default profile restored. New initialization guard lacks actual HF revalidation; current recovery/remote commit/RPO and operator release remain unverified |
| R10: release artifacts, policy and documentation | Actual HF Docker build/run,66 deployed payload bytes exact, scoped tests and source candidate | Current GitHub CI, approved public raw references and operational acceptance remain incomplete |

Each CPU row must be read with its dated, scoped receipt; test presence alone
does not establish a pass. Full328 and subsequent15 materializer/lifecycle checks
are separate scopes. Actual all5 browser downloads cover the current space.js behavior.
Actual GPU and private app checks use real target outputs;
synthetic identities, policies and provider replies remain explicitly synthetic.

## Actual full private storage and candidate admission

[The full private receipt](validation/platform_m5_m6_full_private_review_20261009.json) covers both actual17,670-record drafts, exact decoded JSON/state/history across reopen and snapshot restore, and idempotent retries. The67,154,758-byte local snapshot remains private; restored public reads return503 and mutations stay blocked. Each target produced47 candidate metrics and zero official-rank-eligible metrics. Task3/4 and label-conditioned exclusions remained effective. The actor was a local validation assertion, not an HF identity; no publication, operator attestation, policy approval, recovery release or cloud write occurred.

Full operator review preparations bind the original184-file execution manifest, exact results and14 evidence files per model. Unapproved real reference catalogs and generation preparations were rejected. Reviewer/rights decisions remain empty. This completes preparation rather than the independent review itself.

## Hosting and operation gates

The optional [Static deployment candidate](STATIC_SPACES_GUIDE.md) now executes
the identical Python analysis engine in a browser worker. Full actual two-target
results (35,340 records) passed private localhost browser analysis in101.490s
with resamples0; all five files exactly match the native Python output. Separate
synthetic resamples100 and adversarial resamples20 browser checks also matched.
This changes the available analysis-hosting route, not the M6 acceptance scope.
It has no shared submission backend or approved real public references. In v0.37
full actual resamples100 analysis171.729s also matched all five files; private HF
source hosting is verified. The later v0.38 receipt verifies direct hosted analysis
and the internal report iframe; Hub-parent/submitter identity remains unverified.
Related49 CPU regression tests passed22.197s. The earlier294
test checkpoint predates the new bridge; it is not a full-suite claim for this
addition. [Static validation receipt](validation/platform_m5_static_browser_20261011.json).

- Destination: [KETI-NLP/KoEVD-Explorer](https://huggingface.co/spaces/KETI-NLP/KoEVD-Explorer), private Static development Space.
  Revision0339d618b970737ec6d0b102f5ba1df9a78c6588 is RUNNING with hardwareNone; all22
  uploaded candidate files match. Later signed owner access verified the full direct
  hosted app/internal report iframe with exact native outputs; earlier bearer401
  probes remain historical. Hub-parent/submitter OAuth stays unverified.
  No actual target outputs/DB/credentials were uploaded.
  The earlier Docker attempt returned402 and404; that historical scope is in the
  [organization receipt](validation/platform_space_org_recheck_20261008.json).
- Real Docker/hosted execution requires an available runtime or an activated
  organization plan. Native Linux UID0/1000 checks are [separate evidence](SPACES_RUNTIME_VALIDATION.md).
- CLI authentication does not provision the web OAuth app. Native hf_oauth Space
  configuration needs a created Space before actual callback/login verification.
- The SQLite adapter requires operator-owned local disk. A fresh NFS database
  failed at server startup; its failed DB/logs were preserved. A separate local
  /tmp runtime passed. NFS persistence/recovery is not certified.
- Actual cloud backup/restore needs an explicitly approved existing private Bucket.
  Backup interval is not a guaranteed RPO or synchronous remote commit.
- Public raw references require the documented operator publication attestation.
  The candidate catalog has no actual public baselines; two private uploads already
  support comparison. Private validation outputs are not silently published.
- Production policy ratification, operator recovery reconciliation, public posting
  and paid resources require their own authorized action. No such action is implied
  by a passing local test or matching hash.

The [development plan](PLATFORM_DEVELOPMENT_PLAN.md) retains the original scope.
Missing external gates remain missing; this checklist does not replace them with
native tests, synthetic references, or assertions of approval.

