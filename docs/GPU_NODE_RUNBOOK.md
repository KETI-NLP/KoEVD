# B300 GPU 검증 작업 안내

2026-10-08. 사용자 지정 노드 `GPU_NODE`에서 직접 SSH로 진행한다. 별도 Codex 채팅을 만들거나 다른 채팅에 작업을 보내지 않았다. 공개 게시·유료 자원·기존 서버 종료는 이 작업에 포함하지 않는다.

## 현재 작업 위치와 증거

최신v0.23은 [전체 표준 실행](FULL_STANDARD_RUN_GUIDE.md)이다. `full-core-v1`/exec90124/controller56870을 실제 live로 확인했고8B 서버56951은 healthy다. 새환경/자료는 `incoming/full_standard_v23`, 고정 source는 `source-v2`이며 corrected preflight-v4만 통과 근거다. 기존 full index/97개 파일 hash와 실제token budget을 확인했지만 두 모델 전체 결과/측정/반환 인수는 아직 미완료다. 같은handle/실제PID·명령·로그를 먼저 확인하고 timeout만으로 재시작하지 않는다. Prefix와 기존 GPU66554/46297은 완료했으므로 중복 실행하지 않는다. 아래 준비/실행 기록은 이전 checkpoint의 근거다.

원격 작업 root는 `[private-node-path]`이다. 기존 작업은 `[private-node-path]`에 보존한다. 공유 디스크에 같은 폴더가 보인다는 사실만으로 다른 노드에서 실행 중인 작업이 이 노드에 있다고 가정하지 않는다.

인수한 source checkpoint:

- ZIP: `KoEVD_platform_source_web_20261008.zip`, 131개 source 파일.
- ZIP SHA-256: `0cbccf73f3a363dde8aae50df9cc7a1be5b514d03285fec478551c2cf8c1bdf2`.
- HEAD: `cfb79006a6471ecd3ce89c0bad8a98e85c8a75fb`. 미커밋 변경을 포함한 source manifest가 기준이다.
- 원격 `environment/source-receipt.json`: 독립 checksum·파일 manifest 인수 근거.
- 신규 4개 control script는 `incoming/`에 있다. 원래 core ZIP의 일부로 주장하지 않으며 별도 SHA-256은 [preflight 근거](validation/platform_m4_node_preflight_20261008.json)에 기록했다.

core·measure 설치와 실제 B300 CUDA 연산을 확인했다. Linux 설치 검사는189개 중188개 통과·optional Node 검사1개 skip이다. Qwen3-8B·4B의 prefix4와 prefix96 파이프라인을 terminal pass로 인수했다. 최신 확대는 각각959개 생성/1150 portable 기록이며 전체 표준 평가·정확도·공식 rank를 의미하지 않는다. 최신 상태는 계획v0.17과 [확대 근거](validation/platform_m4_gpu_expanded_20261008.json)가 우선한다.

## 진행 중 작업을 먼저 확인

이 기록을 작성할 때 다음 작업들이 살아 있었다. 상태 파일만으로 process가 살아 있다고 판단하지 않는다. 같은 실행 handle을 poll하고 실제 PID/명령·로그·결과를 재확인한다. 관측 timeout이 나면 재조회하며, 살아 있는 작업을 중복 시작하지 않는다.

| 작업 | 로컬 exec session | 원격 PID 관측 | 상태/로그 |
|---|---:|---:|---|
| 환경 bootstrap | 75701, terminal exit0 | 종료 확인 | `environment/bootstrap-status.json` passed, 설치·dependency check 통과 |
| 고정 artifact 준비 v2 | 19798, terminal exit1 | 종료 확인 | `prepare-artifacts-v2.log`; target `id`/`repo_id` KeyError |
| 고정 artifact 준비 v3 | 22031, terminal exit0 | 종료 확인 | `environment/artifact-receipt.json` passed, release 5개+target 2개 모두 byte/checksum 확인 |
| 실제 두 target smoke v1 | 97489, terminal exit1 | 종료 확인 | `smoke/checks/status.json`; vLLM의 UUID 정수 변환 오류 |
| 실제 두 target smoke v2 | 70736, terminal exit1 | 종료 확인 | `smoke-v2/checks/status.json`; bundled PTXAS12.8의 sm_103a warmup 실패 |
| 실제 두 target smoke v3 | 31006, terminal exit0 | 소유 server 종료 확인 | `smoke-v3/checks/status.json`; 13단계 통과 |
| 실제 두 target 확대 v3 | 66554, terminal exit0 | 소유 server 두 개 종료 확인 | `expanded-v3/checks/status.json`;13단계 통과, 각959생성/1150portable |
| 고정 응답 측정 감사 | 46297, terminal exit0 | controller39972 종료 확인 | `measurement-matrix-expanded-v1/checks/status.json`;두target14조건 통과,독립ZIP 인수 완료 |

