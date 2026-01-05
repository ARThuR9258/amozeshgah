from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """
    Template filter to get a dictionary value by key.
    Usage: {{ dictionary|get_item:key }}
    """
    if not dictionary:
        return None
    return dictionary.get(str(key))

@register.filter
def dict_get(dictionary, key):
    """
    Alternative dictionary get filter that handles string conversion
    """
    if not dictionary:
        return None
    return dictionary.get(str(key))
