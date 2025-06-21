from django.shortcuts import render, redirect,get_object_or_404
from django.views.decorators.http import require_POST
import datetime, json
from students.models import ServiceOrderModel, ServicesModel,Order,OrderItem
from django.contrib.auth.models import User
from django.http import JsonResponse
from accounts.models import UserProfile,StudentProfile
from django.utils import timezone
import datetime  # ✅ Import datetime module
from club_dashboard.models import Notification
from .utils import send_notification
from django.contrib.auth.decorators import login_required  # ✅ Fix missing import
from django.contrib import messages
from club_dashboard.models import SalonAppointment
from datetime import datetime,timedelta
from receptionist_dashboard.models import BookingService,SalonBooking
import base64
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import translation
from django.utils.translation import get_language
from django.forms import formset_factory
from receptionist_dashboard.forms import SalonBookingForm ,ServiceSelectionForm
from django.db import models, transaction
from students.models import ProductsModel , CartItem,ServiceCartItem,OrderItem,Order

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
    return club

def index(request):
    context = {}
    user = request.user

    # Verify coach access
    if not hasattr(user, 'userprofile') or not hasattr(user.userprofile, 'Coach_profile') or not user.userprofile.Coach_profile:
        messages.error(request, "ليس لديك صلاحية للوصول إلى هذه الصفحة.")
        return redirect('home')

    coach = user.userprofile.Coach_profile
    coach_id = coach.id  # Use coach ID instead of name

    # Get language for messages
    lang = translation.get_language()

    try:
        # Find appointments using coach ID from multiple sources
        confirmed_appointments = []

        # Method 1: Find bookings where this coach is the primary coach
        primary_coach_bookings = SalonBooking.objects.filter(
            primary_coach=coach
        ).select_related('appointment').prefetch_related('services__service')

        for booking in primary_coach_bookings:
            if hasattr(booking, 'appointment') and booking.appointment:
                confirmed_appointments.append(booking.appointment)

        # Method 2: Find bookings where this coach is assigned to specific services
        service_bookings = BookingService.objects.filter(
            coach=coach
        ).select_related('booking__appointment').prefetch_related('service')

        for booking_service in service_bookings:
            if hasattr(booking_service.booking, 'appointment') and booking_service.booking.appointment:
                appointment = booking_service.booking.appointment
                if appointment not in confirmed_appointments:
                    confirmed_appointments.append(appointment)

        # Method 3: Fallback to name-based matching for legacy data
        coach_name = coach.full_name
        legacy_bookings = SalonBooking.objects.filter(
            employee=coach_name
        ).select_related('appointment').prefetch_related('services__service')

        for booking in legacy_bookings:
            if hasattr(booking, 'appointment') and booking.appointment:
                appointment = booking.appointment
                if appointment not in confirmed_appointments:
                    confirmed_appointments.append(appointment)

        # Sort appointments by creation date (newest first) and get the last 4
        confirmed_appointments.sort(
            key=lambda x: x.created_at if hasattr(x, 'created_at') else
            (x.booking.created_at if hasattr(x, 'booking') else x.id),
            reverse=True
        )
        last_four_appointments = confirmed_appointments[:4]

        print(f"Found {len(confirmed_appointments)} appointments for coach ID {coach_id} ({coach.full_name})")

    except Exception as e:
        print(f"Error retrieving appointments: {str(e)}")
        last_four_appointments = []

    club = coach.club if coach and hasattr(coach, 'club') else None
    context['LANGUAGE_CODE'] = lang
    context['CoachAppointments'] = last_four_appointments
    context['coachName'] = coach.full_name
    context['coachId'] = coach_id

    return render(request, 'coach_dashboard/index.html', context)






