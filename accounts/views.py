import random
from django.utils.timezone import now,timedelta
import base64
from django.core.mail import send_mail
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages  # Import Django messages framework
from .forms import StudentProfileForm, DirectorSignupForm , ReceptionistSignupForm,AdministratorSignupForm,ForgotPasswordForm,ResetPasswordForm,VendorRegistrationForm,VendorApprovalForm
from .models import UserProfile, DirectorProfile, ClubsModel,ReceptionistProfile, CoachProfile
from .models import UserProfile, StudentProfile, OTP,PasswordResetToken
from django.utils import translation
import string
from django.core.exceptions import ValidationError
from django.conf import settings


def get_main_club():
    """Get the main club instance"""
    try:
        return ClubsModel.objects.get(id=settings.MAIN_CLUB_ID)
    except ClubsModel.DoesNotExist:
        # Fallback to first club if main club doesn't exist
        return ClubsModel.objects.first()


def generate_otp():
    return str(random.randint(100000, 999999))

def signin(request):
    """Step 1: Verify email/username & password, then send OTP"""

    context = {}
    if request.method == 'POST':
        email_or_username = request.POST.get('email').strip().lower()
        password = request.POST.get('password')

        # Try to find user by email first, then by username
        user = User.objects.filter(email=email_or_username).first()
        if not user:
            user = User.objects.filter(username=email_or_username).first()

        if user:
            user = authenticate(username=user.username, password=password)
            if user:
                # Generate and save OTP
                otp_code = generate_otp()
                OTP.objects.update_or_create(user=user, defaults={"otp_code": otp_code, "created_at": now()})

                # Send OTP via email
                try:
                    send_mail(
                        "Your OTP Code",
                        f"Your OTP code is {otp_code}. It expires in 5 minutes.",
                        "noreply@yourdomain.com",  # Replace with your actual sender email
                        [user.email],
                        fail_silently=False,
                    )
                except Exception as e:
                    return render(request, 'accounts/sign/signin.html', {"error": f"Error sending email: {str(e)}"})

                request.session['otp_user_id'] = user.id  # Store user ID for OTP verification
                return redirect('verify_otp')  # Redirect to OTP verification page

        return render(request, 'accounts/sign/signin.html', {"error": "Invalid email/username or password."})

    context['LANGUAGE_CODE'] = translation.get_language()
    return render(request, 'accounts/sign/signin.html', context)

from django.db import IntegrityError
def verify_otp(request):
    context = {}
    """Step 2: Verify the OTP and complete the login process"""
    if request.method == "POST":
        otp_code = request.POST.get("otp", "").strip()
        user_id = request.session.get('otp_user_id')

        if not user_id:
            return redirect('signin')

        # Add better error handling for user retrieval
        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            # User no longer exists, clear session and redirect
            request.session.pop('otp_user_id', None)
            return redirect('signin')

        # Handle UserProfile creation more safely
        try:
            account_type = user.userprofile.account_type
        except UserProfile.DoesNotExist:
            try:
                # Create a default UserProfile if it doesn't exist
                UserProfile.objects.create(user=user, account_type='3')  # Default to student
                account_type = '3'
            except IntegrityError as e:
                # Handle the case where UserProfile creation fails
                print(f"Error creating UserProfile: {e}")
                return render(request, 'accounts/sign/otp_verify.html', {
                    "error": "Account setup error. Please contact support."
                })

        otp_record = OTP.objects.filter(user=user, otp_code=otp_code).first()

        if otp_record:
            # Check if the OTP is expired (5 minutes validity)
            if (now() - otp_record.created_at).seconds > 300:
                otp_record.delete()
                return render(request, 'accounts/sign/otp_verify.html', {
                    "error": "OTP has expired. Please request a new one."
                })

            # OTP is valid; complete the login
            login(request, user)
            otp_record.delete()  # Delete OTP after successful login
            request.session.pop('otp_user_id', None)  # SAFE deletion

            # Redirect based on user profile account type
            account_type = user.userprofile.account_type
            if account_type == '1':
                return redirect('adminIndex')
            elif account_type == '2':
                return redirect('club_dashboard_index')
            elif account_type == '3':
                return redirect('studentIndex')
            elif account_type == '4':
                return redirect('coachIndex')
            elif account_type == '5':
                return redirect('receptionistIndex')
            elif account_type == '6':
                return redirect('administrator_dashboard_index')
            else:
                return redirect('landingIndex')

        return render(request, 'accounts/sign/otp_verify.html', {"error": "Invalid OTP. Please try again."})

    context['LANGUAGE_CODE'] = translation.get_language()
    return render(request, 'accounts/sign/otp_verify.html', context)

