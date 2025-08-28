from typing import List, Optional
from models import ActionButton
import json
from datetime import datetime

class ScenarioManager:
    def __init__(self):
        self.buttons: List[ActionButton] = []
        self.current_id = 0

    def add_button(self, button_type: str) -> ActionButton:
        self.current_id += 1
        button = ActionButton(
            id=f"btn_{self.current_id}",
            type=button_type,
            x=100,
            y=100,
            duration=1.0 if button_type == 'wait' else 0.5
        )
        if button_type in ('drag', 'click_drag'):
            button.end_x = 200
            button.end_y = 200
        self.buttons.append(button)
        return button

    def delete_button(self, button_id: str) -> bool:
        before = len(self.buttons)
        self.buttons = [b for b in self.buttons if b.id != button_id]
        return len(self.buttons) < before

    def update_button(self, button_id: str, **kwargs) -> Optional[ActionButton]:
        button = next((b for b in self.buttons if b.id == button_id), None)
        if not button:
            return None
        for key, value in kwargs.items():
            if hasattr(button, key):
                setattr(button, key, value)
        return button

    def move_up(self, button_id: str) -> bool:
        idx = next((i for i, b in enumerate(self.buttons) if b.id == button_id), None)
        if idx is not None and idx > 0:
            self.buttons[idx], self.buttons[idx-1] = self.buttons[idx-1], self.buttons[idx]
            return True
        return False

    def move_down(self, button_id: str) -> bool:
        idx = next((i for i, b in enumerate(self.buttons) if b.id == button_id), None)
        if idx is not None and idx < len(self.buttons) - 1:
            self.buttons[idx], self.buttons[idx+1] = self.buttons[idx+1], self.buttons[idx]
            return True
        return False

    def save_to_file(self, filename: str, auto_stop_minutes: str = ""):
        scenario_data = {
            "created": datetime.now().isoformat(),
            "auto_stop_minutes": auto_stop_minutes,
            "buttons": [button.to_dict() for button in self.buttons]
        }
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(scenario_data, f, indent=2, ensure_ascii=False)

    def load_from_file(self, filename: str):
        with open(filename, 'r', encoding='utf-8') as f:
            scenario_data = json.load(f)
        self.buttons.clear()
        for button_data in scenario_data.get('buttons', []):
            button = ActionButton.from_dict(button_data)
            self.buttons.append(button)
        if self.buttons:
            max_id = max(int(b.id.split('_')[1]) for b in self.buttons)
            self.current_id = max_id
        else:
            self.current_id = 0
        auto_stop = scenario_data.get('auto_stop_minutes', "")
        return auto_stop

    # ...các hàm quản lý khác...