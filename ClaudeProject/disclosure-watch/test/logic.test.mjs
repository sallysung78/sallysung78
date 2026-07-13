// 네트워크 불필요 로직 검증: IT필터 + 신규(diff) + 리포트.
// 실행: node --test
import { test } from 'node:test';
import assert from 'node:assert/strict';
import { classifyIT } from '../lib/keywords.mjs';
import { computeNew, itemKey } from '../lib/state.mjs';
import { renderMarkdown } from '../lib/report.mjs';

test('classifyIT: IT 공고를 잡아낸다', () => {
  assert.equal(classifyIT('차세대 정보시스템 구축 사업 입찰 공고').isIT, true);
  assert.equal(classifyIT('클라우드 인프라 유지보수 용역').isIT, true);
  assert.equal(classifyIT('정보보호 관제 솔루션 도입').isIT, true);
});

test('classifyIT: 비IT 공고는 거른다', () => {
  assert.equal(classifyIT('본점 건물 청소용역 입찰 공고').isIT, false);
  assert.equal(classifyIT('임직원 기념품 구매').isIT, false);
  assert.equal(classifyIT('신년 행사대행 업체 선정').isIT, false);
});

test('classifyIT: 매칭 키워드를 보고한다', () => {
  const r = classifyIT('AI 챗봇 고도화 개발 사업');
  assert.ok(r.matched.includes('ai'));
  assert.ok(r.matched.includes('챗봇'));
  assert.ok(r.matched.includes('개발'));
});

test('computeNew: 이미 본 항목은 제외, 신규만 반환', () => {
  const seen = {};
  const old = { company: 'KB국민은행', title: 'A시스템 구축', link: 'https://x/1' };
  seen[itemKey(old)] = { firstSeen: 't0' };
  const state = { seen };
  const items = [
    old,
    { company: 'KB국민은행', title: 'B플랫폼 개발', link: 'https://x/2' },
  ];
  const fresh = computeNew(state, items);
  assert.equal(fresh.length, 1);
  assert.equal(fresh[0].link, 'https://x/2');
});

test('computeNew: 링크 없으면 회사+제목으로 식별', () => {
  const a = { company: '우리은행', title: '망분리 고도화' };
  const b = { company: '우리은행', title: '망분리 고도화' };
  assert.equal(itemKey(a), itemKey(b));
  const fresh = computeNew({ seen: { [itemKey(a)]: {} } }, [b]);
  assert.equal(fresh.length, 0);
});

test('renderMarkdown: 신규 0건이면 안내 문구', () => {
  const md = renderMarkdown({
    date: '2026-06-30',
    windowKst: 'w',
    groups: [
      { group: 'KB', label: 'KB금융그룹', items: [] },
      { group: 'WOORI', label: '우리금융그룹', items: [] },
    ],
  });
  assert.match(md, /신규 IT 공고: \*\*0건\*\*/);
  assert.match(md, /신규 IT 공고가 없습니다/);
});

test('renderMarkdown: 항목을 표로 렌더', () => {
  const md = renderMarkdown({
    date: '2026-06-30',
    windowKst: 'w',
    groups: [
      {
        group: 'KB',
        label: 'KB금융그룹',
        items: [
          { company: 'KB라이프', title: '데이터센터 이전 구축', postedAt: '2026-06-30', link: 'https://x/9', verified: true },
        ],
      },
      { group: 'WOORI', label: '우리금융그룹', items: [] },
    ],
  });
  assert.match(md, /데이터센터 이전 구축/);
  assert.match(md, /\[열기\]\(https:\/\/x\/9\)/);
  assert.match(md, /✅/);
});
