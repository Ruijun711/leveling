# 學習精靈 · ADR-001 小試驗（Godot 4.7.2 + godot-sqlite v4.9）
#
# 要試的 4 件事（adr-001-desktop-framework.md §6）：
#   1. 哥布林出現在桌面上：透明背景、沒有邊框、蓋在其他視窗上面、會移動
#   2. 從按下「送出」到畫面顯示新的經驗值，不超過 3 秒（程式會印出花了幾毫秒）
#   3. 做到可以動要花多久（Avi 記錄）
#   4. 經驗值存進 SQLite，關掉程式重開後還在（ADR-002）
extends Control

# ---------- 規則（prd FR-2） ----------

const XP_PER_CORRECT := 10   # 答對得幾點經驗值（試驗：Avi 可以改這個數字看看）
const XP_PER_LEVEL := 20
const MAX_LEVEL := 9

# 題目：階段 0 的 A1（practice-questions-stage0.md）
const QUESTION := {
	"id": "A1",
	"concept": "字串與數字",
	"code": "a = \"3\"\nb = \"4\"\nprint(a + b)",
	"choices": ["7", "34", "12", "會出現錯誤"],
	"answer": "34",
	"explanation": "\"3\" 和 \"4\" 都是字串，+ 是把兩段字串接起來，不是數學相加。",
}

const GoblinWindow := preload("res://goblin_window.gd")

var db: SQLite
var db_file := ""
var status_label: Label
var result_label: Label
var timing_label: Label
var group := ButtonGroup.new()
var goblin: Window


static func level_from_xp(xp: int) -> int:
	# 等級 = min(9, 1 + INT(經驗值 / 20))（unit-test-stage1.md TC-001～006）
	assert(xp >= 0, "經驗值不能是負數")
	@warning_ignore("integer_division")
	return mini(MAX_LEVEL, 1 + xp / XP_PER_LEVEL)


# ---------- 本機資料：SQLite（ADR-002） ----------

func now_utc() -> String:
	return Time.get_datetime_string_from_system(true) + "Z"


func open_db() -> void:
	var dir := OS.get_environment("APPDATA").path_join("學習精靈-試驗")
	DirAccess.make_dir_recursive_absolute(dir)
	db_file = dir.path_join("godot-spike.db")
	db = SQLite.new()
	db.path = db_file
	db.verbosity_level = 0
	db.open_db()
	db.query("PRAGMA user_version;")
	if int(db.query_result[0]["user_version"]) == 0:
		# 欄位依 data-model.md §2（只取試驗用得到的）
		db.query("BEGIN TRANSACTION;")
		db.query("""CREATE TABLE player_progress (
			id INTEGER PRIMARY KEY CHECK (id = 1),
			xp INTEGER NOT NULL DEFAULT 0 CHECK (xp >= 0),
			created_at TEXT NOT NULL, updated_at TEXT NOT NULL,
			version INTEGER NOT NULL DEFAULT 1, deleted_at TEXT);""")
		db.query("""CREATE TABLE answer_record (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			question_id TEXT NOT NULL, concept TEXT NOT NULL, answered_at TEXT NOT NULL,
			selected_choice TEXT NOT NULL, is_correct INTEGER NOT NULL,
			is_first_attempt INTEGER NOT NULL, xp_gained INTEGER NOT NULL,
			created_at TEXT NOT NULL, updated_at TEXT NOT NULL,
			version INTEGER NOT NULL DEFAULT 1, deleted_at TEXT);""")
		var t := now_utc()
		db.query_with_bindings(
			"INSERT INTO player_progress (id, xp, created_at, updated_at) VALUES (1, 0, ?, ?);", [t, t])
		db.query("PRAGMA user_version = 1;")
		db.query("COMMIT;")


func get_xp() -> int:
	db.query("SELECT xp FROM player_progress WHERE id = 1;")
	return int(db.query_result[0]["xp"])


# 判斷對錯、算經驗值，作答紀錄和經驗值放在同一個 transaction 寫入（AC-10）。
# 回傳結果；有錯誤時回傳 {"error": "..."}
func submit_answer(selected: String) -> Dictionary:
	if selected == "":
		return {"error": "請先選一個答案"}  # AC-7
	if not QUESTION["choices"].has(selected):
		return {"error": "答案不在選項裡"}  # AC-7（Owner 決定 2026-11-08）

	var is_correct: bool = selected == QUESTION["answer"]
	db.query_with_bindings("SELECT COUNT(*) AS n FROM answer_record WHERE question_id = ?;", [QUESTION["id"]])
	var is_first: bool = int(db.query_result[0]["n"]) == 0
	var xp_gained := XP_PER_CORRECT if (is_correct and is_first) else 0

	var old_xp := get_xp()
	var new_xp := old_xp + xp_gained
	var t := now_utc()
	db.query("BEGIN TRANSACTION;")
	var ok := db.query_with_bindings(
		"""INSERT INTO answer_record (question_id, concept, answered_at, selected_choice,
			is_correct, is_first_attempt, xp_gained, created_at, updated_at)
			VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?);""",
		[QUESTION["id"], QUESTION["concept"], t, selected, int(is_correct), int(is_first), xp_gained, t, t])
	ok = ok and db.query_with_bindings(
		"UPDATE player_progress SET xp = ?, updated_at = ?, version = version + 1 WHERE id = 1;", [new_xp, t])
	if not ok:
		db.query("ROLLBACK;")  # 全部成功才算數
		return {"error": "進度沒有存到，請再送出一次。（" + db.error_message + "）"}
	db.query("COMMIT;")
	return {
		"is_correct": is_correct,
		"is_first_attempt": is_first,
		"xp_gained": xp_gained,
		"total_xp": new_xp,
		"level": level_from_xp(new_xp),
		"leveled_up": level_from_xp(new_xp) > level_from_xp(old_xp),
	}


