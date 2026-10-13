# 비공개 주기 백업과 미보존 변경 확인

현재 상태(2026-10-12/plan0.44): v0.44에서 사용자에게 저장 대상·정확한 스냅샷·용량 한도를 제시하고 명시적 승인을 받은 뒤 비공개 `KETI-NLP/KoEVD-Platform-Backups-Dev`를 만들었다. 포함 용량0/3TB를 재확인했고 추가 구독·유료 용량 구매 없이67,154,758바이트 스냅샷1개를 전송했다. 별도 재다운로드·오프라인 복원 후 실제 두 모델35,340기록의 원본·상태·이력과 고정 checkpoint가 일치했다. 복원 공개조회503/변경 차단·없는 객체 조회 실패의 기존 사본 보존도 확인했다. 실행95.062초/exit0이며 코드·GPU·서버 설정은 바꾸지 않았다. 앱의 자동 백업·재시작 복구/최신 상태·RPO·운영자 승인·공개 참조·추가3개 browser 다운로드는 미완료다. [최신 근거](validation/platform_m6_actual_private_cloud_20261012.json). Goal active/원래 범위를 유지한다.

아래 이전 checkpoint는 당시 기록이다. [연결 준비](TEAM_BACKUP_CONNECTION.md).

현재 상태(2026-10-12/plan0.43): v0.43에서 실제 Team 가입을 API로 확인하고 별도 비공개 CPU Docker Space `KETI-NLP/KoEVD-Platform-Dev`를 배포했다. 현재 revision `03e79a75ee35570b83948343d521f684a38fce01`의 payload65개+manifest가 일치하고 RUNNING/cpu-basic이다. 실제 HF 로그인 후 두 모델48+48기록의 업로드·분석·대응 비교와 비공개 draft2건 저장/재조회를 확인했다. 내려받은 원본 JSON 내용·HF OAuth 생성 이력과 분석 JSON/HTML의 native 바이트가 일치한다. v64의 별도 HTTP 검증에서는 다섯 출력·세션 격리·삭제가 통과했다. 현재 브라우저의 나머지3개 다운로드는 확인하지 못했다. Private proxy cookie 누락을 수정했고 관련4+6+3+11 검사가 통과했다. 기존 전체310은 이전 설치 근거다. Public Static은 그대로이며 영구 저장·운영자 승인·공개 참조/공식 순위·production은 미완료다. [최신 근거](validation/platform_m5_m6_team_hosted_20261012.json) Goal active/원래 범위를 유지한다.

아래 이전 검증의 범위·수치는 당시 근거다. [운영 준비](TEAM_SPACE_OPERATIONS.md).

`koevd-backup`은 같은 시점의 **스냅샷 ZIP과 checkpoint**를 한 쌍으로 보존한다. Checkpoint는 복사 이후의 살아 있는 DB가 아니라, 검증한 ZIP 안의 고정 DB에서 계산한다. 따라서 복사 직후 새 철회가 발생해도 그 변경을 백업에 포함됐다고 표시하지 않는다. 복원과 공개 재개는 [별도 복구 절차](RECOVERY_GUIDE.md)를 따른다.

기본 대상은 로컬 비공개 디렉터리다. 기존 비공개 HF Bucket 전송은 명시적 선택 기능이며 실제 클라우드 검증은 아직 수행하지 않았다. 일정 주기로 복사하는 worker가 있다고 해서 Space의 임시 디스크가 영구 저장소로 바뀌거나, 변경이 원격에 즉시 보존되는 것은 아니다.

## 실행 전 준비

