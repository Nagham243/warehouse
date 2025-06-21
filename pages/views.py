import base64
from django.shortcuts import render, redirect,get_object_or_404
from django.conf import settings
from django.contrib.auth.models import User
from accounts.models import UserProfile, ClubsModel
from .forms import  StudentProfileModelForm, DirectorProfileModelForm, ClubsModelForm
import json
from django.utils import translation

BASE_DIR = settings.BASE_DIR
import os
def index(request):
    """
    Load the index page with dynamic data from JSON file
    """
    json_file_path = os.path.join(settings.BASE_DIR, 'pages/index.json')

    try:
        with open(json_file_path, 'r', encoding='utf-8') as file:
            context = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        # Fallback to default data if file is missing or corrupted
        context = {
            "nav_items": [],
            "bullets": [],
            "services": [],
            "pricing": []
        }

    context['LANGUAGE_CODE'] = translation.get_language()
    return render(request, 'pages/index.html', context)

def switch_language_button_view(request):
    """
    View to render a page with a language switching button
    """
    current_language = translation.get_language()
    context = {
        'current_language': current_language,
    }
    return render(request, 'pages/language_button.html', context)




def Profile(request, id):
    is_club = request.GET.get('is_club')

    if is_club:
        return ViewClubProfile(request, id)
    else:
        user = User.objects.get(id=id)
        userprofile = user.userprofile
        if userprofile.account_type == '2':
            return ViewDirectorProfile(request, id)
        elif user.userprofile.account_type == '3':
            return ViewStudentProfile(request, id)
        elif user.userprofile.account_type == '4':
            return ViewCoachProfile(request, id)
        else:
            return redirect('index')



from accounts.models import Subscription, DashboardSettings
import os
import json
from django.conf import settings
from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils import translation

def ViewClubProfile(request, id):
    user = request.user
    userprofile = UserProfile.objects.get(user=user)

    club = ClubsModel.objects.get(id=id)

    # Load pricing data from JSON file
    json_file_path = os.path.join(settings.BASE_DIR, 'pages/index.json')
    pricing = []

    try:
        with open(json_file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            pricing = data.get('pricing', [])

            # Ensure each plan has an ID
            for i, plan in enumerate(pricing, 1):
                if 'id' not in plan:
                    plan['id'] = i
    except (FileNotFoundError, json.JSONDecodeError):
        # Fallback pricing data
        pricing = [
            {
                'id': 1,
                'name': 'الباقة المجانية' if translation.get_language() == 'ar' else 'Free Plan',
                'price': '0 ر.س' if translation.get_language() == 'ar' else 'Free',
                'features': ['إدارة أساسية', 'دعم محدود'] if translation.get_language() == 'ar' else ['Basic Management', 'Limited Support'],
                'amount': 0.0
            },
            {
                'id': 2,
                'name': 'الباقة الأساسية' if translation.get_language() == 'ar' else 'Basic Plan',
                'price': '99 ر.س' if translation.get_language() == 'ar' else '99 SAR',
                'features': ['إدارة المواعيد', 'قاعدة بيانات العملاء', 'التقارير الأساسية'] if translation.get_language() == 'ar' else ['Appointment Management', 'Client Database', 'Basic Reports'],
                'amount': 99.0
            },
            {
                'id': 3,
                'name': 'الباقة المتقدمة' if translation.get_language() == 'ar' else 'Advanced Plan',
                'price': '199 ر.س' if translation.get_language() == 'ar' else '199 SAR',
                'features': ['جميع مميزات الأساسية', 'التسويق عبر الرسائل', 'التقارير المتقدمة'] if translation.get_language() == 'ar' else ['All Basic Features', 'SMS Marketing', 'Advanced Reports'],
                'amount': 199.0
            },
            {
                'id': 4,
                'name': 'الباقة المتقدمة' if translation.get_language() == 'ar' else 'Advanced Plan',
                'price': '199 ر.س' if translation.get_language() == 'ar' else '199 SAR',
                'features': ['جميع مميزات الأساسية', 'التسويق عبر الرسائل', 'التقارير المتقدمة'] if translation.get_language() == 'ar' else ['All Basic Features', 'SMS Marketing', 'Advanced Reports'],
                'amount': 199.0
            }
        ]



    # Get current subscription
    current_subscription = Subscription.get_active_subscription(user)
    current_plan = None

    if current_subscription:
        # User has an active subscription
        current_plan_id = int(current_subscription.plan_id)
        current_plan = next((plan for plan in pricing if plan['id'] == current_plan_id), pricing[0])
    else:
        # No active subscription, check club's current_plan_id or default to free
        current_plan_id = getattr(club, 'current_plan_id', 1)  # Default to plan 1 (free)
        current_plan = next((plan for plan in pricing if plan['id'] == current_plan_id), pricing[0])

        # Create a free subscription if none exists
        if not current_subscription and current_plan_id == 1:
            from django.utils import timezone
            from datetime import timedelta
            current_subscription = Subscription.objects.create(
                user=user,
                club=club,
                plan_id='1',
                plan_name=current_plan['name'],
                amount=0.0,
                status='active',
                end_date=timezone.now() + timedelta(days=365)  # Free plan for 1 year
            )

    # Get dashboard settings
    dashboard_settings, created = DashboardSettings.objects.get_or_create(
        club=club,
        defaults={'show_employee_client_counts': True}
    )

    if request.method == 'POST':
        # Handle bank information update
        if 'bank_name' in request.POST:
            iban = request.POST.get('iban', '').strip()

            # Validate IBAN format
            if iban and not iban.startswith('SA'):
                messages.error(request, 'يجب أن يبدأ رقم الآيبان بـ SA متبوعة بالأرقام' if translation.get_language() == 'ar' else 'IBAN must start with SA followed by numbers')
                return redirect('ViewClubProfile', id=club.id)
            club.bank_name = request.POST.get('bank_name')
            club.account_name = request.POST.get('account_name')
            club.account_number = request.POST.get('account_number')
            club.iban = request.POST.get('iban')
            club.save()

            messages.success(request, 'تم حفظ المعلومات البنكية بنجاح!' if translation.get_language() == 'ar' else 'Bank information saved successfully!')
            return redirect('ViewClubProfile', id=club.id)

    context = {
        'club': club,
        'dashboard_settings': dashboard_settings,
        'pricing': pricing,
        'current_plan': current_plan,
        'current_subscription': current_subscription,
        'LANGUAGE_CODE': translation.get_language()
    }

    return render(request, 'accounts/profiles/Club/ViewClubProfile.html', context)


from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.utils.translation import gettext as _
import json
from accounts.models import DashboardSettings,ClubsModel
@login_required
@require_POST
def toggle_dashboard_counts(request):
    """
    Toggle the show_employee_client_counts setting for the club's dashboard.
    This view handles AJAX requests and returns JSON responses.
    """
    try:
        # Get the club associated with the current user
        # Assuming the user has a club relationship - adjust this based on your user model
        club = request.user.club  # or however you get the club from the user

        # Alternative if you need to get club differently:
        # club = ClubsModel.objects.get(user=request.user)

        # Get or create dashboard settings for the club
        dashboard_settings, created = DashboardSettings.objects.get_or_create(
            club=club,
            defaults={'show_employee_client_counts': True}
        )

        # Toggle the setting
        dashboard_settings.show_employee_client_counts = not dashboard_settings.show_employee_client_counts
        dashboard_settings.save()

        # Prepare response message based on language
        if hasattr(request, 'LANGUAGE_CODE') and request.LANGUAGE_CODE == 'ar':
            if dashboard_settings.show_employee_client_counts:
                message = "تم تفعيل عرض بطاقات العدد بنجاح"
            else:
                message = "تم إخفاء بطاقات العدد بنجاح"
        else:
            if dashboard_settings.show_employee_client_counts:
                message = "Count cards are now visible"
            else:
                message = "Count cards are now hidden"

        return JsonResponse({
            'success': True,
            'status': dashboard_settings.show_employee_client_counts,
            'message': message
        })

    except ClubsModel.DoesNotExist:
        return JsonResponse({
            'success': False,
            'message': _('Club not found')
        }, status=404)

    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': _('An error occurred while updating settings')
        }, status=500)


