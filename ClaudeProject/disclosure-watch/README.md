# disclosure-watch — 금융사 IT 사업공고 추적 하네스

KB금융그룹·우리금융그룹의 공고/입찰 게시판에서 **매일 아침 9시(KST), 전일 09:00 이후 올라온 IT 관련 공고**를 찾아
실재 여부를 검증하고, 어제 대비 **신규만** 골라 저장소·GitHub 이슈·이메일로 보고한다.

이건 "하네스 엔지니어링" 예제다 — 모델 하나에 다 시키지 않고, **역할별 에이전트 + 결정론적 코드 + 스케줄러**로
시스템을 구성한다.

## 구성 (3 에이전트 + 글루 + 스케줄러)

```
                ┌─ kb-disclosure-collector ───┐
 /check-        │   (KB 5개사 공고 수집·IT필터) │
 disclosures ──▶┤                              ├─▶ disclosure-verifier ─▶ bin/diff-report.mjs ─▶ 보고
 (오케스트레이터)│                              │   (링크 실재 검증)        (IT필터·신규diff·     ├ 저장소 커밋
                └─ woori-disclosure-collector ─┘                          리포트·알림)         ├ GitHub 이슈
                    (우리 5개사 수집·IT필터)                                                    └ 이메일
```

| 구성요소 | 역할 | 위치 |
|---|---|---|
| `kb-disclosure-collector` | KB(국민은행·국민카드·KB증권·KB라이프·KB생명) 공고 수집 | `.claude/agents/` |
| `woori-disclosure-collector` | 우리(우리은행·우리카드·우리투자증권·동양생명·ABL생명) 공고 수집 | `.claude/agents/` |
| `disclosure-verifier` | 후보 링크에 실제 진입해 공고 존재 검증 | `.claude/agents/` |
| `/check-disclosures` | 위 3개를 오케스트레이션 + 보고 | `.claude/commands/` |
| `lib/fetch.mjs` | 실제 브라우저(Playwright)로 페이지 렌더링 | `disclosure-watch/lib/` |
| `lib/keywords.mjs` | IT 공고 판별(키워드) | 〃 |
| `lib/state.mjs` | "어제까지 본 공고" 상태 + 신규 diff | 〃 |
| `lib/report.mjs` | 마크다운 리포트 생성 | 〃 |
| `lib/notify.mjs` | 이메일 페이로드/발송 | 〃 |
| `bin/diff-report.mjs` | 필터→신규추출→리포트→알림 (결정론적 파이프라인) | `disclosure-watch/bin/` |

수집/검증(불확실, HTML 가변)은 **에이전트(LLM)**가, 필터/중복제거/리포트(확정적)는 **코드**가 맡는다.

## ⚠️ 전제조건: 네트워크 정책 (가장 중요)

대상 금융사 사이트(`kbstar.com`, `kblife.co.kr`, `wooribank.com` 등)는 단순 fetch를 403으로 막는다 →
이 하네스는 **실제 브라우저(Playwright/Chromium)**로 접근한다.

그런데 **claude.ai/code 원격 환경의 기본 네트워크 정책은 이 외부 도메인들을 차단**한다(egress 게이트웨이 403).
이 경우 수집 에이전트는 해당 회사를 `blocked` 로 보고하고, 리포트엔 "수동 확인 필요"로 표시된다.

라이브 수집을 하려면 **둘 중 하나**:
1. **원격 환경의 네트워크 정책을 변경** — 환경을 만들 때 "제한 없음" 또는 대상 도메인 허용 커스텀 정책 선택.
   설정 방법: https://code.claude.com/docs/en/claude-code-on-the-web
2. **로컬 머신/사내망에서 실행** — 보통 외부 차단이 없어 그대로 동작.

> 네트워크와 무관한 로직(IT필터·신규diff·리포트)은 이미 완성·검증되어 있다(`node --test`). 네트워크만 열리면 즉시 라이브 동작.

## 설치

```bash
cd disclosure-watch
npm install                 # playwright(필수) + nodemailer(선택)
npx playwright install chromium   # 원격 환경엔 이미 설치돼 있으면 생략
```

## 실행

### 에이전트 오케스트레이션(권장)
Claude Code에서:
```
/check-disclosures
```
→ KB·우리 수집 에이전트 병렬 실행 → 검증 에이전트 → 리포트 → 저장소/이슈/이메일 보고.

### 결정론적 파이프라인만(수집 결과가 이미 JSON으로 있을 때)
```bash
node bin/diff-report.mjs <candidates.json> --date 2026-06-30 --commit
npm run demo                # 샘플 데이터로 동작 확인
npm test                    # 로직 유닛테스트
```

`candidates.json` 형식:
```json
[{"group":"KB","company":"KB국민은행","title":"...","link":"https://...","postedAt":"2026-06-30"}]
```

## 매일 09:00(KST) 자동 실행

서버 타임존이 UTC이면 **09:00 KST = 00:00 UTC** → cron `0 0 * * *`.

- **claude.ai/code Routine(권장, 원격)**: 새 세션을 매일 띄워 `/check-disclosures` 를 실행하도록 트리거 생성.
  (네트워크 정책이 열린 환경에서.) 프롬프트 예: "disclosure-watch 하네스를 실행해 오늘 신규 IT 공고를 보고하라. /check-disclosures 단계를 따르라."
- **로컬 cron**:
  ```cron
  0 9 * * * cd /path/to/repo && claude -p "/check-disclosures" >> disclosure-watch/cron.log 2>&1
  ```

## 이메일 발송 설정 (`hsung@redhat.com`)

`lib/notify.mjs` 는 SMTP 환경변수가 있으면 발송, 없으면 페이로드만 만든다. `.env` 또는 환경에 설정:
```
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USER=...
SMTP_PASS=...
SMTP_FROM=disclosure-watch@example.com
DISCLOSURE_MAIL_TO=hsung@redhat.com
```
사내 SMTP/릴레이 또는 메일 API(SendGrid/Resend 등)로 교체 가능. SMTP가 없으면 GitHub 이슈+저장소 커밋이 1차 채널.

## 출력물

- `reports/YYYY-MM-DD.md` — 일자별 신규 IT 공고 리포트(저장소에 커밋)
- `state/kb.json`, `state/woori.json` — 누적 "본 공고" 상태(중복 방지). 매 실행 갱신·커밋
- GitHub 이슈 — 신규 1건 이상일 때 생성
- 이메일 — `hsung@redhat.com`

## 소스 레지스트리 / 키워드 조정

- 공고 페이지 URL: `sources.json` (회사 추가·URL 수정·`login`/`note` 표기)
- IT 판별 키워드: `it_keywords.json` (`include`/`exclude`)

첫 라이브 실행 후, 정확한 게시판 URL이 불명확했던 회사(KB증권·우리투자증권·동양생명·ABL생명)는
에이전트가 찾은 실제 URL로 `sources.json` 을 업데이트하면 이후 더 빠르고 안정적으로 동작한다.
