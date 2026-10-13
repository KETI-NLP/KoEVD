# 관리형 개발 Space 후보: 서버와 검증 백업의 연결

2026-10-12 / plan 0.54. 이 안내는 **미활성화 배포 후보**에 관한 것이다. 현재 실행 중인 비공개 `KETI-NLP/KoEVD-Platform-Dev`는 기본 `apps/spaces/launch.py`와 임시 제출 DB를 사용한다. 아래 후보를 만들거나 Secret을 등록하는 것만으로 현재 Space의 백업이 시작되지는 않는다. 공개 Static `KoEVD-Explorer`에는 이 저장 토큰을 넣지 않는다.

코드는 [managed_launch.py](../apps/spaces/managed_launch.py), 설정 형식은 [managed.example.json](../apps/spaces/managed.example.json), 이미지 구성은 [managed.Dockerfile](../apps/spaces/managed.Dockerfile)에 있다. 기존 분석 엔진·제출 CLI·스냅샷·복구 대기를 재사용한다. 현재 로컬 CPU 검증과 실제 HF Bucket 전송의 범위는 [검증 로그](PLATFORM_VALIDATION_LOG.md), [연결 상태](TEAM_BACKUP_CONNECTION.md)에 구분되어 있다.

## 실제 유한 종료 시험 결과 — plan0.54

별도 승인된 실제 private CPU 시험에서 기준9객체를 보존하고 새 snapshot3개/396,229바이트로 한도를 지켰다. parent 서버 종료 로그 뒤 마지막 capture와 후속 initialization_inventory_mismatch 거부를 확인했다. 두 현재48+48기록 원본·이력은 고정 복원/실제 HF 재로그인 뒤 네 native 파일이 바이트까지 같다. 새 저장·공개 조회는 복구 대기로 거부되고 복원 worker는 꺼져 있다. 최신 기본 revision8e692c88d412d6305879473e3e8e74d46bb7dd2c의66파일/RUNNING/cpu-basic으로 복귀했으며12백업/68,382,317바이트를 보존했다. 이 시험 승인은 종료됐고 상시 백업은 켜지 않았다. 과거 늦은4B 이력 누락이 복구된 것은 아니다. HF host restart 이벤트 로그·상시 운영/RPO·운영자 정책/복구 인수·현재 Docker 전체 용량·공개 참조는 미확보다. [실제 근거](validation/platform_m6_actual_finite_shutdown_20261012.json). 아래 준비 제안과 pending 상태는 해당 시점의 기록이다.

## 유한 시험 종료와 마지막 백업 — plan0.52

v0.52에서 유한 worker의 마지막 capture 전에 소유한 HTTP 서버를 종료·회수하고 전용 stdin으로 마지막 백업을 허용하는 순서를 구현했다. 현재 새 비편집 설치의 source50·고정 의존성25·pip check와 전체352 CPU검사/146.942초/failures0/errors0/skips0가 통과했다. 현재9개 digest를 metadata-only double로 재현한 실제 소유 로컬 HTTP/worker 통합29.344초에서 두48+48기록 원본/이력의 고정 복원 일치, 마지막 SQLite capture 전 서버 종료, 이후 연결 거부, 새 빈 초기화 거부, 복원 대기와 credential 분리를 확인했다. HF/OAuth는 명시적 double이다. Windows 상태 파일 교체의 일시적 WinError5/32/33에만 최대6회·총0.62초 재시도하며 지속 오류는 전달한다. 관측된 WinError5의 근본 원인은 미확정이다. 기본65·관리형68파일 및 초기1+worker2/24MiB/600초의70파일 제안을 로컬에 준비했고 이번 외부 전송·배포는0회다. 앞서 승인된 v0.51 시험은 종료됐으며 새 제안의 권한으로 재사용하지 않는다. 실제 마지막 기본 revision은 `f65a8b1065b934e649e545043c4ac89b18c2d4a5`, 상시 백업 OFF다. 이전 실제 새4B 이력 누락은 복구됐다고 주장하지 않는다. 실제 HF 두 현재 초안의 종료 보존·현재 Docker 전체 용량·운영 인수·공개 참조는 미완료다. [최신 근거](validation/platform_m6_finite_final_capture_20261012.json). Goal active/원래 범위를 유지한다.

