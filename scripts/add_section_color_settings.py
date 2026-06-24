#!/usr/bin/env python3
"""Add standard Dawn/Prestige-style color settings to all theme section schemas."""

import json
import re
from pathlib import Path

SECTIONS_DIR = Path(__file__).resolve().parent.parent / "sections"
RENDER_TAG = "{%- render 'section-color-css' -%}"

STANDARD_SECTION_COLORS = [
    ("background", "color", "Background"),
    ("background_gradient", "color_background", "Background gradient"),
    ("text_color", "color", "Text"),
    ("heading_color", "color", "Heading"),
    ("heading_gradient", "color_background", "Heading gradient"),
    ("button_background", "color", "Button background"),
    ("button_text_color", "color", "Button text"),
    ("card_background", "color", "Card/block background"),
    ("card_text_color", "color", "Card/block text"),
]

BLOCK_COLORS = [
    ("background", "color", "Background"),
    ("text_color", "color", "Text"),
    ("button_background", "color", "Button background"),
    ("button_text_color", "color", "Button text"),
]

# Sections with specialized color systems — only add missing standard keys, no render injection issues
SKIP_RENDER = {
    "cart-drawer.liquid",
    "search-drawer.liquid",
    "privacy-banner.liquid",
    "newsletter-popup.liquid",
    "variant-added.liquid",
}


def make_setting(setting_id: str, setting_type: str, label: str) -> dict:
    return {"type": setting_type, "id": setting_id, "label": label}


def has_colors_header(settings: list) -> bool:
    return any(
        s.get("type") == "header" and "color" in s.get("content", "").lower()
        for s in settings
    )


def existing_ids(settings: list) -> set:
    return {s.get("id") for s in settings if isinstance(s, dict) and "id" in s}


def add_section_colors(settings: list) -> list:
    ids = existing_ids(settings)
    to_add = [make_setting(sid, stype, label) for sid, stype, label in STANDARD_SECTION_COLORS if sid not in ids]
    if not to_add:
        return settings

    if not has_colors_header(settings):
        to_add.insert(0, {
            "type": "header",
            "content": "Colors",
            "info": "Gradient replaces solid colors when set.",
        })

    return settings + to_add


def add_block_colors(blocks: list) -> list:
    for block in blocks:
        if not isinstance(block, dict):
            continue
        block_settings = block.get("settings", [])
        ids = existing_ids(block_settings)
        to_add = [make_setting(sid, stype, label) for sid, stype, label in BLOCK_COLORS if sid not in ids]
        if not to_add:
            continue
        if not has_colors_header(block_settings):
            to_add.insert(0, {"type": "header", "content": "Colors"})
        block["settings"] = block_settings + to_add
    return blocks


def inject_render(liquid: str, filename: str) -> str:
    if filename in SKIP_RENDER or RENDER_TAG in liquid:
        return liquid

    if "{% schema %}" not in liquid:
        return liquid

    spacing = "{%- render 'section-spacing-collapsing' -%}"
    if spacing in liquid:
        replacement = spacing + "\n\n" + RENDER_TAG
        if replacement not in liquid:
            liquid = liquid.replace(spacing, replacement, 1)
        return liquid

    # Insert after first line for sections without spacing-collapsing
    lines = liquid.split("\n", 1)
    if len(lines) == 2 and RENDER_TAG not in lines[0]:
        return lines[0] + "\n" + RENDER_TAG + "\n\n" + lines[1]
    return liquid


def process_file(path: Path) -> bool:
    content = path.read_text(encoding="utf-8")
    match = re.search(r"{% schema %}\s*(\{.*?\})\s*{% endschema %}", content, re.DOTALL)
    if not match:
        return False

    original_json = match.group(1)
    try:
        schema = json.loads(original_json)
    except json.JSONDecodeError as exc:
        print(f"  SKIP {path.name}: invalid JSON ({exc})")
        return False

    if "settings" in schema:
        schema["settings"] = add_section_colors(schema.get("settings", []))
    if "blocks" in schema:
        schema["blocks"] = add_block_colors(schema.get("blocks", []))

    new_json = json.dumps(schema, indent=2, ensure_ascii=False)
    new_content = content[: match.start(1)] + new_json + content[match.end(1) :]
    new_content = inject_render(new_content, path.name)

    if new_content != content:
        path.write_text(new_content, encoding="utf-8")
        return True
    return False


def main():
    updated = 0
    for path in sorted(SECTIONS_DIR.glob("*.liquid")):
        if process_file(path):
            print(f"Updated: {path.name}")
            updated += 1
    print(f"\nDone. Updated {updated} section(s).")


if __name__ == "__main__":
    main()