- 설치한 현재 패키지, 기존 로컬 제출 저장소, 운영자가 독립적으로 관리하는 catalog·역할 파일을 사용한다. `--actor`는 역할 파일의 관리자여야 한다. 이는 로컬 운영자 선언이며 HF 로그인·서명이 아니다.
- 백업 디렉터리는 제출 DB·정책 보관소 밖에 별도로 둔다. 비공개 원본이 들어가므로 접근 권한을 제한한다. Linux 디렉터리0700/파일0600을 적용하며 Windows ACL은 운영 환경에서 별도로 관리한다.
- 표준 규약을 사용하면 `--protocol-registry`를 지정한다. 승인된 정책을 실제 선택했을 때만 `--policy-root`와 `--policy-head-sha256`을 함께 지정한다. 기본 정책을 바꾸거나 새 승인을 만드는 명령이 아니다.
- 백업 대상 외에도 현재 기준 checkpoint·완료 receipt·ZIP byte SHA를 독립된 운영 기록에 보존한다. 같은 장애로 이 기록까지 잃으면 원격 객체 목록이나 수정 시각만으로 최신 상태를 확정할 수 없다.

## 로컬 실행

다음은 운영자가 실제 경로를 선택할 때 사용할 명령 형식이다. 첫 백업은 즉시 수행하고, 완료 후 지정한 간격을 기다린다. 따라서300초 간격은 **시작 간격이나 최대 손실 시간의 보장**이 아니다.

```bash
koevd-backup \
  --store-dir /private/live-store --backup-root /private/backups \
  --catalog /operator/catalog.json \
  --roles-file /operator/roles.json --actor LOCAL_ADMIN \
  run --cycles 2 --interval-seconds 300

koevd-backup \
  --store-dir /private/live-store --backup-root /private/backups \
  --catalog /operator/catalog.json \
  --roles-file /operator/roles.json --actor LOCAL_ADMIN \
  status
```

`python -m koevd_eval.backups`도 같은 명령이다. `--cycles 0`은 종료 신호까지 반복하겠다는 명시적 선택이며 기본은1회다. 이번 개발은 시스템 서비스·예약 작업을 설치하거나 상시 worker를 기동하지 않았다. 단일 worker lock을 사용하며 중단된 프로세스의 lock을 자동으로 빼앗지 않는다. 재실행 전에는 운영자가 해당 프로세스의 종료를 확인해야 한다.

시도별 `attempt-NNNNNN-UUID/`에 다음을 보존한다.

| 파일 | 의미 |
|---|---|
| `attempt.json` | 시도 번호·운영자·시작 시각·대상 |
| `snapshot.zip` | 고정 DB와 선택한 정책 chain |
| `checkpoint.json` | 그 ZIP의 고정 상태에서 계산한 논리 상태 |
| `COMPLETED.json` | 로컬 검증과, 선택한 경우 원격 readback까지 통과한 완료 기록 |
| `FAILURE.json` | 실패 코드. 비공개 응답·provider 오류의 토큰/URL은 기록하지 않음 |

완료 기록은 마지막에 게시한다. 실패·중단한 사본을 성공으로 승격하지 않고 이전 성공본과 부분 파일을 보존한다. 반복 중 실패가 있어도 다음 주기에 재시도하되, 유한 실행의 최종 종료 코드는2다. 선택한 최신 성공본의 바이트나 checkpoint가 달라지면 상태 조회도 실패하며, 조용히 이전 사본으로 돌아가 정상이라고 표시하지 않는다.

기본 보관 상한은8GiB·최대1000시도다. DB 크기+16MiB를 보수적으로 예약하고 보관 파일 총량도 검사한다. SQLite journal·임시 압축 해제 공간까지 제어하는 디스크 quota는 아니다. 기존 성공본 자동 삭제/GC는 구현하지 않았다. 상한에 도달하면 새 시도가 실패하므로 worker를 중지한 상태에서 독립 사본과 운영 기록을 확인하고 보관 정책을 적용해야 한다. 실패 기록도 시도 상한에 포함된다.

## 상태 해석

