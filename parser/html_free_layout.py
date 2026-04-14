from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
from typing import Any

from bs4 import BeautifulSoup, Tag

from parser.css_parser import CssModel, parse_css
from utils.colors import parse_color
from utils.theme import Theme
from utils.units import px_to_inch_x, px_to_inch_y


@dataclass
class Box:
    left: float
    top: float
    width: float
    height: float


def _px(value: str | None, fallback: float = 0.0) -> float:
    if not value:
        return fallback
    s = value.strip().lower().replace("px", "")
    if s == "100%":
        return 1600.0
    try:
        return float(s)
    except ValueError:
        return fallback


def _padding(style: dict[str, str]) -> tuple[float, float, float, float]:
    p = style.get("padding")
    if not p:
        return (
            _px(style.get("padding-top"), 0),
            _px(style.get("padding-right"), 0),
            _px(style.get("padding-bottom"), 0),
            _px(style.get("padding-left"), 0),
        )
    vals = [x.strip() for x in p.split()]
    nums = [_px(v, 0) for v in vals]
    if len(nums) == 1:
        return nums[0], nums[0], nums[0], nums[0]
    if len(nums) == 2:
        return nums[0], nums[1], nums[0], nums[1]
    if len(nums) == 3:
        return nums[0], nums[1], nums[2], nums[1]
    return nums[0], nums[1], nums[2], nums[3]


def _merged_style(el: Tag, css: CssModel) -> dict[str, str]:
    merged: dict[str, str] = {}
    merged.update(css.tag_rules.get("*", {}))
    merged.update(css.tag_rules.get(el.name or "", {}))
    for c in el.get("class", []):
        merged.update(css.class_rules.get(c, {}))
    inline = el.get("style")
    if inline:
        for item in inline.split(";"):
            if ":" in item:
                k, v = item.split(":", 1)
                merged[k.strip().lower()] = v.strip()
    return merged


def _text_style(style: dict[str, str], default_color: tuple[int, int, int]) -> dict[str, Any]:
    rgb = parse_color(style.get("color")) or default_color
    return {
        "font_family": style.get("font-family", 'Microsoft YaHei').split(",")[0].strip('" '),
        "font_size_pt": _px(style.get("font-size"), 16),
        "bold": style.get("font-weight", "").strip() in {"bold", "700", "800"},
        "color": list(rgb),
        "align": "left",
        "valign": "top",
    }


def _mk_text(id_: str, txt: str, box: Box, style: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": id_, "type": "text", "left": box.left, "top": box.top,
        "width": box.width, "height": box.height, "text": txt.strip(), "style": style,
    }


