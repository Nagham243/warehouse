from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views
import club_dashboard.views as club_views

urlpatterns = [
    path('', views.administrator_dashboard_index, name="administrator_dashboard_index"),
    path('viewStudents', club_views.viewStudents, name="viewStudents"),
    path('export-students-excel/', club_views.export_students_excel, name='export_students_excel'),
    path('addStudent', club_views.addStudent, name="addStudent"),
    path('editStudent/<int:id>', club_views.editStudent, name="editStudent"),
    path('deleteStudent/<int:id>', club_views.deleteStudent, name="deleteStudent"),

    # Coaches Management
    path('viewCoachs', club_views.viewCoachs, name="viewCoachs"),
    path('export_coaches_excel/', club_views.export_coaches_excel, name='export_coaches_excel'),
   # path('addCoach', club_views.addCoach, name="addCoach"),
   # path('editCoach/<int:id>', club_views.editCoach, name="editCoach"),
   # path('deleteCoach/<int:id>', club_views.deleteCoach, name="deleteCoach"),

    # Products Management
    path('addProduct', club_views.addProduct, name="addProduct"),
    path('editProduct/<int:id>', club_views.editProduct, name="editProduct"),
    path('DeleteProduct/<int:id>', club_views.DeleteProduct, name="DeleteProduct"),
    path('viewProducts', club_views.viewProducts, name="viewProducts"),
    path('products/shipments/add/', club_views.add_shipment, name='add_shipment'),
    path('products/<int:product_id>/shipments/', club_views.view_product_shipments, name='view_product_shipments'),
    path('products/<int:product_id>/details/', club_views.product_details, name='product_details'),

    path('viewReceptionists', club_views.viewReceptionists, name="viewReceptionists"),
    path('addReceptionist', club_views.addReceptionist, name="addReceptionist"),
    path('editReceptionist/<int:id>', club_views.editReceptionist, name="editReceptionist"),
    path('deleteReceptionist/<int:id>', club_views.deleteReceptionist, name="deleteReceptionist"),

    # Services Management
    path('addServices', club_views.addServices, name="addServices"),
    path('editServices/<int:id>', club_views.editServices, name="editServices"),
    path('DeleteServices/<int:id>', club_views.DeleteServices, name="DeleteServices"),
    path('viewServices', club_views.viewServices, name="viewServices"),

    # Blog Management
    path('articles/', club_views.viewArticles, name="viewArticles"),
    path('articles/add/', club_views.addArticle, name="addArticle"),
    path('articles/edit/<int:id>/', club_views.editArticle, name="editArticle"),
    path('articles/delete/<int:id>/', club_views.DeleteArticle, name="DeleteArticle"),
    path('salon-appointments/', club_views.salon_appointments, name='club_salon_appointments'),
    path('slot_appointments/<str:day>/<str:time>/', club_views.slot_appointments, name='director_slot_appointments'),
    path('salon/appointment/<int:appointment_id>/', club_views.appointment_details, name='director_appointment_details'),
    path('salon/cancel/<int:appointment_id>/', club_views.cancel_appointment, name='director_cancel_appointment'),

    path('mark-notifications-read/', club_views.mark_notifications_read, name='mark_notifications_read'),
    path('notifications/', club_views.viewClubNotifications, name='viewClubNotifications'),  # ✅ Ensure correct name
    path('reviews/', club_views.reviews_list, name='reviews_list'),

    path('club/orders/', club_views.club_orders, name='club_orders'),
    path('club/orders/<int:order_id>/update/', club_views.update_order_status, name='update_order_status'),
    path('club/orders/<int:order_id>/details/', club_views.order_details_api, name='order_details_api'),


    path('profile/administrator/', views.view_administrator_profile, name='view_administrator_profile'),
    path('profile/administrator/edit/', views.edit_administrator_profile, name='edit_administrator_profile'),

]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)