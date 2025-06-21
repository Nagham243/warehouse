from django.shortcuts import render, redirect,get_object_or_404
from accounts.models import ClubsModel, DirectorProfile, UserProfile
from admin_dashboard.models import ActivityLog
from django.contrib import messages
from django.contrib.auth.models import User
from accounts.fields import citys
from .forms import ClubsForm, DirectorForm
from datetime import datetime
from django.contrib.admin.models import LogEntry


# Create your views here.

def index(request):
    user = request.user

    # Get the first club's pricing, or use default if no clubs exist
    try:
        default_club = ClubsModel.objects.first()
        pricing = default_club.pricing if default_club and default_club.pricing else []
    except:
        pricing = []

    # If no pricing data exists, use default pricing
    if not pricing:
        pricing = [
            {
                "name": "الباقة المجانية",
                "price": "0",
                "features": ["مستخدم واحد", "20 لاعب", "تقارير أساسية"]
            },
            {
                "name": "الباقة الأساسية",
                "price": "50",
                "features": ["5 مستخدمين", "100 لاعب", "تقارير متقدمة"]
            },
            {
                "name": "الباقة الاحترافية",
                "price": "150",
                "features": ["10 مستخدمين", "500 لاعب", "تحليل شامل للبيانات"]
            },
            {
                "name": "الباقة المميزة",
                "price": "300",
                "features": [
                    "عدد غير محدود من المستخدمين",
                    "عدد غير محدود من اللاعبين",
                    "كل الميزات المتاحة"
                ]
            }
        ]

    if user.is_authenticated:
        if user.userprofile.account_type == '1':
                    
            userprofile = UserProfile.objects.filter(account_type='2')
            clubs = ClubsModel.objects.all()
            directors = DirectorProfile.objects.all()
            recent_activities = ActivityLog.objects.all().order_by('-timestamp')[:10]

            return render(request, 'admin_dashboard/index.html', {'userprofile':userprofile, 'clubs':clubs, 'directors':directors,'pricing': pricing,'recent_activities': recent_activities})
    return redirect('landingIndex')


def addClub(request):
    form = ClubsForm
    if request.method == 'POST':
        form = ClubsForm(request.POST)
        if form.is_valid():
            club = form.save()
            log_activity(
                activity_type='club_added',
                description=f'تم إضافة نادي جديد: {club.name}',
                user=request.user,
                club=club
            )
    
    return render(request, 'admin_dashboard/Club/addClub.html', {'form':form})

def editClub(request, id):
    club = ClubsModel.objects.get(id=id)
    form = ClubsForm(instance=club)
    if request.method == 'POST':
        form = ClubsForm(request.POST, instance=club)
        if form.is_valid():
            form.save()

    return render(request, 'admin_dashboard/Club/editClub.html', {'form':form})

def viewClub(request):
    clubs = ClubsModel.objects.all()
    return render(request, 'admin_dashboard/Club/viewClub.html', {'clubs':clubs})


def deleteClub(request, id):
    club = ClubsModel.objects.get(id=id)
    club.delete()
    return redirect('viewClub')

from accounts.models import AdministrativeProfile
def addDirector(request):
    clubs = ClubsModel.objects.all()
    if request.method == 'POST':
        username = request.POST.get('username')
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        password = request.POST.get('password')
        club = request.POST.get('club')


        administrator = AdministrativeProfile.objects.create(full_name=full_name, phone=phone, club=ClubsModel.objects.get(id=club))
        administrator.save()

        user = User.objects.create(username=username, email=email)
        user.set_password(password)
        user.save()

        userprofile = UserProfile.objects.create(user=user, account_type='6', administrator_profile=administrator)
        userprofile.save()

        log_activity(
            activity_type='administrator_added',
            description=f'تم تعيين إداري جديد: {full_name} للنادي {administrator.club.name}',
            user=request.user,
            club=administrator.club
        )
        messages.success(request, 'تم إضافة الإداري بنجاح')
        return redirect('viewDirector')
    return render(request, 'admin_dashboard/Director/addDirector.html', {'clubs':clubs})


