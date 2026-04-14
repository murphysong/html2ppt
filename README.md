# html_to_ppt

A dual-mode HTML-to-PPTX project for editable slides.

## Modes

### 1) Template mode
Use semantic page types like:
- cover
- toc
- overview_cards
- compare_2col
- timeline
- left_text_right_image
- conclusion

These are fast, stable, and suitable for batch report generation.

### 2) Free layout mode
Use `page_type = free_layout` and `render.mode = absolute_elements`.

This mode is for high-fidelity page reconstruction from constrained HTML.

## Supported Inputs
- JSON slide spec (`slides.example.json`)
- constrained HTML (`examples/5.html`, `examples/6.html`, `examples/7.html`)

## Constraints for HTML
Recommended:
- fixed 1600x900 canvas
- absolute or stable block layout
- text/image/rect/rounded_rect/line
- simple background, borders, and footer

Not recommended for MVP:
- complex flex/grid dependency chains
- CSS transform
- advanced gradients
- filters
- pseudo-elements
- dynamic scripts

## Commands

Render from JSON:
```bash
python build_ppt.py --input examples/slides.example.json --output output/demo.pptx
```

Render from constrained HTML:
```bash
python build_ppt.py --html examples/5.html --output output/from_html_5.pptx
```
