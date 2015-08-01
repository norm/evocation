from django import template
from django.utils.safestring import mark_safe
import markdown

register = template.Library()


@register.filter()
def from_markdown(text):
    # safe_mode governs how the function handles raw HTML
    return mark_safe(markdown.markdown(text, safe_mode='escape'))
