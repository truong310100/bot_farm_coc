from dataclasses import dataclass, asdict
from typing import Dict, Any, Optional

@dataclass
class ActionButton:
    """Lớp đại diện cho một nút hành động"""
    id: str
    type: str  # 'click', 'drag', 'wait', 'click_drag'
    x: int = 0
    y: int = 0
    duration: float = 0  # cho wait và drag
    end_x: Optional[int] = None  # cho drag, click_drag
    end_y: Optional[int] = None  # cho drag, click_drag
    steps: Optional[int] = None  # chỉ cho click_drag

    def to_dict(self):
        data = asdict(self)
        # Loại bỏ trường None để file json gọn hơn
        return {k: v for k, v in data.items() if v is not None}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]):
        # Đảm bảo luôn có steps cho click_drag
        if data.get("type") == "click_drag":
            if "steps" not in data or data["steps"] is None:
                data["steps"] = 10  # hoặc giá trị mặc định bạn muốn
        # Lọc chỉ lấy các trường có trong ActionButton
        valid_keys = {f.name for f in cls.__dataclass_fields__.values()}
        filtered_data = {k: v for k, v in data.items() if k in valid_keys}
        return cls(**filtered_data)