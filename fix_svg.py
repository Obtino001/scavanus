import os
import re

directory = r'c:\Users\Yasir\Pictures\world-of-comfort\scavanus\sections'

count = 0
for filename in os.listdir(directory):
    if not filename.endswith('.liquid'): continue
    file_path = os.path.join(directory, filename)
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    original_content = content
    
    matches = re.finditer(r'({%-\s*capture\s+sizes\s*-%}.*?{%-\s*endcapture\s*-%}\s*{%-\s*capture\s+widths\s*-%}.*?{%-\s*endcapture\s*-%}\s*{{-\s*(block\.settings\.custom_icon|section\.settings\.custom_icon)\s*\|\s*image_url.*?image_tag:.*?}})', content, re.DOTALL)
    
    for match in matches:
        full_match = match.group(1)
        icon_var = match.group(2)
        
        # Don't replace if already modified with .svg check
        if '.svg' in full_match or 'custom_icon_url contains' in content:
            continue
            
        new_block = f'''{{%- assign custom_icon_url = {icon_var} | image_url -%}}
                  {{%- if custom_icon_url contains '.svg' -%}}
                    <span class="image-icon image-icon--svg" style="--svg-url: url('{{{{ custom_icon_url }}}}'); aspect-ratio: {{{{ {icon_var}.aspect_ratio | default: 1 }}}}; display: inline-block; background-color: currentColor; -webkit-mask: var(--svg-url) no-repeat center center / contain; mask: var(--svg-url) no-repeat center center / contain;"></span>
                  {{%- else -%}}
                    {full_match}
                  {{%- endif -%}}'''
        
        content = content.replace(full_match, new_block)

    if content != original_content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f'Updated SVG rendering in {filename}')
        count += 1

print(f'Total sections updated: {count}')
