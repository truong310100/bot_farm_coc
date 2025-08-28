class ZoomPanState:
    def handle_mouse_down(state, event):
        state["drag_start"] = (event.x, event.y)

    def handle_mouse_move(state, event, draw_callback):
        if state["drag_start"]:
            dx = event.x - state["drag_start"][0]
            dy = event.y - state["drag_start"][1]
            state["dx"] += dx
            state["dy"] += dy
            state["drag_start"] = (event.x, event.y)
            draw_callback()

    def handle_mouse_up(state, event):
        state["drag_start"] = None

    def handle_mouse_wheel(state, event, draw_callback, min_scale=0.1, max_scale=10.0, zoom_factor=1.02):
        # Windows: event.delta, Linux/Mac: event.num
        if hasattr(event, 'delta'):
            delta = event.delta
        elif hasattr(event, 'num'):
            delta = 120 if event.num == 4 else -120
        else:
            delta = 0
        mouse_x = event.x
        mouse_y = event.y
        old_scale = state["scale"]
        if delta > 0:
            state["scale"] = min(state["scale"] * zoom_factor, max_scale)
        else:
            state["scale"] = max(state["scale"] / zoom_factor, min_scale)
        # Giữ điểm dưới chuột không đổi vị trí trên canvas
        state["dx"] = mouse_x - (mouse_x - state["dx"]) * (state["scale"] / old_scale)
        state["dy"] = mouse_y - (mouse_y - state["dy"]) * (state["scale"] / old_scale)
        draw_callback()