위 PID는 시점별 관측이다. 종료 후 재사용될 수 있으므로 PID 번호만으로 kill하지 않는다. 초기 캐시 불완전 실패는 `environment/artifact-receipt-incomplete-cache.json`에 보존했다. v2의 원래 running receipt는 `artifact-receipt-v2-raw-terminal.json`, 실제 exit1·KeyError 설명은 `artifact-receipt-v2-failed.json`에 보존했다. 수정본 `incoming/prepare_gpu_artifacts_v3.py`의 원격 대조 SHA-256은 `901ba795000bbaf533623f25547303963ec7659553d84e98c1cfe18d7399d5e9`다. release의 `repo_id`와 target의 `id`를 모두 처리하며 오류 시 failed receipt를 저장한다. 고정 revision은 변경하지 않았다.

최신 상태에서는 bootstrap/artifact 준비가 모두 passed다. 첫 실제 smoke는 generation 전에 vLLM의 `int(CUDA_VISIBLE_DEVICES)` 경로가 UUID 문자열을 처리하지 못해 종료됐다. `smoke/`의 로그와 실패 status를 보존했다. 수정 실행기는 현재 NVML index를 UUID로 찾아 integer mask/PCI_BUS_ID를 사용하고, 실제 torch CUDA 장치 UUID가 요청 UUID와 같은지 먼저 대조한다. selector 계약 검사 2개가 통과했다. 수정본 `incoming/validate_gpu_pipeline_v2.py`의 SHA-256은 `0c71fa20f61745f8e01b94a8dbfd8df867015475520e6dc8a6550dbb85812e88`다.

`smoke-v2`는 device 선택을 통과했으나 bundled PTXAS12.8의 B300 `sm_103a` 미지원으로 warmup 실패했다. `smoke-v3`는 기존 CUDA13 PTXAS를 process-local로 지정하여 통과했다. controller SHA-256 `f986f582a32baab914f5c0ef196afacff0cddb76a8b1a23be77b4fc8166e902f`, compiler13.0.88 SHA-256 `daba837a68265cae38c832d13399b61dab811891de9b8914defddef143b849f2`, GPU2 요청/관측 UUID 및 integer mask2/PCI_BUS_ID를 기록했다. 시스템 compiler나 기존 의존성은 수정하지 않았다. v1/v2/v3 실패·성공 폴더를 모두 보존한다.

## 환경과 cache 계약

- `envs/core`: 새 Python 3.11.14 + 이 source의 비편집 KoEVD `[dev,hub,serve]` 설치.
- `envs/measure`: 새 Python 3.11.14 + 이 source의 KoEVD 설치. 기존 B200 validation의 site-packages를 명시적 `.pth`로 상속한다. torch 2.9.1+cu130, transformers 5.8.1, peft 0.18.0, accelerate 1.15.0, HF Hub 1.31.0을 실제 import했다. 새 KoEVD 설치 경로가 로드되는 것을 확인했다. 상속한 의존성이 새로 설치됐다고 표현하지 않는다.
- `envs/serve`: vLLM0.13.0+cu130 별도 환경. 설치·dependency check와 두 target의 prefix4 실제 serving은 통과했다. B300에서는 아래 compiler override가 필요했다. 고정 wheel·설치 옵션과 실제 compiler 선택은 receipt에 남긴다.
- 기존 cache의 절대 symlink 일부가 B200의 `/root` 파일을 가리킨다. 그 파일을 고치지 않고 unavailable로 기록한다. 필요한 같은 revision은 이 작업의 `hf-cache/`로 내려받는다.
- 모델·데이터의 byte count와 LFS SHA-256 또는 Git blob SHA-1을 공식 HF pinned revision metadata와 비교한다. artifact hash는 실행 진위나 정확도 인증이 아니다.
- HF 공개 artifact는 익명 read로 내려받는다. 로컬 PC의 토큰을 원격으로 복사하지 않는다. CLI 로그인과 웹 OAuth 앱은 별도다.

