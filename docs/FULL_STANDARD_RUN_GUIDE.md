# 전체 표준 평가 실행과 독립 인수

전체 표준 평가는 `koevd-core-canonical-v1` registry가 고정한 입력을 모두 사용한다. 기존 prefix4/96 결과는 통합 검사이며 전체 표준 기준선으로 등록하지 않는다. **전체 입력 완료와 classifier 정확도·사람 판정·공개 허가·공식 순위 자격은 별도 조건**이다.

| 과업 | 입력/결과 수 | 설명 |
|---|---:|---|
| Task 1 | 2,000 | primary core 입력 위험 판단 |
| Task 2 | 8,000 | 같은 core source의 네 variant |
| Task 3 | 2,659 | core2,000 + tool784 − overlap125의 합집합 생성 |
| Task 4 | 2,659 | Task 3의 같은 답변에 대한 전략 측정. 새 생성 요청 없음 |
| Task 5 | 2,352 | tool784의 세 framing. 실제 도구 실행 없음 |

모델당 생성 요청15,011개·portable 기록17,670개다. Task 3 전체 합집합과 primary core를 구분하고, Task 2/5의 반복 variant를 독립 source로 세지 않는다. 출력 실패·잘림·파싱 문제는 분석에 남기며 의미적 정답과 API 성공을 구분한다.

## 실행 전 입력과 환경 확인

고정 source bundle·wheel·dataset/model revision을 검증한다. 이번 실행은 기존 B300 cache의97개 고유 파일을 다시 hash 검사했다. 새 core/measure 환경은 현재 wheel을 설치하고 기존 의존성 디렉터리를 읽기 전용으로 참조한다. 두 환경의 package Python40개를 source와 비교했다. 기존 GPU 환경과 weights는 변경하지 않았다.

Registry는 dataset 경로를 벗어나는 symlink를 거절한다. Linux HF snapshot은 blobs로 향하는 symlink를 사용할 수 있으므로 규약이 지정한9개 파일을 별도 dataset 디렉터리에 실제 파일로 복사하고 각 SHA-256을 다시 확인한다. 경로 검사를 완화하거나 전체 cache를 데이터 폴더로 간주하지 않는다.

```bash
koevd-results protocol-index \
  --registry /verified/source/configs/protocols \
  --protocol-id koevd-core-canonical-v1 \
  --dataset-dir /private/pinned-dataset \
  --run-dir /private/NEW_OPERATOR_PREPARED \
  --output /private/NEW_OPERATOR_FULL_INDEX.json
```

독립 index의 content SHA는 `0d78a9b2ed412fa3507cf3d68db6b45d102ef0b8e24f0c65f3a10c3a987cd26d`, 규약 SHA는 `501401566487a29fa7252372621c8239a5c7388e90312c7c3dbe920dcd7020a0`다. Windows/Linux의 JSON 줄바꿈에 따른 **파일 byte SHA**는 다를 수 있으므로 content seal·입력별 hash·registry 연결도 확인한다.

다음은 측정 환경 Python에서 수행하는 CPU 길이 검사다. 로컬 tokenizer만 사용하고 GPU 모델을 실행하지 않는다. `BatchEncoding`의 키 수가 아니라 실제 `input_ids` 길이를 센다. 단일 sequence 또는 단일 batch shape를 확인하며 알 수 없는 형식을0으로 처리하지 않는다.

```bash
/private/measure/bin/python /verified/source/scripts/check_gpu_input_budget.py \
  --trusted-index /private/NEW_OPERATOR_FULL_INDEX.json \
  --tokenizer-dir /cache/PINNED_LOCAL_TARGET_TOKENIZER \
  --context-window 16384 --max-tokens 1024 \
  --output /private/NEW_TOKEN_BUDGET.json
```

이번 두 target의 tokenizer config·vocabulary bytes가 같음을 확인했다. 수정한 실제 tokenizer 검사에서 Task 1/2/3/5 최대 입력 token은231/1592/192/1797이며 출력1024를 더해도 모두16384 안에 들어온다. 최초 길이2 결과는 container 키를 잘못 센 검사였으며 무효 근거와 원래 로그를 보존했다. 길이 통과는 이후 API 성공·생성 잘림 없음·분류 정확도를 보장하지 않는다.

## 별도 전체 GPU 실행

`validate_gpu_pipeline.py`는 `--sources 4/96`과 `--full-core`를 동시에 받지 않는다. Full 경로는 제한 없이 prepare한 뒤 `protocol-index`로 registry·데이터·preparation code·전체 expected input을 검증한다. 임의 custom index에 standard 문구를 붙이는 방식이 아니다. 기존 bootstrap/artifact receipt와 serving 환경을 재사용하되 새 source/core/measure 경로를 명시할 수 있다.

```bash
/private/current-core/bin/python /verified/source/scripts/validate_gpu_pipeline.py \
  --root /private/OWNED_VALIDATION_ROOT \
  --gpu-uuid GPU-EXACT_IDLE_UUID --full-core --attempt NEW_ATTEMPT \
  --source-root /verified/source \
  --core-bin /private/current-core/bin --measure-bin /private/current-measure/bin \
  --dataset-dir /private/pinned-dataset \
  --port 18080 --ptxas-path /verified/cuda/bin/ptxas
```

