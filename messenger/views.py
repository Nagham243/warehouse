from django.shortcuts import render, redirect
from .models import MessagesModel, MessengerModel, FavoriteUserModel, BlockUserModel
from accounts.models import UserProfile
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import JsonResponse
from accounts.models import ClubsModel
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import base64
if settings.DEBUG:
    print("Warning: DEBUG mode is on, which might interfere with JSON responses")
# Create your views here.
def get_user_profile_image(user):
    try:
        if hasattr(user, 'userprofile') and user.userprofile.profile_image_base64:
            return user.userprofile.profile_image_base64

        if hasattr(user, 'userprofile'):
            if user.userprofile.director_profile and user.userprofile.director_profile.profile_image_base64:
                return user.userprofile.director_profile.profile_image_base64

            if user.userprofile.student_profile and user.userprofile.student_profile.profile_image_base64:
                return user.userprofile.student_profile.profile_image_base64

            if user.userprofile.Coach_profile and user.userprofile.Coach_profile.profile_image_base64:
                return user.userprofile.Coach_profile.profile_image_base64

            if user.userprofile.receptionist_profile and user.userprofile.receptionist_profile.profile_image_base64:
                return user.userprofile.receptionist_profile.profile_image_base64

        return None
    except Exception:
        return None

def get_user_full_name(user):
    userprofile = user.userprofile

    if userprofile.account_type == '2':
        return userprofile.director_profile.full_name
    elif user.userprofile.account_type == '3':
        return userprofile.student_profile.full_name
    elif user.userprofile.account_type == '4':
        return userprofile.Coach_profile.full_name
    elif user.userprofile.account_type == '5':
        return userprofile.receptionist_profile.full_name
    elif user.userprofile.account_type == '6':
        return userprofile.administrator_profile.full_name
    else:
        return None

def get_user_capacity(user):
    userprofile = user.userprofile

    if userprofile.account_type == '2':
        return 'أدمن'
    elif user.userprofile.account_type == '3':
        return 'لاعب'
    elif user.userprofile.account_type == '4':
        return 'مدرب'
    elif user.userprofile.account_type == '5':
        return 'استقبال'
    elif user.userprofile.account_type == '6':
        return 'مدير عام'
    else:
        return None

def getUserClub(user):
    userprofile = user.userprofile

    if userprofile.account_type == '2':
        return userprofile.director_profile.club
    elif user.userprofile.account_type == '3':
        return userprofile.student_profile.club
    elif user.userprofile.account_type == '4':
        return userprofile.Coach_profile.club
    elif user.userprofile.account_type == '5':
        return userprofile.receptionist_profile.club
    elif user.userprofile.account_type == '6':
        return userprofile.administrator_profile.club
    else:
        return None

def get_user_private_chats(user):
    """Get all private chats for a user with relevant information"""
    user_messengers = MessengerModel.objects.filter(messenger_users=user)
    chats = []

    for messenger in user_messengers:
        if messenger.messenger_users.count() == 2:
            other_user = messenger.messenger_users.exclude(id=user.id).first()

            if other_user:
                unread_count = MessagesModel.objects.filter(
                    messenger_room=messenger,
                    sender=other_user,
                    is_readed=False,
                    is_deleted=False  # Don't count deleted messages
                ).count()

                last_message_obj = MessagesModel.objects.filter(
                    messenger_room=messenger,
                    is_deleted=False  # Don't show deleted messages
                ).order_by('-creation_date').first()

                last_message = last_message_obj.msg if last_message_obj else None

                chat_info = {
                    'room_id': messenger.room_id,
                    'other_user': other_user,
                    'other_user_name': get_user_full_name(other_user),
                    'other_user_capacity': get_user_capacity(other_user),
                    'other_user_img': get_user_profile_image(other_user),
                    'unread_count': unread_count,
                    'last_message': last_message,
                    'last_message_time': last_message_obj.creation_date if last_message_obj else None,
                    'messenger_creation_date': messenger.creation_date
                }

                chats.append(chat_info)

    def get_sort_key(chat):
        from django.utils import timezone

        if chat['last_message_time'] is not None:
            if timezone.is_aware(chat['last_message_time']):
                return timezone.make_naive(chat['last_message_time'])
            return chat['last_message_time']
        elif chat['messenger_creation_date'] is not None:
            if timezone.is_aware(chat['messenger_creation_date']):
                return timezone.make_naive(chat['messenger_creation_date'])
            return chat['messenger_creation_date']
        else:
            import datetime
            return datetime.datetime.min

    chats.sort(key=get_sort_key, reverse=True)

    return chats


