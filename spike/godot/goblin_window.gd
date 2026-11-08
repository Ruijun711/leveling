# 桌面哥布林（試驗第 1 項）：透明、無邊框、永遠在最上層的獨立視窗，左右走動。按右鍵關掉。
extends Window

const SIZE := 140

var dx := 4
var step := 0
var drawing: GoblinDrawing


func _init() -> void:
	size = Vector2i(SIZE, SIZE)
	borderless = true
	transparent = true
	transparent_bg = true
	always_on_top = true
	unfocusable = true
	visible = false


func _ready() -> void:
	drawing = GoblinDrawing.new()
	drawing.size = Vector2(SIZE, SIZE)
	drawing.goblin = self
	add_child(drawing)


func appear() -> void:
	var screen := DisplayServer.screen_get_usable_rect()
	position = Vector2i(screen.position.x + 50, screen.end.y - SIZE - 20)
	show()


func _process(_delta: float) -> void:
	if not visible:
		return
	var screen := DisplayServer.screen_get_usable_rect()
	var x := position.x + dx
	if x < screen.position.x or x + SIZE > screen.end.x:
		dx = -dx
		x = position.x + dx
	step += 1
	var bob := 6 if (step / 8) % 2 == 1 else 0  # 走路時上下晃動
	position = Vector2i(x, screen.end.y - SIZE - 20 - bob)
	drawing.queue_redraw()


class GoblinDrawing extends Control:
	var goblin

	func _gui_input(event: InputEvent) -> void:
		if event is InputEventMouseButton and event.pressed and event.button_index == MOUSE_BUTTON_RIGHT:
			goblin.hide()

	func _ellipse(center: Vector2, rx: float, ry: float, color: Color) -> void:
		draw_set_transform(center, 0.0, Vector2(rx / ry, 1.0))
		draw_circle(Vector2.ZERO, ry, color)
		draw_set_transform(Vector2.ZERO, 0.0, Vector2.ONE)

	func _draw() -> void:
		var green := Color("#5fa83a")
		# 耳朵
		draw_colored_polygon(PackedVector2Array([Vector2(22, 45), Vector2(2, 25), Vector2(35, 38)]), green)
		draw_colored_polygon(PackedVector2Array([Vector2(118, 45), Vector2(138, 25), Vector2(105, 38)]), green)
		# 身體
		draw_rect(Rect2(42, 88, 56, 44), Color("#7a4b26"))
		# 頭
		_ellipse(Vector2(70, 57), 45, 37, green)
		# 眼睛（看向走的方向）
		var look := 4 if goblin.dx > 0 else -4
		_ellipse(Vector2(54, 52), 9, 7, Color("#ffeb3b"))
		_ellipse(Vector2(86, 52), 9, 7, Color("#ffeb3b"))
		draw_circle(Vector2(54 + look, 52), 3, Color.BLACK)
		draw_circle(Vector2(86 + look, 52), 3, Color.BLACK)
		# 嘴巴和牙齒
		draw_rect(Rect2(52, 70, 36, 12), Color("#3b1f0e"))
		draw_colored_polygon(PackedVector2Array([Vector2(57, 70), Vector2(61, 77), Vector2(65, 70)]), Color.WHITE)
		draw_colored_polygon(PackedVector2Array([Vector2(75, 70), Vector2(79, 77), Vector2(83, 70)]), Color.WHITE)
