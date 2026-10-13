# 기본 Docker 후보의 전체 결과 인수

## CPU_VALIDATION_NODE 실제 인수 완료 — v92

v0.59에서 사용자가 지정·전송 승인한 CPU_VALIDATION_NODE의 기존 Docker를 사용해 기본 후보를 실제 검증했다. 이미지1개·개별2개/대응 비교1개의15파일806,504,041바이트 HTTP/CLI 일치·비교의 이전 로컬/HF 일치가 통과했다. 기본CMD/UID:GID1000:1000/network none/포트0·정확한 소유 컨테이너 종료exit0/제거를 확인했다. 최종 컨테이너 검사277.752초·Python3.12.15·분석 패키지43파일·웹lock을 검증했다. 압축 해제 상한/누락Entrypoint 검사기의 초기 실패를 보존하고, inspect JSON을 파싱하는 수정과 관련7 CPU검사0.029초가 통과했다. 제품 core50와 HF 배포는 그대로다. 사용자가 Codex에 위임한 기술 검토에서는 GPU 실행 당시184소스·13단계·두 모델28증거파일·각17,670기록/index·Task3/4 재사용과 잘림/측정 한계를 대조했다. AI 검토를 별도 사람의 증명이나 정확도/공개/공식순위 승인으로 바꾸지 않는다. [컨테이너 근거](validation/platform_m5_actual_b200_container_v92.json), [위임 검토 근거](validation/platform_m4_delegated_generation_review_v92.json).

초기 source ZIP의 검사기는 누락 Entrypoint에서 실패했으며 최종 실제 검사는 별도 hash로 전달한 수정본이다. 아래 미실행/환경 부재 문구는 최초 준비 때의 기록이다.

이 절차는 **로컬 Docker 이미지**에서 현재 기본 개발 앱의 시작 명령과 두 모델 전체 결과의 HTTP/CLI 일치를 검사한다. HF 서버 배포·실제 HF 로그인·관리형 백업·운영자 승인·분류 정확도·새 GPU 생성은 검사하지 않는다. 현재 Windows 환경에는 Docker 실행 도구가 없으며 실제 이미지 실행 근거는 아직 없다.

검사기는 [validate_space_container_runtime.py](../scripts/validate_space_container_runtime.py)다. 이미지 안에서는 [기존 HTTP 검사기](../scripts/validate_space_native_runtime.py)를 실행 중인 loopback 서버에 연결한다. 내부 검사기는 `container_verified: false`를 유지한다. 외부 실행기는 실제 이미지 ID, 자신의 컨테이너 ID·고유 label, UID/GID1000, 기본 CMD, 외부 네트워크와 포트 미사용, 종료·제거를 확인한 경우에만 별도 컨테이너 영수증을 통과시킨다.

## 실행 환경과 입력

- Docker CLI와 **로컬** daemon이 이미 준비된 Linux/Windows 호스트. SSH/TCP remote daemon은 사설 입력 bind mount 대상으로 허용하지 않는다. daemon 설치·권한 변경·원격 작업 발주는 이 절차에 포함하지 않는다.
- 호스트 Python3.12와 현재 소스. 컨테이너 내부 웹 의존성은 후보 Dockerfile이 고정 버전으로 설치한다. 호스트 실행기는 표준 Python 라이브러리를 사용한다.
- `generated/private-space-finite-capture-candidate-20261012-v78` 또는 같은 manifest의 전달 사본. 실제 응답·토큰·활성 관리형 설정은 없다. 독립 고정 입력 index와 데이터 이용 조건은 포함한다.
- 이미 인수한 실제 `Qwen3-8B`, `Qwen3-4B`의 **각17,670기록** 결과. HF나 공개 endpoint에 보내지 않는다. 결과 경로는 후보 밖에 두고 아래 독립 SHA-256과 일치해야 한다.
- 실행/출력 경로는 사설 로컬 디스크를 사용한다. 전체 보고서와 disposable 사본에 실제 응답이 있으므로 공개 artifact로 게시하지 않는다. 최소 수 GiB의 여유 공간과 전체 분석을 감당할 메모리가 필요하다. Docker build는 기존 Dockerfile의 base image/PyPI 다운로드를 수행하므로 노드 운영자의 실행 범위에 맞춘다. 유료 자원은 켜지 않는다.

| 결과 | 독립 결과 파일 SHA-256 |
|---|---|
| Qwen3-8B | `27a4dea555208658133b7713f4f24938cf4e8b8cde23bb1e2003028692ba5a99` |
| Qwen3-4B | `d136bf925164a6604e99da65f8e604541f0236a69d2bfe6479c9549daf293cf1` |

사용할 소스 ZIP과 후보 ZIP의 checksum은 전달자가 ZIP 밖의 checkpoint로 함께 제공한다. ZIP 내부 manifest만으로 전달 경로의 진위를 증명하지 않는다. `checked_context`는 파일 목록·각 바이트 hash·symlink·credential/output/rank 선언을 검사하지만 입력 공개 권한이나 생성 진위를 승인하지는 않는다.

## Docker 노드에서 실행할 명령

아래 예시는 Bash다. `CONTEXT_DIR`, `RESULTS_8B`, `RESULTS_4B`는 실제 전달 위치에 맞춘다. 새 작업 디렉터리를 사용하고 이전 실행 결과를 덮어쓰지 않는다.