## 실제 대상 모델 검증 시작 조건과 명령

`environment/bootstrap-status.json`과 `environment/artifact-receipt.json`의 `status`가 모두 `passed`이고 실제 파일·process 상태와 일치해야 한다. 설치가 실패했으면 실패 로그와 terminal exit를 먼저 분석한다. 실패한 부분을 수정할 때 원래 receipt·명령·조건을 보존하고 새 시도임을 기록한다.

초기 후보 GPU는 UUID `GPU-6e6eae12-0d8b-efc1-d7da-33c239882473`(관측 시 GPU1)이다. 준비 도중 GPU1에 1,538 MiB 점유가 생겼다가 다음 조회에서 0으로 돌아왔다. 시작 직전에 다시 확인하며, 필요하면 당시 비어 있는 GPU2 UUID `GPU-795fabdc-a541-1b0f-aa66-b7efab297b4b`를 지정한다. 실행기는 선택한 장치의 사용 메모리를 확인하고 다른 작업이 점유하면 server를 띄우지 않는다. GPU0은 점유되어 있으므로 사용하지 않는다. 숫자 index만으로 노드 재구성 후 같은 장치라고 가정하지 않는다. 기존 process를 종료해서 GPU를 확보하지 않는다.

다음은 **통과한 smoke-v3 명령의 기록**이다. 이미 존재하는 폴더에 다시 실행하지 않는다.

```bash
python3 [private-node-path] \
  --root [private-node-path] \
  --gpu-uuid GPU-795fabdc-a541-1b0f-aa66-b7efab297b4b \
  --sources 4 --port 18080 --attempt v3 \
  --ptxas-path /usr/local/cuda-13.0/bin/ptxas
```

완료된 확대 명령은 위와 같은 controller/options에서 `--sources 96`을 사용했다. `expanded-v3`/session66554와 후속감사46297은 모두 terminal exit0/독립 인수 완료이므로 재실행하지 않는다. 실패 후 재시도는 원인을 인수하고 새 attempt 폴더를 사용한다.

이 실행기는 두 실제 target(Qwen3-8B/Qwen3-4B)의 고정 revision에 대해 독립 prepare/index → vLLM 생성 → safety/strategy traced batch2 측정 → JSON export → 개별 HTML → 대응 비교를 수행한다. UUID를 확인한 integer `CUDA_VISIBLE_DEVICES`로 선택한 한 GPU만 보이게 한다. target server는 localhost에만 열고 다른 process를 종료하지 않는다. 직접 시작한 serving process group만 `finally`에서 종료한다. API 실패·분모 불일치는 원문을 보존하고 stage 실패로 처리한다.

vLLM 후보 args는 BF16, model length 16,384, GPU memory utilization 0.25, max sequences 16, eager execution이다. 요청은 temperature 0, max_tokens 1,024, seed 요청 없음, thinking off이다. 실제 설치 버전과 args를 기록하고, API가 옵션을 거부해도 조용히 제거하지 않는다. 로컬 단건 preflight는 벤치마크 분모에 포함하지 않는다.

smoke 실패·성공과 측정 한계를 인수하고 prefix96 확대를 시작했다. output root는 새 폴더를 요구한다. 이미 있는 smoke/expanded 폴더를 덮어쓰거나 관측 timeout만으로 재실행하지 않는다. prefix는 대표 표본이나 full standard baseline이 아니다.

이 생성 controller는 traced batch2 baseline까지 담당한다. 후속 frozen controller는 repeat-b2 / untraced-b2 / batch1 / batch4 / reverse / single / FP32-request의7조건을 같은 생성 응답의 별도 clone에서 실행했다. 아래는 완료된 감사 명령의 기록이며 중복 실행하지 않는다.

```bash
[private-node-path] \
  [private-node-path] \
  --root [private-node-path] \
  --baseline-attempt expanded-v3 --attempt expanded-v1 \
  --gpu-uuid GPU-795fabdc-a541-1b0f-aa66-b7efab297b4b
```

