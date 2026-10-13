# 백업 복원 후 변경 대조와 공개 조회 차단

백업을 복원하면 당시 공개됐던 결과도 함께 복원된다. 이후 원본 서비스에서 결과가 철회됐더라도 오래된 백업에는 그 기록이 없다. v0.21은 검증된 스냅샷 복원본을 **복구 대기 상태**로 기록하고, 운영자가 현재 기준과 대조하기 전에는 공개 조회와 변경 요청을 차단한다.

대기는 `submissions.sqlite3`의 불변 `meta` 기록에 남는다. DB 디렉터리를 옮기거나 서버 프로세스를 재시작해도 유지된다. 일반적인 신규 저장소에는 이 대기를 만들지 않는다. 이 기능은 [통합 스냅샷 복원](PRIVATE_SNAPSHOT_GUIDE.md) 경로에 적용된다. 원시 DB 파일을 직접 복사하는 과거 수동 복원에는 표시가 자동으로 생기지 않으므로 운영 복구에 그 방식을 사용하지 않는다.

## 복구 대기 중 가능한 작업

| 작업 | 동작 |
|---|---|
| 공개 목록·공개 응답·요약·리더보드 | `503 recovery_required`. 복구 전 공개 상태를 반환하지 않음 |
| 새 제출·revision·심사·공개·철회·기존 변경 요청 재시도 | 대기 중 거절. 원본 이력과 재시도 응답은 보존 |
| 인증된 소유자/운영자의 비공개 원본·이력 확인 | 기존 권한 검사를 거쳐 가능 |
| 운영자의 checkpoint 생성·대조 | 독립 역할 파일의 로컬 관리자만 CLI 사용 |
| 대기 해제 | 외부에서 고정한 checkpoint와 DB의 논리 상태·입력/규약·정책이 일치해야 가능 |

HTTP에는 대기 해제 경로나 운영 역할 입력을 제공하지 않는다. 파일·DB를 직접 수정할 수 있는 관리자를 막는 보안 장치나 HF 인증의 대체물은 아니다. 로컬 `--actor`는 운영자 선언이며 서명·사람 판정 인증이 아니다.

## Checkpoint에 들어가는 정보

`koevd-recovery checkpoint`는 하나의 SQLite 읽기 트랜잭션에서 다음을 기록한다.

- 각 테이블의 행 수와 정렬된 행의 SHA-256. Artifact BLOB의 실제 바이트도 hash에 반영한다.
- 제출별 마지막 event, 현재 revision·원본 digest·workflow·공개 상태. 누락·변경된 제출을 찾는 데 사용한다.
- 외부 catalog의 입력 digest, registry의 규약 digest, 선택한 typed 정책 digest.
- 전체 논리 상태의 digest와 checkpoint 문서의 canonical JSON content digest.

원본 응답이나 review 사유를 checkpoint에 복사하지 않는다. 제출 ID·상태·hash도 운영 정보이므로 checkpoint는 비공개로 보존한다. SQLite 페이지 배치나 복구 표시 자체는 논리 상태에서 제외해 다른 OS에서 복원해도 원본 상태를 비교할 수 있게 한다. 복구 표시를 제외하는 것은 해당 기록을 삭제한다는 뜻이 아니다. 이전 대조 이력은 DB에 유지된다.

기본 한도는 checkpoint8MiB, 제출10,000개, 전체 검사1,000,000행, 복원100회다. 한도를 넘으면 일부만 검사해 일치했다고 표시하지 않는다.

**Checkpoint 일치는 최신 상태를 인증하지 않는다.** 오래된 백업과 같은 시점의 checkpoint를 고르면 오래된 상태끼리도 일치할 수 있다. 실제 운영자는 현재 기준의 출처와 서비스 변경 중지 시점을 확인하고, 독립적으로 보존한 digest를 선택해야 한다. 성공 결과에도 `latest_state_authenticated:false`를 유지한다.

## 운영 절차

다음은 실제 경로를 선택할 때 사용할 명령 형식이다. 현재 프로젝트에서 실제 운영 복구 대기를 해제한 것은 아니다.

1. 원본 서비스의 변경 요청을 중지하고, 현재 DB와 선택한 정책을 확정한다. Checkpoint와 스냅샷이 같은 기준 상태를 나타내도록 이 기간에 변경을 허용하지 않는다. [백업 worker](BACKUP_WORKER_GUIDE.md)는 한 사본 안의 고정 상태를 일치시켜 보존하지만 현재 source 변경을 중지하지 않는다. 자동 maintenance 전환과 remote commit/RPO 보장은 아직 구현·검증되지 않았다.
2. **원본 서비스의 현재 DB**에서 checkpoint를 생성하고 content digest를 별도 운영 기록에 보존한다. 복원본에서 만든 checkpoint를 현재 기준으로 사용하지 않는다.

```bash
koevd-recovery --store-dir /private/CURRENT_SOURCE_STORE \
  --catalog /operator/catalog.json --protocol-registry /operator/protocols \
  --roles-file /operator/roles.json --actor LOCAL_ADMIN \
  checkpoint --output /operator/NEW_CURRENT_CHECKPOINT.json
```

