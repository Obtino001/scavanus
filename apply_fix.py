import os
import re
import json

SECTIONS_DIR = r"C:\Users\Yasir\Pictures\world-of-comfort\scavanus\sections"

def get_liquid_files():
    return [os.path.join(SECTIONS_DIR, f) for f in os.listdir(SECTIONS_DIR) if f.endswith('.liquid')]

def extract_label_from_selector(pre_text):
    last_brace_close = pre_text.rfind('}')
    if last_brace_close != -1:
        pre_text = pre_text[last_brace_close+1:]
        
    last_brace_open = pre_text.rfind('{')
    if last_brace_open != -1:
        selector = pre_text[:last_brace_open].strip()
        selector = selector.split(',')[0].strip()
        selector = re.sub(r'#shopify-section-\{\{\s*section\.id\s*\}\}\s*', '', selector)
        selector = re.sub(r'#block-\{\{\s*section\.id\s*\}\}-\{\{\s*block\.id\s*\}\}\s*', '', selector)
        
        parts = selector.split()
        if parts:
            last_part = parts[-1]
            last_part = last_part.split(':')[0]
            last_part = last_part.replace('.', '')
            last_part = last_part.replace('-', ' ').replace('_', ' ')
            last_part = last_part.strip().capitalize()
            if last_part:
                return last_part
            
    return "Custom element"

def fix_trailing_commas(json_str):
    json_str = re.sub(r',\s*\}', '}', json_str)
    json_str = re.sub(r',\s*\]', ']', json_str)
    return json_str

def update_liquid_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
        
    schema_match = re.search(r'{%\s*schema\s*%}(.*?){%\s*endschema\s*%}', content, re.DOTALL)
    if not schema_match:
        return False
        
    schema_str = schema_match.group(1)
    try:
        schema = json.loads(fix_trailing_commas(schema_str))
    except Exception as e:
        print(f"Error parsing JSON in {os.path.basename(file_path)}: {e}")
        return False

    style_pattern = re.compile(r'<style[^>]*>(.*?)</style>', re.DOTALL | re.IGNORECASE)
    
    section_settings = []
    block_settings_dict = {}
    
    color_counter = 1
    new_content = content
    
    match_found = False
    
    for style_match in style_pattern.finditer(content):
        style_content = style_match.group(1)
        start_index = max(0, style_match.start() - 500)
        pre_context = content[start_index:style_match.start()]
        
        is_block = False
        block_var = "block"
        loop_match = re.search(r'{%\s*for\s+(\w+)\s+in\s+(?:section\.blocks|vs)\s*%}', pre_context)
        if loop_match:
            is_block = True
            block_var = loop_match.group(1)
        elif 'block.id' in style_content or 'block.settings' in style_content:
            is_block = True
            
        def replacer(match):
            nonlocal color_counter, match_found
            match_found = True
            prop = match.group('prop')
            val = match.group('val')
            
            if 'var(' in val or '{{' in val:
                return match.group(0)
                
            match_start = match.start()
            pre_css = style_content[:match_start]
            label_name = extract_label_from_selector(pre_css)
            
            prop_label = "Background" if "background" in prop else "Text/Icon color"
            if prop in ("border", "border-color", "border-top", "border-bottom"):
                prop_label = "Border color"
                
            full_label = f"{label_name} {prop_label}"
            
            setting_id = f"custom_color_{color_counter}"
            
            new_setting = {
                "type": "color",
                "id": setting_id,
                "label": full_label[:50],
                "default": val.strip()
            }
            
            if is_block:
                if 'blocks' in schema:
                    for b in schema['blocks']:
                        if b['type'] not in block_settings_dict:
                            block_settings_dict[b['type']] = []
                        block_settings_dict[b['type']].append(new_setting)
                replacement = f"{prop}: {{{{{block_var}.settings.{setting_id} | default: '{val.strip()}'}}}}{match.group('end_semi')}"
            else:
                section_settings.append(new_setting)
                replacement = f"{prop}: {{{{section.settings.{setting_id} | default: '{val.strip()}'}}}}{match.group('end_semi')}"
                
            color_counter += 1
            return replacement

        color_pattern = re.compile(r'(?P<prop>color|background|background-color|border|border-color|border-top|border-bottom|fill|stroke)\s*:\s*(?P<val>#[0-9a-fA-F]{3,6}|rgba?\([^)]+\))(?P<end_semi>\s*;?)')
        
        new_style_content = color_pattern.sub(replacer, style_content)
        new_content = new_content.replace(style_match.group(0), f"<style>\n{new_style_content}\n</style>")

    if not match_found:
        return False
        
    if not section_settings and not block_settings_dict:
        return False

    if section_settings:
        if "settings" not in schema:
            schema["settings"] = []
        schema["settings"].append({
            "type": "header",
            "content": "Custom Added Colors"
        })
        schema["settings"].extend(section_settings)
        
    if block_settings_dict and "blocks" in schema:
        for b in schema["blocks"]:
            if b["type"] in block_settings_dict:
                if "settings" not in b:
                    b["settings"] = []
                b["settings"].append({
                    "type": "header",
                    "content": "Custom Added Colors"
                })
                b["settings"].extend(block_settings_dict[b["type"]])

    new_schema_str = json.dumps(schema, indent=2)
    new_content = new_content.replace(schema_str, f"\n{new_schema_str}\n")
    
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(new_content)
        
    return True

def main():
    files = get_liquid_files()
    processed = 0
    for f in files:
        res = update_liquid_file(f)
        if res:
            print(f"Updated {os.path.basename(f)}")
            processed += 1
        else:
            print(f"Skipped {os.path.basename(f)}")
            
    print(f"Total files updated: {processed}")

if __name__ == '__main__':
    main()