controller SHA256는 `6fe5d60b63249441d06a872ca82f8566a8f93662f324d8a957e46bb02ad4d6c7`이다. 최종 terminal/status 통과 후 [MEASUREMENT_MATRIX_RETURN_GUIDE.md](MEASUREMENT_MATRIX_RETURN_GUIDE.md)에 따라 새 반환ZIP을 만들고 ZIP 밖의 인수된 baseline과 독립index로 검증한다. FP32 요청 이름과 실제 parameter dtype를 구분한다. 부분 완료 로그나 로컬 반환 도구의 CPU 검사를 전체 GPU matrix 완료로 표시하지 않는다. full core는 별도 registered `protocol-index` 경로로 수행한다. 상세 요구사항은 [GPU_PLATFORM_VALIDATION_PROMPT.md](GPU_PLATFORM_VALIDATION_PROMPT.md)를 따른다.

## 결과 인수와 다음 작업

최종 frozen matrix도 `generated/KoEVD_measurement_matrix_expanded_20261008_v1.zip`으로 인수했다. SHA256 `695b2e25fb853726a8e37b63c2d38ff12b03484ccbc8b749f96fb56b0505b95b`,27,223,907bytes/221files이며 ZIP 밖 baseline/index로14개조건을 독립 재계산했다. [최종 결과·정밀도 한계](GPU_MEASUREMENT_MATRIX_RESULTS.md)를 참조한다. GPU 감사 작업은 완료됐으며 같은폴더에 재시작하지 않는다.

현재 최신 완료 결과는 prefix96의 `generated/KoEVD_platform_expanded_20261008_v3.zip`이다. SHA256 `6a26dea365322ecd8078b7125eaf77b03867e9285c0ceda86080a7cc5b6375fc`,12,842,931bytes/96files이며 독립v16 prefix96 index로 raw reexport를 인수했다. 두 실제 결과2300-record local app·CLI·노드 profile도 정확히 같다. 아래 prefix4 명령은 이전 checkpoint의 기록이다.

인수된 smoke ZIP은 `generated/KoEVD_platform_smoke_20261008_v3.zip`, SHA-256 `8e5ac01fe4f597c1edf662f6fd301793816c72cbdbf0cba1fbce9dd04e480bf5`다. 다음은 실제 수행한 인수 명령이다. `--trusted-index`는 ZIP 밖에서 독립 준비한 입력이어야 하며 `--output`은 새 비공개 폴더여야 한다.

```powershell
& 'generated/generation-receipt-install-20261008-v1/Scripts/python.exe' scripts/accept_gpu_results_bundle.py `
  --zip generated/KoEVD_platform_smoke_20261008_v3.zip `
  --expected-sha256 8e5ac01fe4f597c1edf662f6fd301793816c72cbdbf0cba1fbce9dd04e480bf5 `
  --trusted-index generated/private-space-deployment-20261008-v14/operator-data/prefix-4-index.json `
  --output generated/gpu-smoke-intake-20261008-v4
```

검증된 byte snapshot을 그대로 추출하며 archive code를 실행하지 않는다. 제한·경로·hash·13단계·실패/분모·독립 입력을 검사하고 raw run 재export가 원본과 정확히 같아야 receipt를 쓴다. 실패 폴더는 보존한다. 현재 로컬 `generated/gpu-smoke-space-ui-20261008/evidence.json`은 실제 두 결과의 HTTP/browser·독립 CLI·노드 분석 일치를 확인했다. 반환 receipt와 UI 검사는 human operator attestation·HF 로그인·공개 동의·모델 진위 인증이 아니다.

`smoke/checks/status.json` 또는 `expanded/checks/status.json`에서 실제 명령·exit·소유 server PID·Task별 generation 분모/hash를 확인한다. 두 target의 results와 shared index로 CLI를 재채점하고, 실제 Spaces HTTP/UI 업로드·수치 일치·문자열 처리·대응 비교를 별도 검증한다. full·측정 조건 감사·사람 판정·생성 receipt 인수·정책 승인·원격 durability·배포 gate를 각각 구분한다.

raw 출력은 분석용 비공개 산출물이다. public reference·리더보드 등록을 자동 수행하지 않는다. 미해결 safety/strategy 문제는 measurement_limited 및 공식 rank 제외를 유지한다. 사람 판정을 임의로 채워 gold나 새로운 F1을 만들지 않는다.

반환 ZIP의 파일 구조와 credential 제외·SHA-256 절차는 GPU 요청 문서를 따른다. weights·HF auth cache·전체 환경변수·내부 API secret은 반환 결과에 넣지 않는다. 최종 생성 결과 ZIP은 source-only ZIP과 구분하며, 실제 두 모델·scope·stage·coverage·남은 gate를 명시한다.
