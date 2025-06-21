from django.contrib import admin
from .models import MessagesModel, MessengerModel, BlockUserModel, FavoriteUserModel

# Register your models here.
admin.site.register(MessagesModel)
admin.site.register(MessengerModel)
admin.site.register(BlockUserModel)
admin.site.register(FavoriteUserModel)