def editDirector(request, id):
    clubs = ClubsModel.objects.all()

    if request.method == 'POST':
        userprofile = UserProfile.objects.get(id=id)

        username = request.POST.get('username')
        full_name = request.POST.get('full_name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        password = request.POST.get('password')
        club = request.POST.get('club')

        director = DirectorProfile.objects.get(id=userprofile.director_profile.id)
        director.full_name = full_name
        director.phone=phone
        director.club = ClubsModel.objects.get(id=club)

        user = User.objects.get(id=userprofile.user.id)
        user.username = username
        user.email = email

        if password:
            user.set_password(password)

        
        director.save()
        user.save()


    userprofile = UserProfile.objects.get(id=id)
    username = userprofile.user.username
    full_name = userprofile.director_profile.full_name
    email = userprofile.user.email
    phone = userprofile.director_profile.phone
    club = userprofile.director_profile.club

    obj = {'username':username, 'full_name':full_name, 'email':email, 'phone':phone, 'club':club, 'clubs':clubs}

    return render(request, 'admin_dashboard/Director/editDirector.html', obj)

def viewDirector(request):
    date_time_now = datetime.now()
    directors = UserProfile.objects.filter(account_type='2')
    this_month_directors = directors.filter(creation_date__year=date_time_now.year, creation_date__month=date_time_now.month)
    Clubs = ClubsModel.objects.all()
    Directors = DirectorProfile.objects.all()

    clubs_have_Director = 0
    for i in Clubs:
        if Directors.filter(club=i).exists():clubs_have_Director+=1
        break

    return render(request, 'admin_dashboard/Director/viewDirector.html', {'directors':directors, 'this_month_directors':this_month_directors, 'clubs_have_Director':clubs_have_Director})

def deleteDirector(request, id):
    userprofile = UserProfile.objects.get(id=id)
    user = User.objects.get(id=userprofile.user.id)
    director = DirectorProfile.objects.get(id=userprofile.director_profile.id)

    director.delete()
    user.delete()

    return redirect('viewDirector')

import os
from django.conf import settings
from django.utils import translation
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib import messages
import json

def update_pricing(request):
    """
    Update the global pricing data in the index.json file
    Handles both individual plan operations and page rendering
    """
    json_file_path = os.path.join(settings.BASE_DIR, 'pages/index.json')

    try:
        with open(json_file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        data = {
            "pricing": [
                {
                    "name": "الباقة المجانية",
                    "price": "0",
                    "features": ["مستخدم واحد", "20 لاعب", "تقارير أساسية"]
                }
            ]
        }

    if request.method == 'POST':
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return handle_ajax_pricing_request(request, data, json_file_path)

        return handle_traditional_pricing_form(request, data, json_file_path)

    return render(request, 'admin_dashboard/Club/update_pricing.html', {
        'pricing_data': data.get('pricing', []),
        'LANGUAGE_CODE': translation.get_language()
    })

def handle_ajax_pricing_request(request, data, json_file_path):
    """
    Handle AJAX requests for individual plan operations
    """
    action = request.POST.get('action')

    try:
        if action == 'save_plan':
            return save_individual_plan(request, data, json_file_path)
        elif action == 'delete_plan':
            return delete_individual_plan(request, data, json_file_path)
        else:
            return JsonResponse({
                'success': False,
                'message': 'إجراء غير معروف' if translation.get_language() == 'ar' else 'Unknown action'
            })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'خطأ في الخادم: {str(e)}' if translation.get_language() == 'ar' else f'Server error: {str(e)}'
        })

