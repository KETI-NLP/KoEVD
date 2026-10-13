# 실제 백업 저장소와 앱 연결의 구분

## 최신 백업·복원 검증 — plan0.54

v0.54에서 별도 승인된 실제 private CPU 유한 종료 시험을 완료했다. 기준9개 보존·새 snapshot3개/396,229바이트로3회/24MiB 한도를 지켰다. 현재 코드에 결합한 parent 종료 로그 뒤 마지막 snapshot이 생겼고 finite worker2회 완료·후속 기동 initialization_inventory_mismatch 거부를 확인했다. 별도 다운로드한3사본 중 두 현재48+48기록 원본/이력이 모두 일치한 digest를 내용으로 선택했다. 고정 복원 후 실제 HF 재로그인의 두 원본·두 이력4파일이 복원 전 native 다운로드와 바이트 일치했고 새 저장/공개 조회 거부·worker OFF·복구 대기를 확인했다. 최신 기본 revision `8e692c88d412d6305879473e3e8e74d46bb7dd2c`의 RUNNING/cpu-basic·66파일 바이트/목록 일치로 복귀했다. Bucket12객체/68,382,317바이트·Secret·public Static을 보존했으며 상시 백업은 꺼져 있다. 이 승인은 시험 종료로 소진됐다. 과거 누락4B 이력이 복구됐다고 주장하거나 과거 횟수 실패를 소급 통과 처리하지 않는다. 실제 HF host restart 이벤트 로그·상시 운영/RPO·현재 Docker 전체 용량·운영자 정책/복구 인수·공개 참조는 미확보다. 실제 GPU/F1/분류 정확도의 새 검증은 아니다. [최신 근거](validation/platform_m6_actual_finite_shutdown_20261012.json). 전체 목표/완료 조건은 유지하며 전체 완료를 선언하지 않는다.

아래 이전 기록은 당시 범위다.

## 최신 백업 상태 — plan0.52

v0.52에서 유한 worker의 마지막 capture 전에 소유한 HTTP 서버를 종료·회수하고 전용 stdin으로 마지막 백업을 허용하는 순서를 구현했다. 현재 새 비편집 설치의 source50·고정 의존성25·pip check와 전체352 CPU검사/146.942초/failures0/errors0/skips0가 통과했다. 현재9개 digest를 metadata-only double로 재현한 실제 소유 로컬 HTTP/worker 통합29.344초에서 두48+48기록 원본/이력의 고정 복원 일치, 마지막 SQLite capture 전 서버 종료, 이후 연결 거부, 새 빈 초기화 거부, 복원 대기와 credential 분리를 확인했다. HF/OAuth는 명시적 double이다. Windows 상태 파일 교체의 일시적 WinError5/32/33에만 최대6회·총0.62초 재시도하며 지속 오류는 전달한다. 관측된 WinError5의 근본 원인은 미확정이다. 기본65·관리형68파일 및 초기1+worker2/24MiB/600초의70파일 제안을 로컬에 준비했고 이번 외부 전송·배포는0회다. 앞서 승인된 v0.51 시험은 종료됐으며 새 제안의 권한으로 재사용하지 않는다. 실제 마지막 기본 revision은 `f65a8b1065b934e649e545043c4ac89b18c2d4a5`, 상시 백업 OFF다. 이전 실제 새4B 이력 누락은 복구됐다고 주장하지 않는다. 실제 HF 두 현재 초안의 종료 보존·현재 Docker 전체 용량·운영 인수·공개 참조는 미완료다. [최신 근거](validation/platform_m6_finite_final_capture_20261012.json). Goal active/원래 범위를 유지한다.

아래 이전 기록은 당시 범위다.

## 최신 백업 상태 — plan0.51

