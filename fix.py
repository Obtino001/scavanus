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

def find_hardcoded_colors(content):
    # Match <style> tags
    style_pattern = re.compile(r'<style[^>]*>(.*?)</style>', re.DOTALL | re.IGNORECASE)
    
    colors = []
    
    for match in style_pattern.finditer(content):
        style_content = match.group(1)
        
        # Regex to find CSS color declarations
        # e.g., color: #3f3f46; background: rgba(247, 245, 242, 1);
        color_pattern = re.compile(r'(?P<prop>color|background|background-color|border|border-color|border-top|border-bottom|fill|stroke)\s*:\s*(?P<val>#[0-9a-fA-F]{3,6}|rgba?\([^)]+\))')
        
        for color_match in color_pattern.finditer(style_content):
            colors.append(color_match.group(0))
            
    return colors

def main():
    files = get_liquid_files()
    total_colors = 0
    for f in files:
        with open(f, 'r', encoding='utf-8') as file:
            content = file.read()
            
        colors = find_hardcoded_colors(content)
        if colors:
            print(f"File: {os.path.basename(f)}")
            for c in colors:
                print(f"  {c}")
            total_colors += len(colors)
            print()
            
    print(f"Total hardcoded colors found: {total_colors}")

if __name__ == '__main__':
    main()
