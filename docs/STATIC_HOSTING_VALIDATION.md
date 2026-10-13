# Static Space 호스팅 검증

## 공개 앱의 익명 접속 검증

2026-10-12에 사용자 승인으로 `KETI-NLP/KoEVD-Explorer`를 Public으로 전환했다.
현재 공개 배포 revision은 `dbf81077126375b0a9bba55436d0c1df5825efc3`이며
후보는 `generated/static-public-space-20261012-v63`이다. 아래 비공개 절차의
이전 revision은 역사적 검증용이며 현재 공개 배포에 owner cookie를 쓰지 않는다.

```bash
python scripts/validate_public_static_hosting.py \
  --repo-id KETI-NLP/KoEVD-Explorer \
  --revision dbf81077126375b0a9bba55436d0c1df5825efc3 \
  --candidate generated/static-public-space-20261012-v63 \
  --node /path/to/node --browser-executable /path/to/chrome \
  --result /private/Qwen3-8B/results.json \
  --result /private/Qwen3-4B/results.json \
  --expected /private/native-analysis/profile-v2.json \
  --resamples 100 --output /private/fresh-public-browser-validation
```

이 도구는 HF API를 `token=False`로 조회하고, 인증 header·cookie 없이 공개
index와 Hub 부모 HTTP 응답을 검사한다. 새 브라우저 context에는 로그인
cookie를 넣지 않고 사용자 profile을 쓰지 않는다. 공통 browser validator의
`--anonymous` 모드는 credential이 포함된 요청을 거절한다. 실제 결과는
브라우저 파일 선택으로 읽고 HTTP로 보내지 않는다. 다섯 다운로드 모두 native
바이트와 대조하며 탭·사례·모바일·삭제·스크린샷을 확인한다.

Hub 부모 HTTP200은 부모 iframe 안에서 전체 파일 선택 흐름을 실행한 증거는
아니다. 실제 직접 앱 검증과 공동 제출·등록·공식 순위는 별도 범위다.

```bash
python -m unittest discover -s tests -p 'test_*static_hosting.py' -v
node --check scripts/validate_hosted_static_space_ui.cjs
```

### HF Hub 부모 페이지의 파일 흐름

별도 `scripts/validate_public_static_parent_ui.cjs`는 익명 context에서 Hub 페이지의
실제 embedded frame을 찾아 파일을 선택하고, 모든 HTTP 쓰기를 차단한 채 다섯
native 출력을 대조한다. 이번 부모 인수는 실제 GPU prefix 두 모델48+48기록이다.
직접 앱 전체35,340기록 검증과 범위를 구분한다. 부모의 AWS WAF/Stripe 부가 GET
두 요청은 검사 allowlist가 차단했고 page error는 없었다. 모바일에서는 중첩
iframe resize와 반응형 shell 적용을 기다린 후 화면을 확인한다.

```bash
node scripts/validate_public_static_parent_ui.cjs \
  --repo-id KETI-NLP/KoEVD-Explorer \
  --origin https://keti-nlp-koevd-explorer.static.hf.space \
  --revision dbf81077126375b0a9bba55436d0c1df5825efc3 \
  --browser-executable /path/to/chrome \
  --files '["/private/8B/results.json","/private/4B/results.json"]' \
  --expected /private/native-prefix/profile-v2.json \
  --output /private/fresh-parent-validation
```

## 이전 비공개 개발 앱 검증

이 절차는 HF가 실제 제공하는 Static 앱에서 기존 결과 파일을 분석하고,
다섯 산출물·차트·응답 탐색·모바일·삭제를 확인한다. 제출자 웹 로그인,
공개 등록·영구 저장·운영자 승인·공식 순위의 인수와 구분한다.
결과 파일은 브라우저 메모리에만 선택하며 서버에 업로드하지 않는다.

## 준비와 원본 대조

현재 미커밋 개발 소스가 필요하다. `hub`와 `dev` extras, Node의 Playwright,
Chrome 또는 Chromium을 준비한다. 실제 검증 환경은 Python3.12.14,
huggingface_hub1.31, Node24.19.0 및 Chrome154다. 기본 HF CLI 로그인과
해당 비공개 Space 읽기 권한이 필요하며, 채팅·명령행·파일에 token을 넣지 않는다.

후보는 [Static 포장 절차](STATIC_SPACES_GUIDE.md)로 만든 manifest와 전체 파일을
그대로 보존한다. HF revision은 배포 영수증의 외부 고정 commit SHA를 공급한다.
원본 모델 결과와 native 분석 파일도 독립 인수한 자료를 사용한다.
Native `profile-v2.json`과 같은 폴더에 나머지 네 분석 파일이 있어야 한다.

```bash
python -m pip install -e '.[hub,dev]'
python scripts/validate_private_static_hosting.py \
  --repo-id KETI-NLP/KoEVD-Explorer \
  --revision 0339d618b970737ec6d0b102f5ba1df9a78c6588 \
  --candidate /private/static-candidate \
  --preflight-only
```

