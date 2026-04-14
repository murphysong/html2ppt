from __future__ import annotations

from utils.theme import Theme


def px_to_inch_x(px: float, theme: Theme) -> float:
    return round(px * theme.px_to_inch_x, 4)


def px_to_inch_y(px: float, theme: Theme) -> float:
    return round(px * theme.px_to_inch_y, 4)
