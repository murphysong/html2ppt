from __future__ import annotations

import re

RGB = tuple[int, int, int]

_HEX = re.compile(r"^#([0-9a-fA-F]{3}|[0-9a-fA-F]{6})$")
_RGB_FN = re.compile(r"rgba?\(([^)]+)\)")


_NAMED: dict[str, RGB] = {
    "white": (255, 255, 255),
    "black": (0, 0, 0),
    "red": (255, 0, 0),
    "blue": (0, 0, 255),
    "gray": (128, 128, 128),
    "grey": (128, 128, 128),
}


def parse_color(value: str | None) -> RGB | None:
    if not value:
        return None
    v = value.strip().lower()
    if v in ("none", "transparent"):
        return None
    if v in _NAMED:
        return _NAMED[v]
    m = _HEX.match(v)
    if m:
        h = m.group(1)
        if len(h) == 3:
            h = "".join(ch * 2 for ch in h)
        return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    rm = _RGB_FN.match(v)
    if rm:
        nums = [x.strip() for x in rm.group(1).split(",")]
        if len(nums) >= 3:
            try:
                return (int(float(nums[0])), int(float(nums[1])), int(float(nums[2])))
            except ValueError:
                return None
    return None