from django.utils import timezone
def signup(request):
    context = {}
    account_type = request.POST.get('account_type', '3')  # Default to Student

    student_form = StudentProfileForm()
    director_form = DirectorSignupForm()
    receptionist_form = ReceptionistSignupForm()
    vendor_form = VendorRegistrationForm()

    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        print(f"DEBUG: Account type: {account_type}, Username: {username}, Email: {email}")

        if account_type == '4':  # Vendor registration
            if CoachProfile.objects.filter(email=email).exists():
                messages.error(request, "البريد الإلكتروني مسجل مسبقًا.")
                return redirect('signup')
        else:
            # Check if user already exists for other account types
            if User.objects.filter(username=username).exists():
                messages.error(request, "اسم المستخدم مأخوذ بالفعل.")
                return redirect('signup')
            elif User.objects.filter(email=email).exists():
                messages.error(request, "البريد الإلكتروني مسجل مسبقًا.")
                return redirect('signup')

        # Check if user already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, "اسم المستخدم مأخوذ بالفعل.")
            return redirect('signup')

        elif User.objects.filter(email=email).exists():
            messages.error(request, "البريد الإلكتروني مسجل مسبقًا.")
            return redirect('signup')

        else:
            if account_type == '4':  # Vendor Registration
                vendor_form = VendorRegistrationForm(request.POST, request.FILES)
                if vendor_form.is_valid():
                    try:
                        vendor = vendor_form.save(commit=False)
                        vendor.approval_status = 'pending'

                        vendor.club = get_main_club()

                        # Handle profile image if uploaded
                        profile_image = request.FILES.get('profile_image')
                        if profile_image:
                            try:
                                image_data = profile_image.read()
                                base64_encoded = base64.b64encode(image_data).decode('utf-8')
                                vendor.profile_image_base64 = base64_encoded
                            except Exception as e:
                                messages.error(request, f"خطأ في معالجة الصورة: {e}")
                                return redirect('signup')

                        # Handle business document file if uploaded
                        business_doc = request.FILES.get('business_document_file')
                        if business_doc:
                            try:
                                # Check file type
                                if not business_doc.name.lower().endswith(('.pdf', '.jpg', '.jpeg', '.png')):
                                    messages.error(request, "يجب أن يكون الملف من نوع PDF أو صورة")
                                    return redirect('signup')

                                # Read and encode the file
                                file_data = business_doc.read()
                                base64_encoded = base64.b64encode(file_data).decode('utf-8')
                                vendor.business_document_file = base64_encoded
                            except Exception as e:
                                messages.error(request, f"خطأ في معالجة الملف: {e}")
                                return redirect('signup')

                        vendor.save()

                        # Send notification to club director
                        send_vendor_approval_notification(vendor)

                        messages.success(request,
                                         "تم تسجيل طلبك بنجاح! سيتم مراجعة طلبك من قبل إدارة النادي وسيتم التواصل معك قريباً.")
                        return redirect('vendor_status', vendor_id=vendor.id)

                    except Exception as e:
                        messages.error(request, f"حدث خطأ غير متوقع: {e}")
                        return redirect('signup')
                else:
                    # Print form errors for debugging
                    print(vendor_form.errors)
                    messages.error(request, "حدث خطأ في بيانات التسجيل، يرجى التحقق منها.")

            elif account_type == '3':
                student_form = StudentProfileForm(request.POST, request.FILES)
                if student_form.is_valid():
                    user = User.objects.create_user(username=username, email=email, password=password)
                    student_profile = student_form.save(commit=False)
                    profile_image = request.FILES.get('profile_image_base64')
                    if profile_image:
                        try:
                            image_data = profile_image.read()
                            base64_encoded = base64.b64encode(image_data).decode('utf-8')
                            student_profile.profile_image_base64 = base64_encoded
                        except Exception as e:
                            messages.error(request, f"خطأ في معالجة الصورة: {e}")
                            return redirect('signup')

                    student_profile.save()
                    UserProfile.objects.create(user=user, account_type='3', student_profile=student_profile)

                    messages.success(request, "تم إنشاء حساب العميل بنجاح! يمكنك الآن تسجيل الدخول.")
                    return redirect('signin')
                else:
                    messages.error(request, "حدث خطأ في بيانات التسجيل، يرجى التحقق منها.")

            elif account_type == '2':  # Director Sign-Up
                director_form = DirectorSignupForm(request.POST, request.FILES)
                if director_form.is_valid():
                    try:
                        # **Step 1: Create the User first**
                        user = User.objects.create_user(username=username, email=email, password=password)

                        # **Step 2: Validate City Selection**
                        city = director_form.cleaned_data['city']
                        from .fields import citys
                        valid_city_values = [c[0] for c in citys]
                        if city not in valid_city_values:
                            messages.error(request, "اختيار المدينة غير صالح.")
                            return redirect('signup')

                        # **Step 3: Check for Existing Club**
                        club_name = director_form.cleaned_data['club_name']
                        existing_club = ClubsModel.objects.filter(name=club_name).first()
                        if existing_club:
                            messages.error(request, "اسم الصالون مستخدم بالفعل.")
                            return redirect('signup')

                        # **Step 4: Create the Club instance**
                        club = ClubsModel.objects.create(
                            name=club_name,
                            city=city,
                            street=director_form.cleaned_data['street'],
                            district=director_form.cleaned_data.get('district'),
                            about=director_form.cleaned_data.get('about'),
                            desc=director_form.cleaned_data.get('desc'),
                            club_profile_image_base64=director_form.cleaned_data.get('club_profile_image_base64', None),
                            current_plan_id=1  # Set to free plan by default
                        )

                        # **Step 5: Create Director Profile linked to the Club**
                        director_profile = DirectorProfile.objects.create(
                            full_name=director_form.cleaned_data['username'],
                            phone=director_form.cleaned_data['phone'],
                            club=club,
                            about=director_form.cleaned_data.get('about')
                        )

                        # **Step 6: Create UserProfile linked to the DirectorProfile**
                        UserProfile.objects.create(user=user, account_type='2', director_profile=director_profile)

                        # **Step 7: Create default free subscription**
                        Subscription.objects.create(
                            user=user,
                            club=club,
                            plan_id='1',
                            plan_name='الباقة المجانية',
                            amount=0.00,
                            status='active',
                            start_date=timezone.now(),
                            end_date=timezone.now() + timedelta(days=365)  # Free plan for 1 year
                        )

                        messages.success(request, f"تم إنشاء النادي {club_name} بنجاح!")
                        # **Redirect to subscription info page instead of signin**
                        return redirect('subscription_info')

                    except Exception as e:
                        messages.error(request, f"حدث خطأ غير متوقع: {e}")
                        return redirect('signup')

                else:
                    messages.error(request, "حدث خطأ في التسجيل، يرجى مراجعة البيانات.")

            elif account_type == '5':  # Receptionist Sign-Up
                receptionist_form = ReceptionistSignupForm(request.POST)
                if receptionist_form.is_valid():
                    try:
                        # Create User
                        user = User.objects.create_user(
                            username=receptionist_form.cleaned_data['username'],
                            email=receptionist_form.cleaned_data['email'],
                            password=receptionist_form.cleaned_data['password']
                        )

                        # Create Receptionist Profile
                        receptionist_profile = ReceptionistProfile.objects.create(
                            full_name=receptionist_form.cleaned_data['full_name'],
                            phone=receptionist_form.cleaned_data['phone'],
                            email=receptionist_form.cleaned_data['email'],
                            club=receptionist_form.cleaned_data['club'],
                            about=receptionist_form.cleaned_data.get('about')
                        )

                        # Create UserProfile
                        UserProfile.objects.create(
                            user=user,
                            account_type='5',
                            receptionist_profile=receptionist_profile
                        )

                        messages.success(request, "تم إنشاء حساب الموظف بنجاح! يمكنك الآن تسجيل الدخول.")
                        return redirect('signin')

                    except Exception as e:
                        messages.error(request, f"حدث خطأ غير متوقع: {e}")
                        return redirect('signup')

            # elif account_type == '6':
            #     administrator_form = AdministratorSignupForm(request.POST)
            #     if administrator_form.is_valid():
            #         try:
            #             # Create User
            #             user = User.objects.create_user(
            #                 username=administrator_form.cleaned_data['username'],
            #                 email=administrator_form.cleaned_data['email'],
            #                 password=administrator_form.cleaned_data['password']
            #             )
            #
            #             # Create administrator Profile
            #             administrator_profile = ReceptionistProfile.objects.create(
            #                 full_name=administrator_form.cleaned_data['full_name'],
            #                 phone=administrator_form.cleaned_data['phone'],
            #                 email=administrator_form.cleaned_data['email'],
            #                 club=administrator_form.cleaned_data['club'],
            #                 about=administrator_form.cleaned_data.get('about')
            #             )
            #
            #             # Create UserProfile
            #             UserProfile.objects.create(
            #                 user=user,
            #                 account_type='6',
            #                 administrator_profile=administrator_profile
            #             )
            #
            #             messages.success(request, "تم إنشاء حساب الاداري بنجاح! يمكنك الآن تسجيل الدخول.")
            #             return redirect('signin')
            #
            #         except Exception as e:
            #             messages.error(request, f"حدث خطأ غير متوقع: {e}")
            #             return redirect('signup')

    context['LANGUAGE_CODE'] = translation.get_language()
    return render(request, 'accounts/sign/signup.html', {
        'student_form': student_form,
        'director_form': director_form,
        'receptionist_form': receptionist_form,
        # 'administrator_form': administrator_form,
        'account_type': account_type,
        'vendor_form': vendor_form,
    })


