import os
import re

def fix_template(filepath):
    print(f"Processing {filepath}...")
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Pattern to find {% if ... %} tags split across lines
    # We look for {% blockname ... that doesn't end with %} on the same line
    
    # Specifically targeting the known problematic blocks
    patterns = [
        (r'\{% if q\.question_image_position == \'middle\' and q\.text_below_image\s+%\}(<br>)?', 
         r'{% if q.question_image_position == \'middle\' and q.text_below_image %}\1'),
        (r'\{% if q\.question_image_position == \'middle\' and q\.text_below_image\n\s+%\}(<br>)?', 
         r'{% if q.question_image_position == \'middle\' and q.text_below_image %}\1'),
    ]

    # More general approach: find any {% ... %} that spans multiple lines and join them
    new_content = re.sub(r'\{%\s+(.*?)\s+%\}', lambda m: '{% ' + m.group(1).replace('\n', ' ').replace('\r', ' ') + ' %}', content, flags=re.DOTALL)
    
    # Clean up double spaces that might result from joining
    new_content = re.sub(r'\s{2,}', ' ', new_content) # Wait, this might kill indentation.
    
    # Accurate joiner: keep relative line structure but join tags
    def join_tags(match):
        inner = match.group(1)
        # Replace newlines and extra spaces inside the tag only
        joined = re.sub(r'\s+', ' ', inner).strip()
        return f'{{% {joined} %}}'

    final_content = re.sub(r'\{% (.*?) %\}', join_tags, content, flags=re.DOTALL)

    if final_content != content:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(final_content)
        print(f"Successfully updated {filepath}")
    else:
        print(f"No changes needed for {filepath}")

# Target files
templates = [
    r'question_paper\templates\create_part_b.html',
    r'question_paper\templates\create_part_c.html'
]

for t in templates:
    if os.path.exists(t):
        fix_template(t)
    else:
        print(f"File not found: {t}")
