import json
import re
from pathlib import Path

path = Path(r"c:\Users\Yasir\Pictures\world-of-comfort\scavanus\sections\main-product.liquid")
content = path.read_text(encoding="utf-8")

match = re.search(r"{% schema %}\s*(\{.*?\})\s*{% endschema %}", content, re.DOTALL)
if not match:
    print("No schema found")
else:
    original_json = match.group(1)
    schema = json.loads(original_json)
    
    countdown_block = {
      "type": "countdown_timer",
      "name": "Countdown timer",
      "settings": [
        {
          "type": "text",
          "id": "prefix_text",
          "label": "Prefix text",
          "default": "Udløber om:"
        },
        {
          "type": "number",
          "id": "evergreen_hours",
          "label": "Timer duration (hours)",
          "info": "Set to 0 to use fixed end date below.",
          "default": 93
        },
        {
          "type": "text",
          "id": "end_date",
          "label": "End date/time",
          "info": "Format: YYYY-MM-DD HH:MM:SS (e.g. 2026-12-31 23:59:59)",
          "default": "2026-12-31 23:59:59"
        },
        {
          "type": "color",
          "id": "bg_color",
          "label": "Background color",
          "default": "#FDEDF5"
        },
        {
          "type": "color",
          "id": "text_color",
          "label": "Text color",
          "default": "#7A0C2E"
        }
      ]
    }
    
    # Check if countdown_timer already exists
    exists = any(b.get("type") == "countdown_timer" for b in schema.get("blocks", []))
    if not exists:
        schema["blocks"].append(countdown_block)
        new_json = json.dumps(schema, indent=2, ensure_ascii=False)
        new_content = content[:match.start(1)] + new_json + content[match.end(1):]
        path.write_text(new_content, encoding="utf-8")
        print("Added countdown_timer block schema")
    else:
        print("countdown_timer already exists")