def send_vendor_approval_notification(vendor):
    """Send email notification to club director about new vendor registration"""
    try:
        # Get the director's email - using the specific email you provided
        director_email = "naghammohamed287@gmail.com"

        subject = f"طلب تسجيل بائع جديد - {vendor.business_name}"
        message = f"""
        تم تسجيل طلب بائع جديد يحتاج إلى موافقتك:
        
        الاسم: {vendor.full_name}
        النشاط التجاري: {vendor.business_name}
        نوع النشاط: {vendor.get_activity_type_display()}
        الهاتف: {vendor.phone}
        البريد الإلكتروني: {vendor.email}
        المدينة: {vendor.city}
        الحي: {vendor.district}
        
        يرجى الدخول إلى لوحة التحكم لمراجعة الطلب.
        """

        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [director_email],
            fail_silently=True,
        )
    except Exception as e:
        print(f"Error sending email notification: {e}")






def subscription_info(request):
    """
    Display subscription information page after successful director signup
    """
    context = {
        'LANGUAGE_CODE': translation.get_language()
    }
    return render(request, 'accounts/subscription_info.html', context)





def signout(request):
    logout(request)
    messages.success(request, "تم تسجيل الخروج بنجاح.")
    return redirect('landingIndex')

import os
import json
from django.conf import settings
def director_pricing(request):
    """
    Display pricing plans for director signup
    """
    # Check if director signup data exists in session
    if 'director_signup_data' not in request.session:
        messages.error(request, "يجب إكمال عملية التسجيل أولاً.")
        return redirect('signup')

    # Load pricing data from JSON file
    json_file_path = os.path.join(settings.BASE_DIR, 'pages/index.json')

    try:
        with open(json_file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            pricing = data.get('pricing', [])

            for i, plan in enumerate(pricing, 1):
                if 'id' not in plan:
                    plan['id'] = i
    except (FileNotFoundError, json.JSONDecodeError):
        # Fallback pricing data
        pricing = [
            {
                'id': 1,
                'name': 'الباقة الأساسية',
                'price': '99 ر.س',
                'features': ['إدارة المواعيد', 'قاعدة بيانات العملاء', 'التقارير الأساسية']
            },
            {
                'id': 2,
                'name': 'الباقة المتقدمة',
                'price': '199 ر.س',
                'features': ['جميع مميزات الأساسية', 'التسويق عبر الرسائل', 'التقارير المتقدمة']
            },
        ]

    context = {
        'pricing': pricing,
        'LANGUAGE_CODE': translation.get_language(),
        'director_data': request.session['director_signup_data']
    }

    return render(request, 'accounts/director_pricing.html', context)


def select_pricing_plan(request, plan_id):
    """
    Handle pricing plan selection for director - redirect to payment
    """
    if request.method == 'POST':
        # Check if director signup data exists in session
        if 'director_signup_data' not in request.session:
            messages.error(request, "يجب إكمال عملية التسجيل أولاً.")
            return redirect('signup')

        # Redirect to checkout page for payment
        return redirect('director_checkout', plan_id=plan_id)

    return redirect('director_pricing')



from .pay_api import generate_token, initiate_payment, execute_payment

def director_checkout(request, plan_id):
    """
    Handle payment initiation for director signup
    """
    if 'director_signup_data' not in request.session:
        messages.error(request, "يجب إكمال عملية التسجيل أولاً.")
        return redirect('signup')

    json_file_path = os.path.join(settings.BASE_DIR, 'pages/index.json')

    try:
        with open(json_file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            pricing = data.get('pricing', [])
    except (FileNotFoundError, json.JSONDecodeError):
        pricing = [
            {'id': 1, 'name': 'الباقة الأساسية', 'price': '99 ر.س', 'amount': 99.0},
            {'id': 2, 'name': 'الباقة المتقدمة', 'price': '199 ر.س', 'amount': 199.0},
        ]

    selected_plan = None
    plan_id_int = int(plan_id)
    plan_id_str = str(plan_id)

    for plan in pricing:
        plan_id_from_json = plan.get('id')
        print(f"Looking for plan_id: {plan_id} (type: {type(plan_id)})")
        print(f"Available plans: {[{'id': p.get('id'), 'type': type(p.get('id'))} for p in pricing]}")
        if (plan_id_from_json == plan_id_int or
                plan_id_from_json == plan_id_str or
                str(plan_id_from_json) == plan_id_str):
            selected_plan = plan
            break

    if not selected_plan:
        messages.error(request, "الباقة المحددة غير موجودة.")
        return redirect('director_pricing')

    request.session['selected_plan'] = selected_plan

    if request.method == "POST":
        mobile = request.POST.get('mobile')
        if not mobile:
            messages.error(request, "يرجى إدخال رقم الجوال.")
            return render(request, 'accounts/director_checkout.html', {
                'plan': selected_plan,
                'director_data': request.session['director_signup_data']
            })

        try:
            token_data, token_headers = generate_token()
            token = token_headers.get("X-Security-Token")
            session_id = token_headers.get("X-Session-Id")

            amount = selected_plan.get('amount', 99.0)
            init_data, init_headers = initiate_payment(token, session_id, amount=amount, mobile=mobile)

            otp_reference = init_data["body"]["otpReference"]
            verification_token = init_headers.get("X-Verification-Token")

            request.session["urpay_token"] = token
            request.session["urpay_session_id"] = session_id
            request.session["urpay_verification_token"] = verification_token
            request.session["urpay_otp_reference"] = otp_reference
            request.session["payment_mobile"] = mobile

            messages.success(request, "تم إرسال رمز التحقق إلى رقم جوالك.")
            return redirect("director_verify_otp")

        except Exception as e:
            messages.error(request, f"حدث خطأ في عملية الدفع: {str(e)}")
            return render(request, 'accounts/director_checkout.html', {
                'plan': selected_plan,
                'director_data': request.session['director_signup_data']
            })

    return render(request, 'accounts/director_checkout.html', {
        'plan': selected_plan,
        'director_data': request.session['director_signup_data']
    })


def director_verify_otp(request):
    """
    Handle OTP verification and payment execution
    """
    required_keys = ['director_signup_data', 'selected_plan', 'urpay_token',
                     'urpay_session_id', 'urpay_verification_token', 'urpay_otp_reference']

    for key in required_keys:
        if key not in request.session:
            messages.error(request, "انتهت صلاحية الجلسة. يرجى البدء من جديد.")
            return redirect('signup')

    if request.method == "POST":
        otp = request.POST.get('otp')
        if not otp:
            messages.error(request, "يرجى إدخال رمز التحقق.")
            return render(request, 'accounts/director_verify_otp.html', {
                'plan': request.session['selected_plan'],
                'mobile': request.session.get('payment_mobile', '')
            })

        try:
            token = request.session["urpay_token"]
            session_id = request.session["urpay_session_id"]
            verification_token = request.session["urpay_verification_token"]
            otp_reference = request.session["urpay_otp_reference"]
            mobile = request.session.get("payment_mobile", "+966568595106")
            amount = request.session['selected_plan'].get('amount', 99.0)

            payment_result = execute_payment(
                token, session_id, verification_token,
                otp_reference, otp, amount, mobile
            )

            if payment_result.get("body", {}).get("status") == "SUCCESS":
                return complete_director_signup_after_payment(request, payment_result)
            else:
                messages.error(request, "فشلت عملية الدفع. يرجى المحاولة مرة أخرى.")
                return render(request, 'accounts/director_verify_otp.html', {
                    'plan': request.session['selected_plan'],
                    'mobile': mobile
                })

        except Exception as e:
            messages.error(request, f"حدث خطأ في تأكيد الدفع: {str(e)}")
            return render(request, 'accounts/director_verify_otp.html', {
                'plan': request.session['selected_plan'],
                'mobile': request.session.get('payment_mobile', '')
            })

    return render(request, 'accounts/director_verify_otp.html', {
        'plan': request.session['selected_plan'],
        'mobile': request.session.get('payment_mobile', '')
    })

from .models import Subscription
def complete_director_signup_after_payment(request, payment_result):
    """
    Complete director account creation after successful payment
    """
    try:
        signup_data = request.session['director_signup_data']
        plan_data = request.session['selected_plan']

        # **Step 1: Create the User**
        user = User.objects.create_user(
            username=signup_data['username'],
            email=signup_data['email'],
            password=signup_data['password']
        )

        # **Step 2: Create the Club instance**
        club = ClubsModel.objects.create(
            name=signup_data['club_name'],
            city=signup_data['city'],
            street=signup_data['street'],
            district=signup_data.get('district'),
            about=signup_data.get('about'),
            desc=signup_data.get('desc'),
            club_profile_image_base64=signup_data.get('club_profile_image_base64', None)
        )

        # **Step 3: Create Director Profile linked to the Club**
        director_profile = DirectorProfile.objects.create(
            full_name=signup_data['username'],
            phone=signup_data['phone'],
            club=club,
            about=signup_data.get('about')
        )

        # **Step 4: Create UserProfile linked to the DirectorProfile**
        UserProfile.objects.create(
            user=user,
            account_type='2',
            director_profile=director_profile
        )

        # **Step 5: Create Subscription record**
        subscription = Subscription.create_subscription(
            user=user,
            club=club,
            plan_data=plan_data,
            payment_reference=payment_result.get("body", {}).get("transactionId"),
            duration_days=30  # 30 days subscription
        )

        # **Step 6: Store current plan ID in club for quick access**
        club.current_plan_id = int(plan_data['id'])
        club.save()

        # Clear session data
        session_keys_to_clear = [
            'director_signup_data', 'selected_plan', 'urpay_token',
            'urpay_session_id', 'urpay_verification_token',
            'urpay_otp_reference', 'payment_mobile'
        ]

        for key in session_keys_to_clear:
            if key in request.session:
                del request.session[key]

        messages.success(request, f"تم إنشاء الصالون {signup_data['club_name']} وتفعيل باقة {plan_data['name']} بنجاح! يمكنك الآن تسجيل الدخول.")
        return redirect('signin')

    except Exception as e:
        messages.error(request, f"حدث خطأ في إنشاء الحساب بعد الدفع: {e}")
        return redirect('signup')

def generate_reset_token():
    """Generate a secure random token for password reset"""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=32))

