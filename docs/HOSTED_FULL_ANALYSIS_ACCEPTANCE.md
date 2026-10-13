# 비공개 HF 기본 앱의 전체 결과 용량 인수

## 2026-10-12 실제 제한 시험 완료

v0.58에서 사람이 승인한 실제 private CPU 전체 전송 인수를 완료했다. Qwen3-8B/4B 각17,670기록 JSON을 각1회/합계89,396,889바이트 전송하고 대응 비교1건을 실행했다. 다섯 다운로드405,679,557바이트가 독립 native 파일과 직접 바이트 일치했으며 로컬 hash 재검사도 통과했다. 총259.906초/exit0, job terminal·pending false·검증 session2개 cleanup200/200·다른 session의 출력 접근 거부를 확인했다. 종료 후 같은 8e692c88 revision/private Docker/RUNNING/cpu-basic/단일 replica를 읽기 전용으로 재확인했다. 제품 core50·기본 프로필을 보존했고 제출/Bucket/snapshot/재배포/restart/Secret/공개/유료 변경은 없다. 이번 승인은 이 제한 시험 완료로 소진됐으며 개별 분석2개나 실제 hosted browser/OAuth·local image UID/CMD·분류 정확도·운영자/공개 권한을 새로 인수한 것은 아니다. [근거](validation/platform_m5_actual_full_hosted_20261012.json).

아래 제안/준비 문구는 실행 전의 절차 기록이다. 동일 전송의 새 실행은 이번 종료된 승인을 재사용하지 않는다.

현재 실제 HF 유한 종료/두48+48 초안 복원은 통과했지만, 현재 Docker 기본 앱의 두 모델 전체 결과 인수는 아직 없다. 이 절차는 이미 실행 중인 비공개 `KETI-NLP/KoEVD-Platform-Dev`에서 **일시 분석**만 수행하는 별도 제안이다. 앞선 snapshot 시험 승인을 재사용하지 않으며 전체 결과 전송 전에 사람이 새 범위를 승인해야 한다.

검사기는 [validate_hosted_private_analysis.py](../scripts/validate_hosted_private_analysis.py)다. 기본 실행은 **preflight-only**다. 기존 HF CLI 권한으로 private resource에 접근하고 revision·private Docker·RUNNING/cpu-basic·단일 replica·health·catalog 한도·익명 앱 경계를 읽는다. 결과 파일 body, 분석 session/job, saved submission, Bucket, repo 변경이나 재시작을 수행하지 않는다. 프록시 resource cookie/JWT와 앱 session token은 메모리에만 두며 앱 사용자 로그인으로 표시하지 않는다.

## 준비된 정확한 범위

| 항목 | 값 |
|---|---|
| 대상 | 기존 비공개 CPU Space `KETI-NLP/KoEVD-Platform-Dev` |
| 현재 고정 revision | `8e692c88d412d6305879473e3e8e74d46bb7dd2c` |
| 입력 | 실제 Qwen3-8B/4B의 각17,670기록, 합계35,340기록 |
| 8B 파일 | 44,779,573바이트, SHA `27a4dea555208658133b7713f4f24938cf4e8b8cde23bb1e2003028692ba5a99` |
| 4B 파일 | 44,617,316바이트, SHA `d136bf925164a6604e99da65f8e604541f0236a69d2bfe6479c9549daf293cf1` |
| 입력 전송 한도 | 두 POST body 합계89,396,889바이트·각1회, 자동 재전송 없음 |
| 실행 | 자체 검증 session1+격리 검사 session1, 대응 비교 job1 |
| 설정 | 서버 기본 bootstrap100/seed1729, 입력의 score/gold를 신뢰하지 않고 고정 index로 재구성 |
| 출력 | JSON·JSONL·CSV·Markdown·HTML5개, 기존 native 합계405,679,557바이트 |
| 출력 body 한도 | decoded report body 합계512MiB 이하; 오류 때 partial/receipt 보존 |
| 기본 profile | 그대로 유지. 배포·restart·hardware·visibility·Secret 변경 없음 |
| 제외 | saved submission, publication/review, Bucket/snapshot, 상시 백업, 새 GPU inference, 분류 정확도/F1 재현 주장 |

업로드 실패는 attempted body를 보수적으로 집계하고, 201 응답으로 확인된 바이트를 별도로 기록한다. 각 다운로드는 accepted native 파일과 **stream chunk를 직접 바이트 대조**하며 잘림·변조·용량 초과는 실패다. 다른 앱 session은 원본 업로드/보고서에 접근할 수 없어야 한다. 두 검증 session만 삭제하며 기존 사용자 session/초안에는 삭제 요청을 보내지 않는다.

