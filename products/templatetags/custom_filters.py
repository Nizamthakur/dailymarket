from django import template

register = template.Library()

@register.filter
def split(value, key):
    """String ke split kore list e convert kore"""
    return value.split(key)

