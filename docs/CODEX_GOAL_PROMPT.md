# KoEVD 플랫폼 지속 개발용 Codex 목표 프롬프트

- 작성·갱신일: 2026-10-12
- 기준 계획: [PLATFORM_DEVELOPMENT_PLAN.md](PLATFORM_DEVELOPMENT_PLAN.md), v0.59
- 용도: 검토 가능한 release candidate까지 개발을 이어가기 위한 목표 문안.

## 사용 방법과 현재 상태

v0.59에서 사용자가 지정·전송 승인한 CPU_VALIDATION_NODE의 기존 Docker를 사용해 기본 후보를 실제 검증했다. 이미지1개·개별2개/대응 비교1개의15파일806,504,041바이트 HTTP/CLI 일치·비교의 이전 로컬/HF 일치가 통과했다. 기본CMD/UID:GID1000:1000/network none/포트0·정확한 소유 컨테이너 종료exit0/제거를 확인했다. 최종 컨테이너 검사277.752초·Python3.12.15·분석 패키지43파일·웹lock을 검증했다. 압축 해제 상한/누락Entrypoint 검사기의 초기 실패를 보존하고, inspect JSON을 파싱하는 수정과 관련7 CPU검사0.029초가 통과했다. 제품 core50와 HF 배포는 그대로다. 사용자가 Codex에 위임한 기술 검토에서는 GPU 실행 당시184소스·13단계·두 모델28증거파일·각17,670기록/index·Task3/4 재사용과 잘림/측정 한계를 대조했다. AI 검토를 별도 사람의 증명이나 정확도/공개/공식순위 승인으로 바꾸지 않는다. [컨테이너 근거](validation/platform_m5_actual_b200_container_v92.json), [위임 검토 근거](validation/platform_m4_delegated_generation_review_v92.json).

아래 기록은 당시 범위다.

v0.58에서 사람이 승인한 실제 private CPU 전체 전송 인수를 완료했다. Qwen3-8B/4B 각17,670기록 JSON을 각1회/합계89,396,889바이트 전송하고 대응 비교1건을 실행했다. 다섯 다운로드405,679,557바이트가 독립 native 파일과 직접 바이트 일치했으며 로컬 hash 재검사도 통과했다. 총259.906초/exit0, job terminal·pending false·검증 session2개 cleanup200/200·다른 session의 출력 접근 거부를 확인했다. 종료 후 같은 8e692c88 revision/private Docker/RUNNING/cpu-basic/단일 replica를 읽기 전용으로 재확인했다. 제품 core50·기본 프로필을 보존했고 제출/Bucket/snapshot/재배포/restart/Secret/공개/유료 변경은 없다. 이번 승인은 이 제한 시험 완료로 소진됐으며 개별 분석2개나 실제 hosted browser/OAuth·local image UID/CMD·분류 정확도·운영자/공개 권한을 새로 인수한 것은 아니다. [근거](validation/platform_m5_actual_full_hosted_20261012.json).

아래 기록은 당시 범위다.

v0.57에서 현재 설치본의 실제 로컬 앱 화면으로 두 전체 결과17,670+17,670기록을 업로드했다. 합계89,396,889바이트 입력과 iframe의199,373,743바이트 HTML을 처리했고, Save 링크로 저장한 다섯 파일405,679,557바이트가 독립 CLI 파일과 일치했다. 전체158.875초/exit0, 분석·preview117.702초이며 비교·측정 한계·한국어 사례·모바일 화면을 시각 검토했다. 세션 격리/삭제·삭제 후 지연 다운로드 링크 거부·실제 서버 PID 일치/종료/포트 거부가 통과했다. 제품 core50는 그대로며 검증기의 대기 시간 옵션/관측 시간만 추가했다. 분석 전용 로컬 서버의 검사로 HF/OAuth/Docker나 새 추론 근거가 아니다. 실제 HF 전체 전송은 별도 승인 대기다. [근거](validation/platform_m5_current_full_app_browser_20261012.json).

아래 기록은 당시 범위다.

v0.56에서 HF 전체 전송 검사기의 opt-in 분기를 설치된 로컬 HTTP 서버로 검증했다. 명시적 HF 접근 모의 응답과 외부 소켓 차단 아래 실제48+48기록 두 업로드·비교1건·다섯 보고서 12,514,875바이트의 독립 CLI 일치·다른 세션 접근 거부·두 세션 삭제를 확인했다. 첫 Windows 가상환경 핸들 종료 검사는 포트 잔류로 실패를 보존했고, 실제 Python PID를 직접 소유한 재실행13.937초에서 PID 일치·종료·연결 거부가 통과했다. HF 요청/전송은0회, 제품 core50와 배포 프로필은 그대로다. 종료된 v83 승인을 재사용하지 않으며 전체 HF 전송은 별도 승인 대기다. [근거](validation/platform_m5_hosted_transfer_fixture_20261012.json).

아래 기록은 당시 범위다.

v0.55에서 현재 private CPU 기본 앱에 두 모델 전체 결과를 일시 분석하는 별도 전송 인수 도구를 추가했다. 기본 preflight는 결과 body/analysis POST/DELETE 없이 resource 접근·고정8e692c88 revision·RUNNING/cpu-basic·단일 replica·한도/익명 app 경계를 읽는다. 실제 HF preflight2.078초/exit0·결과 전송0/job0과 최종6 CPU guard/0.276초가 통과했다. core50 소스는 기존 설치/배포 검증본과 같다. 새 제안은 두 실제17,670+17,670기록 JSON89,396,889바이트 각1회·대응 비교 job1·다섯 native405,679,557바이트와 직접 stream 대조·download512MiB 한도·두 owned analysis session cleanup만 포함한다. 전체 전송은 미승인/미실행이며 앞선 종료된96기록 시험 승인을 재사용하지 않는다. 새 script는 host-side 검사이며 이미 배포된 image를 변경하지 않았다. 이 준비는 실제 full hosted·local image UID/CMD·큰 report UI·운영자 판단·공개 권한을 대신하지 않는다. [최신 근거](validation/platform_m5_full_hosted_preparation_20261012.json), [실행 범위](HOSTED_FULL_ANALYSIS_ACCEPTANCE.md). Goal 도구의 현재 상태active를 확인했고 원래 목표/완료 조건을 유지한다.

아래 Goal 상태/체크포인트는 당시 기록이다.

v0.54에서 별도 승인된 실제 private CPU 유한 종료 시험을 완료했다. 기준9개 보존·새 snapshot3개/396,229바이트로3회/24MiB 한도를 지켰다. 현재 코드에 결합한 parent 종료 로그 뒤 마지막 snapshot이 생겼고 finite worker2회 완료·후속 기동 initialization_inventory_mismatch 거부를 확인했다. 별도 다운로드한3사본 중 두 현재48+48기록 원본/이력이 모두 일치한 digest를 내용으로 선택했다. 고정 복원 후 실제 HF 재로그인의 두 원본·두 이력4파일이 복원 전 native 다운로드와 바이트 일치했고 새 저장/공개 조회 거부·worker OFF·복구 대기를 확인했다. 최신 기본 revision `8e692c88d412d6305879473e3e8e74d46bb7dd2c`의 RUNNING/cpu-basic·66파일 바이트/목록 일치로 복귀했다. Bucket12객체/68,382,317바이트·Secret·public Static을 보존했으며 상시 백업은 꺼져 있다. 이 승인은 시험 종료로 소진됐다. 과거 누락4B 이력이 복구됐다고 주장하거나 과거 횟수 실패를 소급 통과 처리하지 않는다. 실제 HF host restart 이벤트 로그·상시 운영/RPO·현재 Docker 전체 용량·운영자 정책/복구 인수·공개 참조는 미확보다. 실제 GPU/F1/분류 정확도의 새 검증은 아니다. [최신 근거](validation/platform_m6_actual_finite_shutdown_20261012.json). 전체 목표/완료 조건은 유지하며 전체 완료를 선언하지 않는다.

