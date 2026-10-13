# 지표별 등록 정책과 순위 후보

2026-10-08. 계약 버전: `koevd-rank-admission-v1`. 구현: `koevd_eval.eligibility`.

현재 기본 정책은 **candidate**다. 실제 두 target의 prefix4 GPU 통합은 검증했지만 전체 standard baseline·측정 조건 감사·실제 생성 영수증의 독립 operator 인수와 정책 승인은 남아 있다. 로컬 공개 요약과 지표 비교표는 수치·분모·source 수·제외 사유를 반환하며 기본 설정에서 공식 순위를 부여하지 않는다. 웹 후보는 가상 계정·가상 결과로 검증했고 외부 리더보드가 배포되었다는 뜻은 아니다.

## 무엇을 별도로 판단하는가

구조 검증, 결과 공개 동의, 생성 실행 검증, 측정 정확도, 순위 등록은 별개다. 올바른 JSON이나 HF 로그인, checksum 일치, 분류기의 재실행 또는 공개 권한 검토만으로 실제 대상 모델의 생성 실행이 검증되지는 않는다. 업로드한 점수·gold·rank 상태를 읽지 않고 독립적인 operator index로 다시 계산한다.

`evaluate_admission()`은 표준 결과와 operator index를 검증하고, 지표마다 `rank_eligible`, `reasons`, `rate`, `coverage`, `cohort_sha256`을 반환한다. `rate`에는 분자·분모·값·source 수와 가능한 source bootstrap 구간이 포함된다. 0분모는 null이며, API 실패나 해석 실패가 있는 실행의 관찰된 위험 비율 0을 안전한 성능으로 승인하지 않는다.

| 대상 | 구분 | 현재 순위 취급 |
|---|---|---|
| Task 1 | 위험 입력 누락률, 무해 입력 오경보율 | 서로 다른 지표. 해당 라벨 분모와 전체 Task 유효 응답을 확인 |
| Task 2 | 네 variant의 유효 응답 정답률 | variant별 별도 후보, 통합 점수 없음 |
| Task 3 | primary core, tool-overlap, union의 전체·분류된 응답 기준 위험률 | 모든 범위에 `measurement_limited`로 제외 |
| Task 4 | 전략 분류 coverage | 설명용. 전략 빈도는 기존 분석의 15-label 표에서 확인하며 품질 순위 없음 |
| Task 5 | 세 framing의 전체·유효 선택 기준 위험 도구 선택률 | framing별 별도 후보. 거절·허용 도구·직접 답변·명확화 요청 빈도는 설명용 |
| Task 3–5 | framing 및 pooled의 classifier-safe/unsafe 조건부 위험 도구 선택률 | 측정 한계와 모델별 조건부 집단 차이 때문에 설명용, 순위 없음 |

Task 5의 위험 도구 선택률이 낮다고 유용성이나 실제 로봇 안전성이 높다고 주장하지 않는다. 실제 도구를 실행하지 않으며, 이 순위는 선택한 지표의 수치 순서만 의미한다. 대응 비교·metadata 분석·전략 빈도와 사례 탐색은 기존 공통 분석 엔진에서 제공한다.

## 공통 등록 조건

1. 운영자가 선택한 `ProtocolRegistry`의 정확한 protocol 정의와 전체 expected input-set digest 일치. 업로드가 제공한 index나 `standard` 문자열만으로는 통과하지 않는다.
2. 고정 decoding policy 준수, immutable target revision과 기록된 template/dtype/quantization/thinking/engine 조건. 알려지지 않은 값은 추정하지 않는다. 현재 후보는 target commit SHA를 지원하며 commit 없는 로컬 가중치의 공식 등록 경로는 후속 작업이다.
3. 별도 운영자 설정으로 승인된 정책과 승인 결정의 immutable digest. 기본 `RankPolicy()`는 candidate이며 승인 상태를 자동 생성하지 않는다.
4. 정확한 artifact/index/target-generation declaration에 묶인 독립 생성 검증 영수증. `operator_reproduced`와 `actual_gpu`가 모두 필요하다. `measurement_rechecked`와 CPU fixture는 이 조건을 충족하지 않는다.
5. 해당 Task/partition에 해석 가능한 출력이 빠짐없이 있어야 한다. 현재 후보는 임의의 90% 같은 경험적 threshold를 정하지 않고 완전한 valid output을 보수적인 등록 조건으로 둔다. Task 1은 두 label 지표를 함께 계산하되 전체 Task 출력도 완전해야 한다. Task 2/5는 variant/framing 단위로 확인한다. 향후 실제 full baseline 검증과 운영 결정에서 다른 기준을 채택하면 별도 policy version을 사용한다.
6. 지표 분모가 0이 아니어야 한다. 측정 제한이나 설명용 속성은 다른 조건을 만족해도 유지한다.

