# Spaces 배포 후보의 Linux CPU 실행 검증

현재 상태(2026-10-12/plan0.43): v0.43에서 실제 Team 가입을 API로 확인하고 별도 비공개 CPU Docker Space `KETI-NLP/KoEVD-Platform-Dev`를 배포했다. 현재 revision `03e79a75ee35570b83948343d521f684a38fce01`의 payload65개+manifest가 일치하고 RUNNING/cpu-basic이다. 실제 HF 로그인 후 두 모델48+48기록의 업로드·분석·대응 비교와 비공개 draft2건 저장/재조회를 확인했다. 내려받은 원본 JSON 내용·HF OAuth 생성 이력과 분석 JSON/HTML의 native 바이트가 일치한다. v64의 별도 HTTP 검증에서는 다섯 출력·세션 격리·삭제가 통과했다. 현재 브라우저의 나머지3개 다운로드는 확인하지 못했다. Private proxy cookie 누락을 수정했고 관련4+6+3+11 검사가 통과했다. 기존 전체310은 이전 설치 근거다. Public Static은 그대로이며 영구 저장·운영자 승인·공개 참조/공식 순위·production은 미완료다. [최신 근거](validation/platform_m5_m6_team_hosted_20261012.json) Goal active/원래 범위를 유지한다.

아래 이전 검증의 범위·수치는 당시 근거다. [운영 준비](TEAM_SPACE_OPERATIONS.md).

Docker 후보의 웹 의존성과 패키지가 Linux에서 실제로 함께 실행되는지 확인했다. **컨테이너 이미지 빌드·HF 호스팅·실제 OAuth 로그인은 별도 미완료 항목**이다. 이 검사는 기존에 인수한 두 모델의 prefix96 결과를 사용하며, 현재 진행 중인 전체 표준 GPU 평가의 완료 근거가 아니다.

## 확인한 범위

2026-10-08 B300 노드의 새 Python3.12.3 환경에 웹 lock의14개 패키지를 설치하고, 별도 소스 사본에서 KoEVD를 noneditable 설치했다. `pip check`가 통과했고 배포 후보의 전체 manifest63파일 및 설치된 `koevd_eval` 네임스페이스42파일의 이름·바이트가 일치했다. 기존 GPU 환경과 weights는 변경하지 않았다.

실제 loopback HTTP 서버에서 다음 흐름을 확인했다.

1. canonical HF origin 설정, 서버 준비 상태와 임시 저장 안내.
2. 공식 순위·공개 기준 모델 비활성 상태, 실제 로그인 전 상태.
3. 외부 origin 거절 및 분석 세션 인증 요구.
4. 실제 Qwen3-8B·4B 결과 업로드와 두 세션의 격리.
5. 모델별 두 리포트 및 같은 입력에 대한 비교 리포트 생성·다운로드.
6. 세 리포트의 분석 JSON과 별도 CLI 분석의 정확한 일치.
7. 세션 삭제 후 접근 거절과 소유 서버 종료.

첫 native 실행의 UID0과, Dockerfile의 사용자에 맞춰 권한을 낮춘 **UID/GID1000**에서 모두 통과했다. UID1000 실행은 새 소유 `/tmp` 경로에서 수행했다. 원래 NFS GPU 작업 root의0700 권한은 유지했고 시스템 계정·서비스·컨테이너를 만들지 않았다. 실제 응답 사본과 리포트는0700 작업/출력 경로에 비공개로 보존했다. UID0/1000의 세 profile 값·hash도 같다.

| 선택 | 분석 profile SHA-256 |
|---|---|
| Qwen3-8B | `08c26a70f82f2502ac87c196480a2f1b16cd4958f00ca53c812ecb2287b48c47` |
| Qwen3-4B | `ce8e39f194c60f8955fe7b03ad15dfddb7aef58536cc65a2c02f21a703b6ab71` |
| 두 모델 대응 비교 | `f8b323734b5fa7a7bb15a2b101cc976565f8816eb6c54136797681ee35e5f7fd` |