Goal 도구 마지막 상태는 blocked(v82)이며 이번 사용자 승인 작업은 진행으로 기록한다. 아래 상태 메모는 당시 범위다.

현재 목표 상태: **blocked** (2026-10-12/v82). 2026-10-12의 v80·v81·v82에서 같은 필수 외부 조건을3회 연속 재확인했다. 새 HF 시험 승인 답변, 실제 Docker 실행 환경/결과, 독립 운영자 검토·원문 공개 범위가 미확보이며 현재 범위에서 다음 필수 작업을 실행할 수 없다. 이전 두 턴과 이번 턴은 no progress로 기록하며 사용자 답변 대기는 live job의 verified wait가 아니다. Goal 도구가 blocked를 반환했다. 원래 전체 목표·완료 조건·코드·후보·기존 근거는 보존했고 전체 완료를 선언하지 않는다. 실행 승인 또는 인수 결과가 도착하면 해당 단계부터 재개한다. 현재 private CPU/default revision f65a8b1065b934e649e545043c4ac89b18c2d4a5는 RUNNING/cpu-basic/replica1, Bucket9객체/67,986,088바이트가 유지됐다. 이번 추가 전송·배포·tests는0회다.

아래 구현 체크포인트는 당시 상태다.

v0.53에서 기본 Docker 이미지의 CMD를 유지한 로컬 인수 도구와 노드 실행 절차를 추가했다. 이미지 ID·자신의 container ID/label·UID/GID1000·network none·미공개 포트·종료/제거를 외부 실행기에서 확인하고, 내부 HTTP 검사기는 외부 소유 loopback 서버에 연결한다. current source50는 v0.52 설치/352 전체 검사 때와 같고, 새 script 관련12 guard검사/0.111초가 통과했다. 새 연결 경로의 현재 로컬 실제 서버/CLI에서 기존 두 실제 모델 각17,670기록·총35,340기록의 대응 비교와 JSON/JSONL/CSV/Markdown/HTML5파일이 바이트 일치했다. 실행252.344초/exit0, 소유 server terminal이며 Windows terminate의 관측 exit1을 보존했다. 이번에는 개별 모델 보고서2개를 새로 검사하지 않았다. 컨테이너 도구0개라 실제 Docker 실행은 미검증이며 HF/OAuth/새 inference/외부 전송도0회다. 66파일 기본 context ZIP과 실행 안내를 로컬에 준비했고 기존 HF 제한 시험 재승인 질문은 계속 pending이다. 실제 HF 두 현재 초안 종료 보존·Docker 전체 용량·운영 인수·공개 참조를 미완료로 유지한다. [최신 근거](validation/platform_m5_container_runtime_preparation_20261012.json), [실행 절차](CONTAINER_RUNTIME_ACCEPTANCE.md). Goal active/원래 범위를 유지한다.

아래 v0.52 이하는 당시 기록이다.

v0.52에서 유한 worker의 마지막 capture 전에 소유한 HTTP 서버를 종료·회수하고 전용 stdin으로 마지막 백업을 허용하는 순서를 구현했다. 현재 새 비편집 설치의 source50·고정 의존성25·pip check와 전체352 CPU검사/146.942초/failures0/errors0/skips0가 통과했다. 현재9개 digest를 metadata-only double로 재현한 실제 소유 로컬 HTTP/worker 통합29.344초에서 두48+48기록 원본/이력의 고정 복원 일치, 마지막 SQLite capture 전 서버 종료, 이후 연결 거부, 새 빈 초기화 거부, 복원 대기와 credential 분리를 확인했다. HF/OAuth는 명시적 double이다. Windows 상태 파일 교체의 일시적 WinError5/32/33에만 최대6회·총0.62초 재시도하며 지속 오류는 전달한다. 관측된 WinError5의 근본 원인은 미확정이다. 기본65·관리형68파일 및 초기1+worker2/24MiB/600초의70파일 제안을 로컬에 준비했고 이번 외부 전송·배포는0회다. 앞서 승인된 v0.51 시험은 종료됐으며 새 제안의 권한으로 재사용하지 않는다. 실제 마지막 기본 revision은 `f65a8b1065b934e649e545043c4ac89b18c2d4a5`, 상시 백업 OFF다. 이전 실제 새4B 이력 누락은 복구됐다고 주장하지 않는다. 실제 HF 두 현재 초안의 종료 보존·현재 Docker 전체 용량·운영 인수·공개 참조는 미완료다. [최신 근거](validation/platform_m6_finite_final_capture_20261012.json). Goal active/원래 범위를 유지한다.

아래 v0.51 이하는 당시 기록이다.

v0.51에서 별도 승인된 private CPU 정상 기동 시험의 새 snapshot3개/302,021바이트와 finite worker2회 완료·후속 초기화의 `initialization_inventory_mismatch` 거부를 확인했다. 이번 횟수/용량 한도는 통과했지만 두 초안 보존은 미완료다. 실제 HF 로그인으로8B/4B 초안 저장을 관찰했고 종료 경계의4B 다운로드가503을 반환했다. 독립 다운로드/외부 index·registry 검사에서 마지막 사본에는8B48기록/이력만 있고 새4B 이력은 없었다. 과거4B 사본으로 대체하지 않았다.8B의 고정 복원·실제 재로그인 전후 원본/이력 바이트 일치와 새 저장 거부·공개 조회 불가 UI는 확인했다. 승인된 최신 UI 기본 프로필 `f65a8b1065b934e649e545043c4ac89b18c2d4a5`의 RUNNING/cpu-basic·66파일 바이트/목록 일치로 복귀했고9백업/67,986,088바이트·Secret·public Static을 보존했다. 상시 백업은 꺼져 있다. current26 CPU검사/5.350초와 앞선 nonempty6 목록 로컬 통합27.453초는 별도 모의 provider 근거다. 유한 worker의 마지막 snapshot 전에 새 domain 저장을 닫고 수락된 요청을 기다리는 절차가 다음 구현 대상이다. 실제 두 초안 종료 보존·현재 Docker 전체 용량·운영 인수·공개 참조는 미완료다. [최신 근거](validation/platform_m6_positive_trial_partial_20261012.json). Goal active/원래 범위를 유지한다.

아래 v0.50 이하는 당시 기록이다.

