from models import ActionButton

class UIUtils:
    def refresh_tree(self):
        self.tree.delete(*self.tree.get_children())
        for idx, button in enumerate(self.manager.buttons):
            coord = f"({button.x}, {button.y})" if button.type != 'wait' else "-"
            extra = (
                f"→ ({button.end_x}, {button.end_y})" if button.type == 'drag'
                else (f"{button.duration}s" if button.type == 'wait' else "-")
            )
            self.tree.insert('', 'end', iid=button.id, values=(
                button.id, button.type.upper(), coord, extra, idx + 1
            ))
            
    def select_button(self, button: ActionButton):
        self.selected_button = button
        self.tree.selection_set(button.id)
        self.x_var.set(str(button.x))
        self.y_var.set(str(button.y))
        if button.type == 'wait':
            self.duration_var.set(str(button.duration))
            self.end_y_var.set("")
            self.steps_var.set("")
        elif button.type in ('drag', 'click_drag'):
            self.duration_var.set(str(button.end_x))
            self.end_y_var.set(str(button.end_y))
            self.steps_var.set(str(getattr(button, 'steps', 10)))
        else:
            self.duration_var.set("")
            self.end_y_var.set("")
            self.steps_var.set("")

    def edit_button(self, event=None):
        selection = self.tree.selection()
        if selection:
            button_id = selection[0]
            button = next((b for b in self.manager.buttons if b.id == button_id), None)
            if button:
                self.select_button(button)