두 결과는 각각1150 portable records이며 primary96, Task3 union191, Task2 네 variant, Task5 세 framing을 포함한다. 기존 [확대 GPU 검증](validation/platform_m4_gpu_expanded_20261008.json)의 independently accepted byte hash로 입력 사본을 확인했다. 새로운 inference·분류기 정확도·사람 판정·공개 원문 허가를 만들거나 주장하지 않는다. 실제 provider 요청 없이 가상 OAuth 앱 설정만 사용했다.

## 재실행 방법

검사기는 [validate_space_native_runtime.py](../scripts/validate_space_native_runtime.py)다. 별도 검증 node에서 실행하며 Dockerfile과 같은 Python3.12 minor version을 요구한다. 먼저 [배포 후보 생성 절차](../apps/spaces/README.md)에 따라 allowlist context를 만들고 독립 전달 hash와 manifest를 확인한다. 후보에는 결과·credentials를 넣지 않는다.

`pip install`의 소스 빌드는 `build`·egg-info를 생성할 수 있다. **검증할 원래 candidate는 보존하고 별도 build 사본에서 설치한다.** 아래 경로는 모두 작업자가 소유한 새로운 비공개 경로로 대체한다.

```bash
umask 077
python3.12 -m venv /private/NEW_RUNTIME
cp -R /private/CANDIDATE /private/NEW_BUILD_SOURCE
/private/NEW_RUNTIME/bin/python -m pip install \
  -r /private/CANDIDATE/apps/spaces/requirements.lock.txt
/private/NEW_RUNTIME/bin/python -m pip install --no-deps /private/NEW_BUILD_SOURCE
/private/NEW_RUNTIME/bin/python -m pip check

/private/NEW_RUNTIME/bin/python scripts/validate_space_native_runtime.py \
  --candidate /private/CANDIDATE --python /private/NEW_RUNTIME/bin/python \
  --result /private/ACCEPTED_MODEL_A.json --result-sha256 OUTSIDE_A_BYTE_SHA256 \
  --result /private/ACCEPTED_MODEL_B.json --result-sha256 OUTSIDE_B_BYTE_SHA256 \
  --output /private/NEW_NATIVE_CHECK
```

결과 hash는 이전 독립 인수 기록에서 가져온다. 결과가 사용하는 trusted input index는 candidate의 운영자 catalog와 일치해야 한다. 새로운 업로드 결과의 안전성·inference 진위를 이 검사기가 인증하는 것은 아니다. 실제 provider secret 또는 CLI token을 넣을 필요가 없다.

`receipt.json`은 검사 범위·버전·실행 UID·입력 hash·세 profile hash·서버 종료를 기록한다. 출력 폴더에는 원문이 포함된 HTML/JSON도 있으므로 비공개로 보존한다. 실패 시 기록을 지우거나 동일 출력 경로에 덮어쓰지 않고 원인을 확인한 뒤 새 경로를 사용한다.

## 전체 입력 두 fixture의 용량 검사 — v0.25

전체 비교 용량은 실제 GPU 평가와 분리해 검사했다. 고정 full 입력에 CPU fixture 두 결과(각17670records)를 구성하고 외부 index로 검증했다. 독립 CLI와 native HTTP 업로드→비교→다운로드가 통과했으며35340사례·Task별2000/8000/2659/2659/2352행을 보존했다. 분석 profile은 HTTP/CLI의 바이트까지 같았다. 전체 출력303534808bytes(약304MB), HTML149176208bytes이며 현재 report 상한512MiB 안에 들어왔다.

검사기의 `--comparison-only`를 사용하면 두 개 이상 결과의 combined report 한 개만 검증한다. 기본은 개별 리포트와 combined report 모두다. 결과 하나로 comparison-only를 요청하면 출력 생성 전에 거절한다. 관련 guard6검사가 통과했다. 제품 package/UI/용량 상한은 변경하지 않았다.