v0.51에서 별도 승인된 private CPU 정상 기동 시험의 새 snapshot3개/302,021바이트와 finite worker2회 완료·후속 초기화의 `initialization_inventory_mismatch` 거부를 확인했다. 이번 횟수/용량 한도는 통과했지만 두 초안 보존은 미완료다. 실제 HF 로그인으로8B/4B 초안 저장을 관찰했고 종료 경계의4B 다운로드가503을 반환했다. 독립 다운로드/외부 index·registry 검사에서 마지막 사본에는8B48기록/이력만 있고 새4B 이력은 없었다. 과거4B 사본으로 대체하지 않았다.8B의 고정 복원·실제 재로그인 전후 원본/이력 바이트 일치와 새 저장 거부·공개 조회 불가 UI는 확인했다. 승인된 최신 UI 기본 프로필 `f65a8b1065b934e649e545043c4ac89b18c2d4a5`의 RUNNING/cpu-basic·66파일 바이트/목록 일치로 복귀했고9백업/67,986,088바이트·Secret·public Static을 보존했다. 상시 백업은 꺼져 있다. current26 CPU검사/5.350초와 앞선 nonempty6 목록 로컬 통합27.453초는 별도 모의 provider 근거다. 유한 worker의 마지막 snapshot 전에 새 domain 저장을 닫고 수락된 요청을 기다리는 절차가 다음 구현 대상이다. 실제 두 초안 종료 보존·현재 Docker 전체 용량·운영 인수·공개 참조는 미완료다. [최신 근거](validation/platform_m6_positive_trial_partial_20261012.json). Goal active/원래 범위를 유지한다.

아래 이전 기록은 당시 범위다.

## 최신 연결 상태 — plan0.49

v0.49에서 별도 승인된 읽기 전용 시험을 실제 private CPU Space에서 수행했다. 실제 HF 로그인으로 현재 보이는 초안0건·분석 업로드0건을 확인하고 이전 두 모델 원본/이력 4쌍을 재대조했다. 전용 Secret으로 private Bucket 목록을 읽은 진단은 `initialization_inventory_mismatch`/exit2 경로를 반환했다. 이 진단의 RUNTIME_ERROR는 의도한 거부이며 서버·worker·DB·snapshot을 만드는 경로를 호출하지 않는다. Bucket6객체/67,684,067바이트 목록이 유지됐고 새 결과 전송·snapshot 생성은0회다. 기본 프로필 `f160663af378e777616be89374a20b6c38b57938`로 복귀한 뒤 RUNNING/cpu-basic·배포66파일의 바이트/목록 일치와 브라우저 준비 화면을 확인했다. Secret·public Static·기존 snapshot은 보존했고 상시 백업은 꺼져 있다. 현재25 CPU검사/5.652초는 로컬 근거다. 실제 정상 초기화 후 재시작 전체 인수·현재 Docker 전체 용량·운영 승인·공개 참조는 미완료이고, 이전 최대3회 시험의5회 생성 실패도 통과로 변경하지 않는다. [최신 근거](validation/platform_m6_actual_readonly_guard_20261012.json). Goal active/원래 범위를 유지한다.

아래 이전 기록은 당시 범위다.

## 최신 연결 상태 — plan0.48

v0.48에서 초기화 목록 불일치를 민감한 상세 없이 구분하는 진단과 `--check-initialization-baseline` 읽기 전용 모드를 추가했다. 이 모드는 목록이 일치해도 DB·서버·worker·snapshot을 만들지 않는다. 관련25 CPU검사/5.652초/exit0이 통과했고 core50 바이트는 기본 개발 후보와 같다. 실제 private CPU Space는 `8d50fbe9a05c152cb4e3365bea01c52ec0f78419`의 RUNNING/cpu-basic, Bucket은6객체/67,684,067바이트, public Static은 이전 revision으로 재확인했다. 68파일 일반 후보와70파일 읽기 전용 제안을 로컬에 준비했으며 미업로드다. 기존 초안·이력 보존 → 전용 Secret으로 목록 검사 → 기본 프로필 복귀의 별도 승인을 요청했다. 이 제안의 새 결과 전송과 snapshot 쓰기는0회다. 실제 HF guard/정상 초기화·재시작 인수는 아직 없고, 이전 최대3회 시험의5회 생성 실패는 그대로 남는다. 상시 백업은 꺼져 있고 현재 Docker 전체 용량·공개 참조·운영자 인수도 미완료다. [근거](validation/platform_m6_readonly_guard_preparation_20261012.json). Goal active/원래 범위를 유지한다.

아래 이전 기록은 당시 범위다.