실제 선택한 정책이 있으면 `--policy-root /operator/policy-decisions --policy-head-sha256 ACTUAL_SELECTED_HEAD`도 지정한다. 이를 생략하면 candidate 정책을 사용한다. Custom 입력만 사용하는 catalog에서는 registry를 생략할 수 있다. Synthetic 자료는 명시적 `--demo`로만 검사한다.

3. 스냅샷을 [검증 후 새 경로에 복원](PRIVATE_SNAPSHOT_GUIDE.md)한다. 복원 receipt의 `recovery_required:true`와 DB의 대기 기록을 확인한다.
4. 복원 DB와 외부 checkpoint를 대조한다.

```bash
koevd-recovery --store-dir /private/NEW_RESTORE/store \
  --catalog /operator/catalog.json --protocol-registry /operator/protocols \
  --roles-file /operator/roles.json --actor LOCAL_ADMIN \
  compare --current-checkpoint /operator/NEW_CURRENT_CHECKPOINT.json \
  --checkpoint-sha256 INDEPENDENTLY_PINNED_CHECKPOINT_CONTENT_DIGEST
```

`compare`는 진단 명령이다. 실행 exit0만으로 일치를 판단하지 말고 `matches`를 확인한다. 누락·추가·변경된 제출 ID와 달라진 테이블·입력/규약·정책을 표시한다. 불일치 시에는 대기를 해제할 수 없다. 누락된 변경을 포함하는 검증된 최신 스냅샷으로 **다른 새 경로에 복원**해 다시 대조한다. Event·revision·재시도 기록을 SQL로 고쳐 hash만 맞추거나 checkpoint를 임의로 다시 봉인하지 않는다. 현재 코드는 누락 이력을 자동 병합하거나 철회 사실을 추정하지 않는다.

5. 실제 대조와 기준 확인을 마친 로컬 관리자가 해제 사유를 기록한다.

```bash
koevd-recovery --store-dir /private/NEW_RESTORE/store \
  --catalog /operator/catalog.json --protocol-registry /operator/protocols \
  --roles-file /operator/roles.json --actor LOCAL_ADMIN \
  reconcile --current-checkpoint /operator/NEW_CURRENT_CHECKPOINT.json \
  --checkpoint-sha256 INDEPENDENTLY_PINNED_CHECKPOINT_CONTENT_DIGEST \
  --statement "실제로 확인한 현재 기준의 출처·변경 중지 시점·대조 범위를 기록"
```

해제는 DB 쓰기 트랜잭션 안에서 상태를 다시 비교한 뒤 불변 기록으로 남긴다. 복원 sequence·snapshot guard·checkpoint·논리 상태·정책·actor·사유를 연결한다. 동일한 기록의 재시도는 기존 기록을 반환하며 다른 사유·기준으로 덮어쓰지 않는다. 이후 정상적인 새 변경은 기존 domain 규칙에 따라 진행한다.

해제는 서버 시작·HF 게시·정책 승인·classifier 정확도 승인·새 공개 동의를 수행하지 않는다. 공개 조회는 해제 당시 선택한 정책과 서버의 typed 정책 digest가 일치해야 한다. 다른 정책으로 서버를 설정하면 `503 recovery_policy_changed`다. 이미 해제된 복원본을 다시 백업·복원해도 새 sequence로 대기를 다시 요구한다. 과거 해제를 재사용해 새 복원을 자동 활성화하지 않는다.

## 확인된 범위와 남은 운영 검증

신규10개 CPU 검사는 오래된 공개 백업과 이후 철회의 불일치, 공개5경로와 변경 요청 차단, 비공개 원본 접근, 관리자/외부 digest/상한, 선택 정책 불일치, metadata 변조, 재복원 시 새 대기, 실제 module CLI·HTTP 경로를 포함한다. 첫 HTTP fixture의 자동 redirect 설정 오류를 수정했고, 최종 비편집 패키지의 전체268개 검사/110.000초/exit0/skips0를 통과했다.

실제 두 모델의 기존 결과2,300기록을 Windows와 Linux의 새 환경에서 복원해 원본 일치와 공개 차단을 확인했다. Linux 새 프로세스에서도 공개5경로·기존 변경 요청 재시도가 차단되고 대기 기록이 유지됐다. 실제 결과에는 해제 기록을 넣지 않았다. 테스트의 가상 심사·정책·대조는 실제 사람의 검토나 HF 로그인 증거가 아니다.

v0.22의 [백업 worker](BACKUP_WORKER_GUIDE.md)는 주기·실패 보존·미보존 변경 상태를 추가했고 실제 기존 두 결과의 양쪽 OS 검사를 통과했다. 보장된 RPO·실제 HF cloud 저장·현재 기준의 운영 복구는 미완료다. 복구 gate의 [v0.21 근거](validation/platform_m6_recovery_cpu_20261008.json)와 [개발 기록](PLATFORM_VALIDATION_LOG.md)을 참조한다.
