from django import template
from accounts.models import UserProfile, ClubsModel
from students.models import ProductsImage, ServicesImage
from decimal import Decimal
from django.utils.safestring import mark_safe
import datetime

register = template.Library()

@register.simple_tag
def get_product_imgs(product_id):
    """Fetch all images for a given product"""
    return ProductsImage.objects.filter(product__id=product_id)

@register.simple_tag
def get_Service_imgs(service_id):
    """Fetch images for a given service"""
    return ServicesImage.objects.filter(product__id=service_id)  # ✅ تم التصحيح هنا

@register.filter
def avg_price(services):
    if not services:
        return 0
    total_price = sum(service.discounted_price or service.price for service in services)
    return round(total_price / len(services), 1)

@register.filter
def avg_duration(services):
    if not services:
        return 0
    return sum(service.duration for service in services) / len(services)

@register.filter
def floatdiv(value, arg):
    try:
        return float(value) / float(arg)
    except (ValueError, ZeroDivisionError):
        return 0

@register.filter
def floatmod(value, arg):
    try:
        return float(value) % float(arg)
    except (ValueError, ZeroDivisionError):
        return 0

@register.filter
def floordiv(value, arg):
    try:
        return int(float(value) // float(arg))
    except (ValueError, ZeroDivisionError):
        return 0

@register.filter
def mod(value, arg):
    try:
        return int(value) % int(arg)
    except (ValueError, ZeroDivisionError):
        return 0

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
def sum_attr(queryset, attr_name):
    """Sum a specific attribute across all objects in a queryset"""
    return sum(getattr(obj, attr_name, 0) for obj in queryset)

@register.filter
def multiply(value, arg):
    """Multiply the value by the argument"""
    try:
        return float(value) * float(arg)
    except (ValueError, TypeError):
        return 0

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
def divide(value, arg):
    try:
        # Convert arg to Decimal if it's not already
        if not isinstance(arg, Decimal):
            arg = Decimal(str(arg))
        # Convert value to Decimal if it's not already
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
def mul(value, arg):
    """Multiply the arg and the value"""
    return value * arg


@register.filter
def visible_to_user(appointments, user):
    """
    Filter appointments to only show:
    1. Other students' appointments (always visible)
    2. Current student's paid appointments
    """
    visible_appointments = []

    # Check if the user is a student
    is_student = hasattr(user, 'userprofile') and hasattr(user.userprofile, 'student_profile')

    if not is_student:
        # Staff can see all appointments
        return appointments

    student_profile = user.userprofile.student_profile

    for appointment in appointments:
        # If this appointment belongs to another student, show it
        if 'student_name' in appointment and appointment.get('student_name') != student_profile.full_name:
            visible_appointments.append(appointment)
        # If this is the current student's appointment and it's paid, show it
        elif 'is_paid' in appointment and appointment.get('is_paid'):
            visible_appointments.append(appointment)

    return visible_appointments

@register.filter
def timedelta(value, days):
    """Add a given number of days to a date"""
    if value:
        return value + datetime.timedelta(days=days)
    return value

@register.filter
def div(value, arg):
    return value // arg

@register.filter
def divisibleby(value, arg):
    return value // arg

@register.filter
def modulo(value, arg):
    return value % arg

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