2026-10-12. [KETI-NLP/KoEVD-Platform-Backups-Dev](https://huggingface.co/buckets/KETI-NLP/KoEVD-Platform-Backups-Dev)는 **비공개 개발용** 저장소다. 사용자가 정확한 대상·파일·용량 제한을 승인한 뒤, 기존 실제 두 모델의 원본·이력 스냅샷1개를 저장했다. [실제 cloud 검증](validation/platform_m6_actual_private_cloud_20261012.json).

| 확인한 항목 | 실제 결과 |
|---|---|
| 저장 파일 | 67,154,758바이트, 실제 두 모델35,340기록·비공개 draft2건 |
| ZIP 바이트 SHA-256 | `780995a6e048bff02fa0321aac1355b9c0cf538d06d6a5eded6360fcd36ac47b` |
| 원격 key | `koevd-snapshots/780995a6e048bff02fa0321aac1355b9c0cf538d06d6a5eded6360fcd36ac47b.zip` |
| 읽기 검증 | 업로드 후 readback과 독립 새 파일 다운로드의 바이트 일치 |
| 복원 검증 | 외부 고정 index/registry 사용. 원본·상태·이력과 snapshot 시점 checkpoint 일치 |
| 복원 상태 | 공개조회503, domain 변경 차단. 운영 복구 대기 해제 없음 |
| 실패 처리 | 없는 객체 요청은 실패하며 이전 검증 다운로드 유지 |
| 앱 연결 | Space secret·volume·백업 worker·현재 앱 DB 경로를 변경하지 않음 |

이 snapshot은 기존 로컬 검증 actor의 저장본이다. 실제 HF 웹 로그인으로 만든 개발 앱의 두 초안과 다른 저장소이며, 해당 HF 사용자에게 원래 local actor를 연결하거나 현재 서버의 최신 상태라고 표시하지 않는다. 그 앱 초안의 실제 로그인 검증은 [별도 근거](validation/platform_m5_m6_team_hosted_20261012.json)에 있다.

## 이번 허용 범위와 저장 비용

이번 승인은 비공개 Bucket 생성·해당 ZIP1개 전송·재다운로드·오프라인 복원이며 전송은70MiB 이하로 제한했다. 실행 전 조직 화면의 private 사용량0/3TB를 재확인했다. 추가 구독·용량 구매·GPU를 요청하지 않았다. 조직의 다른 사용량이나 추후 대량 업로드에 대한 비용 보장은 아니다.

[HF 공식 저장 한도](https://huggingface.co/docs/hub/storage-limits)에 따르면 Team에는 seat당 private1TB가 포함되고 초과분은 사용량에 따라 과금된다. [Bucket 안내](https://huggingface.co/docs/hub/storage-buckets)는 생성이 무료이며 included storage 이상에는 저장 비용이 적용된다고 설명한다. 이 정보는2026-10-12 확인했으며 향후 변경될 수 있다.

## 다음 연결 후보에서 준비할 설정

1. **Bucket 전용 runtime credential.** 현재 CLI 관리자 토큰을 Space secret으로 복사하지 않는다. 사용자가 해당 private Bucket만 읽고 쓰는 전용 credential을 설정한다. 토큰 자체를 채팅·명령 인자·소스·receipt에 넣지 않는다. OAuth ID/secret은 이 저장 토큰을 대체하지 않는다.
2. **별도 운영 역할과 경로.** 백업 실행 actor/역할과 웹 reviewer/admin을 구분한다. 조직 관리자라고 게시 역할을 자동 부여하지 않는다. DB는 로컬 disk, backup root는 그 DB 밖의 디렉터리로 둔다.
3. **명시적인 주기 백업 후보.** 기존 `koevd-backup`의 exact private target, 독립 snapshot/checkpoint, 실패/미보존 변경 status를 연결한다. 이번1개 ZIP 전송 승인을 무제한 상시 업로드 승인으로 사용하지 않는다.
4. **부팅 복구 후보.** 외부에서 고정한 ZIP 바이트 digest와 독립 catalog/registry로 새 경로에 복원한다. 복원 대기를 유지하고 실제 최신 checkpoint 대조/운영자 인수 후에만 공개를 재개한다. 객체 이름·수정 시각으로 최신 상태를 추정하지 않는다.
5. **인수 시나리오.** disposable 개발 데이터로 저장→검증 백업→서버 재시작→독립 복원→원본/이력 대조, 저장 실패, 이전 성공본 유지, 미보존 변경 표시를 실제 실행한다. 복원 성공을 모델 정확도·생성 진위·게시 권리 승인으로 확대하지 않는다.

현재 주기 worker/CLI는 [백업 안내](BACKUP_WORKER_GUIDE.md), 복원과 대기 해제는 [복구 안내](RECOVERY_GUIDE.md)에 있다. 이번 실제 전송 controller는 불변 검증 기록이며 같은 출력 경로나 기존 Bucket에 다시 생성 요청하는 실행 예제가 아니다.

살아 있는 SQLite를 Bucket/NFS mount에 직접 놓지 않는다. 주기 스냅샷은 마지막 성공 이후의 변경 손실을 없애는 동기 remote commit이 아니며 보장된 RPO도 아니다. 운영 Space 연결 후보는 공개 전 로컬 개발 대상으로 남아 있다.


## 관리형 연결 후보와 Secret 준비 — plan0.45

[MANAGED_SPACE_GUIDE.md](MANAGED_SPACE_GUIDE.md)에 실제 코드·25개 runtime lock·68파일 context와 구조 검사/실제 기동/고정 복원 명령을 정리했다. 현재 후보는 미업로드/미활성화이며 전용 Secret 설정 완료를 기다린다. 새/기존 DB의 첫 백업 실패는 서버 기동을 막고, 고정 복원은 recovery quarantine을 유지한다. 관리형 후보 생성기는 current package/protocol bytes와 빈 웹 역할/참조를 확인한다. 기존 단일 snapshot 승인과 Secret 준비만으로 반복 전송을 시작하지 않는다.


## Secret 등록 확인과 실제 연결 대기 — plan0.46

v0.46에서 관리형 런처의 복원 안내와 종료 처리를 보완했다. 현재 코드의 로컬 실제 서버·worker·HTTP에서 두 기존 모델48+48기록 저장, 첫 백업+worker2회, 종료, 고정 복원 후 원본/이력 일치, 공개503·새 제출 차단을24.719초/exit0로 확인했다. HF/OAuth는 명시적 로컬 test double이며 실제 HF 연결이나 Linux signal 인수는 아니다. 관련18 CPU검사/2.987초/exit0와 이전 전체328 설치의 core50 바이트 유지도 확인했다. 사용자가 Bucket 전용 토큰과 `KOEVD_BACKUP_TOKEN` Secret 등록을 완료했다고 확인했다. 값은 읽거나 출력하지 않았다. 관리형68파일 후보와 기존 private CPU Space를 쓰는70파일 제한 시험 제안을 준비했으며 미업로드/미활성화다. 최대3회·snapshot24MiB 이하 전송과 고정 복원/기본 프로필 복귀에 대한 별도 승인을 요청했다. 실제 관리형 HF 백업·재시작 복구, 현재 Docker 전체 용량, 공개 참조·운영자 인수는 미완료다. [최신 근거](validation/platform_m6_managed_lifecycle_20261012.json), [관리형 안내](MANAGED_SPACE_GUIDE.md). Goal active/원래 범위를 유지한다.


## 실제 연결 후 현재 상태 — plan0.47

v0.47에서 전용 Secret으로 실제 private CPU 서버의 백업·고정 복원을 시험했다. 실제 HF 로그인으로 저장한 두 모델48+48기록의 원본/이력과 분석 JSON을 독립 보존했고, 고정 복원 후 재로그인한 원본/이력 바이트가 모두 일치했다. 공개 HTTP503/recovery_required와 실제 새 제출 거부도 확인했다. 그러나 승인된 최대3회와 달리 새 snapshot5개/529,309바이트가 관측됐다. 24MiB 총량은 지켰지만 횟수 제한은 실패했다. 즉시 PAUSED로 전송을 막고 새 백업 없는 고정 복원을 검증한 뒤 기본 private 프로필 `8d50fbe9a05c152cb4e3365bea01c52ec0f78419`의 RUNNING/cpu-basic으로 복귀했다. Secret·snapshot·공개 Static은 보존했고 상시 백업은 꺼져 있다. 유한 worker 종료 뒤 새 빈 저장소 기동이 반복된 양상에 대응해 v2의 독립 원격 snapshot 기준 목록 검사와 legacy initialize 거부를 구현했다. 관련22 CPU검사/5.497초 및 실제 소유 로컬 재기동·복원27.969초가 통과했다. 이 수정의 실제 HF 재검증은 미완료이며 새68파일 후보는 미업로드/미활성화다. [최신 근거](validation/platform_m6_live_backup_trial_20261012.json), [관리형 안내](MANAGED_SPACE_GUIDE.md). Goal active/원래 범위를 유지한다.
