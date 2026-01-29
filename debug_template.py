
from django.template import Template, Context

# Mock Context
context_data = {
    'question_paper': {
        'revesion': '2021',
        'subject_code': 'CS101',
        'subject_name': 'Mathematics',
        'exam_marks': 75,
        'time': 3,
    }
}

template_content = """
<div>
    TED({{ question_paper.revesion }}){{ question_paper.subject_code }}
</div>
<div style="text-transform:uppercase;">
    {{
    question_paper.subject_name }}
</div>
"""

try:
    templ = Template(template_content)
    rendered = templ.render(Context(context_data))
    print("--- Rendered Output ---")
    print(rendered)
    print("-----------------------")
    
    if '{{' in rendered:
        print("FAIL: Raw tags found in rendered output!")
    else:
        print("SUCCESS: Tags rendered correctly.")
except Exception as e:
    print(f"ERROR: {e}")

