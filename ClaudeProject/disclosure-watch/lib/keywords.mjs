// IT 공고 판별 로직 (네트워크 불필요, 순수 함수 — 테스트 대상)
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const __dir = dirname(fileURLToPath(import.meta.url));
const cfg = JSON.parse(readFileSync(join(__dir, '..', 'it_keywords.json'), 'utf8'));

const INCLUDE = cfg.include.map((k) => k.toLowerCase());
const EXCLUDE = cfg.exclude.map((k) => k.toLowerCase());

/**
 * 제목(+선택적 본문)이 IT 관련 공고인지 판별한다.
 * @param {string} title
 * @param {string} [body]
 * @returns {{ isIT: boolean, matched: string[], excluded: string[] }}
 */
export function classifyIT(title, body = '') {
  const hay = `${title} ${body}`.toLowerCase();
  const excluded = EXCLUDE.filter((k) => hay.includes(k));
  const matched = INCLUDE.filter((k) => hay.includes(k));
  // IT 포함 키워드가 하나라도 잡히면 IT 후보로 본다. exclude 는 참고용으로만 노출하고
  // 자동 탈락시키지 않는다(예: "보안경비" 등 오탈락 방지). 최종 판단은 검증 에이전트/사람.
  return { isIT: matched.length > 0, matched, excluded };
}

export { INCLUDE, EXCLUDE };
