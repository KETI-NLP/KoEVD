# 비공개 제출 데이터와 운영 정책의 백업·복원

현재 상태(2026-10-12/plan0.44): v0.44에서 사용자에게 저장 대상·정확한 스냅샷·용량 한도를 제시하고 명시적 승인을 받은 뒤 비공개 `KETI-NLP/KoEVD-Platform-Backups-Dev`를 만들었다. 포함 용량0/3TB를 재확인했고 추가 구독·유료 용량 구매 없이67,154,758바이트 스냅샷1개를 전송했다. 별도 재다운로드·오프라인 복원 후 실제 두 모델35,340기록의 원본·상태·이력과 고정 checkpoint가 일치했다. 복원 공개조회503/변경 차단·없는 객체 조회 실패의 기존 사본 보존도 확인했다. 실행95.062초/exit0이며 코드·GPU·서버 설정은 바꾸지 않았다. 앱의 자동 백업·재시작 복구/최신 상태·RPO·운영자 승인·공개 참조·추가3개 browser 다운로드는 미완료다. [최신 근거](validation/platform_m6_actual_private_cloud_20261012.json). Goal active/원래 범위를 유지한다.

아래 이전 checkpoint는 당시 기록이다. [연결 준비](TEAM_BACKUP_CONNECTION.md).

현재 상태(2026-10-12/plan0.43): v0.43에서 실제 Team 가입을 API로 확인하고 별도 비공개 CPU Docker Space `KETI-NLP/KoEVD-Platform-Dev`를 배포했다. 현재 revision `03e79a75ee35570b83948343d521f684a38fce01`의 payload65개+manifest가 일치하고 RUNNING/cpu-basic이다. 실제 HF 로그인 후 두 모델48+48기록의 업로드·분석·대응 비교와 비공개 draft2건 저장/재조회를 확인했다. 내려받은 원본 JSON 내용·HF OAuth 생성 이력과 분석 JSON/HTML의 native 바이트가 일치한다. v64의 별도 HTTP 검증에서는 다섯 출력·세션 격리·삭제가 통과했다. 현재 브라우저의 나머지3개 다운로드는 확인하지 못했다. Private proxy cookie 누락을 수정했고 관련4+6+3+11 검사가 통과했다. 기존 전체310은 이전 설치 근거다. Public Static은 그대로이며 영구 저장·운영자 승인·공개 참조/공식 순위·production은 미완료다. [최신 근거](validation/platform_m5_m6_team_hosted_20261012.json) Goal active/원래 범위를 유지한다.

아래 이전 검증의 범위·수치는 당시 근거다. [운영 준비](TEAM_SPACE_OPERATIONS.md).

`koevd-snapshot`은 SQLite 제출 데이터와 운영자가 명시적으로 선택한 정책 결정 이력을 하나의 비공개 ZIP으로 보존한다. 기존 `koevd-submissions backup`은 DB만 백업하므로 정책 보관소를 포함하려면 이 명령을 사용한다. 복원은 검증을 마친 새 디렉터리에만 가능하며, 서버 시작·공개 게시·정책 활성화를 수행하지 않는다.

이 기능은 운영자의 로컬 명령이다. 결과 업로드 화면과 HTTP API에는 백업·복원·정책 선택 기능을 제공하지 않는다. `--actor`는 로컬 운영자 선언이며 HF 로그인이나 서명이 아니다. 독립적으로 관리하는 역할 파일의 관리자만 CLI를 실행할 수 있다.

## 포함되는 정보와 검증 기준

| 항목 | 보존·검증 방식 |
|---|---|
| 제출 원본·revision·event·철회 상태·재시도 응답 | SQLite backup API로 일관된 DB 사본 생성. 살아 있는 DB 파일을 직접 복사하지 않음 |
| 정책 결정 | 명시한 head와 그 부모 이력만 보존. 다른 분기나 수정 시각으로 최신 결정을 추정하지 않음 |
| 입력·평가 규약 | 독립 catalog의 index content digest와 registry definition digest를 manifest에 고정 |
| ZIP과 내부 파일 | 외부에서 지정한 ZIP **바이트** SHA-256 및 각 파일 크기·바이트 SHA-256 검사 |
| DB | 알려진 SQL schema와 일치하는지 먼저 검사한 뒤, 읽기 전용으로 SQLite 무결성·참조·원본 seal·외부 index에 따른 결과 구조·event chain·revision·재시도 JSON·행 수 확인 |
| 복원 결과 | 새 `store/`, 선택한 경우 `policy/`, `restore-receipt.json`. 기존 경로를 덮어쓰지 않음 |

