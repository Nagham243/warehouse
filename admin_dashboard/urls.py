from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name="adminIndex"),

    path('addClub', views.addClub, name="addClub"),
    path('editClub/<int:id>', views.editClub, name="editClub"),
    path('viewClub', views.viewClub, name="viewClub"),
    path('deleteClub/<int:id>', views.deleteClub, name="deleteClub"),


    path('addDirector', views.addDirector, name="addDirector"),
    path('editDirector/<int:id>', views.editDirector, name="editDirector"),
    path('viewDirector', views.viewDirector, name="viewDirector"),
    path('deleteDirector/<int:id>', views.deleteDirector, name="deleteDirector"),
    path('update-pricing/', views.update_pricing, name='UpdatePricing'),
    path('financial-dashboard/', views.financial_dashboard, name='financialDashboard'),
]