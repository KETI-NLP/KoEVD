# 운영 정책 결정의 보존과 명시적 설정

2026-10-08. `koevd-policy`는 운영자가 검토한 순위 정책의 승인·철회 결정을 별도 로컬 보관소에 남긴다. 서버의 기본 정책은 계속 `candidate`이며 공식 순위를 부여하지 않는다. 이 기능의 구현·합성 검사를 실제 정책 승인으로 해석하지 않는다.

운영자는 독립적으로 관리하는 `roles.json`의 관리자여야 한다. `--actor`는 로컬 OS/운영자 선언이며 HF 로그인·전자서명·신원 인증이 아니다. HTTP 업로드로 결정·역할·보관 경로를 입력할 수 없다. 코드가 실제 사람의 승인 사실을 인증하거나 대신 승인하지 않는다.

## 결정 원문

다음 필드만 허용하며 전체 JSON은 최대16KiB다. 실제 승인·철회 후 운영자가 작성한다. 사용자의 결과 JSON, classifier 재검사나 GPU ZIP을 정책 결정으로 변환하지 않는다.

| 필드 | 정의 |
|---|---|
| `format` | `koevd-operator-policy-decision-v1` |
| `admission_version` | 현재 규칙 버전 `koevd-rank-admission-v1` |
| `action` | `ratify` 또는 `revoke` |
| `actor` | 독립 설정에 등록된 로컬 관리자 선언 |
| `decided_at` | `YYYY-MM-DDTHH:MM:SSZ` 형식의 UTC 결정 시점 |
| `reason` | 실제 검토한 범위와 결정 사유, 최대4096 UTF-8 bytes |
| `previous_sha256` | 앞선 결정의 SHA256, 첫 결정만 `null` |

결정에는 지표·threshold·분류기 정확도·생성 영수증·공개 동의를 덮어쓰는 필드를 허용하지 않는다. 현재 지표별 정책 버전의 승인 여부만 설정한다. Task3 측정 한계, Task4 설명용 성격, 모델별 구성원이 달라지는 조건부 비율의 순위 제외는 승인 뒤에도 유지한다. 정책 승인은 각 실행의 별도 등록 조건을 충족시키지 않는다.

## 로컬 원문 보존

운영자가 검토를 끝내고 작성한 실제 파일에 대한 명령 형식이다. 빈 설명이나 가상 판정으로 실행하지 않는다.

```bash
koevd-policy --policy-root /operator/policy-decisions \
  --roles-file /operator/roles.json --actor OPERATOR_ADMIN \
  archive --decision-file /operator/reviewed-policy-decision.json
```

반환되는 `decision_sha256`을 별도로 보존한다. 이는 정렬된 canonical JSON 내용의 SHA256이며, 줄바꿈·공백까지 포함한 파일 전체의 byte hash와 구분한다. 설정에는 CLI가 반환한 결정digest를 사용한다. 승인 기록은 서버 설정을 바꾸거나 제출을 게시하지 않는다. 동일한 결정의 재실행은 같은hash를 반환한다. 새 사유·시점·철회는 별도 파일이며 앞선 원문을 덮어쓰지 않는다.

기록은 `<SHA256>.json`의 content-addressed 원문이다. 새 파일에 쓰고 flush/fsync한 뒤 같은 로컬 filesystem의 hard link로 완성본을 공개한다. 부분 쓰기가 최종 결정 파일로 선택되지 않도록 한다. 중복 쓰기는 기존 파일을 다시 검증한다. 파일hash, 부모 연결, UTC 시점 순서, 최대256개 history와symlink를 검사한다. 변조·부모 누락·지원하지 않는 규칙 버전·크기 초과는 실패하며 예전 승인으로 자동fallback하지 않는다.

이 보관소는 운영자 소유 로컬 디스크용이다. Disk owner의 악의적 변경, 전자서명 인증, cloud bucket의locking/transaction/durability를 보장하지 않는다. 원격 snapshot·복구 연동은 별도 작업이다.

## 명시적으로 선택한 결정 설정

