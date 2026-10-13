# 고정 응답 측정 조건 감사 결과

2026-10-08, GPU_NODE B300. 실제 Qwen3-8B와 Qwen3-4B의 prefix96 생성 결과를 보존한 상태에서 각 7개 조건의 safety/strategy 측정을 완료했다. 생성→측정→export→report→comparison 확대 통합과 이 감사는 다른 검증이다. [확대 통합](validation/platform_m4_gpu_expanded_20261008.json), [최종 감사 근거](validation/platform_m4_gpu_measurement_matrix_20261008.json).

기준은 확대 실행의 traced batch2/BF16-request 측정이다. 각 비교의 Task3와 Task4 분모는 191이며, 원본 입력·생성 파일 8개의 바이트가 모두 동일하다. 모든 조건에서 두 측정 모두 191개가 유효했고 유효·무효 상태 변화는 0건이다. Task4는 동일한 Task3 생성 응답을 사용한다.

| 기준과 비교한 조건 | 8B safety 변화 | 8B strategy 변화 | 4B safety 변화 | 4B strategy 변화 |
|---|---:|---:|---:|---:|
| 같은 traced batch2 반복 | 0 | 0 | 0 | 0 |
| trace 없는 batch2 | 0 | 0 | 0 | 0 |
| traced batch1 | 0 | 5 | 0 | 6 |
| traced batch4 | 0 | 3 | 0 | 9 |
| 입력 역순 traced batch2 | 0 | 1 | 0 | 2 |
| 단건 `predict` | 0 | 5 | 0 | 6 |
| float32 요청 traced batch2 | 0 | 10 | 0 | 9 |

변화는 jointly valid 사례에서 분석 엔진이 정의한 semantic label 비교다. 이 감사에서는 raw-output 변화 수도 위와 같다. 조건 사이에 중복되는 사례가 있으므로 변화 수를 더해 고유 사례 수로 사용하지 않는다. 단건 실행과 batch1은 wrapper 호출 경로도 다르다. 관찰을 배치·순서·정밀도만의 인과 효과로 단정하지 않는다.

조건 전체에서 한 번이라도 라벨이 달라진 고유source는8B11개,4B15개다. 총26사례의 원문과 측정 전후를 `generated/measurement-matrix-changed-cases-20261008-v2`에 비공개로 보존했다. 이 자료는 classifier 출력을 포함한 unblinded 진단이며 사람 판정용gold가 아니다. 사람에게 먼저 제공할 blinded 검토 자료는 별도로 유지한다.

## 정밀도 요청과 실제 관측

두 target의 float32-request 조건에서 safety parameter storage는 BF16 752,393,024개와 FP32 6,389,760개로 남았다. 따라서 **safety의 완전한 FP32 비교는 이 실행에서 실현되지 않았다**. strategy는 FP32 8,234,382,336개로 관측됐다. 일반 BF16-request strategy는 BF16 8,190,735,360개와 FP32 43,646,976개다. 어댑터·base revision과 원래 wrapper는 보존했다.

원본 trace의 dtype counts와 호출 순서·tokenization/output 결합을 독립적으로 검증했다. Parameter storage는 kernel arithmetic의 증명이 아니다. Safety 라벨 변화가 없다는 사실도 정확도·안전성 인증이 아니다. 사람 판정은 미완료이며 모든 classifier 지표의 `measurement_limited`와 공식 rank 제외를 유지한다.

## 반환과 인수

- 실행 handle46297은 terminal exit0, controller39972 종료 확인. 14개 classifier 명령 모두 passed/exit0.
- 반환 ZIP: `generated/KoEVD_measurement_matrix_expanded_20261008_v1.zip`, 27,223,907bytes, 221manifest files.
- 외부 SHA256: `695b2e25fb853726a8e37b63c2d38ff12b03484ccbc8b749f96fb56b0505b95b`.
- 인수: `generated/measurement-matrix-intake-20261008-v1/intake-receipt.json`.
- ZIP 밖의 기존 인수 baseline과 v16 독립 prefix96 index를 사용했다. 원본/variant raw 재export, frozen hashes, trace 조건, 반환 comparison의 독립 재계산이 정확히 일치했다. ZIP의 코드를 실행하지 않았다.

[반환 절차](MEASUREMENT_MATRIX_RETURN_GUIDE.md)는 재검증 방법을 설명한다. 이 결과는 같은 계열 두 모델의 custom prefix96 통합 근거이며, full standard baseline·held-out F1·독립 사람 검토·생성 진위 인증·공개 동의·live Space 배포를 대신하지 않는다.
