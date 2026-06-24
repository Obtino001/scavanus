import os
import glob
import re

directory = r'c:\Users\Yasir\Pictures\world-of-comfort\scavanus\sections'
files = glob.glob(os.path.join(directory, '*.liquid'))

files_fixed = 0

for file in files:
    with open(file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    modified = False

    # 1. Check if section-color-css is rendered inside conditional blocks like {% unless %} or {% if %}
    # An easy way to fix is just to pull it out.
    # Actually, let's just make sure it's at the top level. We can remove it entirely and add it back to the safe spot.
    
    # regex to remove all instances
    content_new = re.sub(r'\{%-?\s*render\s+[\'"]section-color-css[\'"]\s*-?%\}', '', content)
    
    if content_new != content:
        # It was removed. Now let's add it back in a safe place.
        insert_text = "\n{%- render 'section-color-css' -%}\n"
        if '<style>' in content_new:
            content_new = content_new.replace('<style>', insert_text + '<style>', 1)
        elif "{%- render 'section-spacing-collapsing' -%}" in content_new:
            content_new = content_new.replace("{%- render 'section-spacing-collapsing' -%}", "{%- render 'section-spacing-collapsing' -%}" + insert_text, 1)
        else:
            content_new = insert_text + content_new
            
    if content_new != original_content:
        content = content_new
        modified = True

    # 2. Add block-color-css if it's missing entirely but blocks exist
    has_block_color = "render 'block-color-css'" in content or 'render "block-color-css"' in content
    has_blocks = 'section.blocks' in content
    if has_blocks and not has_block_color:
        block_text = "\n{%- for block in section.blocks -%}\n  {%- render 'block-color-css', block: block -%}\n{%- endfor -%}\n"
        # Insert it right after section-color-css
        if "{%- render 'section-color-css' -%}" in content:
            content = content.replace("{%- render 'section-color-css' -%}", "{%- render 'section-color-css' -%}" + block_text, 1)
        else:
            if '<style>' in content:
                content = content.replace('<style>', block_text + '<style>', 1)
            else:
                content = block_text + content
        modified = True
        
    if modified:
        with open(file, 'w', encoding='utf-8') as f:
            f.write(content)
        files_fixed += 1

print(f"Fixed {files_fixed} files.")
