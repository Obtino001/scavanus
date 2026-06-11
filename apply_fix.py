import os
import re
import json

SECTIONS_DIR = r"C:\Users\Yasir\Pictures\world-of-comfort\scavanus\sections"

def get_liquid_files():
    files = []
    for f in os.listdir(SECTIONS_DIR):
        if f.endswith('.liquid'):
            files.append(os.path.join(SECTIONS_DIR, f))
    return files

def update_liquid_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
        
    schema_match = re.search(r'{%\s*schema\s*%}(.*?){%\s*endschema\s*%}', content, re.DOTALL)
    if not schema_match:
        return False
        
    schema_str = schema_match.group(1)
    try:
        schema = json.loads(schema_str)
    except Exception as e:
        print(f"Error parsing JSON in {os.path.basename(file_path)}: {e}")
        return False

    style_pattern = re.compile(r'<style[^>]*>(.*?)</style>', re.DOTALL | re.IGNORECASE)
    
    section_color_settings = []
    block_color_settings = []
    
    color_counter = 1
    
    def replacer(match):
        nonlocal color_counter
        prop = match.group('prop')
        val = match.group('val')
        
        # Avoid replacing things that look like rgb(var(...)) if they don't have hardcoded values
        if 'var(' in val:
            return match.group(0)
            
        setting_id = f"custom_{prop.replace('-', '_')}_{color_counter}"
        
        # Very simple heuristic: if the style is inside a liquid block loop or mentions block.id
        # we assign it to block. Here we just assign all to section unless we can detect block.
        # But wait, without AST parsing, it's hard to tell if <style> is inside a block loop.
        # Let's assume all go to section for now, unless the match string or nearby text has 'block.id'.
        
        # To be safe, we will add to section.settings
        section_color_settings.append({
            "type": "color",
            "id": setting_id,
            "label": f"Custom {prop} {color_counter}",
            "default": val.strip()
        })
        
        replacement = f"{prop}: {{{{ section.settings.{setting_id} }}}}{match.group('end_semi')}"
        color_counter += 1
        return replacement

    # Replace in style tags
    new_content = content
    for style_match in style_pattern.finditer(content):
        style_content = style_match.group(1)
        
        # Regex to find CSS color declarations, capturing the property, value, and following semicolon/space
        color_pattern = re.compile(r'(?P<prop>color|background|background-color|border|border-color|border-top|border-bottom|fill|stroke)\s*:\s*(?P<val>#[0-9a-fA-F]{3,6}|rgba?\([^)]+\))(?P<end_semi>\s*;?)')
        
        new_style_content = color_pattern.sub(replacer, style_content)
        new_content = new_content.replace(style_match.group(0), f"<style>\n{new_style_content}\n</style>")

    if not section_color_settings:
        return False

    if "settings" not in schema:
        schema["settings"] = []
        
    schema["settings"].append({
        "type": "header",
        "content": "Custom Added Colors"
    })
    schema["settings"].extend(section_color_settings)
    
    # We must format schema back to JSON
    new_schema_str = json.dumps(schema, indent=2)
    new_content = new_content.replace(schema_str, f"\n{new_schema_str}\n")
    
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(new_content)
        
    return True

def main():
    files = get_liquid_files()
    processed = 0
    for f in files:
        if update_liquid_file(f):
            print(f"Updated {os.path.basename(f)}")
            processed += 1
            
    print(f"Total files updated: {processed}")

if __name__ == '__main__':
    main()
