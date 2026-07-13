// 리포트(마크다운) 생성 (네트워크 불필요, 테스트 대상)

/**
 * @param {object} p
 * @param {string} p.date      리포트 기준일(YYYY-MM-DD, KST)
 * @param {string} p.windowKst 수집 윈도우 설명 (예: "2026-06-29 09:00 ~ 2026-06-30 09:00 KST")
 * @param {Array}  p.groups    [{ group, label, items: [{company,title,link,postedAt,verified,matched}] }]
 */
export function renderMarkdown({ date, windowKst, groups }) {
  const total = groups.reduce((n, g) => n + g.items.length, 0);
  const lines = [];
  lines.push(`# 금융사 IT 사업공고 — 신규 (${date} KST)`);
  lines.push('');
  lines.push(`- 수집 윈도우: ${windowKst}`);
  lines.push(`- 신규 IT 공고: **${total}건**`);
  lines.push('');

  if (total === 0) {
    lines.push('> 해당 윈도우에 신규 IT 공고가 없습니다.');
    lines.push('');
  }

  for (const g of groups) {
    lines.push(`## ${g.label} (${g.items.length}건)`);
    if (g.items.length === 0) {
      lines.push('');
      lines.push('_신규 없음_');
      lines.push('');
      continue;
    }
    lines.push('');
    lines.push('| 회사 | 공고 제목 | 게시일 | 검증 | 링크 |');
    lines.push('|---|---|---|---|---|');
    for (const it of g.items) {
      const verified = it.verified === true ? '✅' : it.verified === false ? '❌' : '—';
      const link = it.link ? `[열기](${it.link})` : '(링크없음)';
      const title = (it.title || '').replace(/\|/g, '\\|');
      lines.push(`| ${it.company} | ${title} | ${it.postedAt || '-'} | ${verified} | ${link} |`);
    }
    lines.push('');
  }

  lines.push('---');
  lines.push('_자동 생성: disclosure-watch harness. ✅=검증 에이전트가 실제 공고 존재 확인, ❌=링크 깨짐/접근불가._');
  lines.push('');
  return lines.join('\n');
}
