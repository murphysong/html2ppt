from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import tinycss2


UNSUPPORTED = {
    "transform",
    "filter",
    "backdrop-filter",
    "animation",
    "transition",
    "grid-template-areas",
}


@dataclass
class CssModel:
    class_rules: dict[str, dict[str, str]] = field(default_factory=dict)
    tag_rules: dict[str, dict[str, str]] = field(default_factory=dict)
    diagnostics: list[str] = field(default_factory=list)


def _decls(content: list[Any]) -> dict[str, str]:
    out: dict[str, str] = {}
    declarations = tinycss2.parse_declaration_list(content, skip_whitespace=True, skip_comments=True)
    for d in declarations:
        if d.type != "declaration":
            continue
        out[d.name.strip().lower()] = tinycss2.serialize(d.value).strip()
    return out


def parse_css(style_text: str) -> CssModel:
    model = CssModel()
    rules = tinycss2.parse_stylesheet(style_text, skip_whitespace=True, skip_comments=True)
    for rule in rules:
        if rule.type != "qualified-rule":
            continue
        selector = tinycss2.serialize(rule.prelude).strip()
        if "::" in selector:
            model.diagnostics.append(f"Ignored pseudo-element selector: {selector}")
            continue
        decl = _decls(rule.content)
        for k in decl:
            if k in UNSUPPORTED:
                model.diagnostics.append(f"Unsupported CSS property ignored: {k} ({selector})")
        if selector.startswith("."):
            model.class_rules[selector[1:]] = decl
        elif selector.isalpha() or selector in {"*", "body"}:
            model.tag_rules[selector] = decl
        else:
            model.diagnostics.append(f"Complex selector simplified/ignored: {selector}")
    return model