@login_required
def view_coach_profile(request):
    """View the coach's own profile"""
    try:
        user_profile = UserProfile.objects.get(user=request.user)
        coach = user_profile.Coach_profile

        if not coach:
            messages.error(request, "لا يوجد ملف شخصي للمدرب")
            return redirect('dashboard')  # Redirect to a suitable page

        # Get additional context data
        context = {
            'coach': coach,
            'userprofile': user_profile,
            'activity_types': dict(CoachProfile.ACTIVITY_TYPE_CHOICES),
            'approval_statuses': dict(CoachProfile.APPROVAL_STATUS_CHOICES),
            'business_document_types': dict(CoachProfile.BUSINESS_DOCUMENT_CHOICES),
        }
        context['LANGUAGE_CODE'] = translation.get_language()
        return render(request, 'accounts/profiles/Coach/ViewCoachProfile.html', context)
    except UserProfile.DoesNotExist:
        messages.error(request, "لا يوجد ملف شخصي")
        return redirect('dashboard')  # Redirect to a suitable page

from .forms import CoachProfileForm
@login_required
def edit_coach_profile(request):
    """Edit the coach's profile"""
    try:
        user_profile = UserProfile.objects.get(user=request.user)
        coach = user_profile.Coach_profile

        if not coach:
            messages.error(request, "لا يوجد ملف شخصي للمدرب")
            return redirect('dashboard')

        if request.method == 'POST':
            form = CoachProfileForm(request.POST, request.FILES, instance=coach)
            if form.is_valid():
                # Save the form data
                coach_profile = form.save(commit=False)

                # Handle profile image upload
                if 'profile_image_base64' in request.FILES:
                    image_file = request.FILES['profile_image_base64']
                    encoded_image = base64.b64encode(image_file.read()).decode('utf-8')

                    # Save to both coach profile and user profile
                    coach_profile.profile_image_base64 = f"data:image/{image_file.content_type.split('/')[-1]};base64,{encoded_image}"
                    user_profile.profile_image_base64 = coach_profile.profile_image_base64
                    user_profile.save()

                # Handle business document upload
                if 'business_document_file' in request.FILES:
                    doc_file = request.FILES['business_document_file']
                    encoded_doc = base64.b64encode(doc_file.read()).decode('utf-8')
                    file_type = doc_file.content_type
                    coach_profile.business_document_file = f"data:{file_type};base64,{encoded_doc}"

                coach_profile.save()
                messages.success(request, "تم تحديث الملف الشخصي بنجاح")
                return redirect('view_coach_profile')
            else:
                messages.error(request, "يرجى تصحيح الأخطاء في النموذج")
        else:
            form = CoachProfileForm(instance=coach)

        context = {
            'form': form,
            'coach': coach,
            'activity_choices': CoachProfile.ACTIVITY_TYPE_CHOICES,
            'business_document_choices': CoachProfile.BUSINESS_DOCUMENT_CHOICES,
        }
        context['LANGUAGE_CODE'] = translation.get_language()
        return render(request, 'accounts/settings/Coach/EditCoachProfile.html', context)
    except UserProfile.DoesNotExist:
        messages.error(request, "لا يوجد ملف شخصي")
        return redirect('dashboard')

import logging
from django.db import connection
logger = logging.getLogger(__name__)