```bash
python --version
docker context show
docker version
python - <<'PY'
import json, os, subprocess, sys
sys.path.insert(0, 'scripts')
from validate_space_container_runtime import checked_local_endpoint
assert not os.environ.get('DOCKER_HOST'), 'Use an inspected local context'
name = subprocess.check_output(['docker', 'context', 'show'], text=True).strip()
context = json.loads(subprocess.check_output(['docker', 'context', 'inspect', name], text=True))
checked_local_endpoint(context[0]['Endpoints']['docker']['Host'])
print('Local Docker endpoint confirmed')
PY

CONTEXT_DIR=/absolute/path/to/private-space-finite-capture-candidate-20261012-v78
RESULTS_8B=/absolute/path/to/Qwen3-8B/results.json
RESULTS_4B=/absolute/path/to/Qwen3-4B/results.json
WORK_DIR=/absolute/path/to/fresh-private-docker-validation
mkdir -m 700 "$WORK_DIR"

# Dockerfile과 payload는 후보에 포함된 그대로 사용한다.
docker build --iidfile "$WORK_DIR/image-id.txt" \
  --file "$CONTEXT_DIR/Dockerfile" "$CONTEXT_DIR" \
  > "$WORK_DIR/build.log" 2>&1

IMAGE_ID=$(cat "$WORK_DIR/image-id.txt")
python scripts/validate_space_container_runtime.py \
  --candidate "$CONTEXT_DIR" --image-id "$IMAGE_ID" \
  --result "$RESULTS_8B" \
  --result-sha256 27a4dea555208658133b7713f4f24938cf4e8b8cde23bb1e2003028692ba5a99 \
  --result "$RESULTS_4B" \
  --result-sha256 d136bf925164a6604e99da65f8e604541f0236a69d2bfe6479c9549daf293cf1 \
  --output "$WORK_DIR/runtime"
```

검사기는 tag 대신 `sha256:...` 이미지 ID를 요구하며 이미지를 build/pull/push하지 않는다. 기본 CMD `python launch.py`를 유지하고 외부 포트를 열지 않는다. 컨테이너는 network `none`, restart `no`, UID/GID1000으로 실행된다. OAuth에는 합성 문자열만 넣고 실제 HF/백업 Secret이나 Docker socket을 mount하지 않는다. Python 검사와 CLI 비교는 컨테이너 안에서 수행된다. 개인 환경의 `DOCKER_HOST` override는 거부하므로 사용할 daemon은 로컬 context로 선택한다.

사설 원본과 후보는 새 disposable 경로에 복사한 뒤 읽기 전용 mount로 제공한다. 기존 파일의 owner/mode는 바꾸지 않는다. Linux staging은 UID1000 또는 root에서 실행한다. root일 때 **이번에 만든 사본만** UID/GID1000으로 넘긴다. 검사 후 보고서/사본은 보존하며 파일을 자동 삭제하지 않는다. 컨테이너만 자신의 ID·이미지·고유 label·격리 설정을 재확인한 뒤 종료·제거한다. cleanup이 확인되지 않으면 통과하지 않는다.

전체 인수의 기본 실행은 각 모델 분석 두 개와 대응 비교 한 개에서 profile JSON, 사례 JSONL, 지표 CSV, Markdown, HTML **다섯 다운로드 모두를 독립 CLI 파일과 바이트 대조**한다. 별도 `--comparison-only`는 전체 대응 비교만 검사하므로 개별 분석 두 개의 새 검증으로 표시하지 않는다. `--prepare-only`는 checksum/계획만 검사하며 Docker를 호출하거나 결과 사본을 만들지 않는다. `prepared_only`를 실행 통과로 해석하지 않는다.

## 반환할 결과와 실패 처리

사설 검증 bundle에 다음을 포함하고 bundle SHA-256을 별도로 전달한다.

1. `image-id.txt`, `build.log`, 후보 ZIP의 전달 checksum과 소스 ZIP의 전달 checksum.
2. `runtime/receipt.json`: 실제 container flag, 기본 CMD, 정확한 이미지/컨테이너 ID, UID/GID, network/ports/restart, terminal/removal.
3. `runtime/disposable/output/http/receipt.json`: 현재 비편집 설치·웹 의존성, 입력 결과 hashes, individual/comparison selection, 다섯 파일의 bytes/SHA와 HTTP/CLI 일치.
4. 같은 경로의 `http-profile-*.json`, `http-report-*.html`, `cli-*/` 다섯 출력. 모두 실제 응답을 포함할 수 있다. 원본 두 결과는 이미 보유한 것과 hash가 같으면 중복 반환하지 않아도 된다.
5. 실패 시에도 두 영수증과 남은 로그를 보존한다. 자동 재실행하지 말고 실제 container ID가 live인지 확인한다. 도구가 cleanup을 거부한 경우 해당 고유 label/ID를 운영자가 대조한다. 실패한 검증을 native 통과로 바꿔 쓰지 않는다.

이 실행이 통과해도 HF 컨테이너의 전체 용량, HF OAuth, 복구 대기 해제나 production 공개는 별도의 조건이다. 운영 환경의 실행 증거와 이 로컬 이미지 증거를 구분해 기록한다.

Docker의 `--pull=never`, network, user, mount 옵션은 [공식 run 문서](https://docs.docker.com/reference/cli/docker/container/run/)를 따르며, 이미지 정보 조회는 [공식 inspect 문서](https://docs.docker.com/reference/cli/docker/image/inspect/)를 따른다.
