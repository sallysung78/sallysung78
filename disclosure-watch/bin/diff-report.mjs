#!/usr/bin/env node
// 결정론적 파이프라인: 수집된 후보 → IT필터 → 어제 대비 신규 추출 → 리포트 → 알림 페이로드.
//
// 입력: 수집/검증 에이전트가 만든 candidates JSON (경로를 인자로).
//   형식: [{ group:"KB"|"WOORI", label, company, title, link, postedAt, body?, verified? }, ...]
// 사용: node bin/diff-report.mjs <candidates.json> [--date YYYY-MM-DD] [--window "..."] [--commit]
//   --commit 을 주면 상태(state/*.json)에 반영하고 reports/<date>.md 를 쓴다.

import { readFileSync, writeFileSync, mkdirSync, existsSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';
import { classifyIT } from '../lib/keywords.mjs';
import { loadState, computeNew, commitState } from '../lib/state.mjs';
import { renderMarkdown } from '../lib/report.mjs';
import { buildEmail } from '../lib/notify.mjs';

const __dir = dirname(fileURLToPath(import.meta.url));
const ROOT = join(__dir, '..');

function arg(name, def) {
  const i = process.argv.indexOf(name);
  return i >= 0 ? process.argv[i + 1] : def;
}
const candPath = process.argv[2];
if (!candPath || candPath.startsWith('--')) {
  console.error('usage: node bin/diff-report.mjs <candidates.json> [--date YYYY-MM-DD] [--window "..."] [--commit]');
  process.exit(1);
}
const date = arg('--date', new Date().toISOString().slice(0, 10));
const windowKst = arg('--window', '전일 09:00 ~ 금일 09:00 KST');
const doCommit = process.argv.includes('--commit');
const nowIso = new Date().toISOString();

const sources = JSON.parse(readFileSync(join(ROOT, 'sources.json'), 'utf8'));
const labelOf = (g) => sources.groups[g]?.label || g;

const candidates = JSON.parse(readFileSync(candPath, 'utf8'));

// 1) IT 필터
const itItems = candidates
  .map((c) => ({ ...c, ...classifyIT(c.title || '', c.body || '') }))
  .filter((c) => c.isIT);

// 2) 그룹별 신규(어제 대비) 추출
const groupsOut = [];
for (const group of ['KB', 'WOORI']) {
  const items = itItems.filter((c) => c.group === group);
  const state = loadState(group);
  const fresh = computeNew(state, items);
  groupsOut.push({ group, label: labelOf(group), items: fresh });
  if (doCommit) commitState(group, items, nowIso); // 신규+기존 모두 seen 으로 마킹
}

// 3) 리포트
const md = renderMarkdown({ date, windowKst, groups: groupsOut });
const total = groupsOut.reduce((n, g) => n + g.items.length, 0);

if (doCommit) {
  const repDir = join(ROOT, 'reports');
  if (!existsSync(repDir)) mkdirSync(repDir, { recursive: true });
  writeFileSync(join(repDir, `${date}.md`), md, 'utf8');
}

// 4) 알림 페이로드(이메일). 실제 발송은 notify.sendEmail 또는 오케스트레이터가 담당.
const email = buildEmail({ date, markdown: md, totalCount: total });

console.log(md);
console.error(`\n[summary] date=${date} new=${total} committed=${doCommit} mailTo=${email.to}`);
// 오케스트레이터가 파싱하기 쉽게 마지막 줄에 JSON 메타 출력
console.error('[meta] ' + JSON.stringify({ date, total, mailSubject: email.subject, mailTo: email.to }));
