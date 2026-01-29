# question_paper/templatetags/question_tags.py

from django import template
from django.utils.safestring import mark_safe

register = template.Library()


def _nl2br(text: str) -> str:
    """Convert newline to <br> safely."""
    if not text:
        return ""
    return text.replace("\n", "<br>")


@register.simple_tag
def display_question_with_image(question):
    """
    Display question with image using NEW FIELDS:
    - question = text above image
    - text_below_image = text below image (only for middle position)
    - question_image_position in: top, middle, bottom
    """
    if not question:
        return ""

    # If no image -> just return question text
    if not hasattr(question, "question_image") or not question.question_image:
        return mark_safe(_nl2br(getattr(question, "question", "") or ""))

    position = getattr(question, "question_image_position", None) or "top"
    size = getattr(question, "question_image_size", None) or "medium"
    size_class = f"img-{size}"

    text_above = getattr(question, "question", "") or ""
    text_below = getattr(question, "text_below_image", "") or ""

    html = ""

    # TOP: show image first then all question text below
    if position == "top":
        html += f"""
        <div class="question-image-container">
            <img src="{question.question_image.url}"
                 alt="Question Image"
                 class="question-img {size_class}">
        </div>
        """
        if text_above:
            html += f'<div class="question-text-below">{_nl2br(text_above)}</div>'

    # MIDDLE: show question text above, image, then text_below_image
    elif position == "middle":
        if text_above:
            html += f'<div class="question-text-above">{_nl2br(text_above)}</div>'

        html += f"""
        <div class="question-image-container">
            <img src="{question.question_image.url}"
                 alt="Question Image"
                 class="question-img {size_class}">
        </div>
        """

        if text_below:
            html += f'<div class="question-text-below">{_nl2br(text_below)}</div>'

    # BOTTOM: show question text first then image
    else:  # bottom
        if text_above:
            html += f'<div class="question-text-above">{_nl2br(text_above)}</div>'

        html += f"""
        <div class="question-image-container">
            <img src="{question.question_image.url}"
                 alt="Question Image"
                 class="question-img {size_class}">
        </div>
        """

    return mark_safe(html)


@register.filter(name="has_sub_questions")
def has_sub_questions(question):
    """Check if question has sub-questions"""
    if hasattr(question, "sub_questions"):
        return question.sub_questions.exists()
    return False


@register.filter(name="get_sub_questions")
def get_sub_questions(question):
    """Get sub-questions ordered by letter"""
    if hasattr(question, "sub_questions"):
        return question.sub_questions.all().order_by("sub_question_letter", "id")
    return []


@register.filter(name="get_image_size_class")
def get_image_size_class(question):
    """Get CSS class for image size"""
    size = getattr(question, "question_image_size", None) or "medium"
    return f"img-{size}"


@register.simple_tag
def split_question_text(question, part="above"):
    """
    Used in template when you want to print text separately.
    part: "above" or "below"
    """
    if not question:
        return ""

    position = getattr(question, "question_image_position", None) or "top"

    if position == "middle":
        if part == "above":
            return mark_safe(_nl2br(getattr(question, "question", "") or ""))
        if part == "below":
            return mark_safe(_nl2br(getattr(question, "text_below_image", "") or ""))
        return ""

    # for top or bottom you only need `question`
    if part == "above":
        return mark_safe(_nl2br(getattr(question, "question", "") or ""))


    return ""


@register.filter(name="roman")
def roman(value):
    """Convert integer to Roman numeral."""
    try:
        n = int(value)
    except (ValueError, TypeError):
        return value

    if not (0 < n < 4000):
        return str(n)

    val = [
        1000, 900, 500, 400,
        100, 90, 50, 40,
        10, 9, 5, 4,
        1
    ]
    syb = [
        "M", "CM", "D", "CD",
        "C", "XC", "L", "XL",
        "X", "IX", "V", "IV",
        "I"
    ]
    roman_num = ''
    i = 0
    while n > 0:
        for _ in range(n // val[i]):
            roman_num += syb[i]
            n -= val[i]
        i += 1
    return roman_num

@register.filter
def idiv(value, arg):
    """Integer division: value // arg"""
    try:
        return int(value) // int(arg)
    except (ValueError, TypeError, ZeroDivisionError):
        return 0
