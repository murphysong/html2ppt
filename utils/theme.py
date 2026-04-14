from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class Theme:
    def __init__(self, data: dict[str, Any]) -> None:
        self.data = data
        slide = data["slide"]
        calibration = data["calibration"]
        self.slide_width_inch: float = float(slide["width_inch"])
        self.slide_height_inch: float = float(slide["height_inch"])
        self.px_to_inch_x: float = float(calibration["px_to_inch_scale_x"])
        self.px_to_inch_y: float = float(calibration["px_to_inch_scale_y"])

    @classmethod
    def load(cls, path: str | Path) -> "Theme":
        with Path(path).open("r", encoding="utf-8") as f:
            data = json.load(f)
        return cls(data)
