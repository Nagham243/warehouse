"""
URL configuration for sportclub project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
# from django.shortcuts import redirect
# from django.utils import translation

# def set_language_redirect(request, language):
#     translation.activate(language)
#     response = redirect(request.GET.get('next', '/'))
#     response.set_cookie('django_language', language)
#     return response

urlpatterns = [
    path('messenger/', include('messenger.urls')),
    path('', include('pages.urls')),
    path('student/', include('students.urls')),

    path('auth/', include('accounts.urls')),
    path('admin_dashboard/', include('admin_dashboard.urls')),
    path('club_dashboard/', include('club_dashboard.urls')),
    path('coach_dashboard/', include('coach_dashboard.urls')),
    path('receptionist_dashboard/', include('receptionist_dashboard.urls')),
    path('administrator_dashboard/', include('administrator_dashboard.urls')),
    path('admin/', admin.site.urls),
    path('ckeditor/', include('ckeditor_uploader.urls')),
    # path('set-language/<str:language>/', set_language_redirect, name='set_language_redirect'),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)