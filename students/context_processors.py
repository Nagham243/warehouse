from django.db.models import Sum
from .models import CartItem, ServiceCartItem
from django.utils import translation

def cart_items_count(request):
    if request.user.is_authenticated:
        product_count = CartItem.objects.filter(user=request.user).aggregate(
            total=Sum('quantity'))['total'] or 0
        service_count = ServiceCartItem.objects.filter(user=request.user).aggregate(
            total=Sum('quantity'))['total'] or 0
        total_count = product_count + service_count
        return {'cart_count': total_count}
    return {'cart_count': 0}

def language_context(request):
    return {
        'LANGUAGE_CODE': translation.get_language(),
    }

