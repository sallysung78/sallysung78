// 실제 브라우저(Playwright/Chromium)로 페이지를 렌더링해 텍스트+링크를 추출한다.
// 금융사 사이트는 단순 fetch(봇)를 403으로 막으므로 실제 브라우저가 필요하다.
//
// ⚠️ 전제조건: 이 환경/머신의 네트워크 정책이 대상 도메인 송신을 허용해야 한다.
//   - 클라우드 원격 환경(claude.ai/code)에서는 기본 정책이 외부 도메인을 차단할 수 있다.
//     egress 정책을 '제한 없음' 또는 대상 도메인 허용으로 설정해야 동작한다.
//   - 로컬 머신/사내망에서는 보통 그대로 동작한다.
//
// 프록시가 있으면(HTTPS_PROXY) 그 경유로 접속한다.
import { chromium } from 'playwright';

const PROXY = process.env.HTTPS_PROXY || process.env.https_proxy || null;
const UA =
  'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 ' +
  '(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36';

/**
 * @param {string} url
 * @param {object} [opt]
 * @param {number} [opt.waitMs=2500]  렌더 안정화 대기(ms)
 * @param {boolean} [opt.insecureProxyTLS=false]  프록시 CA 미신뢰로 막힐 때만 임시 사용
 * @returns {Promise<{url:string, finalUrl:string, status:number|null, title:string, text:string, links:Array<{text:string,href:string}>}>}
 */
export async function renderPage(url, opt = {}) {
  const { waitMs = 2500, insecureProxyTLS = false } = opt;
  const browser = await chromium.launch({
    headless: true,
    proxy: PROXY ? { server: PROXY } : undefined,
    args: ['--no-sandbox', '--disable-dev-shm-usage'],
  });
  try {
    const ctx = await browser.newContext({
      userAgent: UA,
      locale: 'ko-KR',
      timezoneId: 'Asia/Seoul',
      // 프록시가 TLS 재종단을 하는 환경에서 CA 미신뢰로 막히면(드묾) 임시 우회 옵션.
      ignoreHTTPSErrors: insecureProxyTLS,
    });
    const page = await ctx.newPage();
    const resp = await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 30000 });
    await page.waitForTimeout(waitMs);
    const title = await page.title();
    const text = await page.evaluate(() => document.body?.innerText || '');
    const links = await page.evaluate(() =>
      Array.from(document.querySelectorAll('a[href]')).map((a) => ({
        text: (a.textContent || '').trim().replace(/\s+/g, ' '),
        href: a.href,
      })),
    );
    return { url, finalUrl: page.url(), status: resp ? resp.status() : null, title, text, links };
  } finally {
    await browser.close();
  }
}