from club_dashboard.forms import ProductsModelForm
from students.models import ProductsModel
from club_dashboard.models import ProductImg
from django.core.paginator import Paginator
def addProduct(request):
    print("=== DEBUG: addProduct function started ===")

    context = {}
    user = request.user
    print(f"DEBUG: User: {user}")
    print(f"DEBUG: User is authenticated: {user.is_authenticated}")

    coach_profile = getattr(user.userprofile, 'Coach_profile', None)
    if not coach_profile:
        messages.error(request, "لا تملك صلاحية الوصول كمدرب.")
        return redirect('some_error_page')

    club = coach_profile.club


    print(f"DEBUG: Request method: {request.method}")

    # Initialize form
    form = ProductsModelForm()
    print("DEBUG: Form initialized")

    if request.method == 'POST':
        print("DEBUG: Processing POST request")

        # Debug POST data
        print(f"DEBUG: POST data keys: {list(request.POST.keys())}")
        print(f"DEBUG: POST data: {dict(request.POST)}")

        form = ProductsModelForm(data=request.POST)
        print("DEBUG: Form created with POST data")

        if form.is_valid():
            print("DEBUG: Form is valid")
            print(f"DEBUG: Form cleaned data: {form.cleaned_data}")

            try:
                # Create product but don't save to database yet
                product = form.save(commit=False)
                print(f"DEBUG: Product created (not saved): {product}")

                # Set product attributes
                product.club = club
                product.creator = user
                product.creation_date = timezone.now()
                print(f"DEBUG: Product club set to: {product.club}")
                print(f"DEBUG: Product creator set to: {product.creator}")
                print(f"DEBUG: Product creation_date set to: {product.creation_date}")

                # Set initial approval status
                product.approval_status = 'pending'
                product.is_enabled = False
                print(f"DEBUG: Product approval_status: {product.approval_status}")
                print(f"DEBUG: Product is_enabled: {product.is_enabled}")

                # Save the product to get an ID
                product.save()
                print(f"DEBUG: Product saved successfully with ID: {product.id}")

                # Save many-to-many relationships if any
                form.save_m2m()
                print("DEBUG: Many-to-many relationships saved")

                # Handle product images
                profile_imgs = request.POST.getlist('profile_imgs')
                print(f"DEBUG: Number of profile images: {len(profile_imgs)}")

                for i, img_data in enumerate(profile_imgs):
                    print(f"DEBUG: Processing image {i+1}")
                    print(f"DEBUG: Image data length: {len(img_data) if img_data else 0}")

                    if ';base64,' in img_data:
                        print(f"DEBUG: Image {i+1} contains base64 data")

                        try:
                            format, imgstr = img_data.split(';base64,')
                            ext = format.split('/')[-1] if '/' in format else 'png'
                            print(f"DEBUG: Image {i+1} format: {format}, extension: {ext}")

                            from django.core.files.base import ContentFile
                            import base64, uuid

                            # Generate unique filename
                            filename = f'{uuid.uuid4()}.{ext}'
                            print(f"DEBUG: Generated filename: {filename}")

                            # Decode base64 data
                            decoded_data = base64.b64decode(imgstr)
                            print(f"DEBUG: Decoded data size: {len(decoded_data)} bytes")

                            data = ContentFile(decoded_data, name=filename)
                            print(f"DEBUG: ContentFile created for image {i+1}")

                            # Create ProductImg object
                            product_img = ProductImg.objects.create(
                                product=product,
                                img=data
                            )
                            print(f"DEBUG: ProductImg created with ID: {product_img.id}")

                        except Exception as img_error:
                            print(f"DEBUG ERROR: Failed to process image {i+1} - {img_error}")
                            import traceback
                            print(f"DEBUG ERROR TRACEBACK: {traceback.format_exc()}")
                    else:
                        print(f"DEBUG: Image {i+1} does not contain base64 data")

                print("DEBUG: All images processed successfully")
                messages.success(request, 'تم إرسال المنتج للمراجعة! سيتم إعلامك عند الموافقة عليه.')
                print("DEBUG: Success message added")

                print("DEBUG: Redirecting to coachviewProducts")
                return redirect('coachviewProducts')

            except Exception as save_error:
                print(f"DEBUG ERROR: Failed to save product - {save_error}")
                import traceback
                print(f"DEBUG ERROR TRACEBACK: {traceback.format_exc()}")

        else:
            print("DEBUG: Form is NOT valid")
            print(f"DEBUG: Form errors: {form.errors}")
            print(f"DEBUG: Form non-field errors: {form.non_field_errors()}")

    print("DEBUG: Preparing context and rendering template")
    context['LANGUAGE_CODE'] = translation.get_language()
    print(f"DEBUG: Language code: {context['LANGUAGE_CODE']}")
    print(f"DEBUG: Final context keys: {list(context.keys())}")

    print("DEBUG: Rendering template")
    return render(request, 'coach_dashboard/products/ProductsStock/addProductStock.html', {'form': form, 'club': club})