func reset_progress() -> void:
	# 試驗用：清掉作答紀錄和經驗值，方便重來。
	db.query("BEGIN TRANSACTION;")
	db.query("DELETE FROM answer_record;")
	db.query_with_bindings("UPDATE player_progress SET xp = 0, updated_at = ? WHERE id = 1;", [now_utc()])
	db.query("COMMIT;")


# ---------- 畫面（試驗第 2 項） ----------

func _ready() -> void:
	open_db()
	print("[資料庫] %s，目前經驗值 %d" % [db_file, get_xp()])
	if "--selftest" in OS.get_cmdline_user_args():
		_selftest()
		return

	var theme_ := Theme.new()
	var font := SystemFont.new()
	font.font_names = PackedStringArray(["Microsoft JhengHei", "Microsoft YaHei"])
	theme_.default_font = font
	theme_.default_font_size = 16
	theme = theme_
	get_window().title = "學習精靈 · Godot 小試驗"

	goblin = GoblinWindow.new()
	add_child(goblin)

	var margin := MarginContainer.new()
	margin.set_anchors_preset(Control.PRESET_FULL_RECT)
	for side in ["left", "right", "top", "bottom"]:
		margin.add_theme_constant_override("margin_" + side, 12)
	add_child(margin)
	var box := VBoxContainer.new()
	margin.add_child(box)

	status_label = Label.new()
	status_label.add_theme_font_size_override("font_size", 20)
	box.add_child(status_label)

	var title := Label.new()
	title.text = "%s · %s　這段程式會印出什麼？" % [QUESTION["id"], QUESTION["concept"]]
	box.add_child(title)

	var code := Label.new()
	code.text = QUESTION["code"]
	var mono := SystemFont.new()
	mono.font_names = PackedStringArray(["Consolas"])
	code.add_theme_font_override("font", mono)
	var panel := PanelContainer.new()
	panel.add_child(code)
	box.add_child(panel)

	var letters := ["A", "B", "C", "D"]
	for i in QUESTION["choices"].size():
		var cb := CheckBox.new()
		cb.button_group = group
		cb.text = "(%s) %s" % [letters[i], QUESTION["choices"][i]]
		cb.set_meta("choice", QUESTION["choices"][i])
		box.add_child(cb)

	var buttons := HBoxContainer.new()
	box.add_child(buttons)
	for spec in [["送出", _on_submit], ["叫出哥布林", goblin.appear], ["重設試驗資料", _on_reset]]:
		var b := Button.new()
		b.text = spec[0]
		b.pressed.connect(spec[1])
		buttons.add_child(b)

	result_label = Label.new()
	result_label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	box.add_child(result_label)
	timing_label = Label.new()
	timing_label.modulate = Color(0.6, 0.6, 0.6)
	box.add_child(timing_label)
	var path_label := Label.new()
	path_label.text = "資料庫：" + db_file
	path_label.autowrap_mode = TextServer.AUTOWRAP_ARBITRARY
	path_label.add_theme_font_size_override("font_size", 12)
	box.add_child(path_label)

	refresh_status()


func refresh_status() -> void:
	var xp := get_xp()
	status_label.text = "經驗值 %d　·　等級 %d" % [xp, level_from_xp(xp)]


func _on_submit() -> void:
	var start := Time.get_ticks_usec()
	var pressed := group.get_pressed_button()
	var selected: String = pressed.get_meta("choice") if pressed else ""
	var r := submit_answer(selected)
	if r.has("error"):
		result_label.text = r["error"]
		return

	refresh_status()
	var msg := ""
	if r["is_correct"]:
		msg = "答對了！" + QUESTION["explanation"]
	else:
		msg = "正確答案是「%s」。%s" % [QUESTION["answer"], QUESTION["explanation"]]
	if not r["is_first_attempt"]:
		msg += "（不是第一次作答，不加經驗值）"
	elif r["xp_gained"] > 0:
		msg += "　+%d 經驗值" % r["xp_gained"]
	if r["leveled_up"]:
		msg += "　升到 %d 級！" % r["level"]
	result_label.text = msg

	# 量「送出 → 畫面真的畫出來」：等這一格畫完才停止計時（試驗第 2 項，NFR L1）
	await RenderingServer.frame_post_draw
	var ms := (Time.get_ticks_usec() - start) / 1000.0
	timing_label.text = "送出到畫面更新：%.1f 毫秒（標準：< 3000 毫秒）" % ms
	print("[計時] 送出到畫面更新 %.1f ms" % ms)

	if r["is_correct"]:
		goblin.appear()


func _on_reset() -> void:
	reset_progress()
	refresh_status()
	result_label.text = "已重設：經驗值 0，作答紀錄清空。"
	timing_label.text = ""


# ---------- 自動檢查（Claude 用，不開視窗）：-- --selftest ----------

func _selftest() -> void:
	reset_progress()
	var levels := []
	for x in [0, 19, 20, 160, 170, 180, 1000]:
		levels.append(level_from_xp(x))
	print("levels ", levels, " ok=", levels == [1, 1, 2, 9, 9, 9, 9])
	print("empty  ", submit_answer(""))
	print("bad    ", submit_answer("abc"))
	print("wrong  ", submit_answer("7"))
	print("again  ", submit_answer("34"))
	reset_progress()
	print("first  ", submit_answer("34"))
	db.close_db()
	open_db()  # 模擬關掉重開（試驗第 4 項）
	print("reopen xp=", get_xp())
	get_tree().quit()
