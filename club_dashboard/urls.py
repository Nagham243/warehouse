from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views  # ✅ Import views properly
from .views import mark_notifications_read  # ✅ Import the view
from .views import viewClubNotifications  # ✅ Import the view function
from students.views import salon_appointments
from django.utils import translation
from django.shortcuts import redirect
import administrator_dashboard.views as administrator_views

def set_language_redirect(request, language):
    translation.activate(language)
    response = redirect(request.GET.get('next', '/'))
    response.set_cookie('django_language', language)
    return response

# ✅ Import necessary views once
from .views import (
    viewDirectors, addDirector, editDirector, deleteDirector,
    viewAdmins, addAdmin, editAdmin, deleteAdmin
)

urlpatterns = [
    path('', views.club_dashboard_index, name="club_dashboard_index"),
    path('set-language/<str:language>/', set_language_redirect, name='set_language_redirect'),
    # Students Management
    path('viewStudents', views.viewStudents, name="viewStudents"),
    path('export-students-excel/', views.export_students_excel, name='export_students_excel'),
    path('addStudent', views.addStudent, name="addStudent"),
    path('editStudent/<int:id>', views.editStudent, name="editStudent"),
    path('deleteStudent/<int:id>', views.deleteStudent, name="deleteStudent"),
    path('students/import/', views.import_students, name='import_students'),
    path('students/process-import/', views.process_import_students, name='process_import_students'),
    path('students/download-template/', views.download_sample_template, name='download_sample_template'),

    # Coaches Management
    path('viewCoachs', views.viewCoachs, name="viewCoachs"),
    path('export_coaches_excel/', views.export_coaches_excel, name='export_coaches_excel'),
    path('addCoach', views.addCoach, name="addCoach"),
    path('editCoach/<int:id>', views.editCoach, name="editCoach"),    
    path('deleteCoach/<int:id>', views.deleteCoach, name="deleteCoach"),
    # New Vendor URLs
    path('vendor-status/<int:vendor_id>/', views.vendor_status, name='vendor_status'),
    path('vendor-approval/', views.vendor_approval_list, name='vendor_approval_list'),
    path('vendor-approval/action/<int:vendor_id>/', views.vendor_approval_action, name='vendor_approval_action'),
    path('vendor-approval/<int:vendor_id>/', views.vendor_approval_detail, name='vendor_approval_detail'),
    path('vendors/pending/<int:pk>/', views.VendorApprovalDetailView.as_view(), name='vendor_approval_detail'),
    path('viewReceptionists', views.viewReceptionists, name="viewReceptionists"),
    path('addReceptionist', views.addReceptionist, name="addReceptionist"),
    path('editReceptionist/<int:id>', views.editReceptionist, name="editReceptionist"),
    path('deleteReceptionist/<int:id>', views.deleteReceptionist, name="deleteReceptionist"),
    # Products Management
    path('addProduct', views.addProduct, name="addProduct"),
    path('editProduct/<int:id>', views.editProduct, name="editProduct"),
    path('DeleteProduct/<int:id>', views.DeleteProduct, name="DeleteProduct"),
    path('viewProducts', views.viewProducts, name="viewProducts"),

    path('addProductClassification', views.addProductClassification, name="addProductClassification"),
    path('editProductClassification/<int:id>', views.editProductClassification, name="editProductClassification"),
    path('viewProductsClassification', views.viewProductsClassification, name="viewProductsClassification"),
    path('DeleteProductsClassification/<int:id>', views.DeleteProductsClassification, name="DeleteProductsClassification"),

    # Services Management
    path('addServices', views.addServices, name="addServices"),
    path('editServices/<int:id>', views.editServices, name="editServices"),
    path('DeleteServices/<int:id>', views.DeleteServices, name="DeleteServices"),
    path('viewServices', views.viewServices, name="viewServices"),
    path('services/details/<int:service_id>/', views.viewServiceDetails, name='viewServiceDetails'),

    path('addServicesClassification', views.addServicesClassification, name="addServicesClassification"),
    path('editServicesClassification/<int:id>', views.editServicesClassification, name="editServicesClassification"),
    path('DeleteServicesClassification/<int:id>', views.DeleteServicesClassification, name="DeleteServicesClassification"),
    path('viewServicesClassification', views.viewServicesClassification, name="viewServicesClassification"),


    # Service Management URLs
    path('services/manage/', views.manage_services, name='manage_services'),
    path('services/<int:service_id>/approve/', views.approve_service, name='approve_service'),
    path('services/<int:service_id>/reject/', views.reject_service, name='reject_service'),
    path('services/<int:service_id>/detail/', views.service_detail, name='service_detail'),
    path('services/<int:service_id>/toggle-status/', views.toggle_service_status, name='toggle_service_status'),
    path('services/bulk-approve/', views.bulk_approve_services, name='bulk_approve_services'),
    path('services/bulk-reject/', views.bulk_reject_services, name='bulk_reject_services'),

    # Blog Management
    path('articles/', views.viewArticles, name="viewArticles"),
    path('articles/add/', views.addArticle, name="addArticle"),
    path('articles/edit/<int:id>/', views.editArticle, name="editArticle"),
    path('articles/delete/<int:id>/', views.DeleteArticle, name="DeleteArticle"),
    path('salon-appointments/', views.salon_appointments, name='club_salon_appointments'),
    path('slot_appointments/<str:day>/<str:time>/', views.slot_appointments, name='director_slot_appointments'),
    path('salon/appointment/<int:appointment_id>/', views.appointment_details, name='director_appointment_details'),
    path('salon/cancel/<int:appointment_id>/', views.cancel_appointment, name='director_cancel_appointment'),
    path('viewDirectors/', viewDirectors, name="viewDirectors"),  # ✅ This now matches your working URL
    path('viewDirectors/add/', addDirector, name="addDirector"),
    path('edit-director/<int:id>/<str:role>/', views.editDirector, name='editDirector'),
    path('delete-director/<int:id>/<str:role>/', views.deleteDirector, name='deleteDirector'),
    path('mark-notifications-read/', mark_notifications_read, name='mark_notifications_read'),
    path('notifications/', viewClubNotifications, name='viewClubNotifications'),  # ✅ Ensure correct name
    path('notifications/delete/<int:notification_id>/', views.delete_notification, name='delete_notification'),
    path('notifications/delete-all/', views.delete_all_notifications, name='delete_all_notifications'),
    path('reviews/', views.reviews_list, name='reviews_list'),
    path('delete-review/<int:review_id>/', views.delete_review, name='delete_review'),

    # ✅ Correct URL
    path('club/orders/', views.club_orders, name='club_orders'),
    path('club/orders/<int:order_id>/update/', views.update_order_status, name='update_order_status'),
    path('club/orders/<int:order_id>/details/', views.order_details_api, name='order_details_api'),
    path('club/orders/<int:order_id>/full-details/', views.order_full_details, name='order_full_details'),
    path('orders/cancellation/<int:order_id>/', views.get_cancellation_details, name='get_cancellation_details'),
    path('products/shipments/add/', views.add_shipment, name='add_shipment'),
    path('products/<int:product_id>/shipments/', views.view_product_shipments, name='view_product_shipments'),
    path('shipments/edit/<int:shipment_id>/', views.edit_shipment, name='edit_shipment'),
    path('shipments/delete/<int:shipment_id>/', views.delete_shipment, name='delete_shipment'),
    path('products/<int:product_id>/details/', views.product_details, name='product_details'),
    path('financial-dashboard/', views.club_financial_dashboard, name='club_financial_dashboard'),
    path('profile/director/', views.view_director_profile, name='view_director_profile'),
    path('profile/director/edit/', views.edit_director_profile, name='edit_director_profile'),
    path('profile/administrator/', administrator_views.view_administrator_profile, name='view_administrator_profile'),
    path('profile/administrator/edit/', administrator_views.edit_administrator_profile, name='edit_administrator_profile'),
    path('toggle-dashboard-counts/', views.toggle_dashboard_counts, name='toggle_dashboard_counts'),
    path('club/update-descriptions/<int:club_id>/', views.update_club_descriptions, name='UpdateClubDescriptions'),

    # Category URLs
    path('categories/', views.category_list, name='category_list'),
    path('categories/add/', views.add_category, name='add_category'),
    path('categories/<int:category_id>/edit/', views.edit_category, name='edit_category'),
    path('categories/<int:category_id>/delete/', views.delete_category, name='delete_category'),
    path('categories/<int:category_id>/detail/', views.category_detail, name='category_detail'),

    # Subcategory URLs
    path('subcategories/add/', views.add_subcategory, name='add_subcategory'),
    path('subcategories/<int:subcategory_id>/edit/', views.edit_subcategory, name='edit_subcategory'),
    path('subcategories/<int:subcategory_id>/delete/', views.delete_subcategory, name='delete_subcategory'),

    # AJAX URLs
    path('categories/<int:category_id>/subcategories/', views.get_subcategories, name='get_subcategories'),
    path('categories/<int:category_id>/toggle-status/', views.toggle_category_status, name='toggle_category_status'),
    path('subcategories/<int:subcategory_id>/toggle-status/', views.toggle_subcategory_status, name='toggle_subcategory_status'),

    # Product management URLs
    path('manage-products/', views.manage_products, name='manage_products'),
    path('approve-product/<int:product_id>/', views.approve_product, name='approve_product'),
    path('reject-product/<int:product_id>/', views.reject_product, name='reject_product'),
    path('product-detail/<int:product_id>/', views.product_detail, name='product_detail'),
    path('bulk-approve-products/', views.bulk_approve_products, name='bulk_approve_products'),
    path('bulk-reject-products/', views.bulk_reject_products, name='bulk_reject_products'),

    # Commission management URLs
    path('commissions/', views.commission_list, name='commission_list'),
    path('commissions/create/', views.commission_create, name='commission_create'),
    path('commissions/<int:commission_id>/edit/', views.commission_edit, name='commission_edit'),
    path('commissions/<int:commission_id>/delete/', views.commission_delete, name='commission_delete'),
    path('commissions/<int:commission_id>/toggle-status/', views.commission_toggle_status, name='commission_toggle_status'),
    path('commissions/<int:commission_id>/detail/', views.commission_detail, name='commission_detail'),
    path('commissions/vendor-management/', views.vendor_commission_management, name='vendor_commission_management'),
    path('commissions/analytics/', views.commission_analytics, name='commission_analytics'),


    # Dashboard and main views
    path('refund_dashboard/', views.refund_dashboard, name='dashboard'),
    path('dispute/<int:dispute_id>/', views.refund_detail, name='detail'),

    # Actions
    path('dispute/<int:dispute_id>/approve/', views.approve_refund, name='approve'),
    path('dispute/<int:dispute_id>/reject/', views.reject_refund, name='reject'),
    path('dispute/<int:dispute_id>/investigate/', views.mark_investigating, name='investigate'),
    path('dispute/<int:dispute_id>/resolve/', views.resolve_dispute, name='resolve'),
    path('dispute/<int:dispute_id>/priority/', views.update_dispute_priority, name='update_priority'),

    # Bulk actions
    path('bulk-action/', views.bulk_action, name='bulk_action'),

    # Export
    path('export/', views.export_disputes, name='export'),

    # API endpoints
    path('api/stats/', views.get_dispute_stats, name='api_stats'),



]

# ✅ Ensure media files work in debug mode
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
