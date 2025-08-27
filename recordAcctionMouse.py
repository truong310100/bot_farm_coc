import tkinter as tk
from tkinter import ttk, messagebox
from pynput import mouse
import threading
import time
import json

class MouseRecorderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Mouse Recorder")
        self.actions = []
        self.recording = False
        self.listener = None

        # UI
        self.create_widgets()

    def create_widgets(self):
        frame = ttk.Frame(self.root, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)

        btn_frame = ttk.Frame(frame)
        btn_frame.pack(fill=tk.X, pady=5)
        ttk.Button(btn_frame, text="Ghi lại", command=self.start_record, width=10).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Dừng ghi", command=self.stop_record, width=10).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Phát lại", command=self.play_actions, width=10).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Lưu", command=self.save_actions, width=10).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Tải", command=self.load_actions, width=10).pack(side=tk.LEFT, padx=2)

        self.tree = ttk.Treeview(frame, columns=("type", "x", "y", "button"), show="headings", height=15)
        self.tree.heading("type", text="Loại")
        self.tree.heading("x", text="X")
        self.tree.heading("y", text="Y")
        self.tree.heading("button", text="Nút")
        self.tree.pack(fill=tk.BOTH, expand=True, pady=5)

    def start_record(self):
        if self.recording:
            return
        self.actions = []
        self.update_tree()
        self.recording = True
        self.listener = mouse.Listener(
            on_move=self.on_move,
            on_click=self.on_click,
            on_scroll=self.on_scroll
        )
        self.listener.start()
        messagebox.showinfo("Ghi lại", "Đang ghi lại hành động chuột. Nhấn 'Dừng ghi' để kết thúc.")

    def stop_record(self):
        if self.listener:
            self.listener.stop()
        self.recording = False

    def on_move(self, x, y):
        if self.recording:
            self.actions.append({"type": "move", "x": x, "y": y, "button": ""})
            self.update_tree()

    def on_click(self, x, y, button, pressed):
        if self.recording and pressed:
            self.actions.append({"type": "click", "x": x, "y": y, "button": str(button)})
            self.update_tree()

    def on_scroll(self, x, y, dx, dy):
        if self.recording:
            self.actions.append({"type": "scroll", "x": x, "y": y, "button": f"{dx},{dy}"})
            self.update_tree()

    def play_actions(self):
        if not self.actions:
            messagebox.showwarning("Cảnh báo", "Chưa có bản ghi nào!")
            return
        def do_play():
            from pynput.mouse import Controller, Button
            m = Controller()
            for act in self.actions:
                if act["type"] == "move":
                    m.position = (act["x"], act["y"])
                elif act["type"] == "click":
                    m.position = (act["x"], act["y"])
                    btn = Button.left if "left" in act["button"] else Button.right
                    m.click(btn)
                elif act["type"] == "scroll":
                    m.position = (act["x"], act["y"])
                    dx, dy = map(int, act["button"].split(","))
                    m.scroll(dx, dy)
                time.sleep(0.05)
        threading.Thread(target=do_play, daemon=True).start()

    def update_tree(self):
        self.tree.delete(*self.tree.get_children())
        for act in self.actions:
            self.tree.insert("", "end", values=(act["type"], act["x"], act["y"], act["button"]))

    def save_actions(self):
        if not self.actions:
            messagebox.showwarning("Cảnh báo", "Không có dữ liệu để lưu!")
            return
        from tkinter import filedialog
        file = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON", "*.json")])
        if file:
            with open(file, "w") as f:
                json.dump(self.actions, f)
            messagebox.showinfo("Lưu", "Đã lưu bản ghi!")

    def load_actions(self):
        from tkinter import filedialog
        file = filedialog.askopenfilename(filetypes=[("JSON", "*.json")])
        if file:
            with open(file, "r") as f:
                self.actions = json.load(f)
            self.update_tree()
            messagebox.showinfo("Tải", "Đã tải bản ghi!")

if __name__ == "__main__":
    root = tk.Tk()
    app = MouseRecorderApp(root)
    root.mainloop()