ZIP에는 gold/index 파일, 운영 역할, 로그인 토큰, 서버 설정을 넣지 않는다. 복원 시 catalog와 registry를 **백업 ZIP 밖에서** 공급하고 같은 바인딩인지 확인한다. 해당 파일은 운영자의 별도 배포·보존 대상이다. ZIP에서 꺼낸 index를 신뢰 입력으로 사용하지 않는다. 표준 index는 외부 registry 검증도 필요하다.

스냅샷은 특정 시점의 DB와 명시적으로 선택한 불변 정책 chain의 묶음이다. 두 보관소를 하나의 전역 트랜잭션으로 묶거나 실행 중인 서버의 현재 정책을 자동 관측하지 않는다. SHA·schema·이력 검사는 일관성 검사이며 사람의 승인이나 모델 생성 진위를 인증하지 않는다.

## 생성과 새 디렉터리 복원

현재 후보를 설치하면 `koevd-snapshot`을 사용할 수 있다. `python -m koevd_eval.snapshots`도 같은 명령이다. 다음은 실제 운영자가 선택할 경로를 보여주는 명령 형식이며 가상의 정책 승인을 실행하는 예시가 아니다.

```bash
koevd-snapshot --catalog /operator/catalog.json \
  --protocol-registry /operator/protocols \
  --roles-file /operator/roles.json --actor LOCAL_ADMIN \
  create --store-dir /private/submissions \
  --policy-root /operator/policy-decisions \
  --policy-head-sha256 ACTUAL_SELECTED_DECISION_SHA256 \
  --output /private/backups/NEW_SNAPSHOT.zip
```

기본 candidate 정책을 보존하려면 `--policy-root`와 `--policy-head-sha256` 둘 다 생략한다. 하나만 지정하면 실패한다. 현재 정책이 실제로 승인되었다고 가정하지 않는다. 표준 index가 없는 custom catalog는 `--protocol-registry`를 생략할 수 있다. Synthetic catalog 검사는 명시적 `--demo`가 필요하며 실제 GPU나 사람 검토의 증거가 아니다.

성공 출력의 ZIP SHA-256을 별도 운영 기록에 보존한다. 내려받은 파일과 같은 저장소의 임의 manifest에서 기대 hash를 가져오지 않는다.

```bash
koevd-snapshot --catalog /operator/catalog.json \
  --protocol-registry /operator/protocols \
  --roles-file /operator/roles.json --actor LOCAL_ADMIN \
  restore --input /private/downloads/SNAPSHOT.zip \
  --sha256 INDEPENDENTLY_PINNED_ZIP_SHA256 \
  --destination /private/NEW_OFFLINE_RESTORE
```

검사 실패 시 최종 복원 디렉터리를 게시하지 않는다. 복원 명령끼리 잠금 파일로 경로 생성을 직렬화한다. 프로세스가 강제 종료되어 잠금이나 임시 파일이 남으면 운영자가 실행 중인 명령과 경로를 확인한 뒤 정리한다. 복원 receipt 없는 경로를 운영 저장소로 사용하지 않는다. POSIX 디렉터리/DB/ZIP은 비공개 권한으로 보존하며 Windows ACL은 운영자가 관리한다. 디스크를 임의로 수정하는 관리자에 대한 보호는 아니다.

복원 receipt는 `automatic_activation:false`, `latest_state_verified:false`, `requires_withdrawal_reconciliation:true`를 기록한다. v0.21부터 DB 안에도 새 복구 대기 sequence를 추가하고 `recovery_required:true`를 반환한다. 원본 제출·artifact·event·재시도 기록을 바꾸지 않으며 receipt의 기존 counts는 입력 스냅샷의 수량이다. 복구 metadata는 그 이후에 추가된다. 대기 중 공개 조회와 domain 변경 요청은 차단하고 기존 권한에 따른 비공개 원본·이력 확인만 허용한다. [복구 대조 가이드](RECOVERY_GUIDE.md)에 외부 checkpoint 대조·불일치·해제 절차를 설명했다. 오래된 스냅샷에는 이후의 철회나 정책 철회가 없을 수 있으므로 복원했다고 현재 상태가 되거나 과거 공개 결과를 다시 노출할 권한이 생기지 않는다. 정책 적용도 [운영 정책 가이드](OPERATOR_POLICY_GUIDE.md)의 별도 명시적 설정 절차를 따른다.

