from django.urls import path
from . import views
from django.utils import translation
from django.shortcuts import redirect

def set_language_redirect(request, language):
    translation.activate(language)
    response = redirect(request.GET.get('next', '/'))
    response.set_cookie('django_language', language)
    return response

urlpatterns = [

    path('', views.index, name="coachIndex"),
    path('set-language/<str:language>/', set_language_redirect, name='set_language_redirect'),
    path('vendorProfile', views.view_coach_profile, name="coachVendorProfile"),
    path('editProfile', views.edit_coach_profile, name="editCoachProfile"),
    # Products Management
    path('addProduct', views.addProduct, name="coachaddProduct"),
    path('editProduct/<int:id>', views.editProduct, name="coacheditProduct"),
    path('DeleteProduct/<int:id>', views.DeleteProduct, name="coachDeleteProduct"),
    path('viewProducts', views.viewProducts, name="coachviewProducts"),
    path('products/shipments/add/', views.add_shipment, name='coachadd_shipment'),
    path('products/<int:product_id>/shipments/', views.view_product_shipments, name='coachview_product_shipments'),
    path('shipments/edit/<int:shipment_id>/', views.edit_shipment, name='coachedit_shipment'),
    path('shipments/delete/<int:shipment_id>/', views.delete_shipment, name='coachdelete_shipment'),
    path('products/<int:product_id>/details/', views.product_details, name='coachproduct_details'),

    # Services Management
    path('addServices', views.addServices, name="coachaddServices"),
    path('editServices/<int:id>', views.editServices, name="coacheditServices"),
    path('DeleteServices/<int:id>', views.DeleteServices, name="coachDeleteServices"),
    path('viewServices', views.viewServices, name="coachviewServices"),
    path('services/details/<int:service_id>/', views.viewServiceDetails, name='coachviewServiceDetails'),

    path('addServicesClassification', views.addServicesClassification, name="coachaddServicesClassification"),
    path('editServicesClassification/<int:id>', views.editServicesClassification, name="coacheditServicesClassification"),
    path('DeleteServicesClassification/<int:id>', views.DeleteServicesClassification, name="coachDeleteServicesClassification"),
    path('viewServicesClassification', views.viewServicesClassification, name="coachviewServicesClassification"),
    path('notifications/', views.viewCoachNotifications , name='viewCoachNotifications'),  # ✅ Ensure correct name
    path('notifications/delete/<int:notification_id>/', views.delete_notification, name='delete_notification'),
    path('notifications/delete-all/', views.delete_all_notifications, name='delete_all_notifications'),

]