def parse_html_to_render(html_path: str | Path, theme: Theme) -> dict[str, Any]:
    source = Path(html_path).read_text(encoding="utf-8")
    soup = BeautifulSoup(source, "lxml")
    style_text = "\n".join(x.get_text() for x in soup.find_all("style"))
    css = parse_css(style_text)
    diags = list(css.diagnostics)

    slide = soup.select_one(".slide")
    if not slide:
        raise ValueError("No .slide root found")
    slide_style = _merged_style(slide, css)
    slide_w = _px(slide_style.get("width"), 1600)
    slide_h = _px(slide_style.get("height"), 900)
    if slide_w != 1600 or slide_h != 900:
        diags.append(f"Canvas normalized from {slide_w}x{slide_h}px to 1600x900 assumption")
    p_top, p_right, p_bottom, p_left = _padding(slide_style)

    elements: list[dict[str, Any]] = []

    # top border bar detection
    top_bar_h = 0.0
    border_top = slide_style.get("border-top")
    if border_top:
        m = re.search(r"([\d.]+)px", border_top)
        if m:
            top_bar_h = float(m.group(1))
            col = parse_color(border_top.split()[-1]) or (0, 82, 212)
            elements.append({
                "id": "top_border_bar",
                "type": "shape",
                "shape": "rect",
                "left": 0.0,
                "top": 0.0,
                "width": theme.slide_width_inch,
                "height": px_to_inch_y(top_bar_h, theme),
                "style": {"fill_color": list(col), "line_color": list(col), "line_width_pt": 0.0},
            })
    else:
        header_line = slide.select_one(".header-line")
        if header_line:
            hs = _merged_style(header_line, css)
            top_bar_h = _px(hs.get("height"), 8)
            col = parse_color(hs.get("background")) or (67, 100, 247)
            elements.append({
                "id": "top_border_bar", "type": "shape", "shape": "rect",
                "left": 0.0, "top": 0.0,
                "width": theme.slide_width_inch,
                "height": px_to_inch_y(top_bar_h, theme),
                "style": {"fill_color": list(col), "line_color": list(col), "line_width_pt": 0.0},
            })
            if "gradient" in (hs.get("background", "") or ""):
                diags.append("Gradient background downgraded to solid color for top bar")

    content_left = p_left
    cursor_top = p_top + max(top_bar_h, 0)
    content_width = 1600 - p_left - p_right

    # title blocks
    idx = slide.select_one(".title-index, .index")
    if idx:
        s = _merged_style(idx, css)
        box = Box(px_to_inch_x(content_left, theme), px_to_inch_y(cursor_top, theme), px_to_inch_x(content_width * 0.45, theme), px_to_inch_y(40, theme))
        elements.append(_mk_text("title_index", idx.get_text(" ", strip=True), box, _text_style(s, (67, 100, 247))))
        cursor_top += 42

    title = slide.select_one(".title-main, .title")
    if title:
        s = _merged_style(title, css)
        box = Box(px_to_inch_x(content_left, theme), px_to_inch_y(cursor_top, theme), px_to_inch_x(content_width * 0.9, theme), px_to_inch_y(62, theme))
        elements.append(_mk_text("title", title.get_text(" ", strip=True), box, _text_style(s, (26, 26, 26))))
        cursor_top += 68

    subtitle = slide.select_one(".subtitle")
    if subtitle:
        s = _merged_style(subtitle, css)
        border = s.get("border-left")
        if border:
            bcol = parse_color(border.split()[-1]) or (67, 100, 247)
            bw = _px(border.split()[0], 4)
            elements.append({
                "id": "subtitle_bar", "type": "shape", "shape": "rect",
                "left": px_to_inch_x(content_left, theme), "top": px_to_inch_y(cursor_top, theme),
                "width": px_to_inch_x(bw, theme), "height": px_to_inch_y(36, theme),
                "style": {"fill_color": list(bcol), "line_color": list(bcol), "line_width_pt": 0.0},
            })
        box = Box(px_to_inch_x(content_left + 15, theme), px_to_inch_y(cursor_top - 2, theme), px_to_inch_x(content_width * 0.9, theme), px_to_inch_y(40, theme))
        elements.append(_mk_text("subtitle", subtitle.get_text(" ", strip=True), box, _text_style(s, (102, 102, 102))))
        cursor_top += 52

    # cards/panels
    cards = slide.select(".card, .case-card, .comp-box, .eval-card, .constraint-card, .case-item, .alert-box")
    cols = 2
    if slide.select_one(".constraint-grid"):
        cols = 3
    x_gap = 20
    y_gap = 20
    card_w = (content_width - x_gap * (cols - 1)) / cols
    y = cursor_top
    for i, c in enumerate(cards):
        cs = _merged_style(c, css)
        bg = parse_color(cs.get("background")) or parse_color(cs.get("background-color")) or (248, 249, 250)
        line = parse_color(cs.get("border", "").split()[-1] if cs.get("border") else None) or (230, 235, 240)
        radius = _px(cs.get("border-radius"), 10)
        h = max(_px(cs.get("height"), 160), 120)
        col_idx = i % cols
        row_idx = i // cols
        left_px = content_left + col_idx * (card_w + x_gap)
        top_px = y + row_idx * (h + y_gap)
        elements.append({
            "id": f"panel_{i+1}", "type": "shape", "shape": "rounded_rect",
            "left": px_to_inch_x(left_px, theme), "top": px_to_inch_y(top_px, theme),
            "width": px_to_inch_x(card_w, theme), "height": px_to_inch_y(h, theme),
            "style": {"fill_color": list(bg), "line_color": list(line), "line_width_pt": 1.0, "radius_inch": px_to_inch_x(radius, theme)},
        })
        text = c.get_text(" ", strip=True)
        if text:
            elements.append({
                "id": f"panel_{i+1}_text", "type": "text",
                "left": px_to_inch_x(left_px + 14, theme), "top": px_to_inch_y(top_px + 12, theme),
                "width": px_to_inch_x(card_w - 28, theme), "height": px_to_inch_y(h - 20, theme),
                "text": text,
                "style": {
                    "font_family": "Microsoft YaHei", "font_size_pt": 14.0,
                    "color": [68, 68, 68], "align": "left", "valign": "top"
                },
            })

    # footer separator & footer text
    footer = slide.select_one(".footer")
    if footer:
        fs = _merged_style(footer, css)
        footer_top = 900 - p_bottom - 35
        line_col = parse_color((fs.get("border-top") or "").split()[-1]) or (238, 238, 238)
        elements.append({
            "id": "footer_separator", "type": "line", "left": 0, "top": 0, "width": 0, "height": 0,
            "x1": px_to_inch_x(content_left, theme), "y1": px_to_inch_y(footer_top, theme),
            "x2": px_to_inch_x(1600 - p_right, theme), "y2": px_to_inch_y(footer_top, theme),
            "style": {"line_color": list(line_col), "line_width_pt": 1.0},
        })
        parts = [x.get_text(" ", strip=True) for x in footer.find_all(recursive=False) if isinstance(x, Tag)]
        if not parts:
            parts = [footer.get_text(" ", strip=True)]
        if parts:
            elements.append(_mk_text(
                "footer_left",
                parts[0],
                Box(px_to_inch_x(content_left, theme), px_to_inch_y(footer_top + 8, theme), px_to_inch_x(content_width * 0.7, theme), px_to_inch_y(24, theme)),
                {"font_family": "Microsoft YaHei", "font_size_pt": 10.0, "color": [153, 153, 153], "align": "left", "valign": "middle"},
            ))
        if len(parts) > 1:
            elements.append(_mk_text(
                "footer_right",
                parts[-1],
                Box(px_to_inch_x(content_left + content_width * 0.72, theme), px_to_inch_y(footer_top + 8, theme), px_to_inch_x(content_width * 0.28, theme), px_to_inch_y(24, theme)),
                {"font_family": "Aptos", "font_size_pt": 10.0, "color": [153, 153, 153], "align": "right", "valign": "middle"},
            ))

    return {"mode": "absolute_elements", "elements": elements, "diagnostics": diags}