def editProduct(request, id):
    context = {}
    user = request.user
    product = ProductsModel.objects.get(id=id)
    profile_img_objs = ProductImg.objects.filter(product=product)
    form = ProductsModelForm(instance=product)
    club = getattr(user.userprofile.Coach_profile, 'club', None)

    if request.method == 'POST':
        form = ProductsModelForm(data=request.POST, instance=product)
        if form.is_valid():
            profile_imgs = request.POST.getlist('profile_imgs')
            images_changed = request.POST.get('images_changed', 'false') == 'true'

            updated_product = form.save(commit=False)
            updated_product.updated_at = timezone.now()
            updated_product.save()
            form.save_m2m()

            if images_changed:
                ProductImg.objects.filter(product=product).delete()

                for img_data in profile_imgs:
                    if img_data.startswith('data:image'):
                        format, imgstr = img_data.split(';base64,')
                        ext = format.split('/')[-1]

                        import uuid
                        filename = f"{uuid.uuid4()}.{ext}"

                        from django.core.files.base import ContentFile
                        import base64
                        data = ContentFile(base64.b64decode(imgstr))

                        img_obj = ProductImg(product=product)
                        img_obj.img.save(filename, data, save=False)
                        img_obj.save()

            messages.success(request, 'تم تعديل المنتج بنجاح')
            return redirect('coachviewProducts')

    context = {
        'form': form,
        'profile_imgs': profile_img_objs,
        'club' :club,
    }
    context['LANGUAGE_CODE'] = translation.get_language()
    return render(request, 'coach_dashboard/products/ProductsStock/editProductStock.html', context)

def viewProducts(request):
    context = {}
    user = request.user
    club = getattr(user.userprofile.Coach_profile, 'club', None)
    products = ProductsModel.objects.filter(creator=user)
    total_products = products.count()

    total_value = 0
    low_stock_count = 0
    out_of_stock_count = 0
    expiring_soon_count = 0
    expired_count = 0
    low_stock_threshold = 10

    for product in products:
        product_value = product.price * product.stock
        total_value += product_value

        if 0 < product.stock <= low_stock_threshold:
            low_stock_count += 1

        if product.stock == 0:
            out_of_stock_count += 1

        if product.is_expiring_soon:
            expiring_soon_count += 1

        if product.is_expired:
            expired_count += 1

    paginator = Paginator(products, 6)
    page_number = request.GET.get('page', 1)
    paginated_products = paginator.get_page(page_number)

    context = {
        'products': paginated_products,
        'total_products': total_products,
        'total_value': total_value,
        'low_stock_count': low_stock_count,
        'out_of_stock_count': out_of_stock_count,
        'expiring_soon_count': expiring_soon_count,
        'expired_count': expired_count,
        'low_stock_threshold': low_stock_threshold,
        'club':club
    }
    context['LANGUAGE_CODE'] = translation.get_language()
    return render(request, 'coach_dashboard/products/ProductsStock/viewProductsStock.html', context)


def DeleteProduct(request, id):
    art = get_object_or_404(ProductsModel, id=id)
    art.delete()
    messages.success(request, 'تم حذف المنتج بنجاح!')
    return redirect('coachviewProducts')

from club_dashboard.forms import ProductShipmentForm
def edit_shipment(request, shipment_id):
    """Edit a product shipment"""
    user = request.user
    club = getattr(user.userprofile.Coach_profile, 'club', None)

    try:
        shipment = ProductShipment.objects.get(id=shipment_id, product__club=club)
    except ProductShipment.DoesNotExist:
        messages.error(request, 'الشحنة غير موجودة!' if translation.get_language() == 'ar' else 'Shipment not found!')
        return redirect('coachviewProducts')

    if request.method == 'POST':
        form = ProductShipmentForm(request.POST, instance=shipment, club=club)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم تحديث الشحنة بنجاح!' if translation.get_language() == 'ar' else 'Shipment updated successfully!')
            return redirect('coachview_product_shipments', product_id=shipment.product.id)
        else:
            messages.error(request, 'يرجى تصحيح الأخطاء أدناه.' if translation.get_language() == 'ar' else 'Please correct the errors below.')
    else:
        form = ProductShipmentForm(instance=shipment, club=club)

    context = {
        'form': form,
        'shipment': shipment,
        'product': shipment.product,
        'club': club,
        'LANGUAGE_CODE': translation.get_language(),
        'is_edit': True,
    }

    return render(request, 'coach_dashboard/products/ProductsStock/add_edit_shipment.html', context)


