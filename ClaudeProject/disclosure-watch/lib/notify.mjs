// 결과 알림 — GitHub 이슈 본문/이메일 페이로드 생성 + (옵션) 발송.
// 발송은 환경에 따라 자격증명/네트워크가 필요하므로 "페이로드 생성"과 "실제 전송"을 분리한다.
//
// - GitHub 이슈: 이 저장소 범위에서 mcp__github__issue_write 로 오케스트레이터(Claude)가 생성하는 것을 권장.
//   (스크립트에서 직접 만들려면 GITHUB_TOKEN + REST 호출 필요)
// - 이메일: SMTP 또는 메일 API. 자격증명이 없으면 전송을 건너뛰고 페이로드만 반환한다.

/** 이메일 제목/본문(plain+markdown) 페이로드 생성 */
export function buildEmail({ to, date, markdown, totalCount }) {
  return {
    to: to || process.env.DISCLOSURE_MAIL_TO || 'hsung@redhat.com',
    subject: `[금융사 IT공고] ${date} 신규 ${totalCount}건`,
    text: markdown,
    markdown,
  };
}

/**
 * SMTP 환경변수가 있으면 nodemailer 로 전송. 없으면 {sent:false, reason} 반환.
 * 필요한 env: SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS, (옵션) SMTP_FROM
 */
export async function sendEmail(payload) {
  const host = process.env.SMTP_HOST;
  if (!host) return { sent: false, reason: 'SMTP_HOST 미설정 — 전송 생략(페이로드만 생성)' };
  let nodemailer;
  try {
    nodemailer = (await import('nodemailer')).default;
  } catch {
    return { sent: false, reason: 'nodemailer 미설치 — `npm i nodemailer` 필요' };
  }
  const transport = nodemailer.createTransport({
    host,
    port: Number(process.env.SMTP_PORT || 587),
    secure: Number(process.env.SMTP_PORT) === 465,
    auth: process.env.SMTP_USER
      ? { user: process.env.SMTP_USER, pass: process.env.SMTP_PASS }
      : undefined,
  });
  const info = await transport.sendMail({
    from: process.env.SMTP_FROM || process.env.SMTP_USER,
    to: payload.to,
    subject: payload.subject,
    text: payload.text,
  });
  return { sent: true, messageId: info.messageId };
}