분석의 관측 deadline은20분이다. timeout·실패를 job 종료로 해석하거나 새 job을 재발주하지 않는다. 성공/실패의 실제 terminal 응답과 cleanup 상태를 영수증에 남긴다. 아직 busy이거나 접근 실패로 terminal/cleanup이 미확정이면 `owned_analysis_job_may_remain_pending` 또는 실패 상태를 유지하고 운영자에게 확인을 요청한다. 다른 사람의 작업을 중단하는 pause/restart를 자동 수행하지 않는다. 초기 preflight는 POST/DELETE 자체가 없다.

## 승인 전 사전 검사

repository root에서 다음 명령으로 실제 preflight만 실행한다. `--output`은 새로운 사설 경로다. 전송 승인 flag가 없으면 결과 body를 전송하지 않는다.

```powershell
python scripts/validate_hosted_private_analysis.py `
  --space-id KETI-NLP/KoEVD-Platform-Dev `
  --revision 8e692c88d412d6305879473e3e8e74d46bb7dd2c `
  --candidate generated/private-space-finite-capture-candidate-20261012-v78 `
  --result generated/full-two-gpu-validation-20261009-v54/accepted/full-core-v1/Qwen3-8B/results.json `
  --result-sha256 27a4dea555208658133b7713f4f24938cf4e8b8cde23bb1e2003028692ba5a99 `
  --result generated/full-two-gpu-validation-20261009-v54/accepted/full-core-v1/Qwen3-4B/results.json `
  --result-sha256 d136bf925164a6604e99da65f8e604541f0236a69d2bfe6479c9549daf293cf1 `
  --expected-dir generated/container-runtime-preparation-20261012-v79/full-local-external-server/http/cli-0 `
  --max-upload-bytes 89396889 --max-download-bytes 536870912 `
  --output generated/your-fresh-preflight-directory
```

Python 환경에는 host-side `httpx`와 `huggingface-hub`가 필요하다. 검사 자체는 새 app/image를 설치하지 않는다. 실제 검증된 v78 noneditable CPU 환경과 고정 입력/독립 native 출력을 사용한다. 현재 source ZIP은 generated의 실제 입력·응답·native 보고서를 포함하지 않으므로 다른 노드에서 실행할 경우 이 private 사본을 독립 SHA와 함께 제공해야 한다.

실제 전송은 사람이 이 범위를 승인한 뒤 같은 인수된 입력과 새 output 경로로 `--approve-private-result-transfer`를 추가한다. 이 flag는 법적 공개 권한이나 전체 Goal 승인을 대신하지 않으며 실제 사람의 승인이 먼저 필요하다. `preflight_only`를 실제 전체 upload/report 인수 통과로 표시하지 않는다.

## 결과의 해석

성공은 **선택한 HF 호스팅 환경의 현재 전송 크기·대응 비교·다섯 다운로드·session isolation/cleanup**에 관한 것이다. 개별 분석2개, local Docker image ID/UID/기본 CMD, 브라우저 native 저장/iframe/큰 리포트 visual QA는 별도 범위다. 운영자 생성/정책/복구 판단·공개 원문 권한·production readiness·분류 정확도도 이 자동 검사로 인수하지 않는다. 로컬 Docker 기본 CMD/UID1000 검사는 [별도 노드 절차](CONTAINER_RUNTIME_ACCEPTANCE.md)를 사용한다.

## 외부 전송 없이 실행 경로를 검사하는 방법

`scripts/validate_hosted_analysis_fixture.py`는 설치된 앱의 실제 로컬 HTTP 서버에서 위 검사기의 전송 분기를 실행한다. HF 리소스 조회와 접근 인증만 명시적 모의 응답으로 대체하며, 부모·서버의 외부 소켓 연결과 실제 자격 증명 전달을 차단한다. `--candidate`, 두 `--result`와 `--result-sha256`, 독립 CLI 산출물의 `--expected-dir`, 새로운 `--output` 경로를 지정한다. 실제 HF 인증을 우회하는 배포 옵션은 추가하지 않는다.

2026-10-12의 48+48기록 검사에서 입력 두 건, 비교 작업 한 건, 보고서 다섯 종류의 직접 바이트 대조, 다른 세션의 접근 거부, 두 검증 세션 삭제가 통과했다. 첫 실행은 Windows 가상환경 실행 핸들 종료 후 HTTP 포트가 잠시 남아 실패로 보존했다. 실제 Python 프로세스를 직접 소유하도록 검사기를 수정한 재실행은 13.937초에 통과했으며 PID 일치·프로세스 종료·포트 연결 거부를 확인했다. 이 근거는 로컬 96기록의 실행 경로에 한정된다. 실제 HF에서 전체 35,340기록을 전송·분석한 근거가 아니다.