v0.50에서 공개 목록·상세·비교 재조회 실패가 이전 성공 결과를 현재 결과로 남기던 UI를 수정했다. 목록/상세는 요청 전에 기존 표시를 지우고, 실패는 조회 불가로 표시한다. 비교는 빈 선택기를 잠그며 실패를0건이나 빈 정상 결과로 숨기지 않는다. 오류 원문은 textContent로 표시하고 긴 문자열도 모바일 영역 안에서 줄바꿈한다. 최종 새 비편집 설치50파일/25고정 의존성의 실제 로컬 HTTP·브라우저10흐름/8화면/24.078초가 통과했다. 합성 계정·결과·권한과503/413 응답 double이며 실제 HF/GPU 인수는 아니다. 관련 API38 CPU검사도 통과했고 최종 CSS 보완 전 v74 범위임을 구분했다. 두 UI자산 외48파일·지표·규약·실제 결과는 기존과 같다. 현재 소스의65파일 기본 후보와68파일 관리형 후보를 새로 보존했으며 미업로드다. 실제 private 앱의 마지막 확인 revision은 `f160663af378e777616be89374a20b6c38b57938`이고 이번 UI 수정은 아직 배포하지 않았다. 상시 백업은 꺼져 있고 실제 정상 초기화/재시작·현재 Docker 전체 용량·운영 인수·공개 참조는 미완료다. [최신 근거](validation/platform_m5_public_failure_ui_20261012.json). Goal active/원래 범위를 유지한다.

아래 v0.49 이하는 당시 기록이다.

v0.49에서 별도 승인된 읽기 전용 시험을 실제 private CPU Space에서 수행했다. 실제 HF 로그인으로 현재 보이는 초안0건·분석 업로드0건을 확인하고 이전 두 모델 원본/이력 4쌍을 재대조했다. 전용 Secret으로 private Bucket 목록을 읽은 진단은 `initialization_inventory_mismatch`/exit2 경로를 반환했다. 이 진단의 RUNTIME_ERROR는 의도한 거부이며 서버·worker·DB·snapshot을 만드는 경로를 호출하지 않는다. Bucket6객체/67,684,067바이트 목록이 유지됐고 새 결과 전송·snapshot 생성은0회다. 기본 프로필 `f160663af378e777616be89374a20b6c38b57938`로 복귀한 뒤 RUNNING/cpu-basic·배포66파일의 바이트/목록 일치와 브라우저 준비 화면을 확인했다. Secret·public Static·기존 snapshot은 보존했고 상시 백업은 꺼져 있다. 현재25 CPU검사/5.652초는 로컬 근거다. 실제 정상 초기화 후 재시작 전체 인수·현재 Docker 전체 용량·운영 승인·공개 참조는 미완료이고, 이전 최대3회 시험의5회 생성 실패도 통과로 변경하지 않는다. [최신 근거](validation/platform_m6_actual_readonly_guard_20261012.json). Goal active/원래 범위를 유지한다.

아래 v0.48 이하는 당시 기록이다.

v0.48에서 초기화 목록 불일치를 민감한 상세 없이 구분하는 진단과 `--check-initialization-baseline` 읽기 전용 모드를 추가했다. 이 모드는 목록이 일치해도 DB·서버·worker·snapshot을 만들지 않는다. 관련25 CPU검사/5.652초/exit0이 통과했고 core50 바이트는 기본 개발 후보와 같다. 실제 private CPU Space는 `8d50fbe9a05c152cb4e3365bea01c52ec0f78419`의 RUNNING/cpu-basic, Bucket은6객체/67,684,067바이트, public Static은 이전 revision으로 재확인했다. 68파일 일반 후보와70파일 읽기 전용 제안을 로컬에 준비했으며 미업로드다. 기존 초안·이력 보존 → 전용 Secret으로 목록 검사 → 기본 프로필 복귀의 별도 승인을 요청했다. 이 제안의 새 결과 전송과 snapshot 쓰기는0회다. 실제 HF guard/정상 초기화·재시작 인수는 아직 없고, 이전 최대3회 시험의5회 생성 실패는 그대로 남는다. 상시 백업은 꺼져 있고 현재 Docker 전체 용량·공개 참조·운영자 인수도 미완료다. [근거](validation/platform_m6_readonly_guard_preparation_20261012.json). Goal active/원래 범위를 유지한다.

아래 v0.47 이하는 당시 기록이다.

v0.47에서 전용 Secret으로 실제 private CPU 서버의 백업·고정 복원을 시험했다. 실제 HF 로그인으로 저장한 두 모델48+48기록의 원본/이력과 분석 JSON을 독립 보존했고, 고정 복원 후 재로그인한 원본/이력 바이트가 모두 일치했다. 공개 HTTP503/recovery_required와 실제 새 제출 거부도 확인했다. 그러나 승인된 최대3회와 달리 새 snapshot5개/529,309바이트가 관측됐다. 24MiB 총량은 지켰지만 횟수 제한은 실패했다. 즉시 PAUSED로 전송을 막고 새 백업 없는 고정 복원을 검증한 뒤 기본 private 프로필 `8d50fbe9a05c152cb4e3365bea01c52ec0f78419`의 RUNNING/cpu-basic으로 복귀했다. Secret·snapshot·공개 Static은 보존했고 상시 백업은 꺼져 있다. 유한 worker 종료 뒤 새 빈 저장소 기동이 반복된 양상에 대응해 v2의 독립 원격 snapshot 기준 목록 검사와 legacy initialize 거부를 구현했다. 관련22 CPU검사/5.497초 및 실제 소유 로컬 재기동·복원27.969초가 통과했다. 이 수정의 실제 HF 재검증은 미완료이며 새68파일 후보는 미업로드/미활성화다. [최신 근거](validation/platform_m6_live_backup_trial_20261012.json), [관리형 안내](MANAGED_SPACE_GUIDE.md). Goal active/원래 범위를 유지한다.

아래 v0.46 이하는 당시 기록이다.

v0.46에서 관리형 런처의 복원 안내와 종료 처리를 보완했다. 현재 코드의 로컬 실제 서버·worker·HTTP에서 두 기존 모델48+48기록 저장, 첫 백업+worker2회, 종료, 고정 복원 후 원본/이력 일치, 공개503·새 제출 차단을24.719초/exit0로 확인했다. HF/OAuth는 명시적 로컬 test double이며 실제 HF 연결이나 Linux signal 인수는 아니다. 관련18 CPU검사/2.987초/exit0와 이전 전체328 설치의 core50 바이트 유지도 확인했다. 사용자가 Bucket 전용 토큰과 `KOEVD_BACKUP_TOKEN` Secret 등록을 완료했다고 확인했다. 값은 읽거나 출력하지 않았다. 관리형68파일 후보와 기존 private CPU Space를 쓰는70파일 제한 시험 제안을 준비했으며 미업로드/미활성화다. 최대3회·snapshot24MiB 이하 전송과 고정 복원/기본 프로필 복귀에 대한 별도 승인을 요청했다. 실제 관리형 HF 백업·재시작 복구, 현재 Docker 전체 용량, 공개 참조·운영자 인수는 미완료다. [최신 근거](validation/platform_m6_managed_lifecycle_20261012.json), [관리형 안내](MANAGED_SPACE_GUIDE.md). Goal active/원래 범위를 유지한다.

아래 v0.45 이하는 당시 기록이다.

