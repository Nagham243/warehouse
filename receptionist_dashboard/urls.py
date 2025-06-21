from django.urls import path
from receptionist_dashboard import views
from django.utils import translation
from django.shortcuts import redirect

def set_language_redirect(request, language):
    translation.activate(language)
    response = redirect(request.GET.get('next', '/'))
    response.set_cookie('django_language', language)
    return response

urlpatterns = [
    path('', views.index, name='receptionistIndex'),
    path('set-language/<str:language>/', set_language_redirect, name='set_language_redirect'),
    path('salon/appointments/', views.salon_appointments, name='receptionist_salon_appointments'),
    path('salon/select-day/', views.select_appointment_day, name='select_appointment_day'),
    path('salon/book/<str:day>/', views.book_appointment_details, name='book_appointment_details'),
    path('select-appointment-time/<str:day>/', views.select_appointment_time, name='select_appointment_time'),
    path('verify-and-book-appointment/<str:day>/', views.verify_and_book_appointment, name='verify_and_book_appointment'),
    path('salon/book/<str:day>/<str:time_slot>/', views.book_appointment, name='book_appointment'),
    path('salon/appointment/<int:appointment_id>/', views.appointment_details, name='appointment_details'),
    path('salon/cancel/<int:appointment_id>/', views.cancel_appointment, name='cancel_appointment'),
    path('salon/service-duration/<int:service_id>/', views.get_service_duration, name='get_service_duration'),
    path('salon/service-coach/<int:service_id>/', views.service_coach, name='service_coach'),
    path('salon/service-info/<int:service_id>/', views.get_service_info, name='get_service_info'),
    path('slot_appointments/<str:day>/<str:time>/', views.slot_appointments, name='slot_appointments'),
    path('viewStudents', views.viewStudentss, name="viewStudentss"),
    path('addStudent', views.addStudent, name="addStudentFromReceptionist"),
    path('editStudent/<int:id>/', views.editStudentt, name='editStudentt'),
    path('deleteStudent/<int:id>/', views.deleteStudentt, name='deleteStudentt'),
    path('receptionist/profile/', views.view_receptionist_profile, name='view_receptionist_profile'),
    path('receptionist/profile/edit/', views.edit_receptionist_profile, name='edit_receptionist_profile'),
    path('student-subscriptions/<int:student_id>/', views.student_subscriptions, name='student_subscriptions'),
    path('add-student-subscription/<int:student_id>/', views.add_student_subscription, name='add_student_subscription'),
]