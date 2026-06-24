import os
import re

directory = r'c:\Users\Yasir\Pictures\world-of-comfort\scavanus\sections'

count_visible_if = 0
for filename in os.listdir(directory):
    if not filename.endswith('.liquid'): continue
    file_path = os.path.join(directory, filename)
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content
    # Remove visible_if: .*custom_icon == blank.*
    content = re.sub(r'\"visible_if\":\s*\"{{\s*[^}]*?custom_icon\s*==\s*blank\s*}}\",?', '', content)

    if content != original_content:
        # Also clean up trailing commas from JSON objects if needed
        content = re.sub(r',\s*}', '\n}', content)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f'Removed visible_if from {filename}')
        count_visible_if += 1

print(f'Total visible_if removed: {count_visible_if}')