v0.45에서 비공개 개발 Space의 다운로드를 파일 준비 → 명시적 Save 링크로 보완했다. 현재 revision `5504a5e57e173c96b17272ee0e4c1608e859759c`의 배포 파일66개가 일치하고 RUNNING/cpu-basic이다. 실제 Chrome의48+48기록 분석에서 JSONL/CSV/Markdown/JSON/HTML 다섯 파일 모두 새로 저장되어 native 바이트와 일치했다. 로컬 UI는 삭제된 세션의 지연 다운로드가 Save 링크를 다시 만들지 않는지까지 검증했다. 별도 관리형 서버·백업 후보68파일과 stale 소스/운영 권한 상속 거부를 구현했다. 새 비편집 설치의 전체328 CPU검사·50소스/자산·25런타임 버전 대조와 이후 관련15검사는 별도 근거다. 관리형 후보는 미업로드/미활성화이며 전용 Secret 설정 완료도 아직 확인되지 않았다. 앱 자동 백업·재시작 복구/최신 상태·RPO·운영자 승인·공개 참조·현재 Docker 전체 용량은 미완료다. [최신 근거](validation/platform_m5_m6_prepared_downloads_managed_20261012.json), [관리형 안내](MANAGED_SPACE_GUIDE.md). Goal active/원래 범위를 유지한다.

아래 v0.44 이하는 당시 기록이다.

v0.44에서 사용자에게 저장 대상·정확한 스냅샷·용량 한도를 제시하고 명시적 승인을 받은 뒤 비공개 `KETI-NLP/KoEVD-Platform-Backups-Dev`를 만들었다. 포함 용량0/3TB를 재확인했고 추가 구독·유료 용량 구매 없이67,154,758바이트 스냅샷1개를 전송했다. 별도 재다운로드·오프라인 복원 후 실제 두 모델35,340기록의 원본·상태·이력과 고정 checkpoint가 일치했다. 복원 공개조회503/변경 차단·없는 객체 조회 실패의 기존 사본 보존도 확인했다. 실행95.062초/exit0이며 코드·GPU·서버 설정은 바꾸지 않았다. 앱의 자동 백업·재시작 복구/최신 상태·RPO·운영자 승인·공개 참조·추가3개 browser 다운로드는 미완료다. [최신 근거](validation/platform_m6_actual_private_cloud_20261012.json). Goal active/원래 범위를 유지한다.

아래 v0.43 이하는 당시 기록이다.

v0.43에서 실제 Team 가입을 API로 확인하고 별도 비공개 CPU Docker Space `KETI-NLP/KoEVD-Platform-Dev`를 배포했다. 현재 revision `03e79a75ee35570b83948343d521f684a38fce01`의 payload65개+manifest가 일치하고 RUNNING/cpu-basic이다. 실제 HF 로그인 후 두 모델48+48기록의 업로드·분석·대응 비교와 비공개 draft2건 저장/재조회를 확인했다. 내려받은 원본 JSON 내용·HF OAuth 생성 이력과 분석 JSON/HTML의 native 바이트가 일치한다. v64의 별도 HTTP 검증에서는 다섯 출력·세션 격리·삭제가 통과했다. 현재 브라우저의 나머지3개 다운로드는 확인하지 못했다. Private proxy cookie 누락을 수정했고 관련4+6+3+11 검사가 통과했다. 기존 전체310은 이전 설치 근거다. Public Static은 그대로이며 영구 저장·운영자 승인·공개 참조/공식 순위·production은 미완료다. [최신 근거](validation/platform_m5_m6_team_hosted_20261012.json) Goal active/원래 범위를 유지한다.

아래 v0.42 이하는 당시 기록이다.

v0.42에서 사용자 승인으로 Public Static preview를 배포하고 익명 전체35,340기록 및 HF 부모48+48기록의 파일 분석·다섯 다운로드를 검증했다. 데이터 연구용 약관/출처를 포함했고 core50/engine19·입력은 그대로다. 관련11 CPU검사는 이전 전체310과 별개다. [최신 근거](validation/platform_m5_public_static_20261012.json). Static에는 컨테이너가 필요 없고 OAuth/Bucket은 등록 경로에 따른 선택이다. 공동 제출·권한·검토·이력·철회·정책 기능은 유지하며 다음 독립 개발 대상이다. Goal active/전체 미완료이며 원래 목표 본문은 보존한다. 아래 v0.41 이하는 당시 기록이다.

v0.41에서 같은 필수 외부조건의 반복과 현재 impasse를 확인해 blocked audit를 통과했다. 목표는 미완료이고 원래 본문·범위를 유지한다. 설치50개·서버64개·Static19개와 실제 결과·hosted 근거를 대조했지만 새 구현·테스트 통과로 보고하지 않는다. [재개 안내](EXTERNAL_ACCEPTANCE_HANDOFF.md)에 실제 앱/계정·참조/운영자·cloud·컨테이너/부모 파일 흐름의 정보별 다음 실행을 정리했다. 조건이 준비되면 원래 목표를 재개한다. 아래 v0.40 이하는 당시 기록이다.

v0.40에서 source ZIP에 포함되던 생성 egg-info/dist-info를 제외하고7개 포장 경계 검사0.369초/exit0을 통과했다. 원본 metadata와 기존 ZIP은 보존한다. 비편집 설치50개·서버64개·Static19 engine source와 기존 실제 두 target 결과 SHA는 그대로다. 전체310은 이전 core 근거이며 전체311 검사를 새로 실행한 것은 아니다. [최신 근거](validation/platform_rc_source_hygiene_20261011.json). 실제 OAuth 앱/공개 참조·운영자·cloud·컨테이너와 부모 전체 파일 흐름은 미완료다. 기존 목표 본문·범위는 유지하며 아래 v0.39 이하는 당시 기록이다.

v0.39에서 명시적 secret 없는 HF 공개 OAuth 서버 모드를 구현했다. 기본 기밀 앱 모드와 PKCE/state/권한/게시 경계는 유지한다. 최신 비편집 설치50개 source/assets 일치·pip check·전체310 CPU검사142.623초/실패·오류·skip0과 서버64파일 후보를 확인했다. 실제 HF 부모 페이지의 초기 화면은 표시됐으나 chooser/파일 분석 전체 흐름·실제 제출자 로그인은 미검증이다. [최신 근거](validation/platform_m6_public_oauth_20261011.json). 기존 Goal 본문·M0–M6와 공개 전 후보 범위를 유지하며 아래 v0.38 이하는 당시 기록이다.

v0.38에서 실제 비공개 HF Static 직접 앱의 전체35,340기록/bootstrap100 분석(176.241초),
다섯 native 파일 일치, report iframe·모바일·삭제와 전체 네트워크 요청 검사를 통과했다.
Owner cookie는 메모리로만 사용하고 원본 결과를 서버에 전송하지 않았다. 신규 경계3검사는
이전 설치 전체299와 별도 근거다. [최신 근거](validation/platform_m5_static_hosted_ui_20261011.json).
HF Hub 부모 페이지/제출자 OAuth, 공동 등록·cloud·공개 참조·운영자/원래 서버 인수는 남는다.
기존 목표 본문과 완료 범위를 유지하며 아래 v0.37 이하는 당시 기록이다.

