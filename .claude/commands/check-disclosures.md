---
description: KB·우리금융 IT 사업공고를 수집·검증해 신규 리스트를 만들고 저장소/이슈/이메일로 보고한다.
---

금융사 IT 사업공고 일일 점검을 실행한다. 오늘(KST) 기준으로 **전일 09:00 이후 신규 IT 공고**를 찾아 보고하는 것이 목표다.

## 단계

1. **기준 날짜 확정**: `TZ=Asia/Seoul date '+%Y-%m-%d %H:%M'` 로 KST 현재시각을 구하고, 수집 윈도우를 `전일 09:00 ~ 금일 09:00 KST` 로 잡는다. 날짜 변수 `DATE`(YYYY-MM-DD) 확정.

2. **병렬 수집**: 아래 두 서브에이전트를 **한 번에(병렬로)** 띄운다. 각 프롬프트에 기준 날짜와 "전일 09:00 이후만" 윈도우를 명시한다.
   - `kb-disclosure-collector`
   - `woori-disclosure-collector`
   각각 JSON 배열을 반환한다. `blocked:true` 항목이 있으면 리포트 말미에 "접근 불가 — 수동 확인 필요"로 모아 둔다.

3. **검증**: 두 수집 결과의 공고 후보(blocked 제외)를 합쳐 `disclosure-verifier` 에이전트에 넘긴다. 각 링크 실재 여부를 확인하고 `verified` 가 채워진 JSON 을 받는다.

4. **후보 파일 저장**: 검증된 배열을 `disclosure-watch/.run/candidates.json` 에 쓴다(없으면 디렉터리 생성).

5. **결정론적 파이프라인 실행**(IT필터 + 어제 대비 신규 추출 + 리포트 + 상태반영):
   ```bash
   cd disclosure-watch && node bin/diff-report.mjs .run/candidates.json --date "$DATE" --window "전일 09:00 ~ 금일 09:00 KST" --commit
   ```
   - 이 단계가 `reports/$DATE.md` 를 쓰고 `state/kb.json`·`state/woori.json` 을 갱신한다(다음날 중복 방지).
   - stderr 의 `[meta]` JSON 에서 신규 건수(total)를 읽는다.

6. **보고** (출력 채널 3개):
   - **저장소 커밋**: `reports/$DATE.md` 와 갱신된 `state/*.json` 을 커밋해 작업 브랜치에 푸시한다.
   - **GitHub 이슈**: 신규가 1건 이상이면 `mcp__github__issue_write` 로 이슈 생성. 제목 `[금융사 IT공고] $DATE 신규 N건`, 본문 = 리포트 마크다운.
   - **이메일**: `hsung@redhat.com` 으로 발송. SMTP 환경변수(`SMTP_HOST` 등)가 설정돼 있으면
     `node -e "import('./disclosure-watch/lib/notify.mjs')..."` 로 전송, 없으면 "SMTP 미설정 — 발송 생략"을 리포트에 남기고 이슈/커밋으로 대체한다.

7. **요약 보고**: 사용자에게 신규 건수, 그룹별 분포, 접근 불가 회사, 산출물 위치(리포트 파일/이슈 링크)를 3~5줄로 보고한다.

## 주의
- 수집 에이전트가 `blocked` 를 반환하면 그 회사 네트워크가 정책상 막힌 것이다. 데이터를 추측하지 말고 "수동 확인 필요"로 표기한다.
- 신규 0건이어도 리포트는 만들고(스케줄 정상 동작 증빙), 이메일/이슈는 생략 가능.
