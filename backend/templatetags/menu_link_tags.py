from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.simple_tag
def menu_link(menu_path, current_path, menu_name):
    if current_path in menu_path:
        text = f'<a href="{menu_path}" class="current-menu-item text-dark">{menu_name}</a>'
        return mark_safe(text)
    
    text = f'<a href="{menu_path}">{menu_name}</a>'
    return mark_safe(text)