정책 보관소 경로와 정확한head digest를 **둘 다** 독립 운영 설정에서 제공해야 한다. 어느 하나만 있거나 잘못된chain이면 서버가 시작되지 않는다. 두 값이 모두 없으면 기본candidate다. 가장 최신mtime이나 업로드의 주장으로 결정을 선택하지 않는다.

```bash
koevd-policy --policy-root /operator/policy-decisions \
  --roles-file /operator/roles.json --actor OPERATOR_ADMIN \
  inspect --head-sha256 REVIEWED_DECISION_SHA256
```

`inspect`는 hash·선택된 정책·history 길이만 반환한다. 같은 공통 옵션으로 `history`를 사용하면 관리자용 비공개 원문·사유·actor 이력을 읽는다. 이를 공개 페이지에 출력하지 않는다. 해시는 일관성 증거이며 승인자의 신원 인증이 아니다.

`koevd-submissions`와 `koevd-space`의 공통 옵션에 다음을 추가할 수 있다.

```text
--policy-root /operator/policy-decisions
--policy-head-sha256 REVIEWED_DECISION_SHA256
```

Spaces 서버 설정에서는 `KOEVD_POLICY_ROOT`와 `KOEVD_POLICY_HEAD_SHA256`을 사용할 수 있다. 제출 저장소·독립roles·OAuth·입력catalog를 구성한 환경에서만 사용한다. 선택chain의 마지막 `ratify`는 typed ratified 정책으로, `revoke`는candidate로 로드한다. 서버는 시작 때 선택한 정책을 고정하며 파일 변경을 자동으로 승인·반영하지 않는다. 철회 후 새 결정을 명시적으로 선택해 서버를 재시작하고 공개 지표를 재계산한다. 이미 내려받은 사본을 회수하는 기능은 아니다.

분기chain은 명시적으로 허용한다. 보관소가 유일한 최신 결정을 자동으로 정하지 않으므로 운영자가 현재 승인된branch/head를 책임 있게 선택해야 한다. 과거 승인hash를 명시적으로 고르면 그 과거 정책을 로드하며, 그것을 최신 철회가 적용된 상태로 설명해서는 안 된다.

현재 임시 개발용 `apps/spaces/launch.py`는 두 정책 환경변수를 제거해candidate/no-rank를 고정한다. 실제 운영 활성화는 별도로 검토한 launcher/설정이 필요하다. 배포 후보에 가상 승인 파일·정책 보관소·승인된roles를 넣지 않는다.

## 검증 범위와 남은 사항

CPU 합성 자료로 결정 원문·부모 변조, 크기·중복JSON·symlink·history 한도, 동일 기록의 동시 쓰기와 실패한hard link, 관리자/actor 검증, 실제module CLI, 승인→철회 후 공개 지표 재계산 및서버 startup 경로를 검사했다. 새 비편집 설치의 전체245개 검사와37개 Python source/installed 파일 일치를 확인했다. Linux 노드에서도 새 `/tmp` 폴더에서 실제hard link/directory fsync·symlink 거부·철회/부모변조의4 grouped 검사를 통과했다. Linux 검사는 현재module 한 파일과 기존frozen core 의존성의 범위이며 전체새패키지suite나cloud durability 검사가 아니다. [검증 근거](validation/platform_m6_policy_decisions_cpu_20261008.json).

실제 사람 승인·GPU attestation·HF login·원격durability·컨테이너나live Space 검증은 아니다. 기본 정책은 승인하지 않았으며 실제 생성 영수증·공개 권한·운영 규모의 검증은 각각 별도다.


## DB와 정책 이력의 통합 보존

v0.20의 [비공개 스냅샷 가이드](PRIVATE_SNAPSHOT_GUIDE.md)는 제출 DB와 명시적으로 선택한 정책 부모 chain을 함께 보존·검증하는 `koevd-snapshot`을 설명한다. 복원은 과거 정책을 자동 활성화하거나 최신 철회가 반영됐다고 간주하지 않는다. 기본 DB-only backup과 구분한다. 실제 HF 저장·자동 백업/RPO·운영 복구 검증은 별도 gate다.