## HF Bucket 전송 후보

HF [Bucket 문서](https://huggingface.co/docs/hub/storage-buckets)는 bucket을 변경 가능한 비버전 저장소로 설명한다. [Python API](https://huggingface.co/docs/huggingface_hub/guides/buckets)의 단일 파일 업로드·다운로드를 사용한다. 실제 SDK 1.31.0의 함수 signature도 확인했다. 설치할 때 `pip install '.[storage]'`를 사용한다. 이 경로에는 Bucket API를 제공하는 SDK가 필요하며 오래된 `huggingface-hub>=0.34` 설치만으로 지원된다고 보장하지 않는다.

아래 명령은 별도로 승인·준비된 **기존 비공개 bucket**에서만 실행한다. 이 코드가 bucket을 생성하거나 구독·비용을 활성화하지 않는다. 외부 전송 승인이 없는 현재 개발 과정에서는 실행하지 않았다.

```bash
koevd-snapshot --catalog /operator/catalog.json \
  --protocol-registry /operator/protocols \
  --roles-file /operator/roles.json --actor LOCAL_ADMIN \
  put-hf --bucket ORG/EXISTING_PRIVATE_BUCKET \
  --input /private/backups/SNAPSHOT.zip --sha256 PINNED_ZIP_SHA256

koevd-snapshot --catalog /operator/catalog.json \
  --roles-file /operator/roles.json --actor LOCAL_ADMIN \
  fetch-hf --bucket ORG/EXISTING_PRIVATE_BUCKET \
  --sha256 PINNED_ZIP_SHA256 --output /private/downloads/NEW_SNAPSHOT.zip
```

`put-hf`는 semantic 검사 후 frozen 사본을 `koevd-snapshots/<ZIP-byte-digest>.zip` 한 개 객체로 보낸다. 같은 이름의 객체가 있으면 덮어쓰지 않고 읽어 검증한다. 업로드 후에도 별도 다운로드의 바이트가 일치해야 성공한다. 내려받기는 복원과 별도이며 파일 다운로드만으로 의미 검증이나 운영 복구가 완료되지 않는다. HF 오류의 인증·요청 상세를 로그에 출력하지 않는다.

HF batch 작업은 전역 트랜잭션이 아니며 조건부 쓰기나 WORM을 보장하지 않는다. 업로드 중 장애는 실패로 남고 같은 digest로 재시도한다. 관리자에 의한 객체 삭제·변경, 사전 확인 이후 visibility 변경은 이 adapter가 막을 수 없다. 다운로드 전 metadata 크기를 검사하고 완료 후 크기/hash를 재검사하지만, 전송 중 원격 객체가 커지면 SDK가 바이트를 내려받은 뒤 거절할 수 있다. 초기 후보의 기본 상한은 ZIP 약2GiB+8MiB, DB2GiB, manifest256KiB, 정책256개, 전체 DB 검사1,000,000행이다.

**살아 있는 SQLite DB를 bucket mount에 놓지 않는다.** 단일 호스트의 로컬 DB와 별도 스냅샷 전송을 사용한다. v0.22의 [주기 백업 worker](BACKUP_WORKER_GUIDE.md)는 같은 고정 DB의 ZIP/checkpoint와 실패/미보존 변경 상태를 제공한다. 이는 마지막 저장 이후의 변경 손실을 막는 동기식 remote commit이나 보장된 RPO가 아니다. 실제 HF 저장·현재 기준 운영 복구·상시 기동은 별도 gate다.

## 확인된 범위

- 신규 CPU 검사13개: 실제 CLI 관리자 경계, 원본·이력·철회·재시도 복원, 정책 chain, 외부 표준 registry, 변조·기존 경로·파일 형식·상한·동시 복원·실패 처리, 모의 HF upload/readback 계약.
- 실제 두 모델의 기존 prefix96 결과2,300 records를 비공개 draft 스냅샷으로 생성하고 Windows의 새 저장소 및 Linux 노드의 새 환경에서 외부 원본과 대조해 복원했다. 신규 inference·전체 표준 평가·심사·공개가 아니다.
- 실제 HF Bucket 저장·클라우드 장애 복구·HF login/live Space는 미검증이다. UI 자산은 이번 변경에 포함하지 않았다.

명령·hash·설치 검사 결과는 [검증 기록](PLATFORM_VALIDATION_LOG.md)과 `docs/validation/platform_m6_snapshots_cpu_20261008.json`에 기록한다.
