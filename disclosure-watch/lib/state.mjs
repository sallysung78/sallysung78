// 상태 관리 + diff (네트워크 불필요, 테스트 대상)
// "어제까지 본 공고"를 그룹별 JSON으로 저장하고, 오늘 수집분과 비교해 신규만 골라낸다.
import { readFileSync, writeFileSync, existsSync, mkdirSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const __dir = dirname(fileURLToPath(import.meta.url));
const STATE_DIR = join(__dir, '..', 'state');

/**
 * 공고 항목의 안정적 식별자. 링크가 가장 신뢰도 높고, 없으면 회사+제목으로 대체.
 */
export function itemKey(item) {
  if (item.link) return `url:${item.link.trim()}`;
  return `t:${item.company}|${(item.title || '').trim()}`;
}

export function statePath(group) {
  return join(STATE_DIR, `${group.toLowerCase()}.json`);
}

/** 그룹의 누적 상태(이미 본 항목 key 집합 + 메타) 로드 */
export function loadState(group) {
  const p = statePath(group);
  if (!existsSync(p)) return { group, seen: {}, updatedAt: null };
  return JSON.parse(readFileSync(p, 'utf8'));
}

/**
 * 오늘 수집한 항목들 중 "이전에 본 적 없는 신규"만 반환.
 * @param {object} state loadState 결과
 * @param {Array}  items 오늘 수집/필터된 항목들
 */
export function computeNew(state, items) {
  const seen = state.seen || {};
  const fresh = [];
  for (const it of items) {
    const k = itemKey(it);
    if (!seen[k]) fresh.push(it);
  }
  return fresh;
}

/**
 * 수집 항목들을 상태에 반영(merge)하고 디스크에 저장.
 * @param {string} isoNow 호출측에서 주입(테스트 결정성/타임존 제어용)
 */
export function commitState(group, items, isoNow) {
  const state = loadState(group);
  state.seen = state.seen || {};
  for (const it of items) {
    state.seen[itemKey(it)] = {
      title: it.title,
      company: it.company,
      link: it.link || null,
      postedAt: it.postedAt || null,
      firstSeen: state.seen[itemKey(it)]?.firstSeen || isoNow,
    };
  }
  state.group = group;
  state.updatedAt = isoNow;
  if (!existsSync(STATE_DIR)) mkdirSync(STATE_DIR, { recursive: true });
  writeFileSync(statePath(group), JSON.stringify(state, null, 2) + '\n', 'utf8');
  return state;
}
