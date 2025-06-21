from django.utils import translation

def club_notifications(request):
    context = {
        'pending_orders_count': 0,
        'pending_products_orders_count': 0,
        'pending_services_orders_count': 0,
        'pending_mixed_orders_count': 0,
    }

    if request.user.is_authenticated and hasattr(request.user, 'userprofile'):
        user_profile = request.user.userprofile
        if hasattr(user_profile, 'director_profile') and user_profile.director_profile:
            club = user_profile.director_profile.club

            from students.models import Order, OrderItem
            from django.db.models import Count, Q, Case, When, IntegerField

            pending_orders = Order.objects.filter(
                club=club,
                status='pending',
                payment_method='cash_on_delivery'
            )

            context['pending_orders_count'] = pending_orders.count()

            orders_with_type = pending_orders.annotate(
                has_products=Count('items', filter=Q(items__product__isnull=False)),
                has_services=Count('items', filter=Q(items__service__isnull=False))
            ).annotate(
                order_type=Case(
                    When(has_products__gt=0, has_services=0, then=1),  # Products only
                    When(has_products=0, has_services__gt=0, then=2),  # Services only
                    When(has_products__gt=0, has_services__gt=0, then=3),  # Both
                    default=0,
                    output_field=IntegerField()
                )
            )

            context['pending_products_orders_count'] = orders_with_type.filter(order_type=1).count()
            context['pending_services_orders_count'] = orders_with_type.filter(order_type=2).count()
            context['pending_mixed_orders_count'] = orders_with_type.filter(order_type=3).count()

    return context

def language_context(request):
    return {
        'LANGUAGE_CODE': translation.get_language(),
    }