def get_group_chat_unread_count(user, club):
    """Get unread message count for the group chat"""
    return MessagesModel.objects.filter(
        messenger=club,
        is_readed=False,
        is_deleted=False  # Don't count deleted messages
    ).exclude(sender=user).count()



def messageRoom(request, room_id):
    user = request.user
    user_club = getUserClub(user)
    user_profile = request.user.userprofile
    receiver = getUserClub(user)
    is_blocked = BlockUserModel.objects.filter(creator=receiver, user=user).exists()
    is_favorite = FavoriteUserModel.objects.filter(creator=receiver, user=user).exists()
    messages_list = []
    last_date = None
    msg_date = []
    messages = MessagesModel.objects.filter(messenger__id=room_id, is_deleted=False)
    is_director = user.userprofile.account_type == '2'
    chat_enabled = receiver.chat_enabled


    for msg in messages:
        if last_date == None:
            last_date=msg.creation_date.date()
        elif msg.creation_date.date() != last_date:
            messages_list.append([last_date, msg_date])
            last_date=msg.creation_date.date()
            msg_date = []

        msg_date.append(msg)
    if msg_date:
        messages_list.append([last_date, msg_date])

    profile_image = receiver.club_profile_image_base64
    private_chats = get_user_private_chats(user)
    group_unread_count = get_group_chat_unread_count(user, user_club)
    return render(request, 'messenger/viewMessage.html', {
        'is_blocked': is_blocked,
        'is_favorite': is_favorite,
        'messages_list': messages_list,
        'room_id': room_id,
        'current_room_id': room_id,
        'receiver': receiver,
        'profile_image': profile_image,
        'is_director': is_director,
        'chat_enabled': chat_enabled,
        'club': user_club,
        'private_chats': private_chats,
        'group_unread_count': group_unread_count,
        'user': user,
        'user_profile': user_profile,
    })


def get_messenger_model(sender, receiver):
    messengers = MessengerModel.objects.filter(messenger_users=sender).filter(messenger_users=receiver)
    return messengers

def createMessager(request, receiver_id):
    sender = request.user
    receiver = User.objects.get(id=receiver_id)

    messengers = get_messenger_model(sender, receiver)

    if sender != receiver:
        room_id = None
        if not messengers.exists():
            messenger = MessengerModel.objects.create()
            messenger.messenger_users.set([sender, receiver])
            messenger.save()
            room_id = messenger.room_id
        else:
            room_id = messengers.first().room_id
        return redirect('messageRoom', room_id)
    else:
        return redirect('index')


def AddFavorite(request, receiver_id):
    creator_user = request.user
    receiver = User.objects.get(id=receiver_id)

    # Get the club associated with the creator user
    creator_club = getUserClub(creator_user)

    if not FavoriteUserModel.objects.filter(creator=creator_club, user=receiver).exists():
        fav = FavoriteUserModel.objects.create(creator=creator_club, user=receiver)
        fav.save()

    room = get_messenger_model(sender=creator_user, receiver=receiver).first()

    return redirect('messageRoom', room.room_id)

def DeleteFavorite(request, fav_id):
    sender = request.user
    if request.GET.get('redir'):
        receiver = User.objects.get(id=fav_id)
        room = get_messenger_model(sender=sender, receiver=receiver).first()
        favs = FavoriteUserModel.objects.filter(creator=sender, user=receiver)
        if favs.exists():
            favs.first().delete()
        return redirect('messageRoom', room.room_id)
    else:
        if FavoriteUserModel.objects.filter(id=fav_id).exists():
            fav = FavoriteUserModel.objects.get(id=fav_id)
            receiver = fav.user

            return JsonResponse({'status':True})
        return JsonResponse({'status':False})


def BlockUserMessenger(request, receiver_id):
    creator_user = request.user
    receiver = User.objects.get(id=receiver_id)

    # Get the club associated with the creator user
    creator_club = getUserClub(creator_user)

    if not BlockUserModel.objects.filter(creator=creator_club, user=receiver).exists():
        block = BlockUserModel.objects.create(creator=creator_club, user=receiver)
        block.save()

    room = get_messenger_model(sender=creator_user, receiver=receiver).first()

    return redirect('messageRoom', room.room_id)

def DeleteBlockUser(request, block_id):
    sender = request.user
    if request.GET.get('redir'):
        receiver = User.objects.get(id=block_id)
        room = get_messenger_model(sender=sender, receiver=receiver).first()
        favs = BlockUserModel.objects.filter(creator=sender, user=receiver)
        if favs.exists():
            favs.first().delete()
        return redirect('messageRoom', room.room_id)
    else:
        if BlockUserModel.objects.filter(id=block_id).exists():
            fav = BlockUserModel.objects.get(id=block_id)
            fav.delete()

            return JsonResponse({'status':True})
        return JsonResponse({'status':False})