| 항목 | 해석 |
|---|---|
| `configured_target` | 이번 조회가 로컬만인지, 명시한 HF Bucket인지 |
| `last_verified_sequence` | 해당 대상에서 완료·검증한 마지막 시도. 없으면 `null` |
| `changes_pending` | 현재 DB/입력/규약/선택 정책이 마지막 백업과 다른지. 백업이 없으면 `null` |
| `events_since_verified_backup` | 현재 DB와 백업의 event 행 수 차이. 상태가 뒤로 돌아가면 `null` |
| `comparison` | 다른 제출·테이블·바인딩·정책. event 수가0이어도 다른 변경이 있을 수 있음 |
| `seconds_since_backup_started` | 관측 시각과 마지막 성공 시도의 시작 시각 차이. 시계 역행은 `null` |
| `failed_attempts` / `incomplete_attempts` | 실패 또는 완료 기록 없는 시도 번호 |
| `remote_readback_verified` | 해당 성공 시도에서 원격 바이트 대조까지 통과했는지. 지금의 존재·visibility는 별도 확인 |

이 값은 관측 시점의 상태다. 조회 직후의 변경이나 서버 장애 시점의 손실을 보장하지 않는다. `rpo_guaranteed_seconds:null`, `latest_state_authenticated:false`를 유지한다. RPO는 장애 시 잃을 수 있는 변경의 시간 범위를 뜻하며, 주기·마지막 복사 나이·event 차이를 보장된 RPO로 바꾸어 표기하지 않는다.

## 기존 비공개 HF Bucket 선택

승인된 기존 비공개 대상과 해당 환경의 credential을 준비했을 때만 실행한다. Bucket 생성·플랜 결제·visibility 변경은 수행하지 않는다. SDK는 `pip install '.[storage]'`의1.31이상 API가 필요하다.

```bash
koevd-backup \
  --store-dir /private/live-store --backup-root /private/backups \
  --catalog /operator/catalog.json \
  --roles-file /operator/roles.json --actor LOCAL_ADMIN \
  --bucket ORG/EXISTING_PRIVATE_BUCKET --enable-remote-backup \
  run --cycles 2 --interval-seconds 300
```

두 선택 인수가 모두 필요하다. `status`에도 같은 대상을 지정해야 하며 로컬 성공본이 HF 성공으로 집계되지 않는다. ZIP 한 객체를 digest 기반 key로 보내고 다운로드 바이트를 대조한 후에 완료한다. 정책은 ZIP 안의 선택된 chain이며 독립 catalog·역할·토큰은 포함하지 않는다. 저장 실패는 완료로 남기지 않는다. HF Bucket의 mutable/nontransactional 특성·visibility 경합·다운로드 한계는 [스냅샷 가이드](PRIVATE_SNAPSHOT_GUIDE.md)를 참조한다.

복원하려면 독립적으로 고정한 ZIP byte digest와 외부 catalog/registry로 `koevd-snapshot fetch-hf`·`restore`를 수행한다. 다운받은 ZIP에서 `derive_checkpoint()`로 같은 checkpoint를 다시 계산할 수 있지만, 이는 백업 당시 상태의 일치 확인이다. 현재 변경을 보존했는지와 복구 대기 해제는 현재 기준의 외부 checkpoint 대조로 확인한다. 오래된 완료 receipt나 해당 ZIP의 checkpoint만으로 현재 상태의 복구를 승인하면 안 된다.

## 확인된 범위

신규10개 CPU 검사와 새 비편집 패키지 전체278개 검사/120.094초/exit0/skips0를 통과했다. API 전송 검사는 모의 provider이며 실제 HF cloud 저장 증거가 아니다. 실제 두 모델의 기존2,300기록을 Windows·Linux에서 격리된 비공개 draft로 복사하고 두 주기, 실제 설정 quota 실패, 이전 사본 보존과 미보존 변경1건, 오래된 복원의 대기 유지·대조 거절을 확인했다. Linux 새 프로세스에서는 상태/권한/설치 바이트도 확인했다.

검증을 위한 draft 철회는 CPU workflow 검사이며 실제 사용자 동의 철회·사람의 내용 심사·운영 복구 승인이 아니다. 실제 출력에 공개·복구 해제 기록을 만들지 않았다. [근거 JSON](validation/platform_m6_backups_cpu_20261008.json), [개발 기록](PLATFORM_VALIDATION_LOG.md). 실제 HF 저장/운영 복구·원격 commit/RPO 보장·상시 운영·HF 로그인/컨테이너/live Space는 남아 있다.