이 조건은 사용자 진단 리포트나 공개 요약 자체를 거부하는 조건과 다르다. custom/partial/미해결 측정 결과도 구조가 유효하면 제한을 표시하고 분석할 수 있다. 다만 full standard인 것처럼 순위에 섞지 않는다. 구조가 손상되었거나 score/gold를 주입한 artifact는 먼저 결과 validator에서 거부된다.

## 운영자 증거 경계

`OperatorEvidence`는 trusted boundary가 제공하는 Python 객체다. typed 객체와 digest 자체는 인증·서명·실제 GPU 실행 증거가 아니다. eligibility 모듈 자체는 issuer 인증이나 GPU 반환 검토를 수행하지 않는다. 별도의 로컬 운영자 인수·철회 경로는 [생성 영수증 가이드](GENERATION_RECEIPT_GUIDE.md)에 구현·문서화했다. 독립 관리자와 `operator_local` 경계, 정확한 revision/artifact/index/declaration 결합, immutable audit event와 backup 복원을 사용한다. 검토자가 실제 실행 원본을 직접 확보·확인해야 하며 hash 참조만으로 실행을 인증하지 않는다. 웹 upload에서 객체를 직접 만들거나 `execution_scope=actual_gpu`라는 사용자 문자열을 받아서는 안 된다.

현재 `SubmissionService.public_summary()`는 공개된 정확한 revision에 인수된 활성 영수증이 있으면 그 증거를 공급한다. 없는 경우는 기존과 동일하다. 기본 정책은 candidate이며 인수 자체는 정책 승인·분류기 정확도·공식 순위를 승격하지 않는다. CPU 증거는 실제 GPU 조건을 충족하지 않는다. 영수증 철회와 제출 버전 변화는 응답 직전에 재확인한다. 검토 설명과 증거 파일 참조 원문은 공개 요약에서 제외한다.

## 현재 공개 결과의 지표 비교표

`SubmissionService.public_leaderboard()`와 읽기 전용 `GET /api/public/leaderboard`가 연결됐다. 현재 공개된 정확한 revision의 원본만 운영자 index로 재계산한다. pending/private/withdrawn 결과와 아직 공개하지 않은 새 head는 표에 넣지 않는다. summary-only로 공개한 결과도 승인된 집계 지표만 비교하며 응답 원문·owner·검토 설명·영수증 파일 참조는 반환하지 않는다.

계산은 하나의 전체 공개 목록을 snapshot으로 읽은 뒤 DB read lock을 해제한다. 계산이 끝나면 공개 목록·version·revision·scope와 operator 정책 객체를 재확인한다. 철회·receipt 취소·새 공개 결과 추가 등으로 상태가 바뀌면409 `publication_changed`로 재시도를 요구한다. 현재 후보 한도는50개 공개 entry/원본 합계128MiB이며 넘으면503 `leaderboard_capacity`를 반환한다. 일부 페이지만 계산해 전체 순위로 표시하지 않는다. 운영 규모의 증분 계산·cache는 후속 작업이다.

화면의 **Compare published metrics**에서 지표와 평가 조건 그룹을 선택한다. 비교표에는 수치·분자/분모·source 수·유효 coverage·rank/제외 사유가 나온다. 제외된 entry는 submission ID 순서로 표시하며 임시 순위를 만들지 않는다. 신뢰구간 계산은 이 가벼운 projection에서 disabled/resamples0이고, 화면에 미계산 안내가 나온다. uncertainty를 보려면 독립 분석 리포트를 사용한다. 그룹은 기록된 조건을 대응하며 unknown은 여전히 제외 사유로 남는다.

공개 목록의 metadata는 지표를 재계산하지 않는다. candidate 정책에서는 `official_rank_eligible: false`와 `policy_not_ratified`를 제공한다. trusted ratified 정책에서는 해당 필드를 `null`, 상태를 `not_evaluated_in_listing`으로 제공한다. 목록의 미계산 값을 실제 부적격으로 해석하지 않는다. 상세 `public_summary`와 지표 비교표에서 정확한 revision·활성 영수증·독립 입력을 재검사한 지표별 자격을 확인한다.

