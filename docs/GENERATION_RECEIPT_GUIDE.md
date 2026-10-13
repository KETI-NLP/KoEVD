# 운영자 생성 증거의 검토·인수·철회

2026-10-08. 형식 `koevd-operator-generation-receipt-v1`. 구현은
`generation_receipts.py`와 `SubmissionService`의 로컬 운영자 명령이다.
웹 업로드나 HF 로그인으로 이 증거를 제출·승격할 수는 없다.

## 역할과 한계

사용자가 제공한 결과를 구조 검사했다는 사실과 실제 모델의 생성 실행을
독립적으로 확인했다는 사실은 다르다. 이 기능은 운영자가 실행 원본을 검토한
뒤 그 판단과 증거 파일의 digest를 변경 불가능한 기존 제출 이력에 보존한다.
**파일을 자동으로 읽거나 GPU 실행 진위를 인증하는 기능은 아니다.** 운영자는
참조 파일을 직접 확보하고 checksum, 실행 명령, 모델 revision, runtime,
Task별 출력·분모·실패 상태 및 결과와의 관계를 확인해야 한다.

인수 권한은 서버 설정에 등록된 관리자에게만 있으며, 제출자와 다른 사람이어야
한다. 현재 인수는 `operator_local`이라는 OS 운영자 신뢰 경계에서만 제공한다.
`--actor`는 로그인이나 서명이 아니라 로컬 운영자 선언이다. 이 CLI를 HTTP
요청·사용자 지정 actor/roles/index 경로와 연결해서는 안 된다. 실제 GPU 증거의
독립 검토는 아직 미완료이며 CPU 검사에 쓰인 영수증은 실제 증거가 아니다.

## 영수증에 담는 내용

JSON의 필드는 아래 표와 정확히 일치해야 한다. 최대 32 KiB다. 경로·secret·raw
출력은 넣지 않고, 원본 실행 자료는 별도의 운영자 보관 위치에서 유지한다.

| 필드 | 내용 |
|---|---|
| `format` | `koevd-operator-generation-receipt-v1` |
| `artifact_sha256` | 검토한 정확한 results JSON의 `content_sha256` |
| `input_index_sha256` | 독립 운영자 index의 `content_sha256` |
| `declaration_sha256` | `declaration_identity(results)`로 계산한 모델·생성 설정·규약 identity |
| `execution_scope` | 실제 GPU 근거는 `actual_gpu`; CPU 검사는 `cpu_fixture` |
| `generation_level` | 독립 생성 실행 검토를 의미하는 `operator_reproduced` |
| `evidence_files` | 4–64개 `{kind, sha256, bytes}` 객체. 실제 파일 digest와 양의 byte count |
| `review_statement` | 운영자가 무엇을 직접 확인했는지 4 KiB 이하의 비공개 설명 |

`evidence_files`는 `source_manifest`, `execution_log`, `generation_output`,
`runtime_record` 네 종류를 모두 포함해야 한다. source manifest는 실행 소스,
execution log는 실제 명령·종료·실패 상태, generation output은 frozen 생성
원본, runtime record는 실제 모델/GPU/라이브러리/설정 관측을 가리킨다.
hash 참조를 채우는 것만으로 이 파일들의 실제 내용이 검증되는 것은 아니다.

결과 전체 hash, index hash, 생성 선언이 하나라도 다르면 인수하지 않는다.
측정 재검사만 수행한 자료는 대상 모델 생성 증거로 받아들이지 않는다.

## 로컬 명령

아래는 실제 영수증을 검토한 뒤 실행할 명령 형식이다. 경로·ID·버전·actor는
운영자가 실제 값을 지정한다. 샘플 hash나 가상 판정으로 실증 상태를 만들지 않는다.

```bash
koevd-submissions --store-dir /operator/submissions \
  --trusted-index /operator/trusted_input_index.json --index-id koevd-core \
  --roles-file /operator/roles.json --actor operator-admin \
  accept-generation --id SUBMISSION_ID --revision 1 --expected-version VERSION \
  --receipt-file /operator/reviewed-generation-receipt.json \
  --reason "실행 원본과 반환 결과의 독립 검토 완료" --key UNIQUE_REQUEST_KEY
```

현재 버전은 `get`으로 확인한다. 인수는 제출의 검토·게시 상태를 변경하지 않고
audit event 하나를 추가한다. 같은 요청 key의 재시도는 같은 결과를 반환한다.
동시에 제출이 변경됐으면 버전 충돌로 거부하므로 확인 후 새 요청을 구성한다.
이미 활성 영수증이 있으면 먼저 명시적으로 철회해야 교체할 수 있다.