Preflight는 private/sdk/revision과 전체 로컬 manifest를 검사하고 실제 index를
읽는다. HF가 추가하는 `window.huggingface.variables.SPACE_CREATOR_USER_ID`의
관찰된 고정 형식만 엄격하게 대조한다. 이 구문 하나를 제거한 나머지 HTML은
원본과 바이트까지 일치해야 한다. 새 provider/OAuth 변수를 임의로 허용하지 않는다.

## 격리 브라우저에서 전체 분석

```bash
python scripts/validate_private_static_hosting.py \
  --repo-id KETI-NLP/KoEVD-Explorer \
  --revision 0339d618b970737ec6d0b102f5ba1df9a78c6588 \
  --candidate /private/static-candidate \
  --node /path/to/node \
  --browser-executable /path/to/chrome \
  --result /private/target-A/results.json \
  --result /private/target-B/results.json \
  --expected /private/native-analysis/profile-v2.json \
  --resamples 100 \
  --output /private/fresh-hosted-browser-check
```

Playwright는 해당 Node 환경에서 `require('playwright')`로 읽혀야 한다.
별도 모듈 위치를 쓰는 환경에서는 `NODE_PATH`를 지정한다. Windows에서는
Python·Node·Chrome·파일 경로를 현재 환경의 절대 경로로 맞춘다.
output은 새 비공개 경로여야 하며 실제 유해 응답을 포함하므로 source bundle에 넣지 않는다.

기존 owner 권한으로 HF가 발급한 임시 Space 서명을 사용한다. 서명 요청 후
redirect는 같은 origin의 `/index.html`만 허용하고, HF가 설정한 secure/HttpOnly
cookie는 메모리와 anonymous stdin pipe로만 전달한다. 사용자 브라우저의 로그인
세션을 복사하지 않으며, credential을 argv·파일·HAR·영수증에 기록하지 않는다.
이 개발 접근 권한은 모델 생성 진위나 KoEVD 제출자의 웹 identity를 증명하지 않는다.

브라우저의 최초 요청은 하나의 HTTPS Static origin에 대한 고정 자산 GET만 허용한다.
첫 확인에서는 네 자산이 `https://us.aws.cdn.hf.co`로 이동했다. HF의 cache 상태에
따라 같은 자산이 직접200으로 제공될 수 있으므로 이동 수를 고정하지 않는다. 원래 자산에서
이어진 service redirect만 허용하고, CDN에서 받은 최종 파일도 manifest SHA로
대조한다. 모든 실제 request event를 검사한다. Playwright의 route handler는
redirect의 첫 요청만 받을 수 있으므로 route 기록만으로 외부 요청0을 주장하지 않는다.
서명 query 값은 기록하지 않는다. provider가 추가한 index 구문도 별도로 기록한다.
Chrome inspector가 전체69MB index의 응답을 지우면, 관찰된 동일 asset URL을
독립 GET으로 다시 읽어 SHA를 대조하고 이 별도 다운로드를 영수증에 표시한다.
브라우저 worker 자체도 index SHA를 검사한 뒤 분석한다. Inspector cache 문제를
앱의 입력·분석 실패로 표현하거나 자산 검증을 생략하지 않는다.
분석 후 다섯 파일을 native 산출물과 바이트 대조하고 탭·응답 사례·문자열
비실행·모바일 overflow·다운로드·선택 삭제를 검사한다. 삭제는 worker/URL 해제이며
브라우저 메모리의 물리적 안전 소거 보장이 아니다.

영수증 `evidence.json`은 계산 시간·원본 revision·브라우저·자산 SHA·출력 SHA·
요청 method/path·오류·삭제를 기록한다. 인증 cookie 값·원본 결과·서명 query는
포함하지 않는다. 정상 분석은 `report-v2.html`, `profile-v2.json`, `cases-v2.jsonl`,
`metrics-v2.csv`, `report-v2.md`를 만든다.

## 검증 범위

해당 검사에서 통과한 직접 HF Static 앱과 앱 내부 report iframe만 근거로 삼는다.
HF Hub 부모 페이지의 사용자 로그인/embedding, 실제 스마트폰 전체 계산,
공동 제출 backend, 실제 cloud 복구나 운영 정책은 별도로 인수해야 한다.
공개 실제 참조가 없는 현재 후보에서 두 개인 파일 비교가 성공하더라도
공개 모델 응답 비교와 공식 리더보드가 운영 중인 것은 아니다.

추가 credential 경계 검사는 다음과 같이 실행한다. 합성 cookie 검사는 실제
HF 로그인 통과 근거가 아니다.

```bash
python -m unittest discover -s tests -p test_private_static_hosting.py -v
node --check scripts/validate_hosted_static_space_ui.cjs
```

공식 [Static 변수 안내](https://huggingface.co/docs/hub/spaces-sdks-static#space-variables)와
[HF maintainer의 JWT 접근 설명](https://github.com/huggingface/huggingface_hub/issues/2667)을
참조했다. cookie/redirect/provider 추가 구문의 실제 동작은 이 배포에서 직접 확인한다.
