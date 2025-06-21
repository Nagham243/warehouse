from django import template
from decimal import Decimal

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
def multiply(value, arg):
    """Multiply the value by the argument"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def divide(value, arg):
    try:
        if not isinstance(arg, Decimal):
            arg = Decimal(str(arg))
        if not isinstance(value, Decimal):
            value = Decimal(str(value))
        return value / arg
    except (ValueError, ZeroDivisionError, TypeError):
        return Decimal('0')

@register.filter
def subtract(value, arg):
    try:
        return value - arg
    except (ValueError, TypeError):
        return value

@register.filter
def mul(value, arg):
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return ''

@register.filter
def div(value, arg):
    return value // arg

@register.filter
def tax_amount(total_price, tax_rate=15):
    try:
        tax_fraction = Decimal(tax_rate) / Decimal(100) + 1
        before_tax = total_price / tax_fraction
        tax = total_price - before_tax
        return round(tax, 2)
    except Exception:
        return 0

@register.filter
def sub(value, arg):
    try:
        return float(value) - float(arg)
    except (ValueError, TypeError):
        return ''

@register.filter
def mul(value, arg):
    """Multiply the value by the argument."""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def sub(value, arg):
    """Subtract the argument from the value."""
    try:
        return float(value) - float(arg)
    except (ValueError, TypeError):
        return 0

@register.filter
def percentage(value, total):
    """Calculate percentage of value from total."""
    try:
        if float(total) == 0:
            return 0
        return (float(value) / float(total)) * 100
    except (ValueError, TypeError):
        return 0

@register.filter
def format_currency(value):
    """Format number as currency with thousand separators."""
    try:
        return "{:,.2f}".format(float(value))
    except (ValueError, TypeError):
        return "0.00"

@register.filter(name='add_class')
def add_class(value, arg):
    css_classes = value.field.widget.attrs.get('class', '').split(' ')
    if arg not in css_classes:
        css_classes = list(filter(None, css_classes))  # Remove empty classes
        css_classes.append(arg)
    return value.as_widget(attrs={'class': ' '.join(css_classes)})