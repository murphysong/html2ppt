# HTML to PPT Engineering Rules

## Project Goal
Build a Python-based pipeline that converts constrained HTML slides into editable PPTX using python-pptx.

## Core Principles
1. Prefer stable, modular code over clever shortcuts.
2. Separate parsing, normalization, and PPT rendering.
3. Support two modes:
   - template mode
   - free_layout mode
4. Always preserve editability. Never rasterize a whole slide unless explicitly requested.
5. Record degraded mappings for unsupported HTML/CSS features.
6. Keep all layout decisions deterministic and configurable.

## Required Workflow
1. Validate JSON against schema before rendering.
2. Keep theme-driven rendering parameters in config/theme.json.
3. Put HTML parsing logic in parser/.
4. Put pptx drawing logic in renderer/.
5. Put size/unit/color helpers in utils/.
6. Add logs for unsupported CSS or approximated mappings.

## Coding Rules
- Use Python 3.11+
- Add type hints where practical
- Avoid giant single-file scripts
- Keep functions small and testable
- Do not hardcode slide-specific constants inside renderer modules
- All dimensions must be in inches after normalization
- All colors must be normalized to RGB tuples before rendering

## Rendering Rules
- Slide size is 13.333 x 7.5 inch by default
- HTML prototype base is 1600 x 900 px
- Convert px to inch through theme calibration
- Text boxes must preserve alignment and margins
- Rounded rectangles should use nearest PowerPoint approximation
- Unsupported features must be reported, not silently ignored

## Output Expectations
When you modify rendering logic:
- explain what changed
- explain known limitations
- list degraded mappings
- keep sample inputs runnable

## Useful Commands
- python build_ppt.py --input examples/slides.example.json --output output/demo.pptx
- python build_ppt.py --html examples/5.html --output output/from_html_5.pptx
