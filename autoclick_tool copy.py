import sys, os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import keyboard
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import pyautogui
import time
import threading
from datetime import datetime
from typing import List
from models import ActionButton

class AutoClickTool:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Auto Click Tool")
        self.root.geometry("800x600")
        keyboard.add_hotkey('F8', self.stop_scenario)
        # Dữ liệu
        self.buttons: List[ActionButton] = []
        self.current_id = 0
        self.is_running = False
        self.selected_button = None
        
        # Tạo giao diện
        self.create_widgets()
        
        # Thiết lập pyautogui
        pyautogui.FAILSAFE = True
        pyautogui.PAUSE = 0.1
        
    def create_widgets(self):
        """Tạo giao diện người dùng"""
        # Frame chính
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Frame điều khiển
        control_frame = ttk.LabelFrame(main_frame, text="Điều khiển", padding=10)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Thay thế 4 nút thêm action bằng combobox + nút Thêm
        action_types = ['click', 'drag', 'wait', 'click_drag']
        self.action_type_var = tk.StringVar(value=action_types[0])
        ttk.Label(control_frame, text="Loại hành động:").pack(side=tk.LEFT, padx=5)
        action_type_cb = ttk.Combobox(control_frame, textvariable=self.action_type_var, values=action_types, state='readonly', width=12)
        action_type_cb.pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Thêm", command=lambda: self.add_button(self.action_type_var.get())).pack(side=tk.LEFT, padx=5)
        
        # Separator
        ttk.Separator(control_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=10)
        
        # Nút chạy/dừng
        self.run_button = ttk.Button(control_frame, text="Chạy kịch bản", 
                                    command=self.run_scenario)
        self.run_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = ttk.Button(control_frame, text="Dừng", 
                                     command=self.stop_scenario, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        # Separator
        ttk.Separator(control_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=10)
        
        # Nút lưu/tải
        ttk.Button(control_frame, text="Lưu kịch bản", 
                  command=self.save_scenario).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Tải kịch bản", 
                  command=self.load_scenario).pack(side=tk.LEFT, padx=5)
        
        # Thêm checkbox lặp kịch bản
        self.loop_enabled = tk.BooleanVar(value=False)
        ttk.Checkbutton(control_frame, text="Lặp kịch bản", variable=self.loop_enabled).pack(side=tk.LEFT, padx=5)
        
        self.auto_stop_minutes = tk.StringVar(value="")  # Thêm biến lưu số phút
        ttk.Label(control_frame, text="Tự dừng sau (phút):").pack(side=tk.LEFT, padx=5)
        ttk.Entry(control_frame, textvariable=self.auto_stop_minutes, width=6).pack(side=tk.LEFT, padx=2)
        
        # Thêm biến lưu số bước click_drag
        self.steps_var = tk.StringVar(value="10")
        
        # Frame danh sách nút
        list_frame = ttk.LabelFrame(main_frame, text="Danh sách hành động", padding=10)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        
        # Treeview để hiển thị danh sách
        columns = ('ID', 'Loại', 'Tọa độ', 'Thời gian/Điểm cuối', 'Thứ tự')
        self.tree = ttk.Treeview(list_frame, columns=columns, show='headings', height=10)
        
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120)
        
        # Scrollbar cho treeview
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Bind sự kiện
        self.tree.bind('<Double-1>', self.edit_button)
        self.tree.bind('<Button-3>', self.show_context_menu)
        self.tree.bind('<ButtonRelease-1>', self.on_tree_select)  # Thêm dòng này
        
        # Frame chỉnh sửa
        edit_frame = ttk.LabelFrame(main_frame, text="Chỉnh sửa hành động", padding=10)
        edit_frame.pack(fill=tk.X)
        
        # Tọa độ
        coord_frame = ttk.Frame(edit_frame)
        coord_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(coord_frame, text="X:").pack(side=tk.LEFT)
        self.x_var = tk.StringVar()
        ttk.Entry(coord_frame, textvariable=self.x_var, width=10).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(coord_frame, text="Y:").pack(side=tk.LEFT, padx=(10, 0))
        self.y_var = tk.StringVar()
        ttk.Entry(coord_frame, textvariable=self.y_var, width=10).pack(side=tk.LEFT, padx=5)
        
        # Thời gian/Điểm cuối
        extra_frame = ttk.Frame(edit_frame)
        extra_frame.pack(fill=tk.X, pady=5)
        
        ttk.Label(extra_frame, text="Thời gian/End X:").pack(side=tk.LEFT)
        self.duration_var = tk.StringVar()
        ttk.Entry(extra_frame, textvariable=self.duration_var, width=10).pack(side=tk.LEFT, padx=5)
        
        ttk.Label(extra_frame, text="End Y:").pack(side=tk.LEFT, padx=(10, 0))
        self.end_y_var = tk.StringVar()
        ttk.Entry(extra_frame, textvariable=self.end_y_var, width=10).pack(side=tk.LEFT, padx=5)
        
        # Thêm vào phần chỉnh sửa
        extra2_frame = ttk.Frame(edit_frame)
        extra2_frame.pack(fill=tk.X, pady=5)
        ttk.Label(extra2_frame, text="Số bước click_drag:").pack(side=tk.LEFT)
        self.steps_entry = ttk.Entry(extra2_frame, textvariable=self.steps_var, width=10)
        self.steps_entry.pack(side=tk.LEFT, padx=5)
        
        # Nút cập nhật và lấy tọa độ
        button_frame = ttk.Frame(edit_frame)
        button_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(button_frame, text="Lấy tọa độ hiện tại", 
                  command=self.get_current_position).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cập nhật", 
                  command=self.update_selected_button).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Xóa", 
                  command=self.delete_selected_button).pack(side=tk.LEFT, padx=5)
        
        # Menu chuột phải
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Chỉnh sửa", command=self.edit_button)
        self.context_menu.add_command(label="Xóa", command=self.delete_selected_button)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Di chuyển lên", command=self.move_up)
        self.context_menu.add_command(label="Di chuyển xuống", command=self.move_down)
        
        ttk.Button(control_frame, text="Hiển thị vị trí", command=self.show_overlay).pack(side=tk.LEFT, padx=5)
    
    def add_button(self, button_type: str):
        """Thêm nút mới"""
        self.current_id += 1
        button = ActionButton(
            id=f"btn_{self.current_id}",
            type=button_type,
            x=100,
            y=100,
            duration=1.0 if button_type == 'wait' else 0.5
        )
        # Thêm mặc định cho click_drag
        if button_type in ('drag', 'click_drag'):
            button.end_x = 200
            button.end_y = 200
        self.buttons.append(button)
        self.refresh_tree()
        self.select_button(button)
    
    def refresh_tree(self):
        """Cập nhật danh sách hiển thị"""
        # Xóa tất cả items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Thêm vào tree
        for idx, button in enumerate(self.buttons):
            self.tree.insert('', 'end', iid=button.id, values=(
                button.id,
                button.type.upper(),
                f"({button.x}, {button.y})" if button.type != 'wait' else "-",
                f"→ ({button.end_x}, {button.end_y})" if button.type == 'drag' else (f"{button.duration}s" if button.type == 'wait' else "-"),
                idx+1
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
            if hasattr(button, 'steps') and button.steps:
                self.steps_var.set(str(button.steps))
            else:
                self.steps_var.set("10")
        else:
            self.duration_var.set("")
            self.end_y_var.set("")
            self.steps_var.set("")
    
    def edit_button(self, event=None):
        """Chỉnh sửa nút được chọn"""
        selection = self.tree.selection()
        if selection:
            button_id = selection[0]
            button = next((b for b in self.buttons if b.id == button_id), None)
            if button:
                self.select_button(button)
    
    def update_selected_button(self):
        if not self.selected_button:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn một hành động để cập nhật!")
            return
        try:
            self.selected_button.x = int(self.x_var.get()) if self.x_var.get() else 0
            self.selected_button.y = int(self.y_var.get()) if self.y_var.get() else 0
            if self.selected_button.type == 'wait':
                self.selected_button.duration = float(self.duration_var.get()) if self.duration_var.get() else 1.0
            elif self.selected_button.type in ('drag', 'click_drag'):
                self.selected_button.end_x = int(self.duration_var.get()) if self.duration_var.get() else 0
                self.selected_button.end_y = int(self.end_y_var.get()) if self.end_y_var.get() else 0
                if self.selected_button.type == 'click_drag':
                    try:
                        self.selected_button.steps = int(self.steps_var.get())
                    except Exception:
                        self.selected_button.steps = 10
            self.refresh_tree()
            messagebox.showinfo("Thành công", "Đã cập nhật hành động!")
        except ValueError as e:
            messagebox.showerror("Lỗi", f"Giá trị không hợp lệ: {e}")
    
    def delete_selected_button(self):
        """Xóa nút được chọn"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Cảnh báo", "Vui lòng chọn một hành động để xóa!")
            return
        
        if messagebox.askyesno("Xác nhận", "Bạn có chắc muốn xóa hành động này?"):
            button_id = selection[0]
            self.buttons = [b for b in self.buttons if b.id != button_id]
            self.selected_button = None
            self.refresh_tree()
            
            # Xóa form
            self.x_var.set("")
            self.y_var.set("")
            self.duration_var.set("")
            self.end_y_var.set("")
    
    def get_current_position(self):
        """Lấy tọa độ con trỏ chuột hiện tại"""
        # Ẩn cửa sổ trong 2 giây để người dùng di chuyển chuột
        self.root.withdraw()
        
        def get_pos():
            time.sleep(2)
            x, y = pyautogui.position()
            self.root.after(0, lambda: self.set_position(x, y))
            self.root.after(0, self.root.deiconify)
        
        threading.Thread(target=get_pos, daemon=True).start()
        messagebox.showinfo("Hướng dẫn", "Cửa sổ sẽ ẩn trong 2 giây. Hãy di chuyển chuột đến vị trí mong muốn!")
    
    def set_position(self, x, y):
        """Thiết lập tọa độ vào form"""
        self.x_var.set(str(x))
        self.y_var.set(str(y))
    
    def move_up(self):
        """Di chuyển nút lên trên"""
        if not self.selected_button:
            return
        idx = self.buttons.index(self.selected_button)
        if idx > 0:
            self.buttons[idx], self.buttons[idx-1] = self.buttons[idx-1], self.buttons[idx]
            self.refresh_tree()
            self.select_button(self.selected_button)

    def move_down(self):
        """Di chuyển nút xuống dưới"""
        if not self.selected_button:
            return
        idx = self.buttons.index(self.selected_button)
        if idx < len(self.buttons) - 1:
            self.buttons[idx], self.buttons[idx+1] = self.buttons[idx+1], self.buttons[idx]
            self.refresh_tree()
            self.select_button(self.selected_button)
    
    def show_context_menu(self, event):
        """Hiển thị menu chuột phải"""
        selection = self.tree.selection()
        if selection:
            button_id = selection[0]
            self.selected_button = next((b for b in self.buttons if b.id == button_id), None)
            self.context_menu.post(event.x_root, event.y_root)
    
    def save_scenario(self):
        """Lưu kịch bản vào file JSON"""
        if not self.buttons:
            messagebox.showwarning("Cảnh báo", "Không có hành động nào để lưu!")
            return
        
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                scenario_data = {
                    "created": datetime.now().isoformat(),
                    "buttons": [button.to_dict() for button in self.buttons]
                }
                
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(scenario_data, f, indent=2, ensure_ascii=False)
                
                messagebox.showinfo("Thành công", f"Đã lưu kịch bản vào {filename}")
                
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể lưu file: {e}")
    
    def load_scenario(self):
        """Tải kịch bản từ file JSON"""
        filename = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    scenario_data = json.load(f)
                
                # Xóa dữ liệu hiện tại
                self.buttons.clear()
                self.selected_button = None
                
                # Tải dữ liệu mới
                for button_data in scenario_data.get('buttons', []):
                    button = ActionButton.from_dict(button_data)
                    self.buttons.append(button)
                
                # Cập nhật current_id
                if self.buttons:
                    max_id = max(int(b.id.split('_')[1]) for b in self.buttons)
                    self.current_id = max_id
                
                self.refresh_tree()
                messagebox.showinfo("Thành công", f"Đã tải kịch bản từ {filename}")
                
            except Exception as e:
                messagebox.showerror("Lỗi", f"Không thể tải file: {e}")
    
    def run_scenario(self):
        """Chạy kịch bản"""
        if not self.buttons:
            messagebox.showwarning("Cảnh báo", "Không có hành động nào để chạy!")
            return

        self.is_running = True
        self.run_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.root.withdraw()

        # Lấy số phút tự động dừng (nếu có)
        try:
            auto_stop = float(self.auto_stop_minutes.get()) if self.auto_stop_minutes.get() else None
        except ValueError:
            messagebox.showerror("Lỗi", "Giá trị phút tự dừng không hợp lệ!")
            return

        def run_thread():
            start_time = time.time()
            try:
                while self.is_running:
                    # Kiểm tra thời gian tự động dừng
                    if auto_stop is not None:
                        elapsed_min = (time.time() - start_time) / 60
                        if elapsed_min >= auto_stop:
                            self.is_running = False
                            break
                    # Đợi 3 giây trước khi bắt đầu mỗi vòng lặp
                    for i in range(3, 0, -1):
                        if not self.is_running:
                            return
                        self.root.after(0, lambda i=i: self.root.title(f"Auto Click Tool - Bắt đầu trong {i}s"))
                        time.sleep(1)
                    if not self.is_running:
                        return

                    for i, button in enumerate(self.buttons, 1):
                        if not self.is_running:
                            break
                        self.root.after(0, lambda i=i, total=len(self.buttons):
                                        self.root.title(f"Auto Click Tool - Đang chạy ({i}/{total})"))
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
                        # Kiểm tra thời gian tự động dừng sau mỗi action
                        if auto_stop is not None:
                            elapsed_min = (time.time() - start_time) / 60
                            if elapsed_min >= auto_stop:
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
        """Dừng kịch bản"""
        self.is_running = False
        self.run_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.root.deiconify()
        self.root.title("Auto Click Tool")
    
    def on_tree_select(self, event):
        """Cập nhật selected_button khi chọn dòng mới"""
        selection = self.tree.selection()
        if selection:
            button_id = selection[0]
            button = next((b for b in self.buttons if b.id == button_id), None)
            if button:
                self.select_button(button)
                
    def show_overlay(self):
        """Hiển thị overlay các vị trí nút đã config"""
        overlay = tk.Toplevel(self.root)
        overlay.attributes('-fullscreen', True)
        overlay.attributes('-topmost', True)
        overlay.attributes('-alpha', 0.5)  # tăng độ rõ
        overlay.configure(bg='black')

        screen_width = overlay.winfo_screenwidth()
        screen_height = overlay.winfo_screenheight()
        canvas = tk.Canvas(overlay, width=screen_width, height=screen_height, bg='', highlightthickness=0)
        canvas.pack(fill=tk.BOTH, expand=True)

        # Đảm bảo vẽ đúng tọa độ màn hình
        for button in self.buttons:
            if button.type in ('click', 'drag'):
                x, y = button.x, button.y
                # Kiểm tra tọa độ nằm trong màn hình
                if 0 <= x <= screen_width and 0 <= y <= screen_height:
                    canvas.create_oval(x-20, y-20, x+20, y+20, fill='red', outline='white', width=2)
                    canvas.create_text(x, y, text=button.id, fill='white')
                if button.type == 'drag':
                    ex, ey = button.end_x, button.end_y
                    if 0 <= ex <= screen_width and 0 <= ey <= screen_height:
                        canvas.create_line(x, y, ex, ey, fill='yellow', width=2, arrow=tk.LAST)
                        canvas.create_oval(ex-15, ey-15, ex+15, ey+15, fill='orange', outline='white', width=1)
        # Đóng overlay khi click chuột
        overlay.bind('<Button-1>', lambda e: overlay.destroy())
    
    def perform_click_drag(self, button):
        """Vừa di chuyển chuột vừa click liên tục từ (x, y) đến (end_x, end_y)"""
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
        """Chạy ứng dụng"""
        self.root.mainloop()