`cycles > 0`인 후보는 마지막 worker cycle 직전에 서버를 종료한다. 마지막 사본을 만드는 동안 앱 연결은 실패할 수 있다. worker가 준비 이벤트를 내보낸 뒤 launcher가 소유한 server의 종료를 확인하고 정확한 stdin 명령을 보낸다. 확인이나 release가 실패하면 최종 capture는 시작하지 않는다. server SIGTERM에는5초 유예 후 강제 종료를 적용하며 HTTP 성공 이전의 commit 상태를 snapshot에 보존한다. 모든 진행 중 요청이 성공한다는 보장이나 비정상 host 종료의 보호가 아니다. `cycles: 0`에는 이 종료 절차를 적용하지 않는다. 기본 앱 프로필과 고정 복원에는 백업 worker가 없다.

새 실제 시험 제안은 마지막 관측9개 객체/67,986,088바이트를 고정 기준으로 삼고, 초기1회+worker2회·새 snapshot 총24MiB 이하를 유지한다. 600초 간격 안에 두 초안의 원본과 이력 다운로드를 모두 끝내고 이후 producer 종료/마지막 백업·재기동 거부·독립 다운로드/고정 복원을 확인한다. 실행 직전에 baseline·단일 replica·포함 용량과 현재 초안 보존을 새로 확인해야 한다. 새 전송/서버 전환은 미승인 제안이며 이전 종료된 시험 승인을 재사용하지 않는다.

## 준비할 네 가지

현재 판정(plan0.51): v0.51에서 별도 승인된 private CPU 정상 기동 시험의 새 snapshot3개/302,021바이트와 finite worker2회 완료·후속 초기화의 `initialization_inventory_mismatch` 거부를 확인했다. 이번 횟수/용량 한도는 통과했지만 두 초안 보존은 미완료다. 실제 HF 로그인으로8B/4B 초안 저장을 관찰했고 종료 경계의4B 다운로드가503을 반환했다. 독립 다운로드/외부 index·registry 검사에서 마지막 사본에는8B48기록/이력만 있고 새4B 이력은 없었다. 과거4B 사본으로 대체하지 않았다.8B의 고정 복원·실제 재로그인 전후 원본/이력 바이트 일치와 새 저장 거부·공개 조회 불가 UI는 확인했다. 승인된 최신 UI 기본 프로필 `f65a8b1065b934e649e545043c4ac89b18c2d4a5`의 RUNNING/cpu-basic·66파일 바이트/목록 일치로 복귀했고9백업/67,986,088바이트·Secret·public Static을 보존했다. 상시 백업은 꺼져 있다. current26 CPU검사/5.350초와 앞선 nonempty6 목록 로컬 통합27.453초는 별도 모의 provider 근거다. 유한 worker의 마지막 snapshot 전에 새 domain 저장을 닫고 수락된 요청을 기다리는 절차가 다음 구현 대상이다. 실제 두 초안 종료 보존·현재 Docker 전체 용량·운영 인수·공개 참조는 미완료다. [최신 근거](validation/platform_m6_positive_trial_partial_20261012.json). Goal active/원래 범위를 유지한다.


| 준비물 | 용도와 경계 |
|---|---|
| 독립 catalog와 protocol registry | 서버가 선택한 입력으로 검증·재채점. 업로드 점수·gold를 신뢰하지 않음 |
| 웹 역할과 별도 백업 역할 | 웹 reviewer/admin과 백업 actor를 분리. HF 조직 관리자 권한을 앱 게시 권한으로 자동 변환하지 않음 |
| Bucket 전용 토큰 | 정확한 비공개 Bucket의 읽기·쓰기. 서버 로그인용 OAuth와 별개 |
| 활성화 범위와 복구 기준 | 어떤 자료를 몇 회·얼마나 전송할지, 재시작 시 사용할 독립 snapshot digest/checkpoint를 확정 |

첫 외부 승인은 고정67,154,758바이트 snapshot 한 개였고, 이후 별도 승인된96기록 제한 시험은 종료했다. 이번 시험의 횟수 제한 실패와 기본 복귀를 기록했다. 두 승인을 새로운 시험이나 상시 백업 승인으로 확대하지 않는다. 예시 설정의 `cycles: 0`과 1GiB 보관 상한도 승인된 운영 정책이 아니다. 실제 연결 전에 전송 범위와 포함 용량을 확인해야 한다.