def delete_shipment(request, shipment_id):
    """Delete a product shipment"""
    user = request.user
    club = getattr(user.userprofile.Coach_profile, 'club', None)

    try:
        shipment = ProductShipment.objects.get(id=shipment_id, product__club=club)
        product_id = shipment.product.id
        product_title = shipment.product.title
        quantity = shipment.quantity

        shipment.delete()

        messages.success(
            request,
            f'تم حذف شحنة المنتج "{product_title}" بكمية {quantity} وحدة بنجاح!'
            if translation.get_language() == 'ar'
            else f'Shipment for product "{product_title}" with quantity {quantity} units deleted successfully!'
        )

        return redirect('coachview_product_shipments', product_id=product_id)

    except ProductShipment.DoesNotExist:
        messages.error(request, 'الشحنة غير موجودة!' if translation.get_language() == 'ar' else 'Shipment not found!')
        return redirect('coachviewProducts')


# Update your existing add_shipment view to use the same template
def add_shipment(request):
    """Add a new product shipment"""
    user = request.user
    club = getattr(user.userprofile.Coach_profile, 'club', None)

    # Get product_id from URL parameters if provided
    product_id = request.GET.get('product_id')
    product = None

    if product_id:
        try:
            product = ProductsModel.objects.get(id=product_id, club=club)
        except ProductsModel.DoesNotExist:
            messages.error(request, 'المنتج غير موجود!' if translation.get_language() == 'ar' else 'Product not found!')
            return redirect('coachviewProducts')

    if request.method == 'POST':
        form = ProductShipmentForm(request.POST, club=club)
        if form.is_valid():
            shipment = form.save()
            messages.success(request, 'تمت إضافة الشحنة بنجاح!' if translation.get_language() == 'ar' else 'Shipment added successfully!')
            return redirect('coachview_product_shipments', product_id=shipment.product.id)
        else:
            messages.error(request, 'يرجى تصحيح الأخطاء أدناه.' if translation.get_language() == 'ar' else 'Please correct the errors below.')
    else:
        form = ProductShipmentForm(club=club)
        # Pre-select the product if provided
        if product:
            form.fields['product'].initial = product

    context = {
        'form': form,
        'product': product,
        'club': club,
        'LANGUAGE_CODE': translation.get_language(),
        'is_edit': False,
    }

    return render(request, 'coach_dashboard/products/ProductsStock/add_edit_shipment.html', context)

def view_product_shipments(request, product_id):
    user = request.user
    club = getattr(user.userprofile.Coach_profile, 'club', None)


    try:
        product = ProductsModel.objects.get(id=product_id, club=club)
    except ProductsModel.DoesNotExist:
        messages.error(request, 'المنتج غير موجود!')
        return redirect('coachviewProducts')

    shipments = ProductShipment.objects.filter(product=product).order_by('-created_at')

    expiring_soon_count = sum(1 for s in shipments if s.is_expiring_soon)
    expired_count = sum(1 for s in shipments if s.is_expired)
    valid_count = len(shipments) - expiring_soon_count - expired_count

    total_quantity = sum(s.quantity for s in shipments)
    expiring_soon_quantity = sum(s.quantity for s in shipments if s.is_expiring_soon)
    expired_quantity = sum(s.quantity for s in shipments if s.is_expired)
    valid_quantity = total_quantity - expiring_soon_quantity - expired_quantity

    context = {
        'product': product,
        'shipments': shipments,
        'stats': {
            'total_count': len(shipments),
            'expiring_soon_count': expiring_soon_count,
            'expired_count': expired_count,
            'valid_count': valid_count,
            'total_quantity': total_quantity,
            'expiring_soon_quantity': expiring_soon_quantity,
            'expired_quantity': expired_quantity,
            'valid_quantity': valid_quantity,
        },
        'club':club,
    }
    context['LANGUAGE_CODE'] = translation.get_language()
    return render(request, 'coach_dashboard/products/ProductsStock/view_product_shipments.html', context)