이 데이터는 SYNTHETIC capacity fixture이며 실제 target의 전체 inference·분류 정확도·모든 응답 길이·browser visual QA를 증명하지 않는다. 실제 full 결과가 완료되면 동일 경로에서 용량·수치·UI를 별도로 검증한다. [범위와 근거](validation/platform_m5_full_comparison_capacity_20261008.json).

## 전체 비교 HTML의 브라우저 검사 — v0.26

동일149MB CPU fixture HTML을 오프라인 Chromium154.0.8037.98에서 검증했다. 로딩2.164초,12탭·두 실행 선택·각17670/전체35340기록과 core/overlap/framing의 대응 필터가 통과했다. 유효/무효 출력을 구분하고 Task4의 descriptive-only/no-rank를 확인했다. Pagination·검색·metadata drilldown·모바일 배치와 console/external 요청0도 확인했다. 화면8장을 저장하고 주요4장을 시각 검토했다.

[검사기](../scripts/validate_report_scale_ui.cjs)의 `--expected-runs 2`를 사용했으며 기본값1은 기존 한 실행 검사다. [근거](validation/platform_m5_full_comparison_browser_20261008.json). 이 결과는 CPU 예시 데이터의 화면 근거다. 실제 full GPU 완료·원본 인수·실제 결과 UI·HF 배포 검사는 별도로 남는다.

## 실제 첫 모델의 전체 리포트·앱 검사 — v0.29

Qwen3-8B의 전체17,670기록을 외부 index/registry와 원본 로그 재내보내기로 독립 대조했다. 실제98,774,358bytes HTML의12탭·검색·필터·모바일 화면이 통과했다. 고유 length-limit249응답은 Task3와 이를 재사용하는 Task4 각각249건으로 표시된다. Task5 파싱 실패2건을 보존했다.

같은63파일 후보와 Linux Python3.12.3/14개 고정 웹 의존성의 native 서버에서 실제 결과 한 개를 업로드하고 report/download·세션 격리·삭제·소유 서버 종료를 확인했다. HTTP/독립 CLI profile SHA d41ff7f554ae6dc04d9436001dde664b4145ae693d8d7740921e13b614bea8ed는 GPU 분석과 바이트까지 같다. 82.849초/exit0이며 실제 HF 로그인·컨테이너·영구 저장·두 full 모델 비교를 검사한 것은 아니다. [근거](validation/platform_m4_m5_full8b_report_app_20261008.json).

[브라우저 검사기](../scripts/validate_report_scale_ui.cjs)는 기본 --input-scope fixture이며 합성 모델 ID를 확인한다. 실제 결과에는 --input-scope actual과 각 실행의 --expected-model, --expected-length-limit를 명시한다. 한 실행이면 --expected-runs 1, 두 실행이면2와 각각의 기대값을 반복한다. Browser의 actual 표시는 제공된 실제 결과를 검사했다는 뜻이며 inference 진위/분류 정확도를 인증하지 않는다. 현재4B 전체 작업이 같은90124에서 진행 중이다.

## 실제 두 모델 전체 비교 — v0.33

v0.33: 두 실제 모델의 전체 생성·분류·내보내기·분석·통합 비교 13단계가 종료 코드0으로 완료됐다. 모델당 생성 요청15,011개·평가 기록17,670개, 전체35,340기록을 보존했다. 외부 고정 index/registry와 별도 ZIP SHA를 사용한 원본 재내보내기가 두 모델 모두 정확히 일치했다. 노드·로컬 CLI의 5개 분석 파일이 바이트까지 같고, 앱 HTTP profile도 같다. 실제 HTML199,373,743bytes의 12탭·두 실행·대응 필터·사례 검색·모바일 검사가 통과했다. [근거](validation/platform_m4_m5_full_two_actual_20261009.json). 분류 정확도·공식 순위·실제 HF 로그인/호스팅·클라우드 복구·사람 승인·공개는 별도 미완료 조건이다.