def ViewDirectorProfile(request, id):
    user = User.objects.get(id=id)
    userprofile = UserProfile.objects.get(user=user)
    director = userprofile.director_profile
    return render(request, 'accounts/profiles/Director/ViewDirectorProfile.html', {'director':director, 'userprofile':userprofile})

def ViewStudentProfile(request, id):
    user = User.objects.get(id=id)
    userprofile = UserProfile.objects.get(user=user)
    student = userprofile.student_profile

    return render(request, 'accounts/profiles/Student/ViewStudentProfile.html', {'student':student, 'userprofile':userprofile})

def ViewCoachProfile(request, id):
    user = User.objects.get(id=id)
    userprofile = UserProfile.objects.get(user=user)
    coach = userprofile.Coach_profile
    return render(request, 'accounts/profiles/Coach/ViewCoachProfile.html', {'coach':coach, 'userprofile':userprofile})


def EditDirectorProfile(request, id):
    user = User.objects.get(id=id)
    userprofile = UserProfile.objects.get(user=user)
    director = userprofile.director_profile

    form = DirectorProfileModelForm(instance=director)
    if request.method == 'POST':
        form = DirectorProfileModelForm(request.POST, instance=director)
        if form.is_valid():
            form.save()
    return render(request, 'accounts/settings/Director/EditDirectorProfile.html', {'form':form})

def EditStudentProfile(request, id):
    user = User.objects.get(id=id)
    userprofile = UserProfile.objects.get(user=user)
    student = userprofile.student_profile

    form = StudentProfileModelForm(instance=student)
    if request.method == 'POST':
        form = StudentProfileModelForm(request.POST, instance=student)
        if form.is_valid():
            form.save()

    return render(request, 'accounts/settings/Student/EditStudentProfile.html', {'form':form})

def EditCoachProfile(request, id):
    user = User.objects.get(id=id)
    userprofile = UserProfile.objects.get(user=user)
    coach = userprofile.Coach_profile
    form = CoachProfileModelForm(instance=coach)
    if request.method == 'POST':
        form = CoachProfileModelForm(request.POST, instance=coach)
        if form.is_valid():
            form.save()

    return render(request, 'accounts/settings/Coach/EditCoachProfile.html', {'form':form})

from django.shortcuts import render, get_object_or_404, redirect
from .models import ClubsModel
from .forms import ClubsModelForm
import base64

def EditClubProfile(request, id):
    user = request.user
    userprofile = get_object_or_404(UserProfile, user=user)
    club = get_object_or_404(ClubsModel, id=id)

    if request.method == 'POST':
        form = ClubsModelForm(request.POST, request.FILES, instance=club)
        if form.is_valid():
            # Save the form first
            club_instance = form.save(commit=False)

            # Handle the image file separately
            image_file = request.FILES.get('club_profile_image_base64')
            if image_file:
                # Convert image to Base64
                image_data = image_file.read()
                base64_encoded = base64.b64encode(image_data).decode("utf-8")
                club_instance.club_profile_image_base64 = base64_encoded

            # Save the instance with all changes
            club_instance.save()
            return redirect("club_dashboard_index")
    else:
        form = ClubsModelForm(instance=club)

    return render(request, 'accounts/settings/Club/EditClubProfile.html', {'form': form, 'club': club})


