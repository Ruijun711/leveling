/**
 * 學習精靈 · 階段 0 Python 練習（2 週、分 4 次出題，驗證「持續練習」）
 *
 * 使用方式（在 https://script.google.com 新增一個專案，貼上本檔全部內容）：
 *   1. 執行 createStage0Form()：建立表單（測驗模式）和試算表。只執行一次。
 *      執行紀錄（Logger）會印出「發給同學的連結」，請記到 連結.txt。
 *   2. 依出題表執行（每次會在同一個表單加 3 題，並更新試算表公式）：
 *        第 1 週週一 → releaseBatch1()     第 1 週週四 → releaseBatch2()
 *        第 2 週週一 → releaseBatch3()     第 2 週週四 → releaseBatch4()
 *   3. 只把「經驗值」工作表「發布到網路」給同學看；「統計」工作表只給 Avi 看
 *      （裡面有學程式多久、每週交卷次數）。
 *   4. 在「統計」工作表 H2 填入「答應參加的人數」，H4 才會算出 G1 比例。
 *
 * 規則（Owner 決定 2026-11-08，見 roadmap.md §3「階段 0 細節」）：
 *   一題 10 點；等級從 1 級開始 = 1 + INT(經驗值 / 20)；每題只算第一次作答。
 *   G1：從第 1 次出題那天起算，第 1～7 天是第 1 週、第 8～14 天是第 2 週，
 *       兩週都至少交卷 1 次的人 ÷ 答應參加的人數。
 *       「交卷」指至少答 1 題；只填暱稱的空白交卷不算（Owner 決定 2026-11-08）。
 *   暱稱不分大小寫、忽略前後空白：Avi 和 avi 算同一人（code review F-002）。
 *
 * 題目內容對應 practice-questions-stage0.md，修改時兩邊要一起改。
 */

var XP_PER_PROBLEM = 10;
var XP_PER_LEVEL = 20;
var XP_ROWS = 60;          // 預留的人數列；暱稱超過這個數量時，執行紀錄會提醒

var NICK_TITLE = '你的暱稱';
var EXP_TITLE = '你學寫程式大約多久了？';
var NOTE_TITLE = '（選填）有哪一題不太確定？卡在哪裡？';

