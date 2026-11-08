/**
 * 學習精靈 · 程式練習習慣問卷
 * 在 https://script.google.com 執行 createForm()，會在你的 Google 雲端硬碟建立表單。
 * 題目內容對應 questionnaire.md。
 */
function createForm() {
  var form = FormApp.create('學習精靈 · 程式練習習慣問卷');
  form.setDescription(
    '嗨！我正在做一個幫助大家持續練習寫程式的專案，想了解你平常練習的真實情況。' +
    '沒有標準答案，照實回答就好。問卷匿名。謝謝你！\n\n' +
    '預計作答時間：約 5 分鐘'
  );
  form.setCollectEmail(false);
  form.setProgressBar(true);

  // A. 基本狀態
  form.addSectionHeaderItem().setTitle('A. 基本狀態');

  form.addMultipleChoiceItem()
    .setTitle('1. 你目前的程式學習狀態是？')
    .setChoiceValues(['aipe05 課程學員', '其他課程學員', '自學中', '已在工作，下班後進修'])
    .showOtherOption(true)
    .setRequired(true);

  form.addMultipleChoiceItem()
    .setTitle('2. 你學寫程式大約多久了？')
    .setChoiceValues(['未滿 3 個月', '3–6 個月', '6 個月–1 年', '1 年以上'])
    .setRequired(true);

  // B. 練習行為
  form.addSectionHeaderItem().setTitle('B. 練習行為');

  form.addMultipleChoiceItem()
    .setTitle('3. 過去兩週，除了課堂作業之外，你主動寫練習題（例如 LeetCode）大約幾次？')
    .setChoiceValues(['0 次', '1–2 次', '3–5 次', '6 次以上'])
    .setRequired(true);

  form.addMultipleChoiceItem()
    .setTitle('4. 下面哪一句最像你？')
    .setChoiceValues([
      '我有固定的練習習慣，大致都能維持',
      '有空才練，時間不固定',
      '曾經有在練，但漸漸停下來了',
      '幾乎沒有主動練習過'
    ])
    .setRequired(true);

  form.addCheckboxItem()
    .setTitle('5. 練習時卡住了，你通常會怎麼做？')
    .setHelpText('可複選')
    .setChoiceValues(['問 AI', '上網搜尋', '問同學或老師', '直接看解答', '先放著，之後再說', '就不做了'])
    .showOtherOption(true)
    .setRequired(true);

  form.addMultipleChoiceItem()
    .setTitle('6. 一題卡多久，你會開始想放棄？')
    .setChoiceValues(['10 分鐘內', '10–30 分鐘', '30–60 分鐘', '1 小時以上', '不太會想放棄'])
    .setRequired(true);

  // C. 你的真實經驗
  form.addSectionHeaderItem()
    .setTitle('C. 你的真實經驗')
    .setHelpText('請用自己的話寫，想到什麼寫什麼就好。');

  form.addParagraphTextItem()
    .setTitle('7. 請描述最近一次你「不想再練了」的情況：當時在做什麼題目、發生了什麼事、心裡在想什麼？')
    .setRequired(true);

  form.addParagraphTextItem()
    .setTitle('8. 練習寫程式時，最讓你挫折的是什麼？')
    .setRequired(true);

  // D. 動力來源
  form.addSectionHeaderItem().setTitle('D. 動力來源');

  form.addCheckboxItem()
    .setTitle('9. 什麼會讓你更願意繼續練習？')
    .setHelpText('最多選 3 項')
    .setChoiceValues([
      '看得到自己的進步',
      '和同學一起練或互相比較',
      '完成後有獎勵',
      '有人提醒或督促',
      '題目本身有趣',
      '練習內容和自己想做的作品有關'
    ])
    .showOtherOption(true)
    .setValidation(FormApp.createCheckboxValidation().requireSelectAtMost(3).build())
    .setRequired(true);

  form.addScaleItem()
    .setTitle('10. 想像一個工具：每完成一次練習，你的角色就能獲得經驗值；升級後可以用技能點數學技能；' +
              '到特定等級還能挑戰 Boss、有機會拿到寶物。你對這個工具有多大興趣？')
    .setBounds(1, 5)
    .setLabels('完全沒興趣', '非常有興趣')
    .setRequired(true);

  form.addParagraphTextItem()
    .setTitle('11. 承上題，為什麼會給這個分數？')
    .setRequired(true);

  form.addParagraphTextItem()
    .setTitle('12. 你用過有「streak、badge、level」這類設計的學習工具嗎？如果用過，後來還有在用嗎？為什麼？')
    .setRequired(false);

  Logger.log('編輯表單：' + form.getEditUrl());
  Logger.log('發給同學的連結：' + form.getPublishedUrl());
}
