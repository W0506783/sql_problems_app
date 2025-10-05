import markdown
from django import template
from django.template.defaultfilters import stringfilter

register = template.Library()

@register.filter(name='convert_markdown')
@stringfilter
def convert_markdown(value):
    return markdown.markdown(value, extensions=['tables', 'fenced_code'])