def save_individual_plan(request, data, json_file_path):
    """
    Save or update an individual pricing plan
    """
    plan_id = request.POST.get('plan_id')
    name = request.POST.get('name', '').strip()
    price = request.POST.get('price', '').strip()
    features_text = request.POST.get('features', '').strip()

    if not name or not price:
        return JsonResponse({
            'success': False,
            'message': 'اسم الباقة والسعر مطلوبان' if translation.get_language() == 'ar' else 'Plan name and price are required'
        })

    features_list = [f.strip() for f in features_text.split(',') if f.strip()] if features_text else []

    plan_data = {
        'name': name,
        'price': price,
        'features': features_list
    }

    if 'pricing' not in data:
        data['pricing'] = []

    try:
        plan_index = int(plan_id) - 1
    except (ValueError, TypeError):
        return JsonResponse({
            'success': False,
            'message': 'معرف الباقة غير صحيح' if translation.get_language() == 'ar' else 'Invalid plan ID'
        })

    if 0 <= plan_index < len(data['pricing']):
        data['pricing'][plan_index] = plan_data
    else:
        data['pricing'].append(plan_data)

    try:
        with open(json_file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=2)

        return JsonResponse({
            'success': True,
            'message': 'تم حفظ الباقة بنجاح' if translation.get_language() == 'ar' else 'Plan saved successfully'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'خطأ في حفظ البيانات: {str(e)}' if translation.get_language() == 'ar' else f'Error saving data: {str(e)}'
        })

def delete_individual_plan(request, data, json_file_path):
    """
    Delete an individual pricing plan
    """
    plan_id = request.POST.get('plan_id')

    try:
        plan_index = int(plan_id) - 1
    except (ValueError, TypeError):
        return JsonResponse({
            'success': False,
            'message': 'معرف الباقة غير صحيح' if translation.get_language() == 'ar' else 'Invalid plan ID'
        })

    if 'pricing' not in data:
        data['pricing'] = []

    if not (0 <= plan_index < len(data['pricing'])):
        return JsonResponse({
            'success': False,
            'message': 'الباقة غير موجودة' if translation.get_language() == 'ar' else 'Plan not found'
        })

    if len(data['pricing']) <= 1:
        return JsonResponse({
            'success': False,
            'message': 'لا يمكن حذف الباقة الأخيرة' if translation.get_language() == 'ar' else 'Cannot delete the last plan'
        })

    try:
        del data['pricing'][plan_index]

        with open(json_file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=2)

        return JsonResponse({
            'success': True,
            'message': 'تم حذف الباقة بنجاح' if translation.get_language() == 'ar' else 'Plan deleted successfully'
        })
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': f'خطأ في حذف البيانات: {str(e)}' if translation.get_language() == 'ar' else f'Error deleting data: {str(e)}'
        })

def handle_traditional_pricing_form(request, data, json_file_path):
    """
    Handle traditional form submission (legacy support)
    """
    new_pricing = []
    i = 1

    while f'name_{i}' in request.POST:
        name = request.POST.get(f'name_{i}')
        price = request.POST.get(f'price_{i}')
        features = request.POST.get(f'features_{i}', '')

        if name and price:
            features_list = [f.strip() for f in features.split(',') if f.strip()]
            new_pricing.append({
                'name': name,
                'price': price,
                'features': features_list
            })
        i += 1

    data['pricing'] = new_pricing

    try:
        with open(json_file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=2)

        messages.success(request, "تم تحديث التسعير بنجاح" if translation.get_language() == 'ar' else "Pricing updated successfully")
    except Exception as e:
        messages.error(request, f"خطأ في حفظ البيانات: {str(e)}" if translation.get_language() == 'ar' else f"Error saving data: {str(e)}")

    return redirect('UpdatePricing')

