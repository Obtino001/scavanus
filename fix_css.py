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

    has_section_color = "render 'section-color-css'" in content or 'render "section-color-css"' in content
    has_block_color = "render 'block-color-css'" in content or 'render "block-color-css"' in content
    has_blocks = 'section.blocks' in content
    
    # 1. Inject section-color-css if missing
    if not has_section_color:
        insert_text = "\n{%- render 'section-color-css' -%}\n"
        # Try to insert before <style>
        if '<style>' in content:
            content = content.replace('<style>', insert_text + '<style>', 1)
        elif "{%- render 'section-spacing-collapsing' -%}" in content:
            content = content.replace("{%- render 'section-spacing-collapsing' -%}", "{%- render 'section-spacing-collapsing' -%}" + insert_text, 1)
        else:
            # Just put it at the very top
            content = insert_text + content
        modified = True

    # 2. Inject block-color-css if missing but has blocks
    if has_blocks and not has_block_color:
        block_text = "\n{%- for block in section.blocks -%}\n  {%- render 'block-color-css', block: block -%}\n{%- endfor -%}\n"
        # Insert it right after section-color-css
        if "{%- render 'section-color-css' -%}" in content:
            content = content.replace("{%- render 'section-color-css' -%}", "{%- render 'section-color-css' -%}" + block_text, 1)
        else:
            # Fallback
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