var BATCHES = [
  // 第 1 次：第 1 週週一
  [
    {
      title: 'A1 · 字串與數字',
      code: 'a = "3"\nb = "4"\nprint(a + b)',
      choices: ['7', '34', '12', '會出現錯誤'],
      answer: '34',
      explanation: '"3" 和 "4" 都是字串，+ 是把兩段字串接起來，不是數學相加。'
    },
    {
      title: 'B1 · range 和 for',
      code: 'for i in range(3):\n    print(i)',
      choices: ['0 1 2 3', '1 2 3', '3', '0 1 2'],
      answer: '0 1 2',
      explanation: 'range(3) 從 0 開始、不包含 3，所以是 0、1、2（每個數字印一行）。'
    },
    {
      title: 'C1 · if/elif',
      code: 'x = 7\nif x > 10:\n    print("A")\nelif x > 5:\n    print("B")\nelif x > 3:\n    print("C")\nelse:\n    print("D")',
      choices: ['C', 'B', 'B 和 C', 'D'],
      answer: 'B',
      explanation: '由上往下檢查，x > 5 第一個成立就印 B，後面的 elif、else 都不會再檢查。'
    }
  ],
  // 第 2 次：第 1 週週四
  [
    {
      title: 'D1 · list 索引',
      code: 'fruits = ["蘋果", "香蕉", "橘子"]\nprint(fruits[1])',
      choices: ['蘋果', '香蕉', '橘子', '會出現錯誤'],
      answer: '香蕉',
      explanation: '索引從 0 開始，[1] 是第 2 個。'
    },
    {
      title: 'A2 · 字串與數字',
      code: 'age = "18"   # input() 拿到的都是字串\nprint(age + 1)',
      choices: ['19', '181', '會出現錯誤', '18'],
      answer: '會出現錯誤',
      explanation: '字串不能直接加數字（TypeError），要先用 int(age) 轉成數字。'
    },
    {
      title: 'B2 · range 和 for',
      code: 'total = 0\nfor i in range(1, 4):\n    total = total + i\nprint(total)',
      choices: ['10', '3', '6', '4'],
      answer: '6',
      explanation: 'range(1, 4) 是 1、2、3（不包含 4），加起來是 6。'
    }
  ],
  // 第 3 次：第 2 週週一
  [
    {
      title: 'C2 · if/elif',
      code: 'x = 7\nif x > 5:\n    print("A")\nif x > 3:\n    print("B")',
      choices: ['先印出 A，再印出 B', '只印出 A', '只印出 B', '什麼都不印'],
      answer: '先印出 A，再印出 B',
      explanation: '這是兩個獨立的 if，不是 elif，兩個都會檢查，兩個都成立。'
    },
    {
      title: 'D2 · list 索引',
      code: 'nums = [5, 10, 15]\nprint(nums[3])',
      choices: ['15', '5', '會出現錯誤', '30'],
      answer: '會出現錯誤',
      explanation: '3 個元素的索引是 0～2，[3] 超出範圍（IndexError）。'
    },
    {
      title: 'A3 · 字串與數字',
      code: 'n = int("7")\nprint(n * 3)',
      choices: ['21', '777', '會出現錯誤', '73'],
      answer: '21',
      explanation: 'int("7") 已經把字串轉成數字 7，所以是數學相乘。對照：如果是 "7" * 3，結果會是 777。'
    }
  ],
  // 第 4 次：第 2 週週四
  [
    {
      title: 'B3 · range 和 for',
      code: 'print(list(range(0, 10, 3)))',
      choices: ['[0, 3, 6, 9]', '[3, 6, 9]', '[0, 3, 6]', '[0, 3, 6, 9, 12]'],
      answer: '[0, 3, 6, 9]',
      explanation: '從 0 開始每次加 3，到 10 之前停下，不包含 10。'
    },
    {
      title: 'C3 · if/elif',
      code: 'x = 2\nif x > 5:\n    print("A")\n    print("B")\nprint("C")',
      choices: ['只印出 C', 'A、B、C', 'B、C', '什麼都不印'],
      answer: '只印出 C',
      explanation: '有縮排的兩行都在 if 裡面，條件不成立就都不執行；print("C") 沒有縮排，一定會執行。'
    },
    {
      title: 'D3 · list 索引',
      code: 'nums = [1, 2, 3, 4, 5]\nprint(nums[-2])',
      choices: ['2', '5', '會出現錯誤', '4'],
      answer: '4',
      explanation: '負數索引從後面數，[-1] 是最後一個，[-2] 是倒數第 2 個。'
    }
  ]
];

// ---------- 1. 建立表單和試算表（只執行一次） ----------

