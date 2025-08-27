import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import keyboard
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pyautogui
import time
import threading
from models import ActionButton
from scenario_manager import ScenarioManager

class AutoClickTool:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Auto Click Tool")
        self.root.geometry("900x500")
        keyboard.add_hotkey('F8', self.stop_scenario)
        self.manager = ScenarioManager()
        self.is_running = False
        self.selected_button = None
        self.create_widgets()
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.1
        self.load_default_scenario()

    def create_widgets(self):
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        left_frame = ttk.Frame(main_frame)
        left_frame.grid(row=0, column=0, sticky="nswe", padx=(0, 10))
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(0, weight=1, minsize=220)
        right_frame = ttk.Frame(main_frame)
        right_frame.grid(row=0, column=1, sticky="nswe")
        main_frame.columnconfigure(1, weight=0)

        # Control Frame
        control_frame = ttk.LabelFrame(left_frame, text="Điều khiển", padding=10)
        control_frame.pack(fill=tk.X, pady=(0, 10))

        # Add Action
        add_frame = ttk.Frame(control_frame)
        add_frame.pack(fill=tk.X, pady=2)
        action_types = ['click', 'drag', 'wait', 'click_drag']
        self.action_type_var = tk.StringVar(value=action_types[0])
        action_type_cb = ttk.Combobox(add_frame, textvariable=self.action_type_var, values=action_types, state='readonly', width=12)
        action_type_cb.pack(side=tk.LEFT, padx=2)
        ttk.Button(add_frame, text="Thêm", command=lambda: self.add_button(self.action_type_var.get()), width=8).pack(side=tk.LEFT, padx=2)

        # Start/Stop/Loop
        action_btn_frame = ttk.Frame(control_frame)
        action_btn_frame.pack(fill=tk.X, pady=2)
        self.run_button = ttk.Button(action_btn_frame, text="Start", command=self.run_scenario, width=8)
        self.run_button.pack(side=tk.LEFT, padx=2)
        self.stop_button = ttk.Button(action_btn_frame, text="Dừng", command=self.stop_scenario, state=tk.DISABLED, width=8)
        self.stop_button.pack(side=tk.LEFT, padx=2)
        self.loop_enabled = tk.BooleanVar(value=True)
        ttk.Checkbutton(action_btn_frame, text="Lặp", variable=self.loop_enabled).pack(side=tk.LEFT, padx=2)

        # Save/Load
        file_frame = ttk.Frame(control_frame)
        file_frame.pack(fill=tk.X, pady=2)
        ttk.Button(file_frame, text="Lưu kịch bản", command=self.save_scenario, width=10).pack(side=tk.LEFT, padx=2)
        ttk.Button(file_frame, text="Tải kịch bản", command=self.load_scenario, width=10).pack(side=tk.LEFT, padx=2)

        # Auto Stop Minutes
        time_frame = ttk.Frame(control_frame)
        time_frame.pack(fill=tk.X, pady=2)
        self.auto_stop_minutes = tk.StringVar(value="")
        ttk.Label(time_frame, text="Phút chạy:").pack(side=tk.LEFT, padx=2)
        ttk.Entry(time_frame, textvariable=self.auto_stop_minutes, width=6).pack(side=tk.LEFT, padx=2)

        # Action List
        list_frame = ttk.LabelFrame(left_frame, text="Hành động", padding=10)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        columns = ('ID', 'Loại', 'Tọa độ', 'Thời gian/Điểm cuối', 'Thứ tự')
        self.tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=18)
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=100)
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.bind('<Double-1>', self.edit_button)
        self.tree.bind('<Button-3>', self.show_context_menu)
        self.tree.bind('<ButtonRelease-1>', self.on_tree_select)

        # Edit Frame
        edit_frame = ttk.LabelFrame(right_frame, text="Chỉnh sửa hành động", padding=10)
        edit_frame.pack(fill=tk.BOTH, expand=True)
        coord_frame = ttk.Frame(edit_frame)
        coord_frame.pack(fill=tk.X, pady=5)
        ttk.Label(coord_frame, text="X:").pack(side=tk.LEFT)
        self.x_var = tk.StringVar()
        ttk.Entry(coord_frame, textvariable=self.x_var, width=10).pack(side=tk.LEFT, padx=5)
        ttk.Label(coord_frame, text="Y:").pack(side=tk.LEFT, padx=(10, 0))
        self.y_var = tk.StringVar()
        ttk.Entry(coord_frame, textvariable=self.y_var, width=10).pack(side=tk.LEFT, padx=5)

        extra_frame = ttk.Frame(edit_frame)
        extra_frame.pack(fill=tk.X, pady=5)
        ttk.Label(extra_frame, text="Thời gian/End X:").pack(side=tk.LEFT)
        self.duration_var = tk.StringVar()
        ttk.Entry(extra_frame, textvariable=self.duration_var, width=10).pack(side=tk.LEFT, padx=5)
        ttk.Label(extra_frame, text="End Y:").pack(side=tk.LEFT, padx=(10, 0))
        self.end_y_var = tk.StringVar()
        ttk.Entry(extra_frame, textvariable=self.end_y_var, width=10).pack(side=tk.LEFT, padx=5)

        extra2_frame = ttk.Frame(edit_frame)
        extra2_frame.pack(fill=tk.X, pady=5)
        self.steps_var = tk.StringVar(value="10")
        ttk.Label(extra2_frame, text="Số bước click_drag:").pack(side=tk.LEFT)
        self.steps_entry = ttk.Entry(extra2_frame, textvariable=self.steps_var, width=10)
        self.steps_entry.pack(side=tk.LEFT, padx=5)

        button_frame = ttk.Frame(edit_frame)
        button_frame.pack(fill=tk.X, pady=5)
        ttk.Button(button_frame, text="Lấy tọa độ đầu", command=lambda: self.get_current_position('start')).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Lấy tọa độ cuối", command=lambda: self.get_current_position('end')).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cập nhật", command=self.update_selected_button).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Xóa", command=self.delete_selected_button).pack(side=tk.LEFT, padx=5)

        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Chỉnh sửa", command=self.edit_button)
        self.context_menu.add_command(label="Xóa", command=self.delete_selected_button)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Di chuyển lên", command=self.move_up)
        self.context_menu.add_command(label="Di chuyển xuống", command=self.move_down)

    def add_button(self, button_type: str):
        button = self.manager.add_button(button_type)
        self.refresh_tree()
        self.select_button(button)

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

    def update_selected_button(self):
        if not self.selected_button:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn một hành động để cập nhật!")
            return
        try:
            kwargs = {
                "x": int(self.x_var.get() or 0),
                "y": int(self.y_var.get() or 0),
            }
            if self.selected_button.type == 'wait':
                kwargs["duration"] = float(self.duration_var.get() or 1.0)
            elif self.selected_button.type in ('drag', 'click_drag'):
                kwargs["end_x"] = int(self.duration_var.get() or 0)
                kwargs["end_y"] = int(self.end_y_var.get() or 0)
                if self.selected_button.type == 'click_drag':
                    kwargs["steps"] = int(self.steps_var.get() or 10)
            button = self.manager.update_button(self.selected_button.id, **kwargs)
            if button:
                self.refresh_tree()
                messagebox.showinfo("Thành công", "Đã cập nhật hành động!")
        except ValueError as e:
            messagebox.showerror("Lỗi", f"Giá trị không hợp lệ: {e}")

    def delete_selected_button(self):
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn một hành động để xóa!")
            return
        if messagebox.askyesno("Xác nhận", "Bạn có chắc muốn xóa hành động này?"):
            button_id = selection[0]
            self.manager.delete_button(button_id)
            self.selected_button = None
            self.refresh_tree()
            self.x_var.set("")
            self.y_var.set("")
            self.duration_var.set("")
            self.end_y_var.set("")

    def get_current_position(self, pos_type='start'):
        self.root.withdraw()
        def get_pos():
            time.sleep(2)
            x, y = pyautogui.position()
            self.root.after(0, lambda: self.set_position(x, y, pos_type))
            self.root.after(0, self.root.deiconify)
        threading.Thread(target=get_pos, daemon=True).start()
        messagebox.showinfo("Hướng dẫn", f"Cửa sổ sẽ ẩn trong 2 giây. Hãy di chuyển chuột đến vị trí {'bắt đầu' if pos_type=='start' else 'kết thúc'}!")

    def set_position(self, x, y, pos_type='start'):
        if pos_type == 'start':
            self.x_var.set(str(x))
            self.y_var.set(str(y))
        else:
            self.duration_var.set(str(x))
            self.end_y_var.set(str(y))

    def move_up(self):
        if self.selected_button and self.manager.move_up(self.selected_button.id):
            self.refresh_tree()
            self.select_button(self.selected_button)

    def move_down(self):
        if self.selected_button and self.manager.move_down(self.selected_button.id):
            self.refresh_tree()
            self.select_button(self.selected_button)

    def show_context_menu(self, event):
        selection = self.tree.selection()
        if selection:
            button_id = selection[0]
            self.selected_button = next((b for b in self.manager.buttons if b.id == button_id), None)
            self.context_menu.post(event.x_root, event.y_root)

    def save_scenario(self):
        if not self.manager.buttons:
            messagebox.showwarning("Cảnh báo", "Không có hành động nào để lưu!")
            return
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            try:
                self.manager.save_to_file(filename, self.auto_stop_minutes.get())
                messagebox.showinfo("Thành công", f"Đã lưu kịch bản vào {filename}")
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể lưu file: {e}")

    def load_scenario(self):
        filename = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            try:
                auto_stop = self.manager.load_from_file(filename)
                self.selected_button = None
                self.auto_stop_minutes.set(str(auto_stop))
                self.refresh_tree()
                messagebox.showinfo("Thành công", f"Đã tải kịch bản từ {filename}")
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể tải file: {e}")

    def load_default_scenario(self):
        default_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")
        if os.path.exists(default_file):
            try:
                auto_stop = self.manager.load_from_file(default_file)
                self.selected_button = None
                self.auto_stop_minutes.set(str(auto_stop))
                self.refresh_tree()
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể tải file mặc định: {e}")
        else:
            messagebox.showinfo("Thông báo", "Không tìm thấy file config.json, vui lòng chọn file kịch bản!")
            self.load_scenario()

    def run_scenario(self):
        if not self.manager.buttons:
            messagebox.showwarning("Cảnh báo", "Không có hành động nào để chạy!")
            return
        self.is_running = True
        self.run_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.root.withdraw()
        try:
            auto_stop = float(self.auto_stop_minutes.get()) if self.auto_stop_minutes.get() else None
        except ValueError:
            messagebox.showerror("Lỗi", "Giá trị phút tự dừng không hợp lệ!")
            return

        def run_thread():
            start_time = time.time()
            try:
                while self.is_running:
                    if auto_stop is not None and (time.time() - start_time) / 60 >= auto_stop:
                        self.is_running = False
                        break
                    for i in range(3, 0, -1):
                        if not self.is_running:
                            return
                        self.root.after(0, lambda i=i: self.root.title(f"Auto Click Tool - Bắt đầu trong {i}s"))
                        time.sleep(1)
                    if not self.is_running:
                        return
                    for idx, button in enumerate(self.manager.buttons, 1):
                        if not self.is_running:
                            break
                        self.root.after(0, lambda idx=idx, total=len(self.manager.buttons):
                                        self.root.title(f"Auto Click Tool - Đang chạy ({idx}/{total})"))
                        if button.type == 'click':
                            pyautogui.click(button.x, button.y)
                        elif button.type == 'drag':
                            pyautogui.moveTo(button.x, button.y)
                            pyautogui.dragTo(button.end_x, button.end_y, duration=0.5, button='left')
                        elif button.type == 'click_drag':
                            self.perform_click_drag(button)
                        elif button.type == 'wait':
                            time.sleep(button.duration)
                        time.sleep(0.1)
                        if auto_stop is not None and (time.time() - start_time) / 60 >= auto_stop:
                            self.is_running = False
                            break
                    if not self.loop_enabled.get():
                        break
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("Lỗi", f"Lỗi khi chạy kịch bản: {e}"))
            finally:
                self.root.after(0, self.stop_scenario)
        threading.Thread(target=run_thread, daemon=True).start()

    def stop_scenario(self):
        self.is_running = False
        self.run_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.root.deiconify()
        self.root.title("Auto Click Tool")

    def on_tree_select(self, event):
        selection = self.tree.selection()
        if selection:
            button_id = selection[0]
            button = next((b for b in self.manager.buttons if b.id == button_id), None)
            if button:
                self.select_button(button)

    def perform_click_drag(self, button):
        steps = getattr(button, 'steps', 10)
        x0, y0 = button.x, button.y
        x1, y1 = button.end_x, button.end_y
        for i in range(steps + 1):
            if not self.is_running:
                break
            t = i / steps
            x = int(x0 + (x1 - x0) * t)
            y = int(y0 + (y1 - y0) * t)
            pyautogui.moveTo(x, y)
            pyautogui.click()
            time.sleep(0.03)

    def run(self):
        self.root.mainloop()