로컬 CLI의 읽기 전용 `public-leaderboard`도 같은 경로다. 기존 `koevd-submissions` 공통 옵션에 `--protocol-registry /operator/configs/protocols`를 추가해 운영자가 선택한 규약을 검사할 수 있다. `koevd-space`에서도 같은 옵션/`KOEVD_PROTOCOL_REGISTRY`를 지원한다. 개발 launcher는 준비된 registry를 지정한다. 기본 정책은 그대로 candidate이고 HTTP query/body나 upload로 정책·영수증을 지정할 수 없다. 운영 결정의 별도 로컬 보존과 명시적digest 설정은 [OPERATOR_POLICY_GUIDE.md](OPERATOR_POLICY_GUIDE.md)에 구현했다. Typed `RankPolicy`와 설정된 결정hash는 신원 인증이나 실제 사람 승인 증거가 아니다. 실제 승인·운영 활성화 검토는 별도 gate이며 기본 개발launcher는 정책 환경변수를 제거해 no-rank를 유지한다.

## 계산 엔진 사용

```python
from koevd_eval.eligibility import RankPolicy, evaluate_admission, leaderboard
from koevd_eval.protocols import ProtocolRegistry

registry = ProtocolRegistry("configs/protocols")  # operator-controlled directory
policy = RankPolicy()                           # candidate: no official ranks
admission = evaluate_admission(results, trusted_index,
    registry=registry, policy=policy, resamples=500)

# Entries come from an operator-selected current publication snapshot.
# The caller must recheck withdrawal/revision visibility before returning it.
boards = leaderboard([
    ("published-entry-id", results, trusted_index, None),
], registry=registry, policy=policy)
assert boards["boards"] == []
```

`results`와 `trusted_index`는 독립적으로 로드한 원본 문서다. 입력된 admission JSON이나 집계 점수는 순위 계산 인자가 아니다. 실제 GPU/승인 증거 없이 등록을 활성화하는 예시 명령은 제공하지 않는다. 테스트의 `ratified/actual_gpu` 객체는 긍정 경로를 확인하는 명시적 CPU 가상 객체이며 실제 승인·GPU 검증에 재사용할 수 없다.

`leaderboard()`는 metric ID와 cohort별로 별도 표를 생성한다. cohort에는 policy·protocol·index·generation·template/dtype/quantization/thinking 조건이 들어간다. 대상 모델 ID와 revision은 비교 대상이므로 cohort에서 제외한다. 설정이 다르면 같은 표에 섞이지 않는다. 정수 분자/분모를 `Fraction`으로 비교하고 정확히 같은 비율은 경쟁 순위의 동점을 유지한다. entry ID는 동점 표시 순서만 정한다. source 수, 구간, coverage와 제외 사유를 감추지 않으며 수치 순위를 유의성으로 표현하지 않는다.

bootstrap은 source 단위의 기존 공통 엔진을 쓴다. 순위 계산의 기본은 500 resamples이며 단일 source·0분모는 구간 계산 한계를 표시한다. 가벼운 로컬 공개 요약의 admission은 0 resamples로 실행하고 구간을 disabled로 표시한다. 정책·순위 엔진의 검증은 authenticated HTTP UI, 운영 receipt 저장·철회 snapshot 재확인과 배포 검증을 대체하지 않는다.

## 남은 운영 인수

- prefix96 확대와 두 target의7조건 frozen matrix는 독립 인수 완료다. [측정 감사 결과](GPU_MEASUREMENT_MATRIX_RESULTS.md). full baseline·사람 판정·실제 생성 receipt의 독립 operator 인수는 남아 있다.
- 정책 결정의 로컬 보존·명시적chain 설정은 구현됐다. 실제 근거에 기반한 사람 승인·운영 활성화·원격 snapshot 보존/복구는 남아 있다.
- OAuth/server identity의 실제 HF 로그인 인수. transport는 합성 CPU/browser 후보로 구현됐으며 actual 로그인은 아직 미검증. 권한 있는 생성 receipt API와 immutable 이력은 별도 미완료.
- 현재 공개 revision/철회·metric 비교표 연결은 가상 HTTP/browser에서 확인했다. 가상 ratified/actual_gpu 조건의 service 연결도 CPU 검사 범위이며 실제 승인·receipt-backed 공식 순위·운영 규모의 인수는 미완료.
- 원격 영구 저장, 실제 컨테이너·Space 검증.

이 항목이 남아 있는 동안 전체 M6와 release candidate 완료를 선언하지 않는다.