function createStage0Form() {
  var props = PropertiesService.getScriptProperties();
  if (props.getProperty('FORM_ID')) {
    throw new Error('已經建立過表單了。要重來，請先到「專案設定 → 指令碼屬性」刪除 FORM_ID、SHEET_ID、RELEASED、START_DATE。');
  }

  var form = FormApp.create('學習精靈 · 階段 0 Python 練習');
  form.setIsQuiz(true);
  form.setDescription(
    'Python 選擇題，每題都是「這段程式會印出什麼？」\n\n' +
    '・接下來 2 週會分 4 次加新題目（每週一、四各 3 題），都用這個連結\n' +
    '・答對一題得 ' + XP_PER_PROBLEM + ' 點經驗值，' + XP_PER_LEVEL + ' 點升一級，從 1 級開始\n' +
    '・每題只算你「第一次作答」的答案；已經做過的題目留空就好\n' +
    '・交卷後可以看到每題的對錯和解說\n\n' +
    '每次都要填「完全一樣」的暱稱（大小寫、空白都要一樣），經驗值才會累積在一起。請不要用真名，因為暱稱和經驗值會公開給同學看。'
  );
  form.setCollectEmail(false);
  form.setAllowResponseEdits(false);

  form.addTextItem()
    .setTitle(NICK_TITLE)
    .setHelpText('請不要用真名；每次都填完全一樣的暱稱（大小寫、空白都要一樣）')
    .setRequired(true);

  form.addMultipleChoiceItem()
    .setTitle(EXP_TITLE)
    .setChoiceValues(['未滿 3 個月', '3–6 個月', '6 個月–1 年', '1 年以上'])
    .setRequired(true);

  form.addParagraphTextItem()
    .setTitle(NOTE_TITLE)
    .setRequired(false);

  var ss = SpreadsheetApp.create('學習精靈 · 階段 0 經驗值');
  ss.getSheets()[0].setName('經驗值');
  ss.insertSheet('統計');
  form.setDestination(FormApp.DestinationType.SPREADSHEET, ss.getId());

  props.setProperties({
    FORM_ID: form.getId(),
    SHEET_ID: ss.getId(),
    RELEASED: '0'
  });

  Logger.log('編輯表單：' + form.getEditUrl());
  Logger.log('發給同學的連結：' + form.getPublishedUrl());
  Logger.log('經驗值試算表：' + ss.getUrl());
  Logger.log('下一步：第 1 週週一執行 releaseBatch1()');
}

// ---------- 2. 分次出題 ----------

function releaseBatch1() { releaseBatch_(1); }
function releaseBatch2() { releaseBatch_(2); }
function releaseBatch3() { releaseBatch_(3); }
function releaseBatch4() { releaseBatch_(4); }

/** 公式壞掉或手動改過工作表時，可以執行這個重建公式。 */
function rebuildSheets() {
  var props = PropertiesService.getScriptProperties();
  var released = Number(props.getProperty('RELEASED') || '0');
  if (released < 1) {
    throw new Error('還沒出題，不需要重建。');
  }
  buildSheets_(SpreadsheetApp.openById(props.getProperty('SHEET_ID')), released);
}

function releaseBatch_(n) {
  var props = PropertiesService.getScriptProperties();
  var formId = props.getProperty('FORM_ID');
  if (!formId) {
    throw new Error('還沒建立表單，請先執行 createStage0Form()。');
  }
  var released = Number(props.getProperty('RELEASED') || '0');
  if (n !== released + 1) {
    throw new Error('目前已出到第 ' + released + ' 次，下一次應該執行 releaseBatch' + (released + 1) + '()。');
  }

  var form = FormApp.openById(formId);
  var ss = SpreadsheetApp.openById(props.getProperty('SHEET_ID'));
  BATCHES[n - 1].forEach(function (p) {
    addProblem_(form, p);
  });

  if (n === 1) {
    // 用試算表的時區，和交卷時間一致（code review F-005）
    props.setProperty('START_DATE',
      Utilities.formatDate(new Date(), ss.getSpreadsheetTimeZone(), 'yyyy-MM-dd'));
  }
  props.setProperty('RELEASED', String(n));

  SpreadsheetApp.flush();
  buildSheets_(ss, n);

  Logger.log('已加上第 ' + n + ' 次的 3 題：' +
    BATCHES[n - 1].map(function (p) { return p.title; }).join('、'));
}

