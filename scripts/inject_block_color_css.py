#!/usr/bin/env python3
"""Inject block-color-css render into section block loops."""

import re
from pathlib import Path

SECTIONS_DIR = Path(__file__).resolve().parent.parent / "sections"
RENDER = "{%- render 'block-color-css', block: block -%}"
PATTERN = re.compile(r"(\{%-?\s*for\s+block\s+in\s+section\.blocks\s*-?%\})", re.IGNORECASE)


def main():
    updated = []
    for path in sorted(SECTIONS_DIR.glob("*.liquid")):
        content = path.read_text(encoding="utf-8")
        if RENDER in content or "for block in section.blocks" not in content:
            continue

        def replacer(match):
            return match.group(1) + "\n            " + RENDER

        new_content, count = PATTERN.subn(replacer, content, count=1)
        if count:
            path.write_text(new_content, encoding="utf-8")
            updated.append(path.name)

    print(f"Injected block-color-css in {len(updated)} sections")
    for name in updated:
        print(f"  {name}")


if __name__ == "__main__":
    main()