## 전용 토큰을 Secret에 등록

1. [HF Access Tokens](https://huggingface.co/settings/tokens)에서 새 **Fine-grained** 토큰을 만든다. 이름 예: `KoEVD-Platform-Dev-Backup`.
2. 리소스 선택에서 `KETI-NLP/KoEVD-Platform-Backups-Dev` Bucket 하나의 읽기·쓰기만 허용한다. 해당 Bucket을 선택할 수 없다면 조직 전체 쓰기로 대체하지 않고 권한 설정을 먼저 확인한다. 공식 문서는 Bucket에 범위를 제한한 User Access Token을 사용할 수 있다고 설명한다. [Bucket 권한](https://huggingface.co/docs/hub/storage-buckets-security), [토큰 안내](https://huggingface.co/docs/hub/security-tokens).
3. [개발 Space Settings](https://huggingface.co/spaces/KETI-NLP/KoEVD-Platform-Dev/settings)의 Variables and secrets에서 **Secret**으로 저장한다. 이름은 정확히 `KOEVD_BACKUP_TOKEN`, 값은 생성한 토큰 전체다. [Secret 안내](https://huggingface.co/docs/hub/spaces-overview#managing-secrets-and-environment-variables).
4. 토큰 값은 채팅·명령 인자·source·receipt에 넣지 않는다. 설정 완료 여부만 전달한다. 사용자가 Bucket 전용 토큰과 Secret 등록 완료를 확인했다. 값은 읽거나 출력하지 않았으며, 실제 runtime에서 이 Bucket의 읽기·쓰기는 제한 시험으로 확인했다. 다른 리소스에 대한 권한까지 없음을 자동 증명한 것은 아니며, 토큰의 제한 범위는 사용자가 설정한 내용이다.

런처는 이 Secret만 사용하며 로컬 CLI 로그인으로 대체하지 않는다. 웹 서버 child에서는 백업 토큰을 제거하고, 백업 child에서는 OAuth client ID/secret을 제거한다. 백업 토큰은 백업 child의 환경에만 `HF_TOKEN`으로 전달한다. 양쪽 command argv에는 토큰이 없다. 이 분리는 실제 HF 토큰 권한 범위를 자동으로 인증하는 기능이 아니므로 토큰 생성 시의 범위 확인도 필요하다.

## 검토할 배포 context 만들기

저장소 root에서 실행한다. `BASE`는 manifest를 독립적으로 대조한 기존 개발 context이며, `OUT`은 존재하지 않는 새 경로여야 한다.

```bash
python scripts/materialize_managed_space.py \
  --repo . --base-candidate BASE --output OUT
```

현재 materializer는 기존 context의 두 package namespace·protocol·pyproject 바이트를 현재 저장소와 비교하고, 실제 운영 역할·참조·managed 설정의 상속을 거부한다. 현재 후보는 `generated/managed-positive-candidate-20261012-v76`이며 기본 context는 `generated/private-space-public-failure-candidate-20261012-v75`이다. 이전 v72는 당시 소스 후보다. payload 68개와 manifest를 갖고 있지만 **실제 `operator-data/managed.json`, 백업 역할 파일, 토큰은 포함하지 않는다**. 따라서 그대로 기동할 수 없다. 이 명령은 업로드·Space 설정 변경·유료 자원 활성화를 하지 않는다.

기존 `operator-data/catalog.json`과 `configs/protocols/`를 보존한다. `operator-data/managed.example.json`을 복사한 `managed.json`에서 실제 경로·mode·actor·cycles를 정하고 별도의 `backup-roles.json`을 제공한다. 예시의 `OPERATOR_SELECTED_BACKUP_ACTOR`를 그대로 운영자로 채택하지 않는다. 백업 actor는 백업 역할 파일의 `admins` 목록에 명시되어야 한다. 웹 `roles.json`에는 게시 권한을 별도로 승인받은 계정만 넣는다.

## 시작 방식은 명시적으로 선택

| `mode` | 요구사항 | 동작 |
|---|---|---|
| `initialize` | DB root가 아직 없음, v2의 독립 원격 snapshot 기준 목록 | private Bucket/기준 목록 확인 후 root를 원자적으로 생성. 첫 원격 snapshot/readback이 성공해야 서버 시작 |
| `existing` | 지정 root에 `submissions.sqlite3` 존재 | 기존 DB를 검증하고 첫 원격 snapshot/readback 성공 후 시작. DB가 사라지면 빈 DB로 대체하지 않음 |
| `restore` | 새 restore root, 그 아래 `store`를 DB root로 지정, 외부에서 고정한 SHA-256 | 지정 snapshot만 새 파일로 다운로드·독립 index/registry 대조 후 복원. 복구 대기 유지, 백업 worker는 시작하지 않음 |

`store_root`와 `backup_root`는 서로 포함되지 않는 별도 경로여야 한다. restore root와 backup root도 분리한다. symlink 경로와 기존 복원 다운로드 덮어쓰기를 거부한다. 객체 수정 시각이나 이름 정렬로 최신 상태를 선택하지 않는다.

`restore` 결과에 운영 정책 head가 있으면 이 후보는 정책을 활성화하지 않고 기동을 거절한다. 복원 산출물은 보존한다. 정책 없는 복원도 공개 조회와 domain 변경은 대기 상태로 차단된다. 복구 해제는 [RECOVERY_GUIDE.md](RECOVERY_GUIDE.md)의 독립 최신 기준 대조 및 실제 운영자 판단을 따른다.

## 구조 검사와 실제 실행의 차이

CPU 환경에서는 다음 의존성을 설치한다. 후보 Dockerfile은 [25개 고정 런타임 버전](../apps/spaces/managed.requirements.lock.txt)을 먼저 설치하고 현재 패키지를 `--no-deps`로 설치한다.

```bash
python -m pip install ".[serve,storage]"
python apps/spaces/managed_launch.py --config operator-data/managed.json --check
```

`--check`에는 HF가 제공하는 canonical `SPACE_HOST` 환경값이 필요하다. 로컬 검토에서는 검토 대상 host를 명시한다. 출력의 `configuration_structurally_valid: true`는 경로·역할 목록·설정 형식·argv 검사만 뜻한다. `catalog_and_Bucket_validated: false`, `external_operations_performed: false`를 함께 읽어야 한다. Secret이나 네트워크를 사용하지 않으며 실제 인증 성공을 증명하지 않는다.

실제 실행은 승인된 전송 범위와 Secret·OAuth가 준비된 환경에서만 한다.

```bash
python apps/spaces/managed_launch.py --config operator-data/managed.json
```

실행 시 catalog/registry, confidential OAuth 설정, 전용 토큰으로 접근한 정확한 private Bucket을 확인한다. 새/기존 DB의 첫 백업 실패 시 서버 child를 시작하지 않는다. 이후 두 child를 소유 프로세스로 관리하고 한 child가 종료하면 나머지도 정리한다. 부분 기동 실패에도 이미 만든 child를 정리한다. 유한 `cycles`는 worker가 끝나면 서버도 종료하는 제한 시험용 설정이다. 최초 기동에서 수행한 검증 백업 1회는 worker의 `cycles`와 별도이므로 예상 전송 횟수에 함께 포함해야 한다.

## 실패·재시작·보관 한계

첫 전송이 실패해도 DB root나 부분 사본을 지우지 않는다. 원인을 확인한 뒤 기존 DB를 계속 사용할지 별도 새 시험 경로를 만들지 선택한다. 같은 `initialize` 설정으로 재실행하면 이미 생긴 root 때문에 거절될 수 있다. 실제 DB 존재와 보존 여부를 확인한 후 `existing`을 선택해야 한다.

현재 예시의 DB와 backup root는 `/tmp`다. 재빌드·재시작 뒤 사라질 수 있으므로 재기동은 자동 빈 DB 초기화가 아니라 외부 고정 snapshot에 대한 명시적 복원 절차로 검증한다. 이 후보는 최신 snapshot 자동 발견이나 복구 대기 자동 해제를 제공하지 않는다.

`interval_seconds`는 복사 완료 후 대기 시간이다. `cycles: 0`은 반복 실행이며, `retained_quota_bytes`는 로컬 보관 파일 검사다. HF 조직 전체 저장 비용 상한·업로드 총량·SQLite 임시 공간 quota가 아니다. 동일 상태의 연속 snapshot도 서로 다른 ZIP이 될 수 있으므로 원격 누적 용량은 별도로 감시해야 한다. 실패·미완료 시도와 이전 성공본을 유지하고 자동 GC는 하지 않는다. 주기 snapshot을 동기 remote commit이나 보장된 RPO로 표현하지 않는다.

## 다음 실제 인수에서 확보할 근거

전송 범위가 확정되면 disposable 개발 데이터로 저장 → 검증 백업 → 원본·이력 독립 사본 → 서버 종료 → 새 경로에 고정 복원 → 원본/이력/checkpoint 비교를 수행한다. 현재 앱의 최신 상태라고 주장하려면 snapshot 이후 변경도 독립적으로 대조해야 한다. 복원 대기 유지, 잘못된/누락 snapshot, 실패 시 이전 사본 보존, 마지막 검증 백업 뒤 미보존 변경 표시를 실제 런타임에서 확인한다.

현재 로컬 CPU 검사는 SQLite/백업/readback/복원과 소유 child 정리를 포함하지만 전송 provider는 명시적 test double이다. 기존 실제 HF Bucket 시험은 고정 snapshot 한 개의 독립 전송 근거다. 둘을 합쳐 **관리형 HF 컨테이너·상시 백업·재시작 복구 통과**라고 표시하지 않는다. 실제 공개 참조, 운영자 심사·생성 receipt·공식 순위 정책, production 전환도 별도 미완료 조건이다.


## 이전 로컬 통합 검증과 제한 HF 시험 제안 — plan0.46 (당시 기록)

[검사기](../scripts/validate_managed_space_lifecycle.py)는 원본 SHA가 고정된 기존 실제 두 모델48+48기록을 사용한다. 실제 소유 server/worker를 기동하고 HTTP 비공개 저장 → 첫 백업+worker2회 → 종료 → 별도 고정 복원 서버 → 원본/이력 대조 → 공개503/새 제출 차단을 확인했다. HF 전송과 OAuth exchange는 명시적 로컬 test double이다. Test hook은 loopback binding/임시 origin, 외부 connect 거부와45초 watchdog를 사용한다. server child에 저장 토큰이 없고 worker child에 OAuth secret이 없는지도 값 없이 확인했다. 총24.719초/exit0이며 모든 소유 child가 종료됐다. [근거](validation/platform_m6_managed_lifecycle_20261012.json). 최초 HTTPX 재진입 오류와 소유 child 종료 기록도 보존한다.

실제 런처는 SIGTERM을 cleanup 경로로 연결하고 복원 server child의 handle도 관리한다. 관련18 CPU검사와 위 실제 프로세스 검증은 Windows 범위다. Linux/HF의 실제 SIGTERM 전달·컨테이너 인수를 대신하지 않는다. 복원 안내는 worker가 실행 중이 아님을 명시한다.

현재 HF 시험 제안은 `generated/managed-space-bounded-trial-20261012-v69`의70파일 context다. 실제 설정/기술적 backup actor 제안이 있으나 승인되지 않았다. 웹 역할/참조 목록은 계속 비어 있다. Secret은 현재 private CPU Space에 사용자가 등록했고 값은 context에 없다. initialize의 첫 gate1회와 worker2회, 완료 후 대기600초, 로컬 보관24MiB로 제한한다. 각 put 전의 보관 검사와 최대3시도로 전송 snapshot ZIP 합계도24MiB 이하로 제한한다. 이는 조직 quota나 retry network traffic 상한이 아니다. worker 종료 시 서버도 중지되고, 실제 고정 복원 확인 후 기존 기본 개발 프로필로 돌아가는 별도 시험 범위다. 기존 앱 원본/이력의 사본을 확보하고 included capacity가24MiB 미만이면 시작하지 않는다. 실제 HF 연결, 새 초안 데이터 전송·프로필 전환에 대한 사용자 승인 대기 상태이며 상시 백업은 포함하지 않는다.


## 실제 HF 시험 결과와 재초기화 방어 — plan0.47

[실제 근거](validation/platform_m6_live_backup_trial_20261012.json). 전용 Secret 연결·실제 비공개 저장·snapshot 전송·고정 복원 후 HTTP 원본/이력 일치는 통과했다. 그러나 최대3회 승인에 대해5개 snapshot이 생성됐다. 총529,309바이트는24MiB 이하였지만 횟수 조건을 충족하지 못했다. 즉시 Space를 일시 중지하고 고정 복원 검증 후 기본 개발 프로필로 복귀했다. 현재RUNNING/cpu-basic이며 Secret과6개 전체 객체(기존1+새5)를 보존했고 상시 백업은 꺼져 있다. 일부 항목의 성공을 운영 백업 전체 인수로 표현하지 않는다. 이전 v69/v70 initialize 후보는 재배포하지 않는다.

새 설정 형식은 `koevd-managed-space-v2`다. `initialize`에서는 `initialization_baseline_snapshot_sha256`에 독립적으로 고정한 기존 snapshot digest 목록을 명시한다. `[]`는 원격 snapshot namespace가 비어 있어야 한다는 뜻이다. 현재 개발 Bucket은 비어 있지 않으므로 기본 예시 그대로 초기화할 수 없다. 부팅 시 원격 목록을 읽어 자동으로 기준 목록에 추가하지 않는다. 기준 목록과 다르면 DB root 생성/서버/추가 백업 전에 거절하며, 첫 백업이 기준 목록의 기존 digest이면 서버를 시작하지 않는다. 이미 첫 백업이 있는 뒤 로컬 disk가 새로 만들어지는 상황을 실제 로컬 프로세스에서 재현해 거절을 확인했다. v2의 `existing`/`restore`에서는 이 필드는 `null`이다. v1 `existing`/고정 `restore`는 유지하지만 v1 `initialize`는 거절한다.

22개 CPU검사와27.969초의 실제 소유 로컬 server/worker/HTTP 재기동·복원 검사가 통과했다. 후자는 HF/OAuth test double이며 새 guard의 실제 HF 검증은 아니다. 이 기준 목록 검사는 원격 원자적 lock이나 악의적 Bucket 관리자에 대한 보호가 아니다. 한 초기화 주체·명시적 운영 설정을 사용하고 기존 객체를 외부에서 고정해야 한다. 새 실제 시험·상시 활성화는 별도의 전송 범위와 승인이 필요하다.

## 새 전송 없는 원격 초기화 목록 진단 — plan0.48

`--check`는 기존처럼 네트워크 없는 구조 검사다. 별도 `--check-initialization-baseline`은 initialize 설정에 한해 전용 Secret으로 private Bucket과 고정된 목록을 검사한다. 독립 catalog/registry를 읽고, 목록 불일치는 exit2와 `initialization_inventory_mismatch`로 구분한다. 일치하면 exit0/`initialization_baseline_matches: true`를 출력하지만 DB·백업·child를 만들지 않는다. OAuth 로그인이나 사용자 저장 성공을 증명하지 않는다. 두 플래그는 함께 사용할 수 없다.

읽기 전용 후보는 `generated/managed-readonly-probe-20261012-v72/candidate`이고 Docker CMD도 해당 진단으로 고정했다. 70payload+manifest이며 Secret은 포함하지 않는다. 현재 원격6객체와 빈 기준 목록으로 거부를 관찰할 제안이다. 별도 승인 후 실제 목록 불일치 거부를 관찰했고 새 snapshot 없이 기본 프로필로 복귀했다. 전환 전 현재 초안0건을 확인했으며 이전 원본·이력은 재대조해 보존했다. 이 진단은 정상 초기화/재시작 인수가 아니다.

## 실제 읽기 전용 시험의 인수 범위 — plan0.49

v0.49에서 별도 승인된 읽기 전용 시험을 실제 private CPU Space에서 수행했다. 실제 HF 로그인으로 현재 보이는 초안0건·분석 업로드0건을 확인하고 이전 두 모델 원본/이력 4쌍을 재대조했다. 전용 Secret으로 private Bucket 목록을 읽은 진단은 `initialization_inventory_mismatch`/exit2 경로를 반환했다. 이 진단의 RUNTIME_ERROR는 의도한 거부이며 서버·worker·DB·snapshot을 만드는 경로를 호출하지 않는다. Bucket6객체/67,684,067바이트 목록이 유지됐고 새 결과 전송·snapshot 생성은0회다. 기본 프로필 `f160663af378e777616be89374a20b6c38b57938`로 복귀한 뒤 RUNNING/cpu-basic·배포66파일의 바이트/목록 일치와 브라우저 준비 화면을 확인했다. Secret·public Static·기존 snapshot은 보존했고 상시 백업은 꺼져 있다. 현재25 CPU검사/5.652초는 로컬 근거다. 실제 정상 초기화 후 재시작 전체 인수·현재 Docker 전체 용량·운영 승인·공개 참조는 미완료이고, 이전 최대3회 시험의5회 생성 실패도 통과로 변경하지 않는다. [최신 근거](validation/platform_m6_actual_readonly_guard_20261012.json). Goal active/원래 범위를 유지한다.

## 공개 조회 실패와 비공개 원본 — plan0.50

v0.50에서 공개 목록·상세·비교 재조회 실패가 이전 성공 결과를 현재 결과로 남기던 UI를 수정했다. 목록/상세는 요청 전에 기존 표시를 지우고, 실패는 조회 불가로 표시한다. 비교는 빈 선택기를 잠그며 실패를0건이나 빈 정상 결과로 숨기지 않는다. 오류 원문은 textContent로 표시하고 긴 문자열도 모바일 영역 안에서 줄바꿈한다. 최종 새 비편집 설치50파일/25고정 의존성의 실제 로컬 HTTP·브라우저10흐름/8화면/24.078초가 통과했다. 합성 계정·결과·권한과503/413 응답 double이며 실제 HF/GPU 인수는 아니다. 관련 API38 CPU검사도 통과했고 최종 CSS 보완 전 v74 범위임을 구분했다. 두 UI자산 외48파일·지표·규약·실제 결과는 기존과 같다. 현재 소스의65파일 기본 후보와68파일 관리형 후보를 새로 보존했으며 미업로드다. 실제 private 앱의 마지막 확인 revision은 `f160663af378e777616be89374a20b6c38b57938`이고 이번 UI 수정은 아직 배포하지 않았다. 상시 백업은 꺼져 있고 실제 정상 초기화/재시작·현재 Docker 전체 용량·운영 인수·공개 참조는 미완료다. [최신 근거](validation/platform_m5_public_failure_ui_20261012.json). Goal active/원래 범위를 유지한다.

## 유한 종료의 실제 한계 — plan0.51

v0.51에서 별도 승인된 private CPU 정상 기동 시험의 새 snapshot3개/302,021바이트와 finite worker2회 완료·후속 초기화의 `initialization_inventory_mismatch` 거부를 확인했다. 이번 횟수/용량 한도는 통과했지만 두 초안 보존은 미완료다. 실제 HF 로그인으로8B/4B 초안 저장을 관찰했고 종료 경계의4B 다운로드가503을 반환했다. 독립 다운로드/외부 index·registry 검사에서 마지막 사본에는8B48기록/이력만 있고 새4B 이력은 없었다. 과거4B 사본으로 대체하지 않았다.8B의 고정 복원·실제 재로그인 전후 원본/이력 바이트 일치와 새 저장 거부·공개 조회 불가 UI는 확인했다. 승인된 최신 UI 기본 프로필 `f65a8b1065b934e649e545043c4ac89b18c2d4a5`의 RUNNING/cpu-basic·66파일 바이트/목록 일치로 복귀했고9백업/67,986,088바이트·Secret·public Static을 보존했다. 상시 백업은 꺼져 있다. current26 CPU검사/5.350초와 앞선 nonempty6 목록 로컬 통합27.453초는 별도 모의 provider 근거다. 유한 worker의 마지막 snapshot 전에 새 domain 저장을 닫고 수락된 요청을 기다리는 절차가 다음 구현 대상이다. 실제 두 초안 종료 보존·현재 Docker 전체 용량·운영 인수·공개 참조는 미완료다. [최신 근거](validation/platform_m6_positive_trial_partial_20261012.json). Goal active/원래 범위를 유지한다.

`initialization_store_root_exists`는 기존 로컬 root 때문에, `initialization_inventory_mismatch`는 고정한 원격 목록과 달라서 초기화를 거부한 진단이다. 두 경우 모두 이번 시도의 DB 생성/child 시작은 없다. 이번 실제 후속 시도에서는 원격 목록 불일치 코드가 관측됐다. 원자적 원격 잠금/최신 상태 인증/RPO를 뜻하지 않는다.
