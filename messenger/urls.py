from django.urls import path
from . import views

urlpatterns = [
    path('messageRoom/<str:room_id>', views.messageRoom, name="messageRoom"),
    path('createMessager/<int:receiver_id>', views.createMessager, name="createMessager"),

    path('toggle_favorite/<int:user_id>/', views.toggle_favorite, name="toggle_favorite"),
    path('toggle_block/<int:user_id>/', views.toggle_block, name="toggle_block"),
    path('AddFavorite/<int:receiver_id>', views.AddFavorite, name="AddFavorite"),
    path('BlockUserMessenger/<int:receiver_id>', views.BlockUserMessenger, name="BlockUserMessenger"),
    path('DeleteFavorite/<int:fav_id>', views.DeleteFavorite, name="DeleteFavorite"),
    path('DeleteBlockUser/<int:block_id>', views.DeleteBlockUser, name="DeleteBlockUser"),
    path('api/user-status/<int:user_id>/', views.get_user_status, name="get_user_status"),
    
    # path('DeleteFavorite/<int:fav_id>', views.DeleteFavorite, name="DeleteFavorite"),
    # path('DeleteBlockUser/<int:block_id>', views.DeleteBlockUser, name="DeleteBlockUser"),
    path('toggle_chat_status/<int:club_id>/', views.toggle_chat_status, name="toggle_chat_status"),
    path('createPrivateChat/<int:user_id>', views.createPrivateChat, name="createPrivateChat"),
    path('privateMessageRoom/<str:room_id>', views.privateMessageRoom, name="privateMessageRoom"),
    path('api/club-members/<int:club_id>/', views.get_club_members, name="get_club_members"),
]