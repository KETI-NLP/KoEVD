# GPU 노드 Codex용 플랫폼 검증 요청

이 문서는 현재 미커밋 플랫폼 후보를 실제 두 대상 모델로 검증하기 위한 요청이다. 아래 본문과 source ZIP·그 ZIP의 외부 SHA-256을 함께 전달한다. 공개 main만 내려받으면 이 후보의 검증이 아니다. 이 문서 작성과 source 준비만으로 GPU 작업이 시작되지는 않는다.

## 전달할 프롬프트

```text
첨부된 KoEVD 플랫폼 source 후보를 GPU 노드에서 실제로 검증해줘. CPU 가상 fixture 통과가 아니라 최소 두 실제 target model의 생성→두 측정 모델→표준 JSON→HTML→모델 대응 비교→로컬 Spaces 업로드 수치 일치를 확인하는 작업이다. 아래 문서의 실행 예와 configs/validation/platform-gpu-candidate-v1.json을 함께 읽어줘.

1. 전달받은 ZIP의 SHA-256을 사용자가 전달한 값과 먼저 비교해줘. 새 작업 폴더에서 bundle manifest의 파일 집합/hash를 검증하고, 기존 작업·모델·캐시를 보존해줘. source HEAD와 bundle hash, 설치된 모듈 경로를 기록해줘. 현재 후보의 미커밋 변경을 과거 공개 main으로 대체하지 말아줘. 실제 checkout의 AGENTS.md도 확인해줘.
2. 노드의 사용 가능한 GPU/메모리·디스크와 실행 중 프로세스를 확인해줘. 다른 사용자의 서버를 종료하지 말아줘. 이 작업이 직접 시작한 PID만 관리해줘. 목표 모델 serving과 분류기를 별도 환경 및 단계로 실행하고, 단일 GPU이면 serving 자원을 해제한 뒤 분류기를 순차 로드해줘. 유료 외부 자원을 만들거나 public Space/GitHub/HF에 게시하지 말아줘.
3. 고정 lock의 데이터·두 adapter·두 base·두 target revision을 사용해줘. 기본 target은 Qwen3-8B와 Qwen3-4B다. 두 classifier를 두 target으로 세지 말아줘. 같은 Qwen family라는 관계도 기록하고 독립 cross-family 연구라고 표현하지 말아줘. cache를 쓸 때도 repo/revision 및 실제 snapshot 파일 hash를 확인해줘. 접근/자원 문제로 모델을 바꿔야 하면 이유와 새 immutable revision·조건을 별도 기록하고 원래 조건 완료로 표시하지 말아줘.
4. vLLM과 measurement 환경의 실제 Python/torch/transformers/peft/accelerate/vLLM/HF Hub 버전, GPU/driver와 server args를 기록해줘. target 조건은 BF16, thinking off, temperature 0, max_tokens 1024, seed 요청 없음이다. 실제 template와 설정의 근거를 저장해줘. extra parameter를 지원하지 않는다고 조용히 제거하지 말아줘. reference 측정 prompt/parser/default token budget을 임의 수정하지 말아줘.
5. 데이터와 기대 입력을 독립적으로 prepare해줘. 각 target에서 smoke(4 primary 및 4 tool prefix), 확대(96 primary 및 96 tool prefix)를 먼저 검증하고, free GPU/시간이 허용되면 전체 core를 수행해줘. Task별 실제 분모와 Task 3 union/primary/overlap, Task 2 네 variant·Task 5 세 framing을 확인해줘. prefix subset은 비대표 동작 검사이며 standard full baseline이 아니다. full은 target당 생성 15,011회, 결과 record 17,670개다. Task 4는 Task 3 답변을 재사용해줘.
6. 생성 파일은 고정하고 각 측정 조건을 별도 새 run 복제에서 실행해줘. baseline untraced batch2, traced batch2, traced batch1, traced batch4, traced batch2 reverse, traced single 경로를 비교해줘. BF16 기준으로 실행하고 FP32 비교는 메모리·시간을 확인해 가능한 범위에서 추가해줘. trace를 켰을 때의 영향도 baseline과 비교해줘. 다른 생성 답변을 사용한 차이를 batch 영향으로 해석하지 말아줘.
7. 실제 토큰 hash/비패딩 길이/단건 template parity, 관찰된 call order, 실제 parameter dtype, 길이 제한 단서, raw classifier output과 파싱 실패를 sidecar로 보존해줘. trace sidecar는 관찰 기록이지 생성 진위나 정확도 인증이 아니다. token parity나 dtype 차이가 발견되면 원문/조건을 보존하고 원인을 분석해줘. 테스트를 통과시키기 위한 parser 완화·raw 라벨 덮어쓰기·의심 답변 자동 재생성은 하지 말아줘. 실패 sidecar와 원래 generation도 반환해줘.
8. source ID new_template3_1st_13794 / new_template3_1st_05843 / new_template3_1st_05104가 실제 선택 집합에 있는지 확인해줘. 없으면 missing이라고 기록하고 full 또는 명시된 추가 diagnostic subset에서 별도 검사해줘. 입력 severity를 생성 답변의 gold로 사용하지 말아줘. 사람 판정이 없으면 의심/불일치만 보고하고 오답률·새 F1이나 정확도 해결을 주장하지 말아줘.
9. koevd-audit로 frozen 측정 변형을 비교하고 blinded review 자료를 만들어줘. 실제 가이드라인 ID/version을 쓰고, 사람이 검토하지 않았으면 template을 채워 넣어 실제 annotation처럼 제출하지 말아줘. 원래 classifier와 사람 판정은 별도 유지해줘. 미해결 측정은 measurement_limited/rank 제외 상태를 유지해줘.
10. 두 실제 결과를 같은 input index에서 export하고 공통 diagnose로 각각의 HTML/CSV와 두 모델 비교를 만들어줘. 실제 로컬 Space app에 업로드해 CLI profile과 수치 일치를 검증해줘. synthetic demo reference를 actual baseline으로 바꾸지 말아줘. raw 공개 동의가 없으면 세션 업로드만 사용하고 공개 참조/리더보드 등록은 하지 말아줘. 전체 입력의 실패/누락/미분류와 N/A를 숨기지 말아줘.
11. README/문서 명령이 실제 실행되는지 확인하고 필요한 코드 수정은 최소화해줘. 변경하면 patch·이유·수정 전후 결과와 회귀 검증을 남겨줘. 원래 source bundle과 수정된 source hashes를 구분해줘. 기존 successful CPU 검사를 아무 변경 없이 의미 없이 반복하는 데 GPU 시간을 쓰지 말아줘.
12. 결과를 아래 반환 구조로 ZIP에 묶고 상대 경로별 bytes/SHA-256 manifest를 만들어줘. weights, auth cache/token, .env, Authorization header, 전체 환경변수, 외부 사용자의 출력은 넣지 말아줘. GPU 완료 범위·실패·남은 요건을 요약하고 ZIP 절대 경로와 전체 ZIP SHA-256을 마지막 답변에 적어줘. 다른 대화에 자동으로 메시지를 보내지 말아줘.

성공의 의미는 실제 두 target의 검증된 연결 경로와 정직한 측정 한계 보고다. classifier 실행 성공을 정확도로 표현하지 말아줘. smoke만 통과했으면 확대/full 미수행을 표시해줘. 필수 stage가 실패하면 증거를 보존하고 그 stage를 미완료로 반환해줘. 계획 18절의 전체 플랫폼 Goal이 이 GPU 작업만으로 완료됐다고 선언하지 말아줘.
```

