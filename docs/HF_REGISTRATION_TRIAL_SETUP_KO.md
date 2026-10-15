# 비공개 등록 시험용 HF Secret 설정

이 안내는 준비된 비공개 시험 앱의 자격증명 설정에 관한 것이다. Secret 설정은 원본 전송·시험 실행·공개 게시 승인을 대신하지 않는다. 설정 중 앱 활성화와 초기화는 0, Space는 PAUSED로 유지한다.

2026-10-14 06:23 UTC의 읽기 전용 확인에서 아래 네 Secret 이름은 모두 미등록이었다. 이후 준비 코드만 revision `71c010860056b6f80d13f8e1da7a4b92a3bbca4a`으로 갱신했고 비공개·PAUSED·활성화/초기화 0을 확인했다. 재개 시 현재 설정을 다시 확인한다.

## 필요한 값과 저장 위치

모두 [시험 Space의 Settings](https://huggingface.co/spaces/KETI-NLP/KoEVD-Platform-Registration-Dev/settings)에 **Secret**으로 저장한다. 일반 Variable에 토큰을 넣지 않는다. Secret 값은 채팅·스크린샷·명령 로그로 전달하지 않는다. Space는 Secret과 일반 환경변수를 설정 화면에서 구분한다. [HF Space 설정 안내](https://huggingface.co/docs/hub/spaces-overview#managing-secrets-and-environment-variables)

| Secret 이름 | 넣을 값 | 허용 대상 |
|---|---|---|
| `KOEVD_STATE_TOKEN` | 새 state 전용 HF fine-grained 토큰 | `KETI-NLP/KoEVD-Platform-State-Dev` 읽기·쓰기 |
| `KOEVD_STATE_ACCESS_KEY_ID` | 위 토큰에서 생성한 S3 access key ID | 같은 state Bucket |
| `KOEVD_STATE_SECRET_ACCESS_KEY` | 같은 쌍의 S3 secret access key | 같은 state Bucket |
| `KOEVD_REFERENCE_TOKEN` | 별도로 만든 reference 전용 HF fine-grained 토큰 | `KETI-NLP/KoEVD-Platform-Backups` 읽기만 |

두 토큰의 대상과 권한은 다르다. 기존 `...Platform-Dev`의 백업 토큰이나 CLI 관리용 토큰을 이 앱의 state 쓰기 토큰으로 재사용하지 않는다. 앱 구현은 관리용 토큰으로 자동 대체하지 않는다.

## 1. state 전용 토큰

1. [HF Access Tokens](https://huggingface.co/settings/tokens)를 연다.
2. 새 토큰을 만들고 fine-grained 유형을 선택한다. 이름은 예를 들어 `koevd-registration-state-dev`로 정한다.
3. 대상 리소스를 정확히 `KETI-NLP/KoEVD-Platform-State-Dev` 하나로 제한한다. 해당 Bucket의 목록 확인·다운로드·업로드에 필요한 읽기·쓰기 권한을 선택한다.
4. 조직 전체나 다른 model/dataset/Space/Bucket의 쓰기를 추가하지 않는다. Bucket 단위 제한을 선택할 수 없거나 조직 승인 대기 상태라면 그 상태를 알려준다.
5. 토큰을 생성하고 시험 Space의 Settings에서 Secret 이름 `KOEVD_STATE_TOKEN`으로 직접 저장한다.

HF는 production용으로 fine-grained 토큰과 용도별 토큰 분리를 권장한다. 이 안내의 특정 리소스·권한 범위는 KoEVD 앱의 실행 계약이다. [HF 토큰 안내](https://huggingface.co/docs/hub/security-tokens)

## 2. 같은 토큰에서 S3 자격증명 생성

1. 토큰 목록에서 **방금 만든 state 토큰**의 메뉴를 연다.
2. `Generate S3 credentials`를 선택한다.
3. 생성된 access key ID를 `KOEVD_STATE_ACCESS_KEY_ID` Secret에 저장한다.
4. 함께 생성된 secret access key를 `KOEVD_STATE_SECRET_ACCESS_KEY` Secret에 저장한다.

S3 자격증명은 원래 HF 토큰의 권한을 이어받는다. secret access key는 생성 시 한 번만 표시되므로 두 값을 같은 쌍으로 저장해야 한다. HF 토큰 문자열을 S3 secret access key 대신 넣지 않는다. 메뉴가 보이지 않으면 조직 전체 쓰기 토큰으로 바꾸지 말고 알려준다. [HF S3 자격증명 안내](https://huggingface.co/docs/hub/storage-buckets-s3#generating-s3-credentials)

## 3. reference 전용 읽기 토큰

1. 별도의 fine-grained 토큰을 만든다. 이름은 예를 들어 `koevd-registration-reference-dev`로 정한다.
2. 대상은 기존 `KETI-NLP/KoEVD-Platform-Backups` 하나이며 읽기만 허용한다. 새 `...State-Dev`나 옛 `...Backups-Dev`를 선택하지 않는다.
3. 이 값을 시험 Space의 Secret `KOEVD_REFERENCE_TOKEN`에 직접 저장한다.

이 토큰에는 S3 쓰기 자격증명을 만들 필요가 없다. 앱은 기준 결과를 읽고 원본 hash를 확인하는 데만 이 토큰을 사용한다.

## 4. 설정 완료 뒤 확인

값 대신 “시험 Space에 네 Secret 저장 완료”라고 알려준다. 에이전트는 이름의 존재만 확인할 수 있으며 값이나 올바른 권한을 그 확인만으로 증명할 수 없다. 실제 접근·저장·복원 검증은 승인된 제한 시험에서 별도로 진행한다.

유지할 일반 Variables:

- `KOEVD_REGISTRATION_ENABLED=0`
- `KOEVD_STATE_INITIALIZE=0`
- `KOEVD_STATE_BUCKET=KETI-NLP/KoEVD-Platform-State-Dev`
- `KOEVD_STATE_MAX_DATABASE_BYTES=134217728`
- `KOEVD_STATE_MAX_RETAINED_BYTES=1610612736`
- `KOEVD_STATE_MAX_SEQUENCE=12`

HF CLI 로그인과 웹 앱의 HF OAuth 로그인은 별개다. 앱 로그인은 해당 서비스의 Sign in with Hugging Face 흐름에서 확인한다. 저장용 토큰으로 사용자의 로그인이나 모델 생성 검증을 대신하지 않는다.

새 유한 시험은 기존 두 기준 결과 합계 89,396,889바이트 읽기, 최대 3회 startup/restart/restore, 최대 12개 acknowledged checkpoint·DB당 128MiB·보존량 1.5GiB 범위로 별도 요청되어 있다. 실행 전 실제 포함 용량과 승인 여부를 확인하고 시험 후 이 Space를 정지한다. 이 설정 안내를 시험 승인 기록이나 상시 운영 정책으로 사용하지 않는다.
