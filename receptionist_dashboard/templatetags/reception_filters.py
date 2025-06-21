from django import template

register = template.Library()

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
def format_12h_time(time_obj):
    """Converts time to 12-hour format with AM/PM"""
    if not time_obj:
        return ""

    hour = time_obj.hour
    minute = time_obj.minute
    period = 'AM' if hour < 12 else 'PM'

    # Convert to 12-hour format
    hour = hour if hour <= 12 else hour - 12
    if hour == 0:
        hour = 12

    return f"{hour:02d}:{minute:02d} {period}"

@register.filter
def mul(value, arg):
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return ''