from club_dashboard.models import ProductShipment
def product_details(request, product_id):
    user = request.user
    club = getattr(user.userprofile.Coach_profile, 'club', None)

    try:
        product = ProductsModel.objects.get(id=product_id, club=club)
    except ProductsModel.DoesNotExist:
        messages.error(request, 'المنتج غير موجود!')
        return redirect('coachviewProducts')

    product_images = product.product_images.all()

    shipments = ProductShipment.objects.filter(product=product).order_by('-created_at')

    expiring_soon_count = sum(1 for s in shipments if s.is_expiring_soon)
    expired_count = sum(1 for s in shipments if s.is_expired)
    valid_count = len(shipments) - expiring_soon_count - expired_count

    total_quantity = sum(s.quantity for s in shipments)
    expiring_soon_quantity = sum(s.quantity for s in shipments if s.is_expiring_soon)
    expired_quantity = sum(s.quantity for s in shipments if s.is_expired)
    valid_quantity = total_quantity - expiring_soon_quantity - expired_quantity

    context = {
        'product': product,
        'product_images': product_images,
        'shipments': shipments,
        'stats': {
            'total_count': len(shipments),
            'expiring_soon_count': expiring_soon_count,
            'expired_count': expired_count,
            'valid_count': valid_count,
            'total_quantity': total_quantity,
            'expiring_soon_quantity': expiring_soon_quantity,
            'expired_quantity': expired_quantity,
            'valid_quantity': valid_quantity,
        },
        'club':club,
    }
    context['LANGUAGE_CODE'] = translation.get_language()
    return render(request, 'coach_dashboard/products/ProductsStock/product_details.html', context)



from accounts.models import CoachProfile
from club_dashboard.forms import ServicesModelForm, ServicesClassificationModelForm
from students.models import ServicesClassificationModel
from decimal import Decimal
import time
from django.core.files.base import ContentFile
import base64
def addServices(request):
    context = {}
    user = request.user
    club = getattr(user.userprofile.Coach_profile, 'club', None)

    coaches = CoachProfile.objects.filter(club=club)
    classifications = ServicesClassificationModel.objects.filter(club=club)

    form = ServicesModelForm()
    form.fields['coaches'].queryset = coaches
    form.fields['classification'].queryset = classifications

    if request.method == 'POST':
        form = ServicesModelForm(data=request.POST)
        form.fields['coaches'].queryset = coaches
        form.fields['classification'].queryset = classifications

        if form.is_valid():
            ser = form.save(commit=False)
            ser.club = club
            ser.creator = user
            ser.creation_date = timezone.now()

            ser.age_from = 0
            ser.age_to = 100
            ser.subscription_days = 30

            duration = request.POST.get('duration')
            if duration:
                ser.duration = int(duration)
            else:
                ser.duration = 0

            discounted_price = request.POST.get('discounted_price')
            if discounted_price and discounted_price.strip():
                ser.discounted_price = Decimal(discounted_price)

            ser.save()

            # Handle coaches (many-to-many)
            form.save_m2m()

            # Handle classification (single selection for many-to-many field)
            selected_classification = form.cleaned_data.get('classification')
            if selected_classification:
                ser.classification.set([selected_classification])

            image_data = request.POST.get('service_image_data')
            if image_data and image_data.startswith('data:image'):
                format, imgstr = image_data.split(';base64,')
                ext = format.split('/')[-1]

                filename = f"service_{ser.id}_{int(time.time())}.{ext}"
                temp_file = ContentFile(base64.b64decode(imgstr), name=filename)

                ser.image.save(filename, temp_file, save=True)

            return redirect('coachviewServices')
        else:
            print(form.errors)

    context['LANGUAGE_CODE'] = translation.get_language()
    selected_coach_ids = request.POST.getlist('coaches') if request.method == 'POST' else []
    selected_classification_id = request.POST.get('classification') if request.method == 'POST' else None

    return render(request, 'coach_dashboard/services/addServices.html', {
        'form': form,
        'selected_coach_ids': selected_coach_ids,
        'selected_classification_id': selected_classification_id,
        'club': club
    })


