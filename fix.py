import os, json, re

# 1. Clean settings_data.json
with open('config/settings_data.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

if 'color_schemes' in data.get('current', {}):
    del data['current']['color_schemes']

if 'presets' in data:
    for p in data['presets'].values():
        if 'color_schemes' in p:
            del p['color_schemes']

with open('config/settings_data.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, separators=(',', ':'))

# 2. Clean settings_schema.json
with open('config/settings_schema.json', 'r', encoding='utf-8') as f:
    schema_str = f.read()

schema_obj = json.loads(schema_str)
for category in schema_obj:
    if 'settings' in category:
        category['settings'] = [s for s in category['settings'] if s.get('type') != 'color_scheme_group']

with open('config/settings_schema.json', 'w', encoding='utf-8') as f:
    json.dump(schema_obj, f, indent=2)

# 3. Clean all sections
sections_dir = 'sections'
for filename in os.listdir(sections_dir):
    if filename.endswith('.liquid'):
        filepath = os.path.join(sections_dir, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        new_content = re.sub(r'\{\s*"type"\s*:\s*"color_scheme"[^\}]*\},?\s*', '', content)
        new_content = re.sub(r',\s*\]', '\n  ]', new_content)
        
        if content != new_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print('Updated', filename)

print('Done!')
