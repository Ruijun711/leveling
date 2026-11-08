/**
 * 學習精靈 · 第 1 週 Python 練習（選擇題版，concierge 測試）
 * 在 https://script.google.com 執行 createPracticeForm()，會在你的 Google 雲端硬碟建立：
 *   1. 作答用的 Google 表單（5 題選擇題）
 *   2. 連結的 Google 試算表，內含「表單回應」與「經驗值」兩個工作表
 * 題目內容對應 practice-questions.md，修改時兩邊要一起改。
 *
 * 批改方式：自動。「經驗值」工作表會比對答案，每題只算每個人「第一次作答」的答案。
 * 「經驗值」工作表只顯示結果，不顯示答案；用「發布到網路」只發布這一頁給同學看。
 */

var XP_PER_PROBLEM = 10;   // 一題 10 點（暫定）
var XP_PER_LEVEL = 20;     // 20 點升一級：答對 2 題升 1 級、4 題升 2 級（暫定，Owner 2026-11-05）
var XP_ROWS = 20;          // 經驗值表預留的人數列

var PROBLEMS = [
  {
    title: '第 1 題 · 字串與數字',
    code: 'x = "5"\ny = 2\nprint(x * y)',
    choices: ['10', '55', '7', '會出現錯誤'],
    answer: '55'
  },
  {
    title: '第 2 題 · 縮排',
    code: 'for i in range(3):\n    print("A")\nprint("B")',
    choices: ['印出 A、A、A，最後印出 1 次 B', 'A 和 B 交替印 3 次', '印出 A、A、A、B、B、B', '只印出 B'],
    answer: '印出 A、A、A，最後印出 1 次 B'
  },
  {
    title: '第 3 題 · if / elif',
    code: 'score = 85\nif score >= 60:\n    print("及格")\nelif score >= 80:\n    print("良好")\nelse:\n    print("不及格")',
    choices: ['及格', '良好', '及格 和 良好 都會印出', '不及格'],
    answer: '及格'
  },
  {
    title: '第 4 題 · range',
    code: 'print(list(range(1, 5)))',
    choices: ['[1, 2, 3, 4, 5]', '[0, 1, 2, 3, 4]', '[1, 2, 3, 4]', '[2, 3, 4, 5]'],
    answer: '[1, 2, 3, 4]'
  },
  {
    title: '第 5 題 · list',
    code: 'nums = [10, 20, 30]\nnums.append(40)\nprint(nums[1] + nums[-1])',
    choices: ['50', '60', '70', '會出現錯誤'],
    answer: '60'
  }
];

function createPracticeForm() {
  // ---------- 表單 ----------
  var form = FormApp.create('學習精靈 · 第 1 週 Python 練習');
  form.setDescription(
    '5 題 Python 選擇題，每題都是「這段程式會印出什麼？」\n\n' +
    '・答對一題得 ' + XP_PER_PROBLEM + ' 點經驗值，' + XP_PER_LEVEL + ' 點升一級\n' +
    '・每題只算你「第一次作答」的答案，答錯就沒有這題的分數，請想清楚再交\n' +
    '・可以分好幾次交，每次只做幾題也可以；沒做的題目留空就好\n\n' +
    '每次都要填同一個暱稱，經驗值才會累積在一起。'
  );
  form.setCollectEmail(false);
  form.setAllowResponseEdits(false);

  form.addTextItem()
    .setTitle('你的暱稱')
    .setHelpText('每次都填同一個暱稱，經驗值才會累積在一起')
    .setRequired(true);

  PROBLEMS.forEach(function (p) {
    form.addMultipleChoiceItem()
      .setTitle(p.title)
      .setHelpText(p.code + '\n\n這段程式會印出什麼？')
      .setChoiceValues(p.choices)
      .setRequired(false);
  });

  form.addParagraphTextItem()
    .setTitle('（選填）有哪一題不太確定？卡在哪裡？')
    .setRequired(false);

  // ---------- 試算表 ----------
  var ss = SpreadsheetApp.create('學習精靈 · 第 1 週經驗值');
  ss.getSheets()[0].setName('經驗值');
  form.setDestination(FormApp.DestinationType.SPREADSHEET, ss.getId());
  SpreadsheetApp.flush();

  // 重新開啟，才拿得到連結表單後新增的回應工作表
  ss = SpreadsheetApp.openById(ss.getId());
  var responseSheet = findResponseSheet_(ss);
  if (!responseSheet) {
    throw new Error('找不到表單回應工作表，請重新執行一次。');
  }

  // 回應欄位：A 時間戳記、B 暱稱、C～G 第 1～5 題、H 選填說明
  buildXpSheet_(ss.getSheetByName('經驗值'), responseSheet.getName());

  Logger.log('編輯表單：' + form.getEditUrl());
  Logger.log('發給同學的連結：' + form.getPublishedUrl());
  Logger.log('經驗值試算表：' + ss.getUrl());
}

function findResponseSheet_(ss) {
  var sheets = ss.getSheets();
  for (var i = 0; i < sheets.length; i++) {
    if (sheets[i].getFormUrl()) {
      return sheets[i];
    }
  }
  return null;
}

function colLetter_(n) {
  var s = '';
  while (n > 0) {
    var m = (n - 1) % 26;
    s = String.fromCharCode(65 + m) + s;
    n = Math.floor((n - 1) / 26);
  }
  return s;
}

function buildXpSheet_(xp, responseSheetName) {
  var rs = "'" + responseSheetName + "'!";
  var nick = 'TRIM(' + rs + 'B2:B)';

  xp.getRange(1, 1, 1, 6)
    .setValues([['暱稱', '作答題數', '答對題數', '經驗值', '等級', '距離下一級']])
    .setFontWeight('bold');
  xp.setFrozenRows(1);

  // A2：自動列出所有交過的暱稱（去掉前後空白、不重複）
  xp.getRange('A2').setFormula(
    '=IFERROR(UNIQUE(FILTER(' + nick + ',' + rs + 'B2:B<>"")),"")'
  );

  for (var r = 2; r < 2 + XP_ROWS; r++) {
    var a = 'A' + r;
    var answered = [];
    var correct = [];

    PROBLEMS.forEach(function (p, i) {
      var col = rs + colLetter_(3 + i) + '2:' + colLetter_(3 + i);
      var key = '"' + p.answer.replace(/"/g, '""') + '"';
      // 這題有沒有作答過
      answered.push('--(SUMPRODUCT((' + nick + '=' + a + ')*(' + col + '<>""))>0)');
      // 這題「第一次作答」是否答對
      correct.push('--IFERROR(INDEX(FILTER(' + col + ',' + nick + '=' + a + ',' + col + '<>""),1)=' + key + ',FALSE)');
    });

    xp.getRange(r, 2, 1, 5).setFormulas([[
      '=IF(' + a + '="","",' + answered.join('+') + ')',
      '=IF(' + a + '="","",' + correct.join('+') + ')',
      '=IF(' + a + '="","",C' + r + '*' + XP_PER_PROBLEM + ')',
      '=IF(' + a + '="","",INT(D' + r + '/' + XP_PER_LEVEL + '))',
      '=IF(' + a + '="","",' + XP_PER_LEVEL + '-MOD(D' + r + ',' + XP_PER_LEVEL + '))'
    ]]);
  }

  xp.autoResizeColumns(1, 6);
}
