import os
import re

SECTIONS_DIR = r"C:\Users\Yasir\Pictures\world-of-comfort\scavanus\sections"

def get_liquid_files():
    files = []
    for f in os.listdir(SECTIONS_DIR):
        if f.endswith('.liquid'):
            files.append(os.path.join(SECTIONS_DIR, f))
    return files

def inspect_blocks():
    files = get_liquid_files()
    for f in files:
        with open(f, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Regex to find CSS color declarations
        color_pattern = re.compile(r'(?P<prop>color|background|background-color|border|border-color|border-top|border-bottom|fill|stroke)\s*:\s*(?P<val>#[0-9a-fA-F]{3,6}|rgba?\([^)]+\))')
        
        style_pattern = re.compile(r'<style[^>]*>(.*?)</style>', re.DOTALL | re.IGNORECASE)
        for style_match in style_pattern.finditer(content):
            style_content = style_match.group(1)
            colors = list(color_pattern.finditer(style_content))
            if colors:
                # Check if this style block is inside a block loop
                # we'll look around the style tag in the original content
                start_index = max(0, style_match.start() - 500)
                pre_context = content[start_index:style_match.start()]
                
                # Check if there's block logic
                is_block = False
                if 'for block in' in pre_context or 'block.id' in style_content or 'block.settings' in style_content:
                    is_block = True
                
                if is_block:
                    print(f"Block styling found in {os.path.basename(f)}:")
                    for c in colors:
                        print(f"  {c.group(0)}")

if __name__ == '__main__':
    inspect_blocks()
