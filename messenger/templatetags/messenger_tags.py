from django import template
from django.template.defaultfilters import stringfilter
from accounts.models import UserProfile, ClubsModel
register = template.Library()
from messenger.views import getUserClub, get_user_capacity, get_user_full_name
from django.contrib.auth.models import User

@register.simple_tag
@stringfilter
def get_user_club(user_id):
    user = User.objects.get(id=user_id)
    club = getUserClub(user)

    return club

@register.simple_tag
@stringfilter
def get_user_full_name_temp(user_id):
    user = User.objects.get(id=user_id)
    club = get_user_full_name(user)

    return club

@register.simple_tag
@stringfilter
def get_user_capacity_temp(user_id):
    user = User.objects.get(id=user_id)
    club = get_user_capacity(user)

    return club