function addProblem_(form, p) {
  // 上次執行到一半出錯、重新執行時，已經加過的題目就跳過（code review F-004）
  var existing = form.getItems();
  for (var k = 0; k < existing.length; k++) {
    if (existing[k].getTitle() === p.title) {
      Logger.log('「' + p.title + '」已經在表單裡，跳過。');
      return;
    }
  }

  var item = form.addMultipleChoiceItem();
  item.setTitle(p.title)
    .setHelpText(p.code + '\n\n這段程式會印出什麼？')
    .setChoices(p.choices.map(function (c) {
      return item.createChoice(c, c === p.answer);
    }))
    .setPoints(1)
    .setRequired(false);

  item.setFeedbackForCorrect(
    FormApp.createFeedback().setText('答對了！' + p.explanation).build());
  item.setFeedbackForIncorrect(
    FormApp.createFeedback().setText('正確答案是「' + p.answer + '」。' + p.explanation).build());

  // 新題目放在「選填」題的前面
  var items = form.getItems();
  for (var i = 0; i < items.length; i++) {
    if (items[i].getTitle() === NOTE_TITLE) {
      form.moveItem(item.getIndex(), i);
      break;
    }
  }
}

// ---------- 3. 試算表公式 ----------

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

function buildSheets_(ss, released) {
  var responseSheet = findResponseSheet_(ss);
  if (!responseSheet) {
    throw new Error('找不到表單回應工作表。請稍等幾秒後執行 rebuildSheets()。');
  }

  // 用標題找欄位（測驗模式會多一欄「分數」，新題目會加在最後面，所以不能寫死欄位）
  var lastCol = responseSheet.getLastColumn();
  var header = responseSheet.getRange(1, 1, 1, lastCol).getValues()[0];
  var rs = "'" + responseSheet.getName() + "'!";
  function col(title) {
    var idx = header.indexOf(title);
    if (idx < 0) {
      throw new Error('回應工作表找不到「' + title + '」這一欄。請稍等幾秒後執行 rebuildSheets()。');
    }
    var L = colLetter_(idx + 1);
    return rs + L + '2:' + L;
  }

  var tsCol = rs + 'A2:A';
  var nickRaw = col(NICK_TITLE);
  // 不分大小寫：UNIQUE 分大小寫、= 不分，兩邊都轉小寫才不會一人變兩列（code review F-002）
  var nick = 'LOWER(TRIM(' + nickRaw + '))';
  var expCol = col(EXP_TITLE);
  var problems = [];
  for (var b = 0; b < released; b++) {
    problems = problems.concat(BATCHES[b]);
  }
  // 這次交卷至少答了 1 題（空白交卷不算「交卷」，Owner 決定 2026-11-08）
  var answeredAny = '((' + problems.map(function (p) {
    return '(' + col(p.title) + '<>"")';
  }).join('+') + ')>0)';
  var uniqueNick = '=IFERROR(UNIQUE(FILTER(' + nick + ',' + nickRaw + '<>"")),"")';

  // ----- 經驗值（發布給同學看）-----
  var xp = ss.getSheetByName('經驗值');
  xp.clear();
  xp.getRange(1, 1, 1, 6)
    .setValues([['暱稱', '已作答題數', '答對題數', '經驗值', '等級', '距離下一級']])
    .setFontWeight('bold');
  xp.setFrozenRows(1);
  xp.getRange('A2').setFormula(uniqueNick);

  for (var r = 2; r < 2 + XP_ROWS; r++) {
    var a = 'A' + r;
    var answered = [];
    var correct = [];
    problems.forEach(function (p) {
      var c = col(p.title);
      var key = '"' + p.answer.replace(/"/g, '""') + '"';
      answered.push('--(SUMPRODUCT((' + nick + '=' + a + ')*(' + c + '<>""))>0)');
      // 第一次作答是否答對；TO_TEXT 避免「34」這類答案被試算表當成數字
      correct.push('--IFERROR(TO_TEXT(INDEX(FILTER(' + c + ',' + nick + '=' + a + ',' + c + '<>""),1))=' + key + ',FALSE)');
    });
    xp.getRange(r, 2, 1, 5).setFormulas([[
      '=IF(' + a + '="","",' + answered.join('+') + ')',
      '=IF(' + a + '="","",' + correct.join('+') + ')',
      '=IF(' + a + '="","",C' + r + '*' + XP_PER_PROBLEM + ')',
      '=IF(' + a + '="","",1+INT(D' + r + '/' + XP_PER_LEVEL + '))',
      '=IF(' + a + '="","",' + XP_PER_LEVEL + '-MOD(D' + r + ',' + XP_PER_LEVEL + '))'
    ]]);
  }
  xp.autoResizeColumns(1, 6);

  // ----- 統計（只給 Avi 看）-----
  var st = ss.getSheetByName('統計');
  var participants = st.getRange('H2').getValue();   // Avi 手動填的人數，重建時保留
  st.clear();
  st.getRange(1, 1, 1, 5)
    .setValues([['暱稱', '學程式多久', '第 1 週交卷次數（至少答 1 題）', '第 2 週交卷次數（至少答 1 題）', '兩週都有交卷']])
    .setFontWeight('bold');
  st.setFrozenRows(1);
  st.getRange('A2').setFormula(uniqueNick);

  for (var s = 2; s < 2 + XP_ROWS; s++) {
    var n = 'A' + s;
    st.getRange(s, 2, 1, 4).setFormulas([[
      '=IF(' + n + '="","",IFERROR(INDEX(FILTER(' + expCol + ',' + nick + '=' + n + '),1),""))',
      '=IF(' + n + '="","",SUMPRODUCT((' + nick + '=' + n + ')*(' + tsCol + '>=$H$1)*(' + tsCol + '<$H$1+7)*' + answeredAny + '))',
      '=IF(' + n + '="","",SUMPRODUCT((' + nick + '=' + n + ')*(' + tsCol + '>=$H$1+7)*(' + tsCol + '<$H$1+14)*' + answeredAny + '))',
      '=IF(' + n + '="","",IF(AND(C' + s + '>0,D' + s + '>0),"是","否"))'
    ]]);
  }

  st.getRange('G1:G6').setValues([
    ['第 1 次出題日'],
    ['答應參加的人數（Avi 填）'],
    ['兩週都有交卷的人數'],
    ['G1 比例（目標 ≥ 50%）'],
    ['第一次作答答對率（反指標，< 40% 要檢查）'],
    ['目前已出到第幾次']
  ]).setFontWeight('bold');
  // 用 DATEVALUE 確保 H1 是日期，不靠試算表自動轉換（code review F-006）
  st.getRange('H1')
    .setFormula('=DATEVALUE("' + PropertiesService.getScriptProperties().getProperty('START_DATE') + '")')
    .setNumberFormat('yyyy-mm-dd');
  st.getRange('H2').setValue(participants);
  st.getRange('H3').setFormula('=COUNTIF(E2:E,"是")');
  st.getRange('H4').setFormula('=IF(H2="","",H3/H2)').setNumberFormat('0%');
  st.getRange('H5').setFormula("=IFERROR(SUM('經驗值'!C2:C)/SUM('經驗值'!B2:B),\"\")").setNumberFormat('0%');
  st.getRange('H6').setValue(released);
  st.autoResizeColumns(1, 8);

  warnIfTooManyNicknames_(responseSheet, header);
}

/** 不同暱稱超過 XP_ROWS 時，多出來的人不會被計算，提醒 Avi（code review F-003）。 */
function warnIfTooManyNicknames_(responseSheet, header) {
  var lastRow = responseSheet.getLastRow();
  if (lastRow < 2) {
    return;
  }
  var values = responseSheet
    .getRange(2, header.indexOf(NICK_TITLE) + 1, lastRow - 1, 1)
    .getValues();
  var seen = {};
  var count = 0;
  values.forEach(function (row) {
    var key = String(row[0]).trim().toLowerCase();
    if (key && !seen[key]) {
      seen[key] = true;
      count++;
    }
  });
  if (count > XP_ROWS) {
    Logger.log('注意：目前有 ' + count + ' 個不同暱稱，超過 ' + XP_ROWS +
      ' 列，多出來的人不會被計算。請把 XP_ROWS 調大後執行 rebuildSheets()。');
  }
}