실제 GPU inventory의 UUID를 CUDA-visible 장치와 대조한다. 시작 전·서버 시작 전·측정 전 점유를 확인하며 다른 작업을 종료하지 않는다. target 서버를 중지한 뒤 측정 모델을 순차 실행한다. 생성 temperature0/thinking off/max_tokens1024, BF16 요청·무양자화, client workers2, server context16384를 기록한다. Precision의 실제 관측은 측정 trace로 확인하며 요청 이름만으로 full FP32 또는 정확도를 주장하지 않는다.

새 output만 사용한다. 이전 실패·완료 디렉터리를 재시작하거나 덮어쓰지 않는다. 중단한 생성의 일반 재개는 [RUNNER_GUIDE.md](RUNNER_GUIDE.md)의 설정 일치 검사를 따른다. 이 controller가 임의로 실패 기록을 삭제하거나 전체 재실행을 자동 시작하지 않는다.

## 완료 후 최소 replay ZIP과 수신 인수

**controller의 실제 terminal exit0**,13개 단계 완료·두 target의 소유 서버 종료를 확인한 뒤 아래 명령을 실행한다. 현재 진행 중인 결과에는 실행하지 않는다.

```bash
python scripts/build_gpu_results_bundle.py \
  --run-root /private/OWNED_VALIDATION_ROOT/full-core-NEW_ATTEMPT \
  --trusted-index /private/NEW_OPERATOR_FULL_INDEX.json \
  --registry /verified/source/configs/protocols \
  --protocol-id koevd-core-canonical-v1 \
  --output /private/NEW_FULL_RETURN.zip
```

포장은 고정 입력·예측·pipeline manifest·측정/trace와 stage 로그를 보존한다. 독립 index·weights·credential·중복 HTML/case export는 제외한다. 상한은 기존 인수 규칙의 파일256MiB·총512MiB·2000파일이며 상한을 넘으면 실패한다. 의미적 데이터나 필요한 분모를 잘라 넣지 않는다. 출력 파일은 새 경로여야 한다. ZIP 생성 후 검증이 실패한 파일도 성공한 인수로 취급하면 안 된다.

수신 측에서는 ZIP 밖의 index·registry와 별도로 전달받은 byte SHA를 사용한다.

```bash
python scripts/accept_gpu_results_bundle.py \
  --zip /private/NEW_FULL_RETURN.zip --expected-sha256 INDEPENDENT_ZIP_BYTE_SHA \
  --trusted-index /operator/INDEPENDENT_FULL_INDEX.json \
  --registry /operator/INDEPENDENT_REGISTRY \
  --protocol-id koevd-core-canonical-v1 \
  --output /private/NEW_INTAKE
```

전체 표준 claim에는 외부 registry가 필수다. 반환 scope·full flag·규약 digest·Task별 counts와 독립 expected input을 대조한다. ZIP 안 index로 대체하지 않으며 두 결과를 raw run에서 다시 export해 정확한 일치를 확인한다. 인수 후 `koevd-diagnose`로 각 모델과 대응 비교 리포트를 다시 만들고, 같은 portable 결과의 local Spaces/CLI 수치와 UI를 확인한다. 원본 node report도 별도 로컬 경로에 남는다. 이 포장/인수는 hash 기반 무결성 확인이며 inference 진위·classifier 정확도·공개 승인을 인증하지 않는다.

## 현재 검증 상태

새 controller/budget/registry/최소 replay 경계의 관련22개 CPU 검사13.109초/exit0/skips0를 통과했다. 가상 모델 결과와 registry를 사용한 파일/재내보내기 검사다. Package source는 변경하지 않았으므로 기존 v22 전체278검사와 wheel을 보존하며, 이번에 전체 현재 suite를 새로 통과했다고 주장하지 않는다.

v0.33: 두 실제 모델의 전체 생성·분류·내보내기·분석·통합 비교 13단계가 종료 코드0으로 완료됐다. 모델당 생성 요청15,011개·평가 기록17,670개, 전체35,340기록을 보존했다. 외부 고정 index/registry와 별도 ZIP SHA를 사용한 원본 재내보내기가 두 모델 모두 정확히 일치했다. 노드·로컬 CLI의 5개 분석 파일이 바이트까지 같고, 앱 HTTP profile도 같다. 실제 HTML199,373,743bytes의 12탭·두 실행·대응 필터·사례 검색·모바일 검사가 통과했다. [근거](validation/platform_m4_m5_full_two_actual_20261009.json). 분류 정확도·공식 순위·실제 HF 로그인/호스팅·클라우드 복구·사람 승인·공개는 별도 미완료 조건이다.

Exec90124/controller56870은 종료 코드0이고 소유 target 서버/분류/비교 프로세스는 종료됐다. ZIP SHA256은8e8050b085d8194b41b2cbf02a6aff0537c111df4443f6afe4f1e48837f65121이며46파일/확장424903614bytes를 보존했다. 로컬 인수의 두 결과는 원본 replay와 정확히 일치했다. 재시작하지 않는다. Native 앱의 저장 어댑터는 로컬 디스크용이며 새 NFS DB 시작 실패를 보존했다. 실제 HF 저장·로그인·컨테이너·사람/운영자 인수·공개 조건은 남아 있다.