from django.http import JsonResponse
from .models import ClubsModel  # adjust if it's in a different app

def toggle_chat_status(request, club_id):
    print("toggle_chat_status called")
    print("User:", request.user)

    user = request.user
    userprofile = user.userprofile

    print("UserProfile Account Type:", userprofile.account_type)

    if userprofile.account_type == '2':
        try:
            club = ClubsModel.objects.get(id=club_id)
            print("Club found:", club.name)

            club.chat_enabled = not club.chat_enabled
            club.save()
            print("Chat enabled status toggled to:", club.chat_enabled)

            return JsonResponse({
                'status': True,
                'enabled': club.chat_enabled
            })
        except ClubsModel.DoesNotExist:
            print("Club not found")
            return JsonResponse({'status': False, 'message': 'Club not found'})
    else:
        print("Unauthorized access attempt")

    return JsonResponse({'status': False, 'message': 'Unauthorized'})


def createPrivateChat(request, user_id):
    sender = request.user
    user_profile = sender.userprofile

    if user_profile.account_type not in ['2', '4','5']:
        return redirect('index')

    target_user = User.objects.get(id=user_id)

    messengers = get_messenger_model(sender, target_user)

    if sender != target_user:
        if not messengers.exists():
            messenger = MessengerModel.objects.create()
            messenger.messenger_users.set([sender, target_user])
            messenger.save()
            room_id = messenger.room_id
        else:
            room_id = messengers.first().room_id

        return redirect('privateMessageRoom', room_id)
    else:
        return redirect('index')

def privateMessageRoom(request, room_id):
    user = request.user
    user_profile = user.userprofile
    user_club = getUserClub(user)

    messenger = MessengerModel.objects.get(room_id=room_id)

    other_user = messenger.messenger_users.exclude(id=user.id).first()

    if not other_user:
        return redirect('index')

    other_profile = other_user.userprofile
    profile_image = get_user_profile_image(other_user)
    full_name = get_user_full_name(other_user)
    capacity = get_user_capacity(other_user)

    is_blocked = BlockUserModel.objects.filter(creator=getUserClub(user), user=other_user).exists()
    is_favorite = FavoriteUserModel.objects.filter(creator=getUserClub(user), user=other_user).exists()

    messages_list = []
    last_date = None
    msg_date = []
    messages = MessagesModel.objects.filter(messenger_room=messenger, is_deleted=False)

    for msg in messages:
        if last_date == None:
            last_date = msg.creation_date.date()
        elif msg.creation_date.date() != last_date:
            messages_list.append([last_date, msg_date])
            last_date = msg.creation_date.date()
            msg_date = []

        msg_date.append(msg)

    if msg_date:
        messages_list.append([last_date, msg_date])

    private_chats = get_user_private_chats(user)
    group_unread_count = get_group_chat_unread_count(user, user_club)

    return render(request, 'messenger/privateMessage.html', {
        'is_blocked': is_blocked,
        'is_favorite': is_favorite,
        'messages_list': messages_list,
        'room_id': room_id,
        'current_room_id': room_id,
        'other_user': other_user,
        'full_name': full_name,
        'capacity': capacity,
        'profile_image': profile_image,
        'user': user_profile,
        'club': user_club,
        'private_chats': private_chats,
        'group_unread_count': group_unread_count,
    })


@require_http_methods(["GET"])
@csrf_exempt
def get_club_members(request, club_id):
    try:
        user = request.user

        if not user.is_authenticated:
            return JsonResponse({'success': False, 'message': 'Not authenticated'}, status=401)

        if not hasattr(user, 'userprofile') or user.userprofile.account_type != '2':
            return JsonResponse({'success': False, 'message': 'Unauthorized'}, status=403)

        try:
            club = ClubsModel.objects.get(id=club_id)
        except ClubsModel.DoesNotExist:
            return JsonResponse({'success': False, 'message': 'Club not found'}, status=404)

        try:
            if not user.userprofile.director_profile or user.userprofile.director_profile.club.id != club.id:
                return JsonResponse({'success': False, 'message': 'Unauthorized - Not a director of this club'}, status=403)
        except Exception as e:
            return JsonResponse({'success': False, 'message': f'Director profile error: {str(e)}'}, status=500)

        club_members = []

        directors = User.objects.filter(
            userprofile__account_type='2',
            userprofile__director_profile__club=club
        ).exclude(id=user.id)

        students = User.objects.filter(
            userprofile__account_type='3',
            userprofile__student_profile__club=club
        )

        coaches = User.objects.filter(
            userprofile__account_type='4',
            userprofile__Coach_profile__club=club
        )

        receptionists = User.objects.filter(
            userprofile__account_type='5',
            userprofile__receptionist_profile__club=club
        )


        for member in list(directors) + list(coaches) + list(students)+ list(receptionists):
            try:
                member_info = {
                    'id': member.id,
                    'name': get_user_full_name(member),
                    'capacity': get_user_capacity(member),
                    'account_type': member.userprofile.account_type
                }

                try:
                    image_path = get_user_img(member)
                    if image_path.startswith('data:'):
                        image_path = image_path.split(',', 1)[1]
                    member_info['img'] = image_path
                except Exception as img_error:
                    import traceback
                    member_info['img'] = None

                club_members.append(member_info)
            except Exception as e:
                continue

        return JsonResponse({
            'success': True,
            'members': club_members
        })

    except Exception as e:
        import traceback
        print("Error in get_club_members:", str(e))
        print(traceback.format_exc())
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