from decimal import Decimal
def editServices(request, id):
    context = {}
    ser = ServicesModel.objects.get(id=id)
    user = request.user
    club = getattr(user.userprofile.Coach_profile, 'club', None)
    classifications = ServicesClassificationModel.objects.filter(club=club)

    coaches = CoachProfile.objects.filter(club=club)
    form = ServicesModelForm(instance=ser)
    form.fields['coaches'].queryset = coaches
    form.fields['classification'].queryset = classifications

    if request.method == 'POST':
        form = ServicesModelForm(data=request.POST, instance=ser)
        form.fields['coaches'].queryset = coaches
        form.fields['classification'].queryset = classifications
        if form.is_valid():
            ser = form.save(commit=False)
            ser.creation_date = timezone.now()

            duration = request.POST.get('duration')
            ser.duration = int(duration) if duration else 0

            discounted_price = request.POST.get('discounted_price')
            if discounted_price and discounted_price.strip():
                ser.discounted_price = Decimal(discounted_price)
            else:
                ser.discounted_price = None

            # Check if the current image should be removed
            remove_current_image = request.POST.get('remove_current_image')
            if remove_current_image == 'true' and ser.image:
                # Delete the old image file
                ser.image.delete(save=False)

            # Handle classification (single selection for many-to-many field)
            selected_classification = form.cleaned_data.get('classification')
            if selected_classification:
                ser.classification.set([selected_classification])

            # Process new image upload if available
            image_data = request.POST.get('service_image_data')
            if image_data and image_data.startswith('data:image'):
                # Get the format and the actual base64 data
                format, imgstr = image_data.split(';base64,')
                ext = format.split('/')[-1]

                # Generate filename and save path
                filename = f"service_{ser.id}_{int(time.time())}.{ext}"
                temp_file = ContentFile(base64.b64decode(imgstr), name=filename)

                # If there's an existing image, delete it first
                if ser.image:
                    ser.image.delete(save=False)

                # Save to the model's ImageField
                ser.image.save(filename, temp_file, save=False)

            ser.save()
            form.save_m2m()
            return redirect('coachviewServices')
        else:
            print(form.errors)

    context['LANGUAGE_CODE'] = translation.get_language()

    # Get the current coaches and classification for the service
    current_coaches = ser.coaches.all()
    selected_coach_ids = [str(coach.id) for coach in current_coaches]

    # Get the current classification (assuming single selection)
    current_classification = ser.classification.first()
    selected_classification_id = str(current_classification.id) if current_classification else None

    # Add pricing period choices to context
    context.update({
        'form': form,
        'selected_coach_ids': selected_coach_ids,
        'club': club,
        'selected_classification_id': selected_classification_id,
        'pricing_period_choices': ServicesModel.PRICING_PERIOD_CHOICES,
    })

    return render(request, 'coach_dashboard/services/editServices.html', context)


