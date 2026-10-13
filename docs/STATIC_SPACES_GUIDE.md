# Static 분석·비교 후보

이 후보는 GPU 평가를 마친 사용자가 동일한 `results.json`을 선택하고,
브라우저에서 분석·응답 탐색·모델 비교·리포트 다운로드를 수행하는 경로다.
2026-10-12에는 사용자 승인으로 [KoEVD Explorer](https://huggingface.co/spaces/KETI-NLP/KoEVD-Explorer)를
Public으로 전환했다. 아래 비공개 hosting 기록은 당시 검증이다. 현재 분석 preview는
로그인 없이 접근하는 배포이며, 공동 등록·공식 순위가 연결됐다는 뜻은 아니다.
기존 Docker/FastAPI 앱과 제출·저장·검토 코드는 보존한다. Static 화면만으로
웹 제출·영구 저장·운영자 승인·철회·공식 순위 기능이 완성됐다고 표현하지 않는다.

## 계산과 데이터의 위치

- GPU 생성·안전/전략 측정: 사용자의 vLLM 및 기존 KoEVD CLI.
- 검증·재채점·분석: Pyodide의 브라우저 Python Web Worker. 기존
  `results.py`, `diagnostics.py`, `reports.py`, parser/scorer를 그대로 실행한다.
  JavaScript에 지표 계산을 복제하지 않는다.
- 입력·정답: 배포자가 독립적으로 준비하고 `InputCatalog`로 검사한 고정 파일.
  사용자가 선택한 결과의 gold·요약 점수·자칭 공개 상태는 허용하지 않는다.
- 결과 파일: 원래 UTF-8 바이트를 브라우저 메모리로 읽는다. JavaScript의
  parse/stringify는 `0.0`을 `0`으로 바꾸므로 Python 검증 전에 사용하지 않는다.
- 공개 참조: 기존 catalog가 실제 원문 권리/공개 근거를 통과한 항목만 포장한다.
  기본 실제 데이터 후보에는 참조가 없다. synthetic demo는 별도 표시한다.
- 공동 등록: 연결되지 않았다. 기존 제출 backend 또는 독립적인 검토·갱신
  작업이 필요하며, 로컬 분석 성공만으로 서버 검증·공식 순위가 부여되지 않는다.

Pyodide와 원본 코드는 같은 origin에서 제공한다. 선택한 결과를 HTTP로
전송하지 않으며 모델 API를 호출하지 않는다. 생성된 HTML은 기존 renderer와
같고 다운로드 후 네트워크 없이 열린다. 미리보기는 `allow-scripts`만 부여한
iframe에 표시하고 원문은 inert JSON/textContent로 렌더링한다. 부모 CSP에는
고정 report.js/report.css hash만 추가한다. 결과 문자열로 CSP를 만들지 않는다.

## 로컬 후보 만들기

현재 미커밋 개발 source가 필요하다. 공개 GitHub main에 아래 코드가 이미
배포돼 있다고 가정하지 않는다. 저장소 root에서 새 가상환경을 준비한다.

```bash
python -m pip install -e .
python scripts/fetch_static_runtime.py --output generated/static-runtime
python examples/make_demo_space.py --output-dir generated/static-demo-inputs
python scripts/materialize_static_space.py \
  --catalog generated/static-demo-inputs/catalog.json \
  --runtime-dir generated/static-runtime \
  --output generated/static-demo-space --demo
python -m http.server 8080 --bind 127.0.0.1 --directory generated/static-demo-space
```

`http://127.0.0.1:8080`에서 SYNTHETIC-A.json을 선택하고 가상 참조 B를 추가한다.
두 결과를 직접 선택해도 된다. 새 output 폴더를 사용하며 기존 자료를 덮어쓰지
않는다. `file://`로 worker를 실행하지 않고 로컬 HTTP/HTTPS를 사용한다.

실제 후보에는 `--demo`를 제거하고 independently registered input catalog를
공급한다. [기존 catalog 준비](SPACES_GUIDE.md)를 따른다. 입력 배포와 실제
모델 응답의 공개 승인 범위는 별개다. 포장 전에 실제 참조의 권리를 검사한다.

```bash
python scripts/materialize_static_space.py \
  --catalog /path/to/operator-data/catalog.json \
  --runtime-dir generated/static-runtime \
  --output generated/static-development-space
```

결과 후보 root의 `README.md`는 `sdk: static`과 `app_file: index.html`을 지정한다.
`deployment-manifest.json`은 파일과 engine source 바이트를 기록한다.
`runtime/runtime-manifest.json`에는 고정 URL·버전·download SHA가 있다.
source bundle에는 WASM·원본 데이터·실제 응답·credential을 넣지 않는다.
후보를 HF에 게시하는 작업은 별도 승인 범위다. 결제나 공개 push는 하지 않는다.

`DATA_LICENSE.md`에 고정 원본 데이터의 KoEVD 연구용 이용약관을 그대로 포함한다.
입력 인덱스는 데이터의 변환본이므로 소프트웨어 Apache-2.0과 라이선스 범위가
다르다. README의 데이터·논문 출처와 초기 화면의 민감한 예시 안내를 보존한다.

## 입력·취소·리포트

1–4개 결과(참조 포함), 파일당 128 MiB, 전체 256 MiB를 허용한다. 출력은
512 MiB를 초과하면 성공 리포트로 반환하지 않는다. Bootstrap 반복 수/seed를
명시하며 0은 신뢰구간 미계산이다. 분석 seed는 생성 seed와 다르다.

선택·결과 지우기는 worker를 종료하고 파일 선택·미리보기·download URL을
해제한다. reload/page 종료도 세션을 종료한다. 브라우저 메모리의 안전한
물리적 소거를 보장하지 않는다. 파일은 서버 저장소에 등록되지 않는다.

다섯 다운로드: `report-v2.html`, `profile-v2.json`, `cases-v2.jsonl`,
`metrics-v2.csv`, `report-v2.md`. 기존 Task별 분모, tool-overlap union,
framing, N/A, 측정 제한과 호환성 사유를 유지한다. Task 4 품질 순위나
종합 윤리 점수는 만들지 않는다. Hash/재계산은 생성 진위·정확도 증명이 아니다.

## 검증과 남은 범위

CPU bridge 검사는 공통 엔진의 다섯 출력 일치, 조작·누락·stale measurement,
미설정 입력/자칭 게시 상태 거부, 중복 결과, runtime/engine 포장 경계 및
미승인 실제 참조 배제를 확인한다. 실제 browser harness는 원본 파일 선택,
Python 실행, profile 일치, 다섯 다운로드, report 탭/응답, 외부 요청·POST 없음,
모바일 overflow와 삭제를 점검한다. CPU fixture는 실제 추론 근거가 아니다.

```bash
python -m unittest discover -s tests -p test_browser_bridge.py -v
node scripts/validate_static_space_ui.cjs \
  --space generated/static-demo-space --output generated/static-browser-check \
  --files '["generated/static-demo-inputs/SYNTHETIC-A.json"]' \
  --reference synthetic-reference-b --expected /path/to/local/profile-v2.json \
  --resamples 100 --browser-executable /path/to/chrome
```

Node helper에는 Playwright가 필요하다. Expected profile은 같은 원본 결과·
독립 index·resamples/seed로 기존 `koevd-diagnose`를 실행해 준비한다.
CPU fixture를 실제 생성이나 공개의 증거로 취급하지 않는다.

초기 runtime은 약12 MiB이며 전체 입력 catalog는 추가로 필요하다. 전체
비교의 브라우저 메모리·속도를 실측해 범위를 기록한다. 모바일 화면 확인은
실제 스마트폰에서의 전체 계산을 보장하지 않는다. 실제 HF iframe·배포 환경,
공개 참조 승인과 공동 등록 backend/OAuth/cloud·운영자 인수는 별도 gate다.

## 현재 확인된 개발 상태 — 2026-10-12

Public/Static/RUNNING revision `dbf81077126375b0a9bba55436d0c1df5825efc3`을 익명 API와 실제 브라우저에서 확인했다. 직접 앱 전체35,340기록/bootstrap100/193.412초·다섯 native 파일 일치와 부모 페이지의 실제48+48기록 파일 선택→분석→다운로드·반응형 배치가 통과했다.23개 payload는 후보와 정확하다. 전용 웹 로그인이나 컨테이너 없이 개인 분석이 가능하다. 기준 참조/공동 등록·공식 순위는 미연결이다. [최신 근거](validation/platform_m5_public_static_20261012.json). 아래 v0.39 이하는 당시 비공개 기록이다.

v0.39에서는 실제 사용자 Chrome의 HF Hub 부모 페이지에서 private/Running과 embedded 초기 분석 화면을 확인했다. 부모의 파일 선택→전체 분석→다운로드는 chooser 설정 확인 대기 상태로 미검증이다. 서버의 공개 OAuth 모드 추가와 최신 설치310 CPU는 별도 범위이며 Static 제출 UI/공동 등록·공개 참조를 활성화한 것이 아니다. [근거](validation/platform_m6_public_oauth_20261011.json). 아래 v0.38의 전체 직접 앱 인수는 그대로 유효하다.

v0.38에서 실제 비공개 HF 직접 앱과 내부 report iframe도 전체35,340기록/bootstrap100,
176.241초·다섯 native 파일 일치·탭/사례/모바일/삭제를 통과했다. 일반 bearer401
이후 HF-issued owner cookie로 접근했다. 고정 입력/런타임의 HF CDN 다운로드만
별도로 검사했으며 사용자 결과 전송은 없다. [검증 CLI와 절차](STATIC_HOSTING_VALIDATION.md),
[최신 근거](validation/platform_m5_static_hosted_ui_20261011.json).
Hub 부모 페이지/제출자 OAuth·공동 등록·cloud·승인된 공개 참조는 미완료다. 아래 v0.37은 당시 기록이다.

두 실제 모델 전체35,340기록의 resamples100 분석은 브라우저171.729초이며
다섯 파일이 기존 GPU/native Python과 정확히 일치했다. 설치 CPU299검사도
오류·실패·skip0이다. 비공개 [개발 Space](https://huggingface.co/spaces/KETI-NLP/KoEVD-Explorer)의
sdkstatic/RUNNING/hardwareNone과22개 업로드 파일의 바이트를 확인했다.
Private app 직접 요청401이므로 실제 HF 화면 제공·웹 로그인 인수는 남는다.
실제 target 결과·DB·credential을 게시하지 않았다. [근거](validation/platform_m5_static_hosting_20261011.json).

개인 결과 분석, 호환성 검사, 승인된 참조와 응답 비교, 지표별 공개 리더보드
읽기는 Static에서 가능하다. 결과 등록·검토·철회와 공용 데이터 갱신에는
기존 backend 또는 독립 검증·승인 후 저장소를 갱신하는 비동기 운영 절차가 필요하다.
후자는 설계 가능 경로이며 현재 운영으로 연결하거나 M6 통과로 취급하지 않는다.
브라우저에서 보이는 파일 선택은 서버 저장·공개 등록과 다르다.

## 공식 자료

- [HF Static Spaces](https://huggingface.co/docs/hub/spaces-sdks-static): 무료 정적 제공.
- [Pyodide 0.29.3](https://pyodide.org/en/0.29.3/usage/index.html): Web Worker 실행.
- [Pyodide source/license](https://github.com/pyodide/pyodide/tree/0.29.3).
- [CPython 3.13.2 source/license](https://github.com/python/cpython/tree/v3.13.2).