v0.36에서 추가 Static 분석 후보의 실제 browser Python 동작을 검증했다.
실제두모델35,340기록(resamples0)과 합성/악성문자열 조건(resamples100/20)의
다섯 출력이 native Python과 바이트까지 일치했다. 관련49회귀가 통과했다.
[Static 경로](STATIC_SPACES_GUIDE.md)는 개인 분석·비교의 추가 후보이며
기존 제출·저장·공식순위/OAuth/cloud 인수 요건을 대체하지 않는다.
v0.37에서 실제 전체bootstrap100/171.729초·다섯 출력 일치와 새 설치299검사/158.045초를 확인했다.
비공개 Static 개발 Space를 생성·업로드하고22파일 일치/RUNNING을 확인했다.
실제 HF 화면·웹로그인·공동 등록과 공개 참조는 미완료다.
[최신 근거](validation/platform_m5_static_hosting_20261011.json).
기존 목표 본문과 완료 범위는 유지한다. 공개 push·production 게시·결제는 하지 않았다.

아래 **권장 목표 프롬프트** 코드 블록의 본문을 목표 입력란에 붙여 넣는다. 지원되는 명령 환경에서는 `/goal` 뒤에 본문을 사용할 수 있다. 목표에는 결과·검증 근거·보존 조건·범위·진행 방식을 명시한다. 실행은 Goal 상태, 예산, 권한과 외부 자원 조건에 따른다. 자세한 기능 설계와 작업 기록은 계획 문서를 참조한다. [공식 Goals 안내](https://developers.openai.com/cookbook/examples/codex/using_goals_in_codex).

이 파일 작성·수정만으로 새 Goal을 설정하거나 기존 Goal을 변경하지 않는다. 현재 이 대화에는 같은 플랫폼 개발을 위한 활성 Goal이 확인됐다. 기존 목표를 이어갈 때는 아래 보충 메시지를 쓰고, 같은 목표를 중복 생성하지 않는다. 다른 대화·checkout의 Goal 상태는 별도로 확인한다.

Windows 저장소 위치:

`[private-local-path]`

workspace가 ethical_survey root이면 계획 경로는 `publication/github/KoEVD/docs/PLATFORM_DEVELOPMENT_PLAN.md`이다. Linux GPU 노드에서는 실제 checkout root를 사용한다. 현재 소스에는 미커밋 개발 변경이 있으므로 **공개 main만 내려받아 현재 후보와 같은 코드라고 가정하지 않는다**. 다른 노드로 넘길 때 source 변경·protocol/환경 lock과 checksum도 함께 전달한다.

v0.35: 최신 전체 두 모델 결과35340기록의 비공개 운영자 검토 자료와 저장·재시작·스냅샷 복원·등록 정책 검증을 완료했다. 실제실행184파일소스manifest와결과를연결했고미승인catalog/검토준비본은등록검사에서거절됐다. 원본JSON내용·제출상태·이력과재요청이일치했으며67154758byte스냅샷복원후공개조회503·변경차단을유지했다. 각47지표에서공식rank는없고Task3/4·조건부비율제외가실제전체데이터에서도유지됐다. [근거](validation/platform_m5_m6_full_private_review_20261009.json). HF관리자로그인은유효하지만지정Space조회404·현재요금제정보미제공이고두환경의컨테이너CLI도없다. 공개·사람인수·복구해제·클라우드·새inference를수행하지않았다.

이전 v0.34: R1–R10의 구현·증거·외부 조건을 [릴리스 점검표](PLATFORM_RELEASE_CANDIDATE.md)에 정리했다. 최신 전체 CPU294검사149.037초/exit0/실패·오류·skip0와 pip check를 통과했다. CI의 누락된 serve/dev 의존성과 Node24·pip check를 보완했으며 공개 CI 파일을 소스 ZIP에 명시적으로 포함하되 다른 숨김 파일은 제외하는 경계를 검증했다. README의 dtype 옵션 설명과 앱 안내의 과거 두 모델 미완료 표현을 수정했다. [근거](validation/platform_rc_audit_20261009.json). Package/UI·모델·GPU 조건은 변경하지 않았다. 실제 GitHub CI matrix·컨테이너/HF 로그인·클라우드 복구·승인된 공개 원문 참조는 아직 미검증이며 전체 RC/Goal을 완료로 표시하지 않는다.

이전 v0.33: 두 실제 모델의 전체 생성·분류·내보내기·분석·통합 비교 13단계가 종료 코드0으로 완료됐다. 모델당 생성 요청15,011개·평가 기록17,670개, 전체35,340기록을 보존했다. 외부 고정 index/registry와 별도 ZIP SHA를 사용한 원본 재내보내기가 두 모델 모두 정확히 일치했다. 노드·로컬 CLI의 5개 분석 파일이 바이트까지 같고, 앱 HTTP profile도 같다. 실제 HTML199,373,743bytes의 12탭·두 실행·대응 필터·사례 검색·모바일 검사가 통과했다. [근거](validation/platform_m4_m5_full_two_actual_20261009.json). 분류 정확도·공식 순위·실제 HF 로그인/호스팅·클라우드 복구·사람 승인·공개는 별도 미완료 조건이다.

이전 v0.32: 실제4B 전체 생성2000+8000+2659+2352=15011요청의 고정 입력 대응을 확인했다. Task5 고유 source784·safe_guided/tool_forced/unsafe_induced 각각784, 누락/중복/API non-ok/빈 응답0, finish_reason stop2352이며 이전Task1/2/3 byte SHA도 그대로다. 소유 생성 서버62528은 실제ps에서 부재하고stopped_owned_child/exit0다. 같은90124/PID56870의 실제 live 상태를26번 확인하며generate passed/measure running으로 전환됐고 실제측정 child66716/argv를 확인했다. [근거](validation/platform_m4_full4b_generation_20261009.json). 최종4B Task3/4 측정 파일은 아직 없고rows null이며weight loading320/320을 측정 완료로 해석하지 않는다. Task3 length213을 보존한다. 측정/export/분석·전체 두 모델 반환 인수/실제 비교/앱/UI와외부 gates는 미완료다.

이전 v0.31: 실제4B Task3 최종2659응답의 전체 sample ID·원본 입력 digest·model 필드를 외부 고정 index와 대조했다. 누락/중복/API non-ok/빈 응답0, finish_reason stop2446/length213이며 Task1/2의 이전 byte SHA도 그대로다. [근거](validation/platform_m4_full4b_task3_input_20261009.json). 같은90124/PID56870의 실제 live 상태를17번 확인하며Task3가 완료되어Task5로 전환됐고 최종 관측123/2352/API 최종 실패0이다. GPU 코드·조건·환경을 변경·재시작하지 않았다. length213을 안전/완전 응답으로 바꾸지 않고 향후 실제 Task3/4 리포트에 각각213건 표시되는지 검증한다. 분류기 측정·Task5 최종·두 모델 전체 반환 인수/실제 비교·외부 gates는 미완료다.

이전 v0.30: 실제4B의 완료된 Task1/2 2000/8000응답을 외부 고정 index의 전체 sample ID·원본 입력 digest·model 필드와 대조했다. 누락/중복/API non-ok/빈 응답0, finish_reason stop2000/8000이며 Task2 네 variant는 각각2000이다. [근거](validation/platform_m4_full4b_partial_input_20261009.json). 초기 검사기의 read_jsonl generator 길이 처리 오류를 수정하고 원래 실패/수정 스크립트를 보존했다. GPU 작업은 변경·재시작하지 않았다. 같은90124/PID56870의4B Task3는 최종965/2659/API 최종 실패0이며 생성/측정/전체 반환 인수·실제 두 모델 비교·외부 gates는 미완료다.

이전 v0.29: 실제 Qwen3-8B의 전체 생성→두 분류기 측정→export→분석이 완료됐다. 외부 고정 index/registry로 17,670기록(Task1–5: 2000/8000/2659/2659/2352)을 검증하고 원본 로그 재내보내기와 정확히 일치함을 확인했다. 실제 HTML 98,774,358bytes의 12탭·검색·필터·모바일 검사와 native HTTP 업로드/다운로드·독립 CLI profile의 바이트 일치가 통과했다. 길이 제한 249개 응답은 Task3/4 재사용으로 각각249건이며, Task5 파싱 실패2건을 보존한다. 검사기에 fixture/actual 구분·외부 model/length 기대값을 추가했고 실제 한 실행과 기본 fixture 회귀 검사가 통과했다. Package/UI/조건/상한/v22 후보는 변경하지 않았다. [근거](validation/platform_m4_m5_full8b_report_app_20261008.json). 같은90124/PID56870의4B 생성은 진행 중이다. 두 모델 전체 반환 인수·실제 full 비교·HF hosting/login/cloud·사람/운영자 gate는 미완료이며 Goal은 active다.

이전 v0.28: 같은90124/PID56870의 실제 live 상태를25번 확인하며8B Task5가908/2352에서2352/2352로 완료돼 generate passed/measure running으로 전환됐다. Task5 최종2352 sample ID·원본 입력 digest·model 필드를 외부 고정 index와 대조했고 unique source784, safe_guided/tool_forced/unsafe_induced 각각784, API non-ok/빈 응답0, finish_reason stop2352를 확인했다. Task1/2/3의 이전 확정 byte SHA도 그대로다. 전체8B 생성2000+8000+2659+2352=15011요청이 완료됐으며 Task4는 별도 생성이 아니다. 소유 vLLM 서버56951은 실제 ps에서 부재하고 exit0/stopped_owned_child다. Controller56870과 실제 분류기 pipeline child61091의 argv를 확인했다. 최종 Task3/4 측정 파일은 아직 없고 rows는 null이며 loading weights320/320을 측정 완료로 해석하지 않는다. Task3 length-limit249건을 보존한다. [근거](validation/platform_m4_full8b_generation_20261008.json). 코드/조건/환경/후보는 변경·재시작하지 않았고 측정·export/report·4B·전체 원본 인수/실제 full app/UI는 미완료다. 외부HF/cloud/operator/공개 gates와 Goal active를 유지한다.

이전 v0.27: 같은 full GPU90124/controller56870의 실제 live 상태를25번 확인했다. 8B Task3는2270/2659에서 완료돼 Task5로 전환됐고 최종 관측248/2352/API 최종 실패0이다. 새 core Python의 읽기 전용 검사로 최종 Task1/2/3 파일2000/8000/2659행을 독립 operator index의 전체 sample ID·원본 입력 digest·model 필드와 대조했다. 외부 byte SHA771f066331e901c06ba960707add109143d75df6b1f603cf4da3439197c6b1b5/content SHA0d78a9b2ed412fa3507cf3d68db6b45d102ef0b8e24f0c65f3a10c3a987cd26d와 index seal을 검증했다. 누락·중복·API non-ok·빈 응답0이며 Task1/2 stop은2000/8000이다. Task3 stop2410/length249이며 기존 diagnostics의 length_limit 보존 경로를 확인했다. 실제 full report에서의249건 표시 검증은 이후 수행한다. [근거](validation/platform_m4_full_generation_partial_20261008.json). 초기 검사 키 expected_records 오류와 잘못 추정한 소스 파일 조회는 보존하고 실제 inputs 구조/모듈로 수정했다. 실행 중인 GPU·조건·package/UI/후보는 변경하지 않았다. 측정/4B/전체 반환 인수·HF/cloud/operator/공개 gate는 미완료이며 Goal은 active다.

이전 v0.26에서 전체 입력 두 CPU fixture의149176208bytes HTML을 실제 Chromium에서 검증했다. 각17670/전체35340사례,12탭, 두 실행 선택, core2000/overlap784/framing784 대응 필터와 valid/invalid 분리, pagination/search/metadata drilldown 및 모바일 배치가 통과했다. 로딩2.164초, console/network 오류0이며 화면8장을 저장하고 주요4장을 시각 검토했다. Task4의 descriptive-only/no-rank도 확인했다. 검사기에 --expected-runs 2 경로를 추가했고 기본1-run 경로는 유지했다. Package/UI/상한/v22 후보는 변경하지 않았다. [근거](validation/platform_m5_full_comparison_browser_20261008.json). 같은 GPU90124/PID56870은 실제 live, 관측8B Task3 1910/2659/API-ok1910/최종 실패0이며4B·full 인수는 미완료다. CPU 화면 검사를 실제 full inference/HF hosting으로 승격하지 않는다.

이전 v0.25는 전체 입력 두 CPU fixture(각17670records)의35,340사례·Task 분모·약304MB 출력과 실제 HTTP/독립 CLI 바이트 일치를 검증했다. Related guard6검사도 통과했다. [근거](validation/platform_m5_full_comparison_capacity_20261008.json). 검사기에 --comparison-only만 추가했고 package/UI/상한·v22 후보는 보존했다. 실제 두 모델 full inference나 모든 응답 길이의 용량 증거는 아니다. 같은 GPU90124/PID56870은 live며 관측8B Task3 1151/2659/API 실패0·4B 미시작이다. 다음 반복은 같은 handle/PID/로그의 verified wait, terminal 후 실제 full 인수·report/app 용량·수치/UI에 집중한다. 아래v0.24는 이전 기록이다.

현재 v0.24는 Linux Python3.12.3의 정확한 웹 lock14개·설치 `koevd_eval` 네임스페이스42파일 및 native UID0/1000의 실제 두 결과 업로드·개별/비교3profile·독립 CLI 일치를 검증했다. Context guard5검사도 통과했다. [가이드](SPACES_RUNTIME_VALIDATION.md), [근거](validation/platform_m5_native_runtime_20261008.json). Build metadata/venv 경로와 NFS0700 접근 실패는 보존하고 별도 사본·소유 /tmp에서 해결했다. 기존 NFS 권한·GPU 환경·package/UI·v22 후보를 변경하지 않았다. 전체 suite 재검사·컨테이너/HF login 통과를 주장하지 않는다. 아래 v0.23은 이전 기록이다. Full90124/controller56870은 같은 작업으로 실행 중이며 관측8B Task1/2 최종2000/8000,Task3 checkpoint701/2659/API 실패0·4B 미시작이다. 다음은 동일 handle/PID/log 확인 후 terminal full 인수를 진행한다.

현재 v0.23은 full controller·실제 input_ids 길이 검사·독립 registry 인수·최소 replay 포장을 보완했다. 관련22 CPU 검사13.109초/exit0/skips0와 B300 전체 입력/97개 고정 artifact 파일 preflight를 통과했고, full-core-v1/session90124/controller56870이 실제 실행 중이다. 두 모델 전체 생성/측정/분석/반환 인수는 미완료다. [전체 실행 가이드](FULL_STANDARD_RUN_GUIDE.md)와 [preflight/실행 근거](validation/platform_m4_full_standard_preflight_20261008.json)를 참조한다. 최초 HF symlink·새 의존성 경로 실패와 잘못된 container 길이2 근거는 보존했으며 수정한 preflight-v4만 통과 근거다.

Package source는 이번에 변경하지 않았다. Wheel `generated/backups-wheel-20261008-v22/koevd_eval-0.2.0-py3-none-any.whl`, 설치 `generated/backups-install-20261008-v22`, 배포 후보 `generated/private-space-deployment-20261008-v22`의63파일과 기존 전체278검사를 보존했다. 이번 전체 현재 suite를 새로 검사했다고 주장하지 않는다. 후보에는 실제 응답/backup/checkpoint/정책/weights/credential이 없고 worker는 자동 기동하지 않는다. 기존 실제2300기록의 양쪽 OS 백업/복구 대기와 기본candidate/no-rank·classifier 제외를 유지한다. 실제 HF Bucket은 미검증이며 주기·checkpoint가 latest state/RPO·사람 승인·생성 진위를 인증하지 않는다.

기존 GPU66554/46297은 완료됐으므로 재시작하지 않는다. 현재90124와 실제 PID/argv·status/로그부터 확인한다. Node root는 `[private-node-path]`, 출력은 `full-core-v1`, 새 환경/근거는 `incoming/full_standard_v23`다. Source v2 ZIP SHAbea8f1f0ca8f4fa5de17bf5b5cae8caec67e0d5493b553a3c202339c5321b39a와 별도 budget helper를 고정했다. Timeout만으로 재시작하지 말고 terminal 후 최소 ZIP을 밖의 canonical index/registry로 독립 재내보내기·공통 분석·앱 수치를 인수한다. 측정 한계는 [GPU 최종 결과](GPU_MEASUREMENT_MATRIX_RESULTS.md)에 남는다. 실제 cloud/운영 복구·RPO 보장·기존 비공개 HF Bucket 질문은 미완료/미응답이며 생성·전송·결제를 수행하지 않는다.

Full standard 기준선은 고정 registry/설정의 별도 실행이다. 실제 사람 판정·독립 generation receipt 인수·정책 승인·HF login/iframe·컨테이너/live Space도 남는다. KETI-NLP Docker Space 생성은 HF402/후속404로 미생성이다. 동일 조건을 반복 재시도하거나 static shell을 완성 서버로 대체하지 않는다. 현재 checkout과 [개발 계획](PLATFORM_DEVELOPMENT_PLAN.md)의 최신 증거를 우선하며 전체 Goal은 active다.

## 권장 목표 프롬프트

아래 코드 블록의 내용만 복사한다.

```text
KoEVD 저장소를 docs/PLATFORM_DEVELOPMENT_PLAN.md에 따라 구현·검증된 평가·분석·모델 비교 플랫폼 release candidate까지 지속 개발해줘. 사용자가 자신의 모델을 vLLM으로 실행하고 KoEVD Task 1–5를 평가하여 표준 results.json을 내보내고, 차트와 실제 응답 사례를 담은 오프라인 HTML 리포트를 만든 뒤, 같은 결과를 Hugging Face Spaces 앱에 업로드하여 기준 모델과 비교하고 지표별 리더보드 등록을 신청할 수 있는 상태가 목표다. 계획 설명에서 끝내지 말고 코드·작동 예시·검증 증거·운영 후보를 완성해줘.

먼저 실제 repository root, HEAD, dirty 상태와 적용되는 AGENTS.md를 확인하고 계획 전체 및 연결된 현재 검증 근거를 읽어줘. ethical_survey가 workspace root이면 저장소는 publication/github/KoEVD 아래다. 다른 노드에서는 실제 checkout을 찾아줘. 논문·데이터·가중치·기존 사용자 변경을 보존하고, 미커밋 후보를 과거 공개 main과 혼동하지 말아줘. 새로 시작할 때는 M0부터, 이미 진행 기록이 있으면 완료 증거를 확인하고 가장 중요한 미완료 작업부터 이어가줘.

M0–M6의 결과 계약·공식 입력 검증·migration/export, 생성 실행기·진행률·중단 후 재개, 공통 분석·차트·전체 사례 탐색, 측정 감사·실제 GPU 검증, Spaces 업로드·참조 비교, 제출·영구 저장·이력·철회·지표별 리더보드를 완성해줘. 현재 API와 호환되는 최소 구조를 선택하고 결정 이유를 남겨줘. 구현되지 않은 CLI나 성공하지 않은 실행을 문서에서 완료된 것으로 제시하지 말아줘.

연구 의미와 결과 해석은 다음 기준을 지켜줘.
- 기존 Task별 scorer/parser와 논문 지표를 보존하고 새 strict 진단은 별도 버전으로 구분해줘. Task 3 primary/tool-overlap/union과 Task 2 네 variant·Task 5 세 framing, 전체·유효 응답 분모를 구분해줘. 누락·실패·미분류·N/A를 안전 또는 0으로 처리하지 말아줘.
- 임의 종합 윤리 점수를 만들지 말고 Task 4 전략 빈도를 품질 순위로 사용하지 말아줘. 모델마다 집단이 달라지는 Task 3–5 조건부 비율도 대응 진단으로 제공하고 품질 순위를 부여하지 말아줘. metadata별 차이는 관찰된 경향으로 설명하고 보편적 안전·인과·사회집단 편향으로 단정하지 말아줘. Task 5의 실제 도구·로봇을 실행하지 말아줘.
- 로컬 리포트와 Spaces는 같은 분석 엔진을 사용하고, 업로드한 점수·gold·공식이라고 주장한 index는 신뢰하지 말아줘. 운영자가 독립적으로 고정한 입력·정답·메타데이터로 검증·재채점해줘. 동일 prompt/input hash의 대응 비교와 protocol·measurement 호환성 사유를 제공해줘.
- 생성 모델과 측정 모델, run·generation·measurement·analysis·publication 상태를 구분해줘. 실제 기록 없는 revision·precision·truncation·finish_reason은 unknown으로 보존해줘. checksum·HF 로그인·CPU 재채점만으로 실제 weights와 생성 진위가 보장된다고 표현하지 말아줘.

측정 감사와 GPU 검증은 필수다. 최소 두 실제 target model의 생성→두 측정 모델→export→report→대응 비교를 GPU 증거로 확인해줘. 두 classifier 실행이나 CPU synthetic fixture로 두 target 검증을 대체하지 말아줘. 동일하게 고정한 답변의 batch/order/precision 변화, 잘림·반복·파싱 실패와 기존 safety 의심 사례를 감사하고 원래 출력·라벨을 보존해줘. 사람 판정 없는 의심 사례를 오답으로 확정하거나 정확도를 추정하지 말아줘. smoke·확대 검증과 standard 전체 평가를 구분하고 부분 결과를 공식 full baseline으로 등록하지 말아줘. 미해결 측정 지표는 진단용으로 표시하고 공식 rank에서 제외하는 정책을 코드로 검증해줘.

Spaces·제출 기능에서는 임시 업로드 분석과 공개 등록을 분리해줘. 세션 격리·업로드 한도·원문 비실행·credential 보호, 서버 검증한 identity·검토자 권한, immutable 결과/revision·이벤트 이력·동시 저장·restart·철회를 구현해줘. 공개 참조는 실제 target output이며 공개 가능 범위가 확인된 것만 사용해줘. ephemeral disk만으로 영구 저장 완료를 선언하지 말아줘. rank eligibility는 지표별 조건과 사유를 반환하고 custom·partial·미해결 측정 결과를 적절히 제한해줘.

각 반복에서 현재 증거를 확인하고 가장 중요한 미완료 요건을 실제로 구현·검증해줘. 사용자에게 매번 다음 단계 진행 여부를 묻지 말고 합의된 범위의 일반적인 구현 선택은 자율적으로 처리해줘. 계획의 Progress, Surprises & Discoveries, Decision Log, Outcomes & Retrospective와 검증 로그에 변경 파일·실제 명령·종료 상태·scope·evidence path·미완료 요건·다음 행동을 남겨줘. 계획만 수정하거나 이미 통과한 테스트를 의미 없이 반복하지 말아줘. 변경에 필요한 회귀 검사와 UI visual QA를 수행해줘.

GPU·사람 판정·credential·공개 허가가 없으면 독립적인 개발을 계속해줘. 실제 외부 검증이 필요하면 GPU 노드용 요청 프롬프트, 정확한 source/protocol/model lock, 실행 명령·자원 요구·결과 bundle·SHA-256 검증 절차를 준비해줘. 다른 대화나 노드에 권한 없이 메시지를 보내거나 작업을 발주하지 말아줘. 필수 외부 증거는 확보되기 전까지 미완료로 유지하고, 독립 작업도 남지 않은 실제 차단 상태는 도구 규칙에 따라 정확히 보고해줘.

완료는 계획 18절과 R1–R10 인수 시나리오에 따라 판단해줘. 기존 기능 보존, 동작하는 문서·예시, schema·분모·호환성·resume·UI·저장 검증, 최소 두 실제 target 모델 GPU 통합 증거, 측정 한계에 맞는 rank 제외, 로컬/Spaces 수치 일치와 검토 가능한 release/deployment candidate가 모두 필요하다. 해결되지 않은 정확도를 해결됐다고 주장할 필요는 없지만 해당 제한 정책은 실제 동작해야 한다. 필수 GPU 검증이 없거나 저장·등록 기능이 미구현이면 전체 Goal을 완료로 표시하지 말아줘.

작업 범위는 로컬 구현·검증과 공개 전 후보 준비다. GitHub/HF 공개 push, production Space 게시, 유료 자원 활성화, 외부 사용자 결과 공개는 자동 실행 범위에 포함하지 않는다. 필요한 준비를 마치고 concrete diff·검증 근거·배포 대상·권한·비용 조건을 제시한 뒤 해당 공개 단계의 승인 범위를 확인해줘. 최종 보고에는 quickstart, 변경 요약, CPU/GPU 검증 범위, 산출물·checksum, 측정 제한·등록 정책, 남은 공개 절차를 포함해줘.

지금 최신 checkout과 Progress를 확인하고 가장 중요한 미완료 단계부터 실제 작업을 시작해줘. 현재 기록과 같으면 구현된 CPU 감사 도구를 활용하여 M4 실제 조건 로그·adjudication·GPU 요청 및 반환 검증을 준비하고, GPU와 독립적인 M6 operator receipt의 독립 인수·immutable 보존·공식 순위 연결과 실제 로그인/원격 저장 인수를 이어서 구현해줘. 목표의 필수 완료 조건이 충족될 때까지 증거를 기반으로 계속 진행해줘.
```

## 짧은 목표 문안

긴 본문 대신 아래 문안을 사용해도 상세 계획의 완료 기준은 유지한다.

```text
KoEVD 저장소의 docs/PLATFORM_DEVELOPMENT_PLAN.md 전체와 최신 Progress·검증 근거를 읽고 M0–M6 및 R1–R10을 구현·검증된 release candidate까지 지속 개발해줘. vLLM 자체 모델 평가→표준 JSON→차트·실제 사례 HTML→동일 엔진의 Spaces 업로드·비교→제출·영구 저장·지표별 리더보드를 완성해줘. 기존 사용자 변경·연구 지표·분모·버전을 보존하고 실패/N/A와 측정 한계를 숨기지 말아줘. 최소 두 실제 target 모델 GPU 증거, 로컬/Spaces 수치 일치, schema·호환성·resume·UI·storage 검증을 완료 근거로 남겨줘. 미해결 측정 지표와 Task 4는 공식 rank에서 제외해줘. GPU가 없으면 독립 개발을 계속하며 외부 실행용 source lock·프롬프트·명령·반환 bundle·checksum 검증을 준비하고 필수 검증을 미완료로 유지해줘. 최신 증거를 따라 완료한 단계를 반복하지 말고 중요한 미완료 요건을 구현하며 Progress·결정·실행 근거를 갱신해줘. 공개 push·production 게시·유료 자원·외부 결과 공개 없이 검토 가능한 후보까지 완성하고 공개 단계는 준비 후 승인 범위를 확인해줘.
```

## 기존 목표를 이어갈 때의 보충 메시지

```text
현재 Goal을 유지하면서 docs/PLATFORM_DEVELOPMENT_PLAN.md의 최신 Progress·결정·검증 근거를 확인하고 가장 중요한 미완료 작업부터 구현·검증을 이어가줘. 완료한 M0–M3와 M5 CPU 앱을 처음부터 다시 만들지 말고, M4 측정 감사·실제 두 target GPU, M5 실제 결과·컨테이너 검증, M6 operator 생성 영수증·실제 HF 로그인·공식 순위 연결·원격 저장을 완성해줘. GPU가 필요하면 재현 가능한 source bundle과 실행 요청·반환 검증을 준비하면서 독립 CPU 개발을 계속해줘. 필수 인수 기준이 충족될 때까지 부분 완료와 최종 완료를 구분해줘.
```

## 최종적으로 받을 결과

- 실행 가능한 설치·vLLM·단계별 평가·export·리포트·Spaces quickstart.
- 결과/protocol/metric/measurement version과 과거 형식 migration 설명.
- 실제 로컬 HTML·Spaces candidate, 동일 입력의 모델 비교 예시와 UI 근거.
- CPU 검사·실제 두 target GPU 검증의 명령·범위·결과 bundle·checksum.
- 해결·미해결 측정 사항, 지표별 등록/공식 rank 포함·제외 사유.
- 저장·동시성·restart·identity·검토·철회 검증과 운영 문서.
- 검토 가능한 release diff·package/container 후보·공개 대상과 필요한 권한.
- production 미배포라면 그 상태와 다음 공개 절차.
