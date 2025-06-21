from django import template

register = template.Library()

@register.filter
def divisibleby(value, arg):
    return value // arg

@register.filter
def modulo(value, arg):
    return value % arg

@register.filter
def get_item(dictionary, key):
    """Returns an item from a dictionary by key"""
    if isinstance(key, int):
        # Handle numeric indices for lists
        try:
            return dictionary[key]
        except (IndexError, TypeError):
            return None
    # Handle dictionary keys
    return dictionary.get(key)

@register.filter
def get_range(value):
    """Returns a range of numbers from 0 to value-1"""
    return range(value)

@register.filter
def mul(value, arg):
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return ''

