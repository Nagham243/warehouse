from django.urls import path
from . import views
from django.urls import path
from django.utils import translation
from django.shortcuts import redirect
from .views import switch_language_button_view

def set_language_redirect(request, language):
    translation.activate(language)
    response = redirect(request.GET.get('next', '/'))
    response.set_cookie('django_language', language)
    return response


urlpatterns = [
    path('', views.index, name='landingIndex'),
    path('set-language/<str:language>/', set_language_redirect, name='set_language_redirect'),
    # path('language-switcher/', switch_language_button_view, name='language_switcher'),
    path('Profile/<int:id>', views.Profile, name='Profile'),
    
    
    path('ViewClubProfile/<int:id>', views.ViewClubProfile, name='ViewClubProfile'),
    path('toggle-dashboard-counts/', views.toggle_dashboard_counts, name='toggle_dashboard_counts'),
    # path('ViewDirectorProfile/<int:id>', views.ViewDirectorProfile, name='ViewDirectorProfile'),
    # path('ViewStudentProfile/<int:id>', views.ViewStudentProfile, name='ViewStudentProfile'),
    # path('ViewCoachProfile/<int:id>', views.ViewCoachProfile, name='ViewCoachProfile'),
    path('EditDirectorProfile/<int:id>', views.EditDirectorProfile, name='EditDirectorProfile'),
    path('EditStudentProfile/<int:id>', views.EditStudentProfile, name='EditStudentProfile'),
    path('EditCoachProfile/<int:id>', views.EditCoachProfile, name='EditCoachProfile'),
    path('EditClubProfile/<int:id>', views.EditClubProfile, name='EditClubProfile'),
]