def forgot_password(request):
    """Handle forgot password request - send reset email"""
    context = {}
    form = ForgotPasswordForm()

    if request.method == 'POST':
        form = ForgotPasswordForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email'].strip().lower()

            user = User.objects.filter(email=email).first()

            if user:
                reset_token = generate_reset_token()

                PasswordResetToken.objects.filter(user=user).delete()

                PasswordResetToken.objects.create(
                    user=user,
                    token=reset_token,
                    expires_at=now() + timedelta(hours=1)
                )

                try:
                    reset_url = request.build_absolute_uri(f'/auth/reset-password/{reset_token}/')

                    send_mail(
                        subject="إعادة تعيين كلمة المرور - Reset Password",
                        message=f"""
مرحباً {user.username},

لقد تلقينا طلباً لإعادة تعيين كلمة المرور الخاصة بك.

اضغط على الرابط التالي لإعادة تعيين كلمة المرور:
{reset_url}

هذا الرابط صالح لمدة ساعة واحدة فقط.

إذا لم تطلب إعادة تعيين كلمة المرور، يرجى تجاهل هذه الرسالة.

---

Hello {user.username},

We received a request to reset your password.

Click the following link to reset your password:
{reset_url}

This link is valid for 1 hour only.

If you didn't request a password reset, please ignore this email.
                        """,
                        from_email="noreply@yourdomain.com",
                        recipient_list=[email],
                        fail_silently=False,
                    )

                    messages.success(request, "تم إرسال رابط إعادة تعيين كلمة المرور إلى بريدك الإلكتروني.")
                    return redirect('signin')

                except Exception as e:
                    messages.error(request, f"حدث خطأ في إرسال البريد الإلكتروني: {str(e)}")
            else:
                messages.success(request, "إذا كان البريد الإلكتروني مسجلاً لدينا، ستتلقى رابط إعادة تعيين كلمة المرور.")
                return redirect('signin')

    context.update({
        'form': form,
        'LANGUAGE_CODE': translation.get_language()
    })

    return render(request, 'accounts/sign/forgot_password.html', context)

def reset_password(request, token):
    """Handle password reset with token"""
    context = {}

    reset_token = PasswordResetToken.objects.filter(
        token=token,
        expires_at__gt=now()
    ).first()

    if not reset_token:
        messages.error(request, "رابط إعادة تعيين كلمة المرور غير صالح أو منتهي الصلاحية.")
        return redirect('forgot_password')

    form = ResetPasswordForm()

    if request.method == 'POST':
        form = ResetPasswordForm(request.POST)
        if form.is_valid():
            new_password = form.cleaned_data['new_password']

            user = reset_token.user
            user.set_password(new_password)
            user.save()

            reset_token.delete()

            messages.success(request, "تم تغيير كلمة المرور بنجاح. يمكنك الآن تسجيل الدخول.")
            return redirect('signin')

    context.update({
        'form': form,
        'token': token,
        'user': reset_token.user,
        'LANGUAGE_CODE': translation.get_language()
    })

    return render(request, 'accounts/sign/reset_password.html', context)