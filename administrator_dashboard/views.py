from django.shortcuts import redirect, render
from django.http import HttpResponseForbidden
from django.urls import reverse
import base64

from accounts.models import UserProfile, StudentProfile, CoachProfile
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from club_dashboard.models import Notification, Review
from django.db.models import Avg, Sum
from django.utils import timezone
import datetime
from django.utils import translation
from students.models import Order
import openpyxl
from openpyxl.styles import Font, Alignment
from django.db.models import Count
from club_dashboard.forms import AdministratorProfileForm

def get_user_club(user):
    user_profile = user.userprofile
    club = None
    if user_profile.account_type == '3':  # Student
        club = user_profile.student_profile.club if hasattr(user_profile, 'student_profile') else None
    elif user_profile.account_type == '4':  # Coach
        club = user_profile.Coach_profile.club if hasattr(user_profile, 'Coach_profile') else None
    elif user_profile.account_type == '2':  # Director
        club = user_profile.director_profile.club if hasattr(user_profile, 'director_profile') else None
    elif user_profile.account_type == '5':  # Receptionist
        club = user_profile.receptionist_profile.club if hasattr(user_profile, 'receptionist_profile') else None
    elif user_profile.account_type == '6': # Administrator
        club = user_profile.administrator_profile.club if hasattr(user_profile, 'administrator_profile') else None
    return club


@login_required
def administrator_dashboard_index(request):
    context = {}
    user = request.user

    # ✅ Ensure the user has a valid director profile
    if not hasattr(user, 'userprofile') or not user.userprofile.administrator_profile:
        messages.error(request, "Unauthorized access.")
        return redirect('administrator_dashboard_index')

    # ✅ Get the correct club for the director
    club = user.userprofile.administrator_profile.club
    club_name = club.name

    # ✅ Get directors linked through UserProfile
    directors = UserProfile.objects.filter(account_type='6', administrator_profile__club=club)
    director_count = directors.count()

    # ✅ Fetch students and coaches from this club
    students = StudentProfile.objects.filter(club=club)

    manual_status_labels = {
        'trial': 'تجريبي',
        'active': 'نشط',
        'expiring_soon': 'سينتهي قريبًا',
        'expired': 'منتهي',
    }

    # Get counts for each manual status
    manual_status_counts = StudentProfile.objects.filter(club=club) \
        .values('manual_status') \
        .annotate(count=Count('manual_status'))

    # Initialize counts for all statuses (even those with 0)
    manual_status_dict = {status: 0 for status in manual_status_labels.keys()}

    # Update with actual counts from database
    for entry in manual_status_counts:
        key = entry['manual_status'] or 'trial'  # Default to 'trial' if None
        if key in manual_status_dict:
            manual_status_dict[key] = entry['count']

    # Prepare labels and data for Chart.js
    manual_chart_labels = [manual_status_labels[k] for k in manual_status_dict.keys()]
    manual_chart_data = list(manual_status_dict.values())


    student_count = students.count()

    coaches = CoachProfile.objects.filter(club=club)
    coach_count = coaches.count()

    # ✅ Notifications
    notifications = Notification.objects.filter(club=club, is_read=False).order_by('-created_at')
    unread_count = notifications.count()
    notifications.update(is_read=True)

    # ✅ Subscriptions
    active_count, expiring_soon_count, expired_count, trial_count = 0, 0, 0, 0
    for student in students:
        status = student.get_subscription_status()
        if status == "active":
            active_count += 1
        elif status == "expiring_soon":
            expiring_soon_count += 1
        elif status == "trial":
            trial_count += 1
        else:
            expired_count += 1

    total_students = max(1, active_count + expiring_soon_count + expired_count + trial_count)

    def calc_percent(v, total):
        return round((v / total) * 100, 2) if total > 0 else 0

    active_percentage = calc_percent(active_count, total_students)
    expiring_soon_percentage = calc_percent(expiring_soon_count, total_students)
    expired_percentage = calc_percent(expired_count, total_students)
    trial_percentage = calc_percent(trial_count, total_students)

    # ✅ Top Rated Coaches
    top_rated_coaches = (
        CoachProfile.objects.filter(club=club)
        .annotate(avg_rating=Avg('coach_reviews__rating'))
        .filter(avg_rating__isnull=False)
        .order_by('-avg_rating')[:5]
    )

    # ✅ Top Reviews
    top_reviews = (
        Review.objects.filter(coach__club=club)
        .order_by('-rating', '-created_at')[:5]
    )



    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    if not start_date:
        start_date = (timezone.now() - timezone.timedelta(days=30)).strftime('%Y-%m-%d')
    if not end_date:
        end_date = timezone.now().strftime('%Y-%m-%d')

    try:
        start_date_obj = datetime.datetime.strptime(start_date, '%Y-%m-%d')
        end_date_obj = datetime.datetime.strptime(end_date, '%Y-%m-%d')
        end_date_obj = end_date_obj.replace(hour=23, minute=59, second=59)
    except ValueError:
        start_date_obj = timezone.now() - timezone.timedelta(days=30)
        end_date_obj = timezone.now()

    orders = Order.objects.filter(
        club=club,
        created_at__gte=start_date_obj,
        created_at__lte=end_date_obj
    ).order_by('-created_at')

    total_revenue = int(orders.filter(status__in=['confirmed', 'completed']).aggregate(Sum('total_price'))['total_price__sum'] or 0)

    context['LANGUAGE_CODE'] = translation.get_language()
    return render(request, 'administrator_dashboard/index.html', {
        'clubName': club_name,
        'students': students,
        'coaches': coaches,
        'directors': directors,
        'director_count': director_count,
        'coach_count': coach_count,
        'student_count': student_count,
        'active_count': active_count,
        'expiring_soon_count': expiring_soon_count,
        'expired_count': expired_count,
        'trial_count': trial_count,
        'active_percentage': active_percentage,
        'expiring_soon_percentage': expiring_soon_percentage,
        'expired_percentage': expired_percentage,
        'trial_percentage': trial_percentage,
        'notifications': notifications,
        'unread_count': unread_count,
        'top_rated_coaches': top_rated_coaches,
        'top_reviews': top_reviews,
        'total_revenue': total_revenue,
        'manual_chart_labels': manual_chart_labels,
        'manual_chart_data': manual_chart_data,
        'user':user,
        'club':club,
    })

