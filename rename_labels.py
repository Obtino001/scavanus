import os
import re
import json

SECTIONS_DIR = r"C:\Users\Yasir\Pictures\world-of-comfort\scavanus\sections"

def get_liquid_files():
    return [os.path.join(SECTIONS_DIR, f) for f in os.listdir(SECTIONS_DIR) if f.endswith('.liquid')]

def extract_label_from_selector(pre_text):
    # Find all selectors by splitting on '}'
    parts = pre_text.split('}')
    if not parts:
        return "Custom element"
    
    # The last part should contain the current selector
    last_part = parts[-1]
    
    # The selector is before the first '{' in this last part
    # But wait, there could be liquid logic like {% if ... %} inside the selector or rule block.
    # Let's remove all liquid logic first.
    
    # Safe remove of closed liquid logic
    clean_text = re.sub(r'\{\{.*?\}\}', '', last_part, flags=re.DOTALL)
    clean_text = re.sub(r'\{%.*?%\}', '', clean_text, flags=re.DOTALL)
    
    # Remove the trailing unclosed {{ or {% that might have caused the issue
    clean_text = re.sub(r'\{\{.*$', '', clean_text, flags=re.DOTALL)
    clean_text = re.sub(r'\{%.*$', '', clean_text, flags=re.DOTALL)
    
    brace_open_idx = clean_text.find('{')
    if brace_open_idx != -1:
        selector = clean_text[:brace_open_idx].strip()
        
        # Clean up selector
        selector = selector.split(',')[0].strip()
        selector = re.sub(r'#shopify-section-\{\{\s*section\.id\s*\}\}\s*', '', selector)
        selector = re.sub(r'#block-\{\{\s*section\.id\s*\}\}-\{\{\s*block\.id\s*\}\}\s*', '', selector)
        selector = selector.replace('#shopify-section-', '').replace('.featured-collections-tabs', '')
        
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

def rename_labels(file_path):
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
    styles = style_pattern.findall(content)
    if not styles:
        return False
    
    combined_styles = "\n".join(styles)
    
    modified = False

    def update_settings_list(settings_list, is_block=False):
        nonlocal modified
        for setting in settings_list:
            if setting.get('type') in ['color', 'color_background'] and 'custom_' in setting.get('id', ''):
                setting_id = setting['id']
                
                if is_block:
                    search_str = f"block.settings.{setting_id}"
                else:
                    search_str = f"section.settings.{setting_id}"
                    
                idx = combined_styles.find(search_str)
                if idx != -1:
                    pre_css = combined_styles[:idx]
                    label_name = extract_label_from_selector(pre_css)
                    
                    last_colon = pre_css.rfind(':')
                    prop_label = "Color"
                    if last_colon != -1:
                        last_semi = max(pre_css.rfind(';'), pre_css.rfind('{'))
                        if last_semi != -1:
                            prop_text = pre_css[last_semi+1:last_colon].strip()
                            if "background" in prop_text:
                                prop_label = "Background"
                            elif "border" in prop_text:
                                prop_label = "Border color"
                            elif "color" in prop_text or "fill" in prop_text or "stroke" in prop_text:
                                prop_label = "Text/Icon color"
                    
                    full_label = f"{label_name} {prop_label}"
                    
                    if "{ Color" in setting.get('label', '') or "Custom color" in setting.get('label', '') or "Custom background" in setting.get('label', ''):
                        setting['label'] = full_label[:50]
                        modified = True

    if 'settings' in schema:
        update_settings_list(schema['settings'], is_block=False)
        
    if 'blocks' in schema:
        for b in schema['blocks']:
            if 'settings' in b:
                update_settings_list(b['settings'], is_block=True)
                
    if modified:
        new_schema_str = json.dumps(schema, indent=2)
        new_content = content.replace(schema_str, f"\n{new_schema_str}\n")
        
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(new_content)
        return True
        
    return False

def main():
    files = get_liquid_files()
    processed = 0
    for f in files:
        if rename_labels(f):
            print(f"Updated labels in {os.path.basename(f)}")
            processed += 1
            
    print(f"Total files updated: {processed}")

if __name__ == '__main__':
    main()