```bash
koevd-submissions --store-dir /operator/submissions \
  --trusted-index /operator/trusted_input_index.json --index-id koevd-core \
  --roles-file /operator/roles.json --actor operator-admin \
  revoke-generation --id SUBMISSION_ID --revision 1 --expected-version VERSION \
  --receipt-sha256 ACCEPTED_RECEIPT_SHA256 \
  --reason "실행 증거를 재검토하여 철회" --key UNIQUE_REQUEST_KEY
```

receipt digest는 인수된 `history` event에 기록된다. 철회해도 원래 영수증과
검토자의 local identity, 이유, hash 연결은 삭제하지 않는다. 기존 일관된 DB
backup으로 영수증과 철회 이력도 복원된다. 저장소 v1 형식을 바꾸거나 별도 DB를
만들지 않는다. Space 임시 디스크가 운영용 영구 저장으로 바뀌는 것은 아니다.

## 공개 요약과 순위

공개된 정확한 revision에 연결된 활성 영수증만 admission 계산에 제공한다.
인수/철회 후 CPU 분석이 끝나기 전에 제출 버전이 바뀌면 오래된 공개 요약을
반환하지 않는다. 새 결과나 재측정 revision은 영수증을 자동 상속하지 않는다.
이전 revision이 계속 공개돼 있으면 그 revision의 증거만 사용한다.

CPU 영수증은 `cpu_fixture_only`이며 실제 GPU 등록 조건을 충족하지 않는다.
실제 GPU 범위로 운영자가 검토·인수한 증거도 생성에 대한 **운영자 판단**이다.
결과 공개 동의, 이용 권한 검토, 분류기 정확도 또는 정책 승인을 대신하지 않는다.
검토 설명과 증거 참조 원문은 공개 요약에 포함하지 않는다.

기본 정책은 계속 candidate다. 영수증 인수만으로 공식 순위를 활성화하지 않는다.
Task 3의 측정 한계, Task 4의 설명용 지표, Task 3–5 조건부 집단의 순위 제외는
유지한다. 실제 정책 승인·운영용 정책 활성화·원격 저장 및 생성 증거에 대한
독립 운영자 검토는 각각 별도 완료 조건이다. 현재 공개 revision의 활성 영수증과
지표 비교표를 연결한 CPU 구현은 있으나 실제 승인을 대신하지 않는다.

## 실제 전체 평가 자료 — 2026-10-09

최신 두 모델의 전체 결과는 각각 17,670개 기록이다. 비공개 검토 자료는
`generated/full-operator-review-preparation-20261009-v56`에 있다. 각 모델의
14개 증거 파일과 실제 실행 소스 184개 파일의 manifest를 정확히 연결했다.
현재 개발 후보를 과거 실행 소스로 소급하지 않았다. 모든 검토 항목과 공개
동의는 미승인이다. 영수증 검증기가 검토 준비본을 거절하고, 기준 모델 검증기가
공개 동의가 null인 실제 결과 catalog를 거절함을 확인했다. 이 자료 검증은
사람의 인수나 공개 권한 승인이 아니다. [범위와 근거](validation/platform_m5_m6_full_private_review_20261009.json).

## 이전 prefix96 자료의 검토 준비 상태

현재 Qwen3-8B·4B prefix96 반환ZIP은 독립index/raw 재export로 인수됐고 각959개
생성 및1150개 portable record를 확인했다. 해당 결과에 대한 별도의 운영자 자료는
`generated/actual-operator-review-preparation-20261008-v1`에 있다. 각 모델의 정확한
artifact/index/생성 선언과15개 원본 소스·명령·생성·runtime 파일의 경로/hash/크기를
연결했다. 실행 소스는 실제 노드의131파일 고정ZIP이며 최신 개발 소스를 과거 실행에
소급하여 붙이지 않는다.

이 자료는 `koevd-operator-generation-review-preparation-v1` 형식이며 인수 영수증이
아니다. 검토자·검토 설명은 비어 있고 모든 항목은 `not_reviewed`다. 실제 영수증
validator가 두 준비 파일을 거절하는 것도 확인했다. 제출DB·정책·공개 상태는
변경하지 않았다. 운영자는 실제 참조 원본을 독립 검토하고 자신이 확인한 내용으로
위 영수증을 작성해야 한다. custom prefix96 자료를 full standard baseline으로
승격하거나 hash 계산을 실행 진위 인증으로 표현하지 않는다.
