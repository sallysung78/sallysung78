/**
 * Red Hat AI 디스커버리 세션 주요 아젠다 – 기존 구글폼에 질문 채우기
 *
 * 폼 파일은 이미 만들어져 있고(슬라이드 9페이지 QR이 이 폼을 가리킵니다),
 * 이 스크립트는 그 폼 안에 질문 2개를 넣고 게시 상태로 바꿉니다.
 *
 * 사용법 (1회, 약 1분)
 *  1. sallysung78@gmail.com으로 로그인한 브라우저에서 https://script.new 접속
 *  2. 기본 코드를 지우고 이 파일 전체를 붙여넣은 뒤 저장(Ctrl+S / ⌘+S)
 *  3. 상단 함수 선택 상자에서 fillForm 선택 → ▶ 실행
 *  4. 권한 요청 창 → 계정 선택 → "고급" → "…(안전하지 않음)으로 이동" → "허용"
 *     (본인이 방금 만든 스크립트라서 나오는 정상 안내입니다)
 *  5. 아래 실행 로그에 응답 링크와 편집 링크가 표시됩니다.
 *     폼 편집 화면에서 오른쪽 위 "게시" 상태만 확인하면 끝입니다.
 *
 * 두 번 실행해도 질문이 중복되지 않습니다(이미 질문이 있으면 건너뜁니다).
 */
const FORM_ID = '1B_nd0U4iS_OKhaE_fXZgMe4F00K-W82X2xRVmWmjRPM';
const FORM_TITLE = 'Red Hat AI 디스커버리 세션 주요 아젠다';
const AGENDA_OPTIONS = [
  '모델반입',
  '모델검증',
  '모델서빙',
  '접근제어',
  '운영관측',
  '거버넌스/보안',
  'AI모델지원/서비스',
];

function fillForm() {
  const form = FormApp.openById(FORM_ID);

  if (form.getItems().length > 0) {
    Logger.log('이미 질문이 ' + form.getItems().length + '개 있어서 추가하지 않았습니다.');
    Logger.log('편집 링크: ' + form.getEditUrl());
    return;
  }

  form.setTitle(FORM_TITLE);
  form.setDescription('관심 있는 아젠다를 모두 선택하고, 선택하신 이유를 적어주세요.');

  form.addCheckboxItem()
    .setTitle('관심 있는 아젠다를 선택해 주세요 (중복 선택 가능)')
    .setChoiceValues(AGENDA_OPTIONS)
    .setRequired(true);

  form.addParagraphTextItem()
    .setTitle('선택 이유')
    .setHelpText('위 아젠다를 선택하신 이유나 기대하는 내용을 자유롭게 적어주세요.');

  form.setAcceptingResponses(true);
  // 최근 Google Forms는 '게시' 상태여야 응답을 받을 수 있습니다.
  if (typeof form.setPublished === 'function') form.setPublished(true);

  Logger.log('완료. 질문 2개 추가됨.');
  Logger.log('응답 링크(참석자용, QR과 동일): https://docs.google.com/forms/d/' + FORM_ID + '/viewform');
  Logger.log('편집 링크(관리자용): ' + form.getEditUrl());
}