def viewServices(request):
    context = {}
    user = request.user
    club = getattr(user.userprofile.Coach_profile, 'club', None)
    services = ServicesModel.objects.filter(creator=user)

    if services:
        # Calculate average monthly price (normalize all prices to monthly rate)
        total_monthly_price = sum(service.monthly_price for service in services)
        avg_monthly_price = total_monthly_price / len(services)
        avg_monthly_price = round(avg_monthly_price, 1)

        # Calculate average duration
        avg_duration = sum(service.duration for service in services) / len(services)
        avg_duration_hours = int(avg_duration // 60)
        avg_duration_minutes = int(avg_duration % 60)

        # Calculate pricing period statistics
        pricing_periods = [service.pricing_period_months for service in services]
        most_common_period = max(set(pricing_periods), key=pricing_periods.count)

        # Get pricing period choices for display
        pricing_period_choices = dict(ServicesModel.PRICING_PERIOD_CHOICES)

    else:
        avg_monthly_price = 0
        avg_duration_hours = 0
        avg_duration_minutes = 0
        most_common_period = 1
        pricing_period_choices = dict(ServicesModel.PRICING_PERIOD_CHOICES)

    context = {
        'services': services,
        'avg_monthly_price': avg_monthly_price,
        'avg_duration_hours': avg_duration_hours,
        'avg_duration_minutes': avg_duration_minutes,
        'most_common_period': most_common_period,
        'pricing_period_choices': pricing_period_choices,
        'club': club,
    }
    context['LANGUAGE_CODE'] = translation.get_language()
    return render(request, 'coach_dashboard/services/viewServices.html', context)

def viewServiceDetails(request, service_id):
    context = {}
    user = request.user
    club = getattr(user.userprofile.Coach_profile, 'club', None)

    try:
        service = ServicesModel.objects.get(id=service_id, club=club)
    except ServicesModel.DoesNotExist:
        messages.error(request, 'Service not found.')
        return redirect('coachviewServices')

    context = {
        'service': service,
        'club': club,
    }
    context['LANGUAGE_CODE'] = translation.get_language()
    return render(request, 'coach_dashboard/services/viewServiceDetails.html', context)

def DeleteServices(request, id):
    art = ServicesModel.objects.get(id=id)
    art.delete()
    return redirect('coachviewServices')

def addServicesClassification(request):
    user = request.user
    club = getattr(user.userprofile.Coach_profile, 'club', None)
    form = ServicesClassificationModelForm()
    if request.method == 'POST':
        form = ServicesClassificationModelForm(data=request.POST)
        if form.is_valid():
            cla = form.save(commit=False)
            cla.club = club
            cla.creator = user
            cla.creation_date = timezone.now()
            cla.save()


    return render(request, 'coach_dashboard/services/Classification/addClassification.html', {'form':form})

def editServicesClassification(request, id):
    cla = ServicesClassificationModel.objects.get(id=id)
    form = ServicesClassificationModelForm(instance=cla)
    if request.method == 'POST':
        form = ServicesClassificationModelForm(data=request.POST, instance=cla)
        if form.is_valid():
            form.save()

    return render(request, 'coach_dashboard/services/Classification/editClassification.html', {'form':form})

def viewServicesClassification(request):
    user = request.user
    club = getattr(user.userprofile.Coach_profile, 'club', None)
    classifications = ServicesClassificationModel.objects.filter(club=club)
    return render(request, 'coach_dashboard/services/Classification/viewClassification.html', {'classifications':classifications})

def DeleteServicesClassification(request, id):
    art = ServicesClassificationModel.objects.get(id=id)
    art.delete()
    return redirect('coachviewServicesClassification')

from .models import Notification
def viewCoachNotifications(request):
    context = {}
    """Displays all coach notifications and marks them as read."""
    user = request.user

    club = getattr(user.userprofile.Coach_profile, 'club', None)
    coach = getattr(user.userprofile, 'Coach_profile', None)

    notifications = Notification.objects.filter(club=coach).order_by('-created_at')

    unread_count = notifications.filter(is_read=False).update(is_read=True)
    context['LANGUAGE_CODE'] = translation.get_language()
    return render(request, 'coach_dashboard/notifications/viewCoachNotifications.html', {
        'notifications': notifications,
        'unread_count': unread_count,
        'club':club,
    })


def delete_notification(request, notification_id):
    """Delete a specific notification"""
    user = request.user
    if request.method == 'POST':
        try:
            notification = Notification.objects.get(id=notification_id)
            # Check if the notification belongs to the user's club
            club = getattr(user.userprofile.Coach_profile, 'club', None)
            if notification.club == club:
                notification.delete()
                messages.success(request, "Notification deleted successfully.")
            else:
                messages.error(request, "You don't have permission to delete this notification.")
        except Notification.DoesNotExist:
            messages.error(request, "Notification not found.")

    return redirect('viewCoachNotifications')

def delete_all_notifications(request):
    user = request.user
    """Delete all notifications for the club"""
    if request.method == 'POST':
        club = getattr(user.userprofile.Coach_profile, 'club', None)
        if club:
            deleted_count, _ = Notification.objects.filter(club=club).delete()
            messages.success(request, f"Deleted {deleted_count} notifications.")
        else:
            messages.error(request, "No club associated with your account.")

    return redirect('viewCoachNotifications')