@login_required
def view_administrator_profile(request):
    """View the administrator's profile"""
    user = request.user
    try:
        userprofile = request.user.userprofile

        if not userprofile.administrator_profile:
            return HttpResponseForbidden("You don't have permission to view this page")

        administrator = userprofile.administrator_profile
        club = administrator.club

        context = {
            'administrator': administrator,
            'userprofile': userprofile,
            'club': club,
            'user': user,
        }
        context['LANGUAGE_CODE'] = translation.get_language()
        return render(request, 'accounts/profiles/Administrator/ViewAdministratorProfile.html', context)
    except UserProfile.DoesNotExist:
        return HttpResponseForbidden("User profile not found")

@login_required
def edit_administrator_profile(request):
    """Edit the administrator's profile"""
    user = request.user
    print(f"[DEBUG] Logged in as: {user.username} (ID: {user.id})")

    try:
        userprofile = request.user.userprofile
        print("[DEBUG] Retrieved UserProfile successfully")

        if not userprofile.administrator_profile:
            print("[WARNING] User is not an administrator")
            return HttpResponseForbidden("You don't have permission to edit this page")

        administrator = userprofile.administrator_profile
        club = administrator.club
        print(f"[DEBUG] Editing AdministratorProfile for: {administrator} (Club: {club})")

        if request.method == 'POST':
            print(f"[DEBUG] POST request received with data: {request.POST}")
            form = AdministratorProfileForm(request.POST, request.FILES, instance=administrator)
            print(f"[DEBUG] Form instantiated. Valid: {form.is_valid()}")

            if form.is_valid():
                administrator = form.save(commit=False)
                administrator.club = club
                administrator.about = form.cleaned_data.get('about')
                administrator.save()
                print("[DEBUG] Administrator profile updated and saved")

                if 'profile_image_base64' in request.FILES:
                    print("[DEBUG] profile_image_base64 file detected in request.FILES")
                    image_file = request.FILES['profile_image_base64']
                    print(f"[DEBUG] Uploaded image: {image_file.name}, content_type: {image_file.content_type}")

                    try:
                        encoded_image = base64.b64encode(image_file.read()).decode('utf-8')
                        image_data = f"data:image/{image_file.content_type.split('/')[-1]};base64,{encoded_image}"

                        userprofile.profile_image_base64 = image_data
                        userprofile.save()
                        print("[DEBUG] Base64 image saved to user profile")
                    except Exception as e:
                        print(f"[ERROR] Failed to process image: {e}")
                else:
                    print("[INFO] No profile_image_base64 file found in request")

                messages.success(request, "Profile updated successfully!")
                return redirect('view_administrator_profile')
            else:
                print(f"[ERROR] Form errors: {form.errors}")
                messages.error(request, "There was an error updating your profile. Please check the form.")
        else:
            print("[DEBUG] GET request received, rendering form")
            form = AdministratorProfileForm(instance=administrator)

        context = {
            'form': form,
            'administrator': administrator,
            'userprofile': userprofile,
            'club': club
        }
        context['LANGUAGE_CODE'] = translation.get_language()
        return render(request, 'accounts/settings/Administrator/EditAdministratorProfile.html', context)

    except UserProfile.DoesNotExist:
        print("[ERROR] UserProfile not found for the current user")
        return HttpResponseForbidden("User profile not found")