def financial_dashboard(request):
    user = request.user

    if not user.is_authenticated or user.userprofile.account_type != '1':
        return redirect('landingIndex')

    now = datetime.now()
    current_year = now.year
    current_month = now.month

    clubs = ClubsModel.objects.all()
    total_clubs = clubs.count()

    monthly_signups = []
    monthly_revenue = []

    CLUB_SUBSCRIPTION_PRICE = 100

    for month in range(1, 13):
        month_clubs = clubs.filter(
            creation_date__year=current_year,
            creation_date__month=month
        ).count()
        monthly_signups.append(month_clubs)
        monthly_revenue.append(month_clubs * CLUB_SUBSCRIPTION_PRICE)

    total_revenue = total_clubs * CLUB_SUBSCRIPTION_PRICE

    current_month_clubs = clubs.filter(
        creation_date__year=current_year,
        creation_date__month=current_month
    ).count()
    current_month_revenue = current_month_clubs * CLUB_SUBSCRIPTION_PRICE

    if current_month == 1:
        last_month = 12
        last_month_year = current_year - 1
    else:
        last_month = current_month - 1
        last_month_year = current_year

    last_month_clubs = clubs.filter(
        creation_date__year=last_month_year,
        creation_date__month=last_month
    ).count()
    last_month_revenue = last_month_clubs * CLUB_SUBSCRIPTION_PRICE

    if last_month_revenue > 0:
        revenue_growth = ((current_month_revenue - last_month_revenue) / last_month_revenue) * 100
    else:
        revenue_growth = 100 if current_month_revenue > 0 else 0

    if last_month_clubs > 0:
        clubs_growth = ((current_month_clubs - last_month_clubs) / last_month_clubs) * 100
    else:
        clubs_growth = 100 if current_month_clubs > 0 else 0

    recent_clubs = clubs.order_by('-creation_date')[:5]

    avg_monthly_revenue = total_revenue / 12 if total_revenue > 0 else 0

    month_names = [
        'يناير', 'فبراير', 'مارس', 'أبريل', 'مايو', 'يونيو',
        'يوليو', 'أغسطس', 'سبتمبر', 'أكتوبر', 'نوفمبر', 'ديسمبر'
    ]

    monthly_data = []
    for i, month_name in enumerate(month_names):
        monthly_data.append({
            'month': month_name,
            'clubs': monthly_signups[i],
            'revenue': monthly_revenue[i]
        })

    if current_month > 0:
        projected_annual_revenue = (sum(monthly_revenue[:current_month]) / current_month) * 12
    else:
        projected_annual_revenue = 0


    top_months = sorted(
        [(month_names[i], monthly_revenue[i], monthly_signups[i]) for i in range(12)],
        key=lambda x: x[1],
        reverse=True
    )[:3]

    q1_revenue = sum(monthly_revenue[0:3])
    q2_revenue = sum(monthly_revenue[3:6])
    q3_revenue = sum(monthly_revenue[6:9])
    q4_revenue = sum(monthly_revenue[9:12])

    quarterly_data = [
        {'quarter': 'الربع الأول', 'revenue': q1_revenue},
        {'quarter': 'الربع الثاني', 'revenue': q2_revenue},
        {'quarter': 'الربع الثالث', 'revenue': q3_revenue},
        {'quarter': 'الربع الرابع', 'revenue': q4_revenue},
    ]

    context = {
        'total_clubs': total_clubs,
        'total_revenue': total_revenue,
        'current_month_clubs': current_month_clubs,
        'current_month_revenue': current_month_revenue,
        'last_month_clubs': last_month_clubs,
        'last_month_revenue': last_month_revenue,
        'revenue_growth': round(revenue_growth, 2),
        'clubs_growth': round(clubs_growth, 2),
        'subscription_price': CLUB_SUBSCRIPTION_PRICE,
        'monthly_data': monthly_data,
        'recent_clubs': recent_clubs,
        'avg_monthly_revenue': round(avg_monthly_revenue, 2),
        'projected_annual_revenue': round(projected_annual_revenue, 2),
        'top_months': top_months,
        'quarterly_data': quarterly_data,
        'current_year': current_year,
        'current_month_name': month_names[current_month - 1],
        'last_month_name': month_names[last_month - 1] if last_month <= 12 else month_names[11]
    }

    return render(request, 'admin_dashboard/financial_dashboard.html', context)


def log_activity(activity_type, description, user=None, club=None):
    ActivityLog.objects.create(
        activity_type=activity_type,
        description=description,
        user=user,
        club=club
    )