def get_user_img(user):
    try:
        if hasattr(user, 'userprofile') and user.userprofile.profile_image_base64:
            return user.userprofile.profile_image_base64

        if hasattr(user, 'userprofile'):
            account_type = user.userprofile.account_type

            if account_type == '2' and user.userprofile.director_profile and user.userprofile.director_profile.profile_image_base64:
                return user.userprofile.director_profile.profile_image_base64

            if account_type == '3' and user.userprofile.student_profile and user.userprofile.student_profile.profile_image_base64:
                return user.userprofile.student_profile.profile_image_base64

            if account_type == '4' and user.userprofile.Coach_profile and user.userprofile.Coach_profile.profile_image_base64:
                return user.userprofile.Coach_profile.profile_image_base64

            if account_type == '5' and user.userprofile.receptionist_profile and user.userprofile.receptionist_profile.profile_image_base64:
                return user.userprofile.receptionist_profile.profile_image_base64

        return None
    except Exception:
        return None

@csrf_exempt
@require_http_methods(["POST"])
def toggle_favorite(request, user_id):
    try:
        creator_user = request.user
        target_user = User.objects.get(id=user_id)

        # Get the club associated with the creator user
        creator_club = getUserClub(creator_user)

        if not creator_club:
            return JsonResponse({'success': False, 'message': 'No club found'}, status=400)

        # Check if favorite already exists
        favorite_exists = FavoriteUserModel.objects.filter(creator=creator_club, user=target_user).exists()

        if favorite_exists:
            # Remove from favorites
            FavoriteUserModel.objects.filter(creator=creator_club, user=target_user).delete()
            is_favorite = False
        else:
            # Add to favorites
            FavoriteUserModel.objects.create(creator=creator_club, user=target_user)
            is_favorite = True

        return JsonResponse({
            'success': True,
            'is_favorite': is_favorite
        })

    except User.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'User not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

@csrf_exempt
@require_http_methods(["POST"])
def toggle_block(request, user_id):
    try:
        creator_user = request.user
        target_user = User.objects.get(id=user_id)

        # Get the club associated with the creator user
        creator_club = getUserClub(creator_user)

        if not creator_club:
            return JsonResponse({'success': False, 'message': 'No club found'}, status=400)

        # Check if block already exists
        block_exists = BlockUserModel.objects.filter(creator=creator_club, user=target_user).exists()

        if block_exists:
            # Remove block
            BlockUserModel.objects.filter(creator=creator_club, user=target_user).delete()
            is_blocked = False
        else:
            # Add block
            BlockUserModel.objects.create(creator=creator_club, user=target_user)
            is_blocked = True

        return JsonResponse({
            'success': True,
            'is_blocked': is_blocked
        })

    except User.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'User not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)

@require_http_methods(["GET"])
def get_user_status(request, user_id):
    try:
        creator_user = request.user
        target_user = User.objects.get(id=user_id)

        # Get the club associated with the creator user
        creator_club = getUserClub(creator_user)

        if not creator_club:
            return JsonResponse({'success': False, 'message': 'No club found'}, status=400)

        is_favorite = FavoriteUserModel.objects.filter(creator=creator_club, user=target_user).exists()
        is_blocked = BlockUserModel.objects.filter(creator=creator_club, user=target_user).exists()

        return JsonResponse({
            'success': True,
            'is_favorite': is_favorite,
            'is_blocked': is_blocked
        })

    except User.DoesNotExist:
        return JsonResponse({'success': False, 'message': 'User not found'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)}, status=500)