Native 검증은 별도 로컬 임시0700 경로에서 수행했다. 업로드·세션 격리·비교 다운로드·독립 CLI profile 일치·세션 삭제와 소유 서버 종료가 통과했다. 초기 NFS 새 DB의 malformed 오류는 보존한다. 이 로컬 SQLite 어댑터를 NFS에 배치한 정상 동작·복구는 미검증이다. 실제 HF OAuth·이미지·durability 검증으로 해석하지 않는다.

## 발견한 문제와 남은 조건

첫 검사는 소스 빌드가 원래 candidate에 파일을 추가해 manifest의 정확한 파일 집합 검사에서 실패했다. 두 번째는 검사기가 Linux venv Python symlink를 base interpreter로 resolve하면서 설치 환경을 잃었다. 후보 사본을 분리하고 venv executable의 원래 경로를 보존해 해결했으며 실패 기록을 유지했다. UID1000의 첫 NFS 실행은 상위 root의0700 때문에 서버를 시작하기 전에 거절됐다. 권한을 완화하지 않고 별도 로컬 임시 경로에서 성공했다. 모두 검증 준비/검사기 문제였으며 배포 package·웹 자산은 수정하지 않았다.

Windows에는 Docker/Podman과 설치된 WSL 배포판이 없었다. B300에는 Docker/Podman/nerdctl이 없고 실제 user namespace 생성도 `Operation not permitted`로 거절됐다. 설치·커널 설정·전역 daemon 변경으로 우회하지 않았다. Native UID1000 검사는 Docker image·base-image digest·컨테이너 정책·HF iframe/browser/login·클라우드 저장/복구 검사를 대체하지 않는다.

`KETI-NLP/KoEVD-Explorer` 생성은 앞서402로 거절됐고 Space/업로드는 없다. 같은 조건의 재시도나 구독·결제 활성화는 하지 않았다. 현재 배포 후보는 `generated/private-space-deployment-20261008-v22`이며 개발용 임시 저장·no-rank를 유지한다. [최종 native 근거](validation/platform_m5_native_runtime_20261008.json), [전체 표준 실행 가이드](FULL_STANDARD_RUN_GUIDE.md).


## 현재 앱의 전체 결과 브라우저 검사 — 2026-10-12 / v0.57

v0.57에서 현재 설치본의 실제 로컬 앱 화면으로 두 전체 결과17,670+17,670기록을 업로드했다. 합계89,396,889바이트 입력과 iframe의199,373,743바이트 HTML을 처리했고, Save 링크로 저장한 다섯 파일405,679,557바이트가 독립 CLI 파일과 일치했다. 전체158.875초/exit0, 분석·preview117.702초이며 비교·측정 한계·한국어 사례·모바일 화면을 시각 검토했다. 세션 격리/삭제·삭제 후 지연 다운로드 링크 거부·실제 서버 PID 일치/종료/포트 거부가 통과했다. 제품 core50는 그대로며 검증기의 대기 시간 옵션/관측 시간만 추가했다. 분석 전용 로컬 서버의 검사로 HF/OAuth/Docker나 새 추론 근거가 아니다. 실제 HF 전체 전송은 별도 승인 대기다. [근거](validation/platform_m5_current_full_app_browser_20261012.json).

`scripts/validate_uploaded_results_ui.cjs`는 실제 loopback 분석 서버에 두 `--result`를 업로드한다. `--expected-profile`과 `--expected-report-dir`에는 독립 CLI의 profile과 다섯 산출물을 지정하고 `--output-dir`은 새로운 사설 경로를 사용한다. `--analysis-timeout-ms 600000`은 관측 대기 상한이며 작업을 반복하거나 서버 분석 조건을 변경하지 않는다. 기본값120000과 허용 범위1000–1200000ms를 유지한다. 이번 브라우저는 설치된 Chrome154에서 실제 원본 전체 두 파일과 현재 v78 설치본을 사용했다. HTML·JSON·JSONL·CSV·Markdown의 visible Save 링크, iframe, 모바일 배치와 세션 삭제 경계를 검사했다. 운영 Space의 proxy/OAuth·CPU/RAM 한도는 이 로컬 결과로 인수하지 않는다.
