from django.urls import path
from . import views
from django.utils import translation
from django.shortcuts import redirect
from django.contrib.auth import views as auth_views
from .views import add_review,edit_review

def set_language_redirect(request, language):
    translation.activate(language)
    response = redirect(request.GET.get('next', '/'))
    response.set_cookie('django_language', language)
    return response

urlpatterns = [
    path('', views.index, name='studentIndex'),
    path('set-language/<str:language>/', set_language_redirect, name='set_language_redirect'),
    # path('login/', auth_views.LoginView.as_view(), name='login'),
    # Products
    path('viewProducts', views.viewProducts, name='StudentViewProducts'),
    path('viewProducts/<int:id>', views.viewProductsSpecific, name='viewProductsSpecific'),

    # Services (Updated to avoid conflicts with club dashboard)
    path('studentViewServices', views.viewServices, name='studentViewServices'),
    path('studentViewServicesSpecific/<int:id>', views.viewServicesSpecific, name='studentViewServicesSpecific'),

    # Blog (Updated to avoid conflicts with club dashboard)
    path('articles/', views.viewArticles, name='clientviewArticles'),
    path('articles/<int:id>/', views.viewArticle, name='viewArticle'),
    path('clientSalonAppointments', views.salon_appointments, name='studentViewArticles'),
    path('slot_appointments/<str:day>/<str:time>/', views.slot_appointments, name='client_slot_appointments'),
    path('salon/appointment/<int:appointment_id>/', views.appointment_details, name='client_appointment_details'),
    path('salon/service-duration/<int:service_id>/', views.get_service_duration, name='get_service_duration'),
    path('salon/service-info/<int:service_id>/', views.get_service_info, name='get_service_info'),
    path('studentViewServicesSpecific/<int:id>', views.viewServicesSpecific, name='viewServicesSpecific'),

    # Order Service
    path('OrderService/<int:service_id>', views.OrderService, name='OrderService'),

    # Reviews
    path('reviews/', views.view_reviews, name='view_reviews'),
    path('add_review/', views.add_review, name='add_review'),  # Add review page
    path('reviews/edit/<int:review_id>/', views.edit_review, name='edit_review'),  # ✅ Edit Review
    path('cart/', views.cart, name='cart'),
    path('cart/add/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/', views.update_cart, name='update_cart'),
    path('cart/count/', views.get_cart_count, name='get_cart_count'),
    path('cart/delete-product/<int:item_id>/', views.delete_product_from_cart, name='delete_product_from_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('place-order/', views.place_order, name='place_order'),
    path('service/cart/add/', views.add_service_to_cart, name='add_service_to_cart'),
    path('service/cart/update/', views.update_service_cart, name='update_service_cart'),
    path('profile/', views.view_student_profile, name='student_profile'),
    path('profile/edit/', views.edit_student_profile, name='edit_student_profile'),
    path('orders/<int:order_id>/', views.order_details, name='order_details'),
    path('student/orders/', views.student_orders, name='student_orders'),
    path('confirm-order/', views.confirm_order, name='confirm_order'),
    path('bank-transfer-info/', views.bank_transfer_info, name='bank_transfer_info'),
    path(
        'upload-transfer-receipt/<int:order_id>/',
        views.upload_transfer_receipt,
        name='upload_transfer_receipt'
    ),

    # Additional views that might be useful
    path('create/', views.create_refund_dispute, name='create'),
    path('dispute/<int:dispute_id>/edit/', views.edit_refund_dispute, name='edit'),
    path('dispute/<int:dispute_id>/attachments/', views.dispute_attachments, name='attachments'),
    path('dispute/<int:dispute_id>/timeline/', views.dispute_timeline, name='timeline'),
    path('refund_dispute/', views.refund_dispute_list, name='list'),

    # Detail view
    path('<int:dispute_id>/', views.refund_dispute_detail, name='clientdetail'),
]