## 고정 자원과 실행 후보

`configs/validation/platform-gpu-candidate-v1.json`이 정확한 revision/조건의 기준이다. Qwen3-4B commit은 2026-10-08 HF 공개 API에서 `1cfa9a7208912126459214e8b04321603b3df60c`로 확인했다. 같은 family의 두 모델은 통합 동작 검사 대상으로 선택한 것이며 모델 family 간 우열 연구가 아니다.

모델 카드에는 vLLM 사용과 thinking 비활성화가 설명돼 있다. 아래는 후보 명령이며 실제 GPU 실행 완료 증거가 아니다. 설치 버전의 CLI 지원 여부와 실제 적용 설정을 노드에서 확인한다. [Qwen3-4B 공식 모델 카드](https://huggingface.co/Qwen/Qwen3-4B), [vLLM 공식 serving 안내](https://docs.vllm.ai/en/latest/serving/online_serving/).

B200 같은 기존 검증 노드를 활용할 수 있으나 특정 VRAM이나 시간 내 완료를 보장하지 않는다. full core에는 target별 15,011개의 generation 요청과 2,659개의 답변에 대한 두 measurement 모델 실행이 필요하다. 측정 변형은 그 답변을 재사용한다. 필요한 disk는 실제 snapshot·generation·trace·HTML 규모를 먼저 확인하며 기존 cache를 중복 다운로드하지 않는다. target serving과 측정 환경은 분리한다.

## 실제 CLI에 맞춘 실행 예

다음 Bash의 경로 변수는 노드의 실제 snapshot/작업 경로로 설정한다. 현재 source를 설치한 `core`와 `measure` 환경의 CLI를 사용한다. `core`에는 `[dev,hub,serve]`, `measure`에는 `[classifiers]` extra가 필요하다. vLLM 환경은 별도로 유지한다. 준비하는 코드·문서와 실제 실행 결과를 구분한다. serving은 별도 터미널 또는 이 작업 소유의 background process로 띄우고, 정상 응답을 확인한 뒤 core 환경의 generate를 실행한다.

```bash
# DATASET / TARGET_PATH / SAFETY_ADAPTER / SAFETY_BASE /
# STRATEGY_ADAPTER / STRATEGY_BASE / RUN / INDEX를 실제 경로로 설정.
# MODEL은 lock의 repo ID, MODEL_PROVENANCE는 실제 선언·근거 JSON.
# EXTRA_BODY에는 {"chat_template_kwargs":{"enable_thinking":false}}를 저장.

koevd-pipeline --stage prepare --dataset-dir "$DATASET" \
  --output-dir "$RUN" --split core --limit-sources 96
koevd-results index --run-dir "$RUN" --output "$INDEX"

# 별도 serving 환경. max-model-len은 실제 준비 입력+출력 여유를 점검한 뒤 결정.
vllm serve "$TARGET_PATH" --served-model-name "$MODEL" \
  --host 127.0.0.1 --port 8000 --dtype bfloat16 --max-model-len 16384

# core 환경에서 실행. 실제 engine version 및 model provenance를 제공.
koevd-pipeline --stage generate --output-dir "$RUN" \
  --base-url http://127.0.0.1:8000/v1 --model "$MODEL" \
  --temperature 0 --max-tokens 1024 --workers 2 --preflight \
  --extra-body-file "$EXTRA_BODY" --model-provenance-file "$MODEL_PROVENANCE" \
  --engine-version "$ACTUAL_VLLM_VERSION"

# serving 자원을 해제한 뒤 measure 환경의 CLI 사용.
# baseline: --trace-measurements를 생략하고 새 baseline clone에서 실행.
koevd-pipeline --stage classify --output-dir "$VARIANT_RUN" \
  --safety-adapter "$SAFETY_ADAPTER" --safety-base "$SAFETY_BASE" \
  --strategy-adapter "$STRATEGY_ADAPTER" --strategy-base "$STRATEGY_BASE" \
  --batch-size 2 --classifier-dtype bfloat16 \
  --measurement-order original --measurement-mode batch --trace-measurements

koevd-results export --run-dir "$VARIANT_RUN" \
  --trusted-index "$INDEX" --output "$VARIANT_RUN/results.json"
koevd-diagnose --input "$VARIANT_RUN/results.json" --trusted-index "$INDEX" \
  --output-dir "$VARIANT_RUN/analysis" --bootstrap-resamples 100 --bootstrap-seed 1729
```

`VARIANT_RUN`에는 `pipeline.json`, 준비 입력과 모든 frozen prediction 및 필요한 generation journals를 복사한다. 새 clone에서 원래 `measurements` manifest 항목을 제거하고 측정 파일·trace·report/export를 복사하지 않는다. original generation/run configuration은 바꾸지 않는다. trace는 새로운 output 파일을 요구하므로 완료한 trace를 덮어쓰지 않는다. raw 생성의 입력/output hash가 모든 clone에서 같은지 확인한다. `single` 모드와 `batch-size 1`은 서로 다른 토큰화 경로의 검사다.

full은 prefix prepare가 아니라 다음 registered 경로를 사용한다.

```bash
koevd-results protocol-index --registry configs/protocols \
  --protocol-id koevd-core-canonical-v1 --dataset-dir "$DATASET" \
  --run-dir "$FULL_RUN" --output "$FULL_INDEX"
```

동일 scope의 두 실제 결과 비교:

```bash
koevd-diagnose --input "$RESULT_A" --input "$RESULT_B" \
  --trusted-index "$SHARED_INDEX" --output-dir "$COMPARE_DIR" \
  --bootstrap-resamples 100 --bootstrap-seed 1729
```

`RESULT_A`/`RESULT_B`는 각각 다른 실제 target의 결과이며 `koevd-audit --variant`는 같은 target의 frozen 답변 재측정 비교다. 두 경로를 혼동하지 않는다. 판정 불일치가 있으면 임의로 값을 일치시키지 않는다. 서로 다른 precision/batch 측정은 비교 제한 사유가 될 수 있다.

## GPU 결과 반환 구조

```text
KoEVD_platform_GPU_validation_<UTC>/
  SUMMARY.md                    실제 완료/실패·coverage·측정 한계·후속 작업
  SHA256.json                   모든 반환 파일의 상대 경로·bytes·SHA-256
  source/                       원본 bundle hash/manifest·변경 patch·현재 source hashes
  protocol/                     사용 lock·규약·trusted input index·준비 manifest
  environment/                  허용된 package/GPU/driver/server 설정 정보
  targets/<target>/<scope>/
    generation/                 frozen input·prediction·journal·run metadata
    measurements/<condition>/   측정 JSONL·trace·pipeline manifest·results.json
    analysis/                   profile-v2.json·cases-v2.jsonl·metrics-v2.csv·MD·HTML
    audit/                      측정 변형 비교·blinded 자료·미검토 template
  comparison/<scope>/           실제 두 target의 공통 엔진 산출물
  space-local/<scope>/          실제 upload/profile 일치·세션 격리·화면 근거
  checks/                       실행 명령·exit code·분모/trace/hash 검사 결과
```

`SHA256.json` 자체는 목록에서 제외한다. archive 경로는 상대 경로만 사용하고 `..`/절대 경로/중복/심볼릭 링크를 넣지 않는다. 파일별 hash 목록과 최종 ZIP hash는 내용의 무결성 근거이며 진위 인증은 아니다. 로그에 raw API key나 credential을 출력하지 않는다. 공개 가능 여부·raw 범위를 별도 명시하며 이 반환 ZIP을 자동 공개 자료로 취급하지 않는다.

현재 로컬에는 GPU가 없어 이 요청의 실제 inference·메모리·처리 시간·두 target 결과는 아직 없다. source-only bundle 검증과 CPU 대역 검사만 통과했으며, GPU 반환 자료의 전체 자동 인수 검증과 human adjudication은 후속 작업이다.

## Source checkpoint update: portable measurement conditions

The current candidate adds `measurement_conditions.py` and its tests, plus stronger EOS/token-budget trace checks. The earlier `KoEVD_platform_GPU_source_20261008.zip` remains an earlier checkpoint. This update uses `KoEVD_platform_GPU_source_conditions_20261008.zip` with an adjacent `.zip.sha256`; verify the actual supplied digest and manifest, not the filename alone.

Return both compact exported conditions and full measurement sidecars. Check that order/mode/options differences appear in Task 3/4 compatibility without affecting Task 1/2/5 or frozen generation. Missing runtime fields remain unknown. No compact block or hash authenticates GPU execution.
