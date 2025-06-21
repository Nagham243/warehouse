from django.shortcuts import render, redirect, get_object_or_404
from club_dashboard.models import SalonAppointment
from django.contrib.auth.decorators import login_required
from .forms import SalonBookingForm ,ServiceSelectionForm,ReceptionistProfileForm
from .models import SalonBooking ,BookingService
from django.contrib import messages
from django.http import JsonResponse
from accounts.models import UserProfile ,StudentProfile
from django.contrib.auth.models import User
from club_dashboard.utils import send_notification
from accounts.forms import StudentProfileForm
from datetime import datetime, timedelta
from django.db import models , transaction
from students.models import ServicesModel
from django.forms import formset_factory
import base64
from django.views.decorators.http import require_GET
from django.utils import translation
from django.utils.translation import get_language

# Helper function to get user's club
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

@login_required
def index(request):
    club = get_user_club(request.user)
    if not club:
        messages.error(request, "No club assigned to your profile. Please contact an administrator.")
        return redirect('signin')

    students = UserProfile.objects.filter(
        account_type='3',
        student_profile__club=club
    ).select_related('user', 'student_profile')

    valid_students = [student for student in students if student.student_profile]

    user = request.user
    receptionist = user.userprofile.receptionist_profile
    if request.user.userprofile.account_type != '5':
        return redirect('signin')

    receptionist_profile = request.user.userprofile.receptionist_profile

    context = {
        'receptionist': receptionist_profile,
        'club': receptionist_profile.club if receptionist_profile else None,
        'students': valid_students
    }
    context['LANGUAGE_CODE'] = translation.get_language()
    return render(request, 'receptionist_dashboard/index.html', context)

@login_required
def salon_appointments(request):
    context = {}

    days = ['السبت', 'الأحد', 'الإثنين', 'الثلاثاء', 'الأربعاء', 'الخميس', 'الجمعة']


    from datetime import time
    time_slots = []
    for hour in range(12, 24):
        time_slots.append(time(hour, 0))
    time_slots.append(time(0, 0))


    schedule = {}

    club = get_user_club(request.user)
    if not club:
        messages.error(request, "No club assigned to your profile. Please contact an administrator.")
        return render(request, 'receptionist_dashboard/salon_appointments.html', {
            'schedule': {},
            'days': days,
            'time_slots': [slot.strftime('%I:%M %p') for slot in time_slots]
        })

    for day in days:
        schedule[day] = []
        appointments = SalonAppointment.objects.filter(
            day=day,
            club=club,
            is_paid=True,
        ).order_by('start_time')

        for slot in time_slots:
            slot_end = (datetime.combine(datetime.today(), slot) + timedelta(hours=1)).time()

            slot_appointments = appointments.filter(
                start_time__gte=slot,
                start_time__lt=slot_end
            )

            booking_count = slot_appointments.count()

            slot_info = {
                'time': slot.strftime('%I:%M %p'),
                'booking_count': booking_count,
                'has_bookings': booking_count > 0,
                'appointments': [
                    {
                        'id': appt.id,
                        'start': appt.start_time.strftime('%I:%M %p'),
                        'end': appt.end_time.strftime('%I:%M %p') if appt.end_time else "N/A"
                    } for appt in slot_appointments if hasattr(appt, 'booking')
                ]
            }

            schedule[day].append(slot_info)
    context['LANGUAGE_CODE'] = translation.get_language()
    return render(request, 'receptionist_dashboard/salon_appointments.html', {
        'schedule': schedule,
        'days': days,
        'time_slots': [slot.strftime('%I:%M %p') for slot in time_slots],
        'club': club,
    })

@login_required
def select_appointment_day(request):
    context ={}
    club = get_user_club(request.user)
    if not club:
        messages.error(request, "No club assigned to your profile. Please contact an administrator.")
        return redirect('index')

    days = ['السبت', 'الأحد', 'الإثنين', 'الثلاثاء', 'الأربعاء', 'الخميس', 'الجمعة']



    if request.method == 'POST':
        selected_day = request.POST.get('day')
        return redirect('book_appointment_details', day=selected_day)
    context['LANGUAGE_CODE'] = translation.get_language()
    return render(request, 'receptionist_dashboard/select_appointment_day.html', {
        'days': days,
        'club':club
    })

@login_required
def book_appointment_details(request, day):
    context = {}
    club = get_user_club(request.user)
    if not club:
        messages.error(request, "No club assigned to your profile. Please contact an administrator.")
        return redirect('index')

    # Get services for this club
    available_services = ServicesModel.objects.filter(club=club, is_enabled=True)

    # Create dynamic formset with extra forms that can be added
    ServiceFormSet = formset_factory(ServiceSelectionForm, extra=1)

    appointments = []
    day_appointments = SalonAppointment.objects.filter(
        day=day,
        available=False,
        club=club,
    ).order_by('start_time')

    for appointment in day_appointments:
        try:
            booking = appointment.booking
            services = BookingService.objects.filter(booking=booking)
            service_names = ", ".join([s.service.title for s in services])

            start_datetime = datetime.combine(datetime.today(), appointment.start_time)
            end_datetime = datetime.combine(datetime.today(), appointment.end_time)
            total_duration = (end_datetime - start_datetime).seconds / 60

            appointments.append({
                'start_time': appointment.start_time,
                'end_time': appointment.end_time,
                'employee_name': booking.employee,
                'total_duration': total_duration,
                'services': service_names
            })
        except:
            # Skip appointments without valid booking information
            continue

    if request.method == 'POST':
        booking_form = SalonBookingForm(request.POST)
        service_formset = ServiceFormSet(request.POST, prefix='services')

        if booking_form.is_valid() and service_formset.is_valid():
            total_duration = 0
            services_data = []
            coaches_data = []

            # Process the service formset data
            for form in service_formset:
                if form.cleaned_data and form.cleaned_data.get('service'):
                    service = form.cleaned_data['service']
                    coach = form.cleaned_data.get('coach')

                    total_duration += service.duration
                    services_data.append({
                        'service_id': service.id,
                        'coach_id': coach.id if coach else None,
                        'coach_name': coach.full_name if coach else None
                    })

            # Store the booking form data
            booking_data = booking_form.cleaned_data.copy()

            # Store the data in the session
            request.session['booking_form_data'] = booking_data
            request.session['services_data'] = services_data
            request.session['total_duration'] = total_duration

            return redirect('select_appointment_time', day=day)
        else:
            messages.error(request, "هناك خطأ في البيانات المدخلة. الرجاء التحقق والمحاولة مرة أخرى.")
    else:
        booking_form = SalonBookingForm()

        # Initialize formset with all available services for the club
        initial_data = []
        service_formset = ServiceFormSet(prefix='services', initial=initial_data)

        # Set queryset for service fields to filter by club
        for form in service_formset:
            form.fields['service'].queryset = available_services

    context['LANGUAGE_CODE'] = translation.get_language()
    return render(request, 'receptionist_dashboard/book_appointment_details.html', {
        'booking_form': booking_form,
        'service_formset': service_formset,
        'day': day,
        'appointments': appointments,
        'club': club,
        'available_services': available_services,
    })

@login_required
def select_appointment_time(request, day):
    context = {}
    club = get_user_club(request.user)
    if not club:
        messages.error(request, "No club assigned to your profile. Please contact an administrator.")
        return redirect('index')

    booking_form_data = request.session.get('booking_form_data', {})
    employee_id = booking_form_data.get('employee_id')
    employee_name = booking_form_data.get('employee_name', '')

    from datetime import time
    time_slots = []
    for hour in range(12, 24):
        time_slots.append(time(hour, 0))
    time_slots.append(time(0, 0))


    total_duration = request.session.get('total_duration', 0)

    available_slots = []
    for i, slot in enumerate(available_slots):
        time_parts = slot['time'].split()
        time_str = time_parts[0]
        period = time_parts[1]

        hours, minutes = time_str.split(':')
        hours = int(hours)
        minutes = int(minutes)

        if period == 'PM' and hours < 12:
            hours += 12
        elif period == 'AM' and hours == 12:
            hours = 0

        slot_time = datetime.strptime(f'{hours:02d}:{minutes:02d}:00', '%H:%M:%S').time()
        slot_end_time = (datetime.combine(datetime.today(), slot_time) + timedelta(minutes=total_duration)).time()

        # If a coach is selected, check their availability
        if employee_id and employee_name:
            coach_conflicts = check_coach_availability(day, slot_time, slot_end_time, employee_id, club)
            if coach_conflicts:
                available_slots[i]['available'] = False
                available_slots[i]['coach_booked'] = True
    context['LANGUAGE_CODE'] = translation.get_language()
    return render(request, 'receptionist_dashboard/select_appointment_time.html', {
        'day': day,
        'time_slots': available_slots,
        'total_duration': total_duration,
        'coach_name': employee_name if employee_name else None,
        'club':club
    })

from accounts.models import CoachProfile
@login_required
def verify_and_book_appointment(request, day):
    club = get_user_club(request.user)

    try:
        receptionist_profile = request.user.userprofile.receptionist_profile
    except AttributeError:
        receptionist_profile = None
        receptionist_name = f"{request.user.first_name} {request.user.last_name}".strip() or request.user.full_name

    if not club:
        messages.error(request, "لم يتم تحديد نادٍ لهذا المستخدم.")
        return redirect('select_club')

    if request.method != 'POST':
        return redirect('select_appointment_time', day=day)

    time_input = request.POST.get('time_input')
    period = request.POST.get('period')

    if not time_input or not period:
        messages.error(request, "يرجى إدخال الوقت والفترة")
        return redirect('select_appointment_time', day=day)

    try:
        if ':' in time_input:
            hours, minutes = time_input.split(':')
            hours = int(hours)
            minutes = int(minutes)

            if hours < 1 or hours > 12:
                messages.error(request, "صيغة الوقت غير صحيحة. يجب أن تكون الساعة من 1 إلى 12")
                return redirect('select_appointment_time', day=day)

            if period == 'PM' and hours < 12:
                hours += 12
            elif period == 'AM' and hours == 12:
                hours = 0

            time_obj = datetime.strptime(f'{hours:02d}:{minutes:02d}:00', '%H:%M:%S').time()
    except ValueError:
        messages.error(request, "صيغة الوقت غير صحيحة. الرجاء استخدام الصيغة HH:MM")
        return redirect('select_appointment_time', day=day)

    booking_form_data = request.session.get('booking_form_data', {})
    services_data = request.session.get('services_data', [])
    total_duration = request.session.get('total_duration', 0)

    if not booking_form_data or not services_data:
        messages.error(request, "بيانات الحجز غير مكتملة. الرجى المحاولة مرة أخرى.")
        return redirect('select_appointment_day')

    start_datetime = datetime.combine(datetime.today(), time_obj)
    end_datetime = start_datetime + timedelta(minutes=total_duration)
    end_time = end_datetime.time()

    # Check for coach availability using coach ID
    for service_data in services_data:
        coach_id = service_data.get('coach_id')
        if coach_id:
            coach_conflicts = check_coach_availability_by_id(day, time_obj, end_time, coach_id, club)
            if coach_conflicts:
                messages.error(request, "أحد الموظفين المختارين لديه موعد آخر في هذا الوقت. الرجاء اختيار وقت آخر ")
                return redirect('select_appointment_time', day=day)

    try:
        with transaction.atomic():
            appointment = SalonAppointment.objects.create(
                day=day,
                start_time=time_obj,
                end_time=end_time,
                available=False,
                club=club,
                is_paid=True,
            )

            # Determine primary coach and display name
            primary_coach = None
            employee_display = "متعدد الموظفين" if len(services_data) > 1 else ""

            # If there's only one service/coach, use that as primary
            if len(services_data) == 1 and services_data[0].get('coach_id'):
                try:
                    primary_coach = CoachProfile.objects.get(id=services_data[0]['coach_id'])
                    employee_display = primary_coach.full_name
                except CoachProfile.DoesNotExist:
                    pass

            booking = SalonBooking.objects.create(
                appointment=appointment,
                employee=employee_display,  # Display name for the booking
                primary_coach=primary_coach,  # Store primary coach reference
                created_by=request.user,
                created_by_type='receptionist',
                created_by_name=receptionist_name if not receptionist_profile else receptionist_profile.full_name,
                created_at=datetime.now()
            )

            # Create BookingService records with coach references
            service_names = []
            employee_names = []

            for service_data in services_data:
                service_id = service_data.get('service_id')
                coach_id = service_data.get('coach_id')
                coach_name = service_data.get('coach_name', '')

                if service_id:
                    service = ServicesModel.objects.get(id=service_id)
                    service_names.append(service.title)

                    # Get coach object if available
                    coach_obj = None
                    if coach_id:
                        try:
                            coach_obj = CoachProfile.objects.get(id=coach_id)
                            employee_names.append(coach_obj.full_name)
                        except CoachProfile.DoesNotExist:
                            pass

                    # Create booking service with coach reference
                    BookingService.objects.create(
                        booking=booking,
                        service=service,
                        coach=coach_obj,  # Store coach object reference
                        coach_id=coach_id,  # Keep coach_id for backward compatibility
                        coach_name=coach_name  # Keep name for display
                    )

            # Create notification with all employee names
            employees_str = ", ".join(set(employee_names)) if employee_names else "غير محدد"
            receptionist_name = request.user.userprofile.receptionist_profile.full_name if hasattr(request.user, 'userprofile') and hasattr(request.user.userprofile, 'receptionist_profile') else request.user.username
            formatted_time = time_obj.strftime('%I:%M %p')
            services_str = ", ".join(service_names)
            notification_message = f" تم حجز موعد جديد بواسطة موظف الاستقبال 📅 {receptionist_name} في يوم {day} الساعة {formatted_time}. الخدمات: {services_str}. المدربين: {employees_str}."
            send_notification(request.user, club, notification_message)

            # Clean up session data
            if 'booking_form_data' in request.session:
                del request.session['booking_form_data']
            if 'services_data' in request.session:
                del request.session['services_data']
            if 'total_duration' in request.session:
                del request.session['total_duration']

            messages.success(request, "تم حجز الموعد بنجاح")
            return redirect('receptionist_salon_appointments')

    except Exception as e:
        messages.error(request, f"حدث خطأ أثناء الحجز: {str(e)}")
        return redirect('select_appointment_time', day=day)


def check_coach_availability_by_id(day, start_time, end_time, coach_id, club):
    """
    Check if a coach is available at the given time slot using coach ID
    Returns True if there are conflicts, False if available
    """
    # Check conflicts in BookingService model using coach ID
    booking_services_conflicts = BookingService.objects.filter(
        coach_id=coach_id,
        booking__appointment__day=day,
        booking__appointment__available=False,
        booking__appointment__club=club
    ).filter(
        models.Q(
            booking__appointment__start_time__lt=end_time,
            booking__appointment__end_time__gt=start_time
        )
    )

    # Also check primary coach conflicts
    primary_coach_conflicts = SalonBooking.objects.filter(
        primary_coach_id=coach_id,
        appointment__day=day,
        appointment__available=False,
        appointment__club=club
    ).filter(
        models.Q(
            appointment__start_time__lt=end_time,
            appointment__end_time__gt=start_time
        )
    )

    return booking_services_conflicts.exists() or primary_coach_conflicts.exists()

@login_required
def get_service_info(request, service_id):
    """
    Returns JSON with service information including duration and associated coaches
    """
    try:
        service = ServicesModel.objects.get(id=service_id)
        coaches = service.coaches.all()

        coach_data = [
            {
                'id': coach.id,
                'name': coach.full_name
            } for coach in coaches
        ]

        return JsonResponse({
            'duration': service.duration,
            'coaches': coach_data
        })
    except ServicesModel.DoesNotExist:
        return JsonResponse({'error': 'Service not found'}, status=404)



def check_coach_availability(day, start_time, end_time, coach_id, club):
    """
    Legacy function - redirects to ID-based check
    """
    return check_coach_availability_by_id(day, start_time, end_time, coach_id, club)

@login_required
def get_service_duration(request, service_id):
    try:
        service = ServicesModel.objects.get(id=service_id)
        return JsonResponse({'duration': service.duration})
    except ServicesModel.DoesNotExist:
        return JsonResponse({'duration': 0})


@login_required
def book_appointment(request, day, time_slot):
    club = get_user_club(request.user)

    if not club:
        messages.error(request, "لم يتم تحديد نادٍ لهذا المستخدم.")
        return redirect('select_appointment_day')

    booking_form_data = request.session.get('booking_form_data', {})
    service_ids = request.session.get('service_ids', [])
    total_duration = request.session.get('total_duration', 0)

    if not booking_form_data or not service_ids:
        messages.error(request, "بيانات الحجز غير مكتملة. الرجاء المحاولة مرة أخرى.")
        return redirect('select_appointment_day')

    try:
        time_parts = time_slot.split()
        time_str = time_parts[0]
        period = time_parts[1]

        hours, minutes = time_str.split(':')
        hours = int(hours)
        minutes = int(minutes)

        if period == 'PM' and hours < 12:
            hours += 12
        elif period == 'AM' and hours == 12:
            hours = 0

        time_obj = datetime.strptime(f'{hours:02d}:{minutes:02d}:00', '%H:%M:%S').time()
    except (ValueError, IndexError):
        messages.error(request, "صيغة الوقت غير صحيحة")
        return redirect('select_appointment_time', day=day)

    start_datetime = datetime.combine(datetime.today(), time_obj)
    end_datetime = start_datetime + timedelta(minutes=total_duration)
    end_time = end_datetime.time()

    conflicts = SalonAppointment.objects.filter(
        day=day,
        available=False,
        club=club,
    ).filter(
        models.Q(start_time__lt=end_time, end_time__gt=time_obj)
    )

    if conflicts.exists():
        messages.error(request, "هناك تعارض في المواعيد. الرجاء اختيار وقت آخر")
        return redirect('select_appointment_time', day=day)

    try:
        with transaction.atomic():
            appointment = SalonAppointment.objects.create(
                day=day,
                start_time=time_obj,
                end_time=end_time,
                available=False,
                club=club
            )

            student_id = booking_form_data.get('student_id')
            employee_id = booking_form_data.get('employee_id')

            if not student_id:
                messages.error(request, "بيانات العميل غير متوفرة. الرجاء المحاولة مرة أخرى.")
                return redirect('select_appointment_day')

            try:
                student = StudentProfile.objects.get(id=student_id)
            except StudentProfile.DoesNotExist:
                messages.error(request, "لم يتم العثور على العميل. الرجاء المحاولة مرة أخرى.")
                return redirect('select_appointment_day')

            employee = booking_form_data.get('employee_name', '')

            if not employee:
                from accounts.models import CoachProfile
                try:
                    coach = CoachProfile.objects.get(id=employee_id)
                    employee = coach.full_name
                except:
                    employee = "غير محدد"

            booking = SalonBooking.objects.create(
                appointment=appointment,
                student=student,
                employee=employee,
                created_at=datetime.now()
            )

            for service_id in service_ids:
                service = ServicesModel.objects.get(id=service_id)
                BookingService.objects.create(
                    booking=booking,
                    service=service
                )


            receptionist_name = request.user.userprofile.receptionist_profile.full_name if hasattr(request.user, 'userprofile') and hasattr(request.user.userprofile, 'receptionist_profile') else request.user.username

            # Format the appointment time nicely
            formatted_time = time_obj.strftime('%I:%M %p')

            # Get service names
            service_names = ", ".join([ServicesModel.objects.get(id=service_id).name for service_id in service_ids])

            # Create notification message with appointment details
            notification_message = f" تم حجز موعد جديد بواسطة موظف الاستقبال 📅 {receptionist_name} في يوم {day} الساعة {formatted_time}. الخدمات: {service_names}. المدربين: {employee}."

            send_notification(request.user, club, notification_message)

            messages.success(request, "تم حجز الموعد بنجاح")

            if 'booking_form_data' in request.session:
                del request.session['booking_form_data']
            if 'service_ids' in request.session:
                del request.session['service_ids']
            if 'total_duration' in request.session:
                del request.session['total_duration']

            return redirect('receptionist_salon_appointments')
    except Exception as e:
        messages.error(request, f"حدث خطأ أثناء الحجز: {str(e)}")
        return redirect('select_appointment_day')

@login_required
def appointment_details(request, appointment_id):
    club = get_user_club(request.user)

    if not club:
        messages.error(request, "لم يتم تحديد نادٍ لهذا المستخدم.")
        return redirect('index')

    appointment = get_object_or_404(SalonAppointment, id=appointment_id)
    if appointment.club != club:
        messages.error(request, "ليس لديك صلاحية لعرض هذا الموعد.")
        return redirect('receptionist_salon_appointments')

    try:
        booking = appointment.booking
        # Explicitly fetch booking services
        booking_services = BookingService.objects.filter(booking=booking).select_related('service')

        if not booking_services.exists():
            messages.warning(request, "لا توجد خدمات مرتبطة بهذا الحجز")

        # For debugging
        print(f"Found {booking_services.count()} services for booking {booking.id}")

        context = {
            'appointment': appointment,
            'booking': booking,
            'employee': booking.employee,
            'booking_services': booking_services,  # Change the variable name to be more explicit
            'total_price': sum(bs.service.price for bs in booking_services),
            'total_duration': sum(bs.service.duration for bs in booking_services),
            'club':club,
            'created_by_type': getattr(booking, 'created_by_type', 'unknown'),
            'created_by_name': getattr(booking, 'created_by_name', 'غير محدد'),
        }
    except Exception as e:
        messages.error(request, f"لم يتم العثور على معلومات الحجز: {str(e)}")
        return redirect('receptionist_salon_appointments')
    context['LANGUAGE_CODE'] = translation.get_language()
    return render(request, 'receptionist_dashboard/appointment_details.html', context)

@login_required
def cancel_appointment(request, appointment_id):
    club = get_user_club(request.user)

    if not club:
        messages.error(request, "لم يتم تحديد نادٍ لهذا المستخدم.")
        return redirect('index')

    appointment = get_object_or_404(SalonAppointment, id=appointment_id)
    if appointment.club != club:
        messages.error(request, "ليس لديك صلاحية لإلغاء هذا الموعد.")
        return redirect('receptionist_salon_appointments')

    try:
        booking = appointment.booking
        BookingService.objects.filter(booking=booking).delete()
        booking.delete()
        appointment.delete()

        messages.success(request, "تم إلغاء الحجز بنجاح")
    except:
        messages.error(request, "لم يتم العثور على حجز لهذا الموعد")

    return redirect('receptionist_salon_appointments')


def viewStudentss(request):
    context = {}
    """Displays all students in the club."""
    club = get_user_club(request.user)

    if not club:
        messages.error(request, "لم يتم تحديد نادٍ لهذا المستخدم.")
        return redirect('index')

    students = UserProfile.objects.filter(
        account_type='3',
        student_profile__club=club
    ).select_related('user', 'student_profile')

    valid_students = [student for student in students if student.student_profile]
    context['LANGUAGE_CODE'] = translation.get_language()
    return render(request, 'receptionist_dashboard/students/viewStudents.html', {'students': valid_students,'club': club})


def addStudent(request):
    context = {}
    """Adds a new student to the club."""
    club = get_user_club(request.user)

    if not club:
        messages.error(request, "لم يتم تحديد نادٍ لهذا المستخدم.")
        return redirect('index')

    form = StudentProfileForm()

    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            return redirect('addStudentFromReceptionist')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email is already in use.")
            return redirect('addStudentFromReceptionist')

        form = StudentProfileForm(request.POST)
        if form.is_valid():
            student = User.objects.create(username=username, email=email)
            if password:
                student.set_password(password)
            student.save()

            student_profile = form.save(commit=False)
            student_profile.user = student
            student_profile.club = club  # تعيين النادي هنا
            student_profile.save()

            UserProfile.objects.create(user=student, account_type='3', student_profile=student_profile)

            messages.success(request, "client added successfully.")
            return redirect('viewStudentss')
        else:
            print(f"Form errors: {form.errors}")
            messages.error(request, f"Form validation failed: {form.errors}")
    from django import forms
    if 'club' in form.fields:
        form.fields['club'].widget = forms.HiddenInput()
        form.initial['club'] = club.id

    context['LANGUAGE_CODE'] = translation.get_language()
    return render(request, 'receptionist_dashboard/students/addStudent.html', {'form': form, 'club': club})


@login_required
def editStudentt(request, id):
    context = {}
    """Edits an existing student's details."""
    club = get_user_club(request.user)

    if not club:
        messages.error(request, "لم يتم تحديد نادٍ لهذا المستخدم.")
        return redirect('index')

    student_profile = get_object_or_404(StudentProfile, id=id)
    if student_profile.club != club:
        messages.error(request, "ليس لديك صلاحية لتعديل هذا الطالب.")
        return redirect('viewStudentss')

    student = get_object_or_404(User, userprofile__student_profile=student_profile)

    form = StudentProfileForm(instance=student_profile)

    if request.method == 'POST':
        new_username = request.POST.get('username')
        new_email = request.POST.get('email')
        password = request.POST.get('password')

        if User.objects.filter(username=new_username).exclude(id=student.id).exists():
            messages.error(request, "Username already exists.")
            return render(request, 'receptionist_dashboard/students/editStudent.html', {
                'form': form,
                'student': student
            })

        if User.objects.filter(email=new_email).exclude(id=student.id).exists():
            messages.error(request, "Email is already in use.")
            return render(request, 'receptionist_dashboard/students/editStudent.html', {
                'form': form,
                'student': student
            })

        form = StudentProfileForm(request.POST, instance=student_profile)
        if form.is_valid():
            student.username = new_username
            student.email = new_email
            if password:
                student.set_password(password)
            student.save()

            student_profile = form.save(commit=False)
            student_profile.user = student
            student_profile.club = club
            student_profile.save()

            messages.success(request, "Student profile updated successfully.")
            return redirect('viewStudentss')
        else:
            print(f"Form errors: {form.errors}")
            messages.error(request, f"Form validation failed: {form.errors}")

    from django import forms
    if 'club' in form.fields:
        form.fields['club'].widget = forms.HiddenInput()
        form.initial['club'] = club.id
    context['LANGUAGE_CODE'] = translation.get_language()
    return render(request, 'receptionist_dashboard/students/editStudent.html', {
        'form': form,
        'student': student,
        'club' : club
    })



@login_required
def deleteStudentt(request, id):
    """Deletes a student from the club."""
    club = get_user_club(request.user)

    if not club:
        messages.error(request, "لم يتم تحديد نادٍ لهذا المستخدم.")
        return redirect('index')

    student_profile = get_object_or_404(StudentProfile, id=id)
    if student_profile.club != club:
        messages.error(request, "ليس لديك صلاحية لحذف هذا الطالب.")
        return redirect('viewStudentss')

    student = get_object_or_404(User, userprofile__student_profile=student_profile)

    student_name = student.username

    student_profile.delete()
    student.delete()



    messages.success(request, "Client has been deleted successfully.")
    return redirect('viewStudentss')

# Helper function to generate available slots
def get_available_time_slots(request,day, duration_minutes):
    """Get available time slots for a given day and duration"""
    club = get_user_club(request.user)

    if not club:
        return []

    time_slots = []
    for hour in range(24):
        for minute in [0, 30]:
            time = datetime.strptime(f'{hour:02d}:{minute:02d}:00', '%H:%M:%S').time()
            time_slots.append(time)

    available_slots = []
    for time in time_slots:
        # Calculate end time based on duration
        start_datetime = datetime.combine(datetime.today(), time)
        end_datetime = start_datetime + timedelta(minutes=duration_minutes)
        end_time = end_datetime.time()

        # Check for conflicts
        conflicts = SalonAppointment.objects.filter(
            day=day,
            available=False,
            club=club,
        ).filter(
            models.Q(start_time__lt=end_time, end_time__gt=time)
        )

        if not conflicts.exists():
            available_slots.append({
                'time': time.strftime('%H:%M'),
                'available': True
            })

    return available_slots


@login_required
def view_receptionist_profile(request):
    club = get_user_club(request.user)
    try:
        user_profile = UserProfile.objects.get(user=request.user)
        receptionist = user_profile.receptionist_profile

        if not receptionist:
            messages.error(request, "لا يوجد ملف شخصي لموظف الاستقبال")
            return redirect('receptionistIndex')

        context = {
            'receptionist': receptionist,
            'userprofile': user_profile ,
            'club': club,
        }
        context['LANGUAGE_CODE'] = translation.get_language()
        return render(request, 'accounts/profiles/receptionist/ViewReceptionistProfile.html', context)
    except UserProfile.DoesNotExist:
        messages.error(request, "لا يوجد ملف شخصي")
        return redirect('receptionistIndex')

@login_required
def edit_receptionist_profile(request):
    club = get_user_club(request.user)
    try:
        user_profile = UserProfile.objects.get(user=request.user)
        receptionist = user_profile.receptionist_profile

        if not receptionist:
            messages.error(request, "لا يوجد ملف شخصي لموظف الاستقبال")
            return redirect('receptionistIndex')

        if request.method == 'POST':
            form = ReceptionistProfileForm(request.POST, instance=receptionist)
            if form.is_valid():
                receptionist_profile = form.save(commit=False)

                if 'profile_image_base64' in request.FILES:
                    image_file = request.FILES['profile_image_base64']
                    encoded_image = base64.b64encode(image_file.read()).decode('utf-8')

                    receptionist_profile.profile_image_base64 = f"data:image/{image_file.content_type.split('/')[-1]};base64,{encoded_image}"
                    user_profile.profile_image_base64 = receptionist_profile.profile_image_base64
                    user_profile.save()

                receptionist_profile.save()
                messages.success(request, "تم تحديث الملف الشخصي بنجاح")
                return redirect('view_receptionist_profile')
        else:
            form = ReceptionistProfileForm(instance=receptionist)

        context = {
            'form': form,
            'receptionist': receptionist,
            'club' : club
        }
        context['LANGUAGE_CODE'] = translation.get_language()
        return render(request, 'accounts/settings/receptionist/EditReceptionistProfile.html', context)
    except UserProfile.DoesNotExist:
        messages.error(request, "لا يوجد ملف شخصي")
        return redirect('receptionistIndex')

@require_GET
def service_coach(request, service_id):
    """API endpoint to get coach associated with a service"""
    try:
        service = ServicesModel.objects.get(id=service_id)
        if service.coach:
            return JsonResponse({
                'coach_id': service.coach.id,
                'coach_name': service.coach.full_name
            })
        return JsonResponse({'message': 'No coach associated with this service'}, status=200)
    except ServicesModel.DoesNotExist:
        return JsonResponse({'error': 'Service not found'}, status=404)

@login_required
def slot_appointments(request, day, time):
    club = get_user_club(request.user)
    if not club:
        messages.error(request, "No club assigned to your profile. Please contact an administrator.")
        return redirect('index')

    try:
        # Parse the time
        if ':' in time:
            hour_str, minute_str = time.split(':')
            hour = int(hour_str)
            minute = int(minute_str.split(' ')[0])
            period = time.split(' ')[1]

            if period == 'PM' and hour < 12:
                hour += 12
            elif period == 'AM' and hour == 12:
                hour = 0

            time_obj = datetime.strptime(f'{hour:02d}:{minute:02d}:00', '%H:%M:%S').time()
            slot_end = (datetime.combine(datetime.today(), time_obj) + timedelta(hours=1)).time()

            # Get all appointments in this time slot
            appointments = SalonAppointment.objects.filter(
                day=day,
                club=club,
                is_paid=True,
                start_time__gte=time_obj,
                start_time__lt=slot_end
            ).select_related('booking')

            # Import the Attendance model
            from coach_dashboard.models import Attendance

            # Prepare the appointment details
            appointment_details = []
            for appt in appointments:
                if hasattr(appt, 'booking'):
                    booking = appt.booking
                    services = BookingService.objects.filter(booking=booking).select_related('service')
                    service_names = ", ".join([s.service.title for s in services])
                    total_price = sum(s.service.price for s in services)

                    # Get attendance records for this appointment
                    attendance_records = Attendance.objects.filter(
                        booking_id=appt.id,
                        appointment_day=day,
                        appointment_start_time=appt.start_time
                    ).select_related('student').order_by('student__username')

                    # Calculate attendance statistics
                    total_students = attendance_records.count()
                    present_students = attendance_records.filter(is_present=True).count()
                    absent_students = total_students - present_students
                    attendance_percentage = (present_students / total_students * 100) if total_students > 0 else 0

                    appointment_details.append({
                        'id': appt.id,
                        'services': service_names,
                        'employee': booking.employee,
                        'start_time': appt.start_time.strftime('%I:%M %p'),
                        'end_time': appt.end_time.strftime('%I:%M %p'),
                        'total_price': total_price,
                        'club': club,
                        'attendance_records': attendance_records,
                        'attendance_stats': {
                            'total': total_students,
                            'present': present_students,
                            'absent': absent_students,
                            'percentage': round(attendance_percentage, 1)
                        }
                    })

            context = {
                'day': day,
                'time_slot': time,
                'appointments': appointment_details
            }
            context['LANGUAGE_CODE'] = translation.get_language()
            return render(request, 'receptionist_dashboard/slot_appointments.html', context)

    except Exception as e:
        messages.error(request, f"Error retrieving appointments: {str(e)}")
        return redirect('receptionist_salon_appointments')


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone, translation
from django.db import transaction
from django.contrib.auth.models import User
from decimal import Decimal
import logging
from students.models import ServiceOrderModel,ServicesModel,Order,OrderItem

logger = logging.getLogger(__name__)

@login_required
def student_subscriptions(request, student_id):
    """View to display student's subscriptions and allow adding new ones"""
    context = {}
    club = get_user_club(request.user)

    if not club:
        messages.error(request, "لم يتم تحديد نادٍ لهذا المستخدم." if translation.get_language() == 'ar' else "No club assigned to this user.")
        return redirect('index')

    student_user = get_object_or_404(User, id=student_id)
    try:
        student = student_user.userprofile
        if student.account_type != '3' or student.student_profile.club != club:
            messages.error(request, "غير مسموح لك بعرض اشتراكات هذا اللاعب." if translation.get_language() == 'ar' else "You're not allowed to view this student's subscriptions.")
            return redirect('viewStudentss')
    except:
        messages.error(request, "لاعب غير صحيح." if translation.get_language() == 'ar' else "Invalid student.")
        return redirect('viewStudentss')

    # Fixed: Added prefetch_related for coaches (without __user for now)
    subscriptions = ServiceOrderModel.objects.filter(
        student=student_user
    ).select_related('service').prefetch_related('service__coaches').order_by('-creation_date')

    # Also prefetch for available services
    available_services = ServicesModel.objects.filter(club=club).prefetch_related('coaches')

    context.update({
        'student': student,
        'subscriptions': subscriptions,
        'available_services': available_services,
        'current_time': timezone.now(),
        'LANGUAGE_CODE': translation.get_language(),
        'club': club
    })

    return render(request, 'receptionist_dashboard/students/student_subscriptions.html', context)


@login_required
def add_student_subscription(request, student_id):
    """Add a new subscription for a student (receptionist action)"""
    if request.method != 'POST':
        return redirect('student_subscriptions', student_id=student_id)

    club = get_user_club(request.user)
    lang = translation.get_language()

    if not club:
        messages.error(request, "لم يتم تحديد نادٍ لهذا المستخدم." if lang == 'ar' else "No club assigned to this user.")
        return redirect('index')

    student_user = get_object_or_404(User, id=student_id)
    try:
        student = student_user.userprofile
        if student.account_type != '3' or student.student_profile.club != club:
            messages.error(request, "غير مسموح لك بإضافة اشتراك لهذا اللاعب." if lang == 'ar' else "You're not allowed to add subscription for this student.")
            return redirect('viewStudentss')
    except:
        messages.error(request, "لاعب غير صحيح." if lang == 'ar' else "Invalid student.")
        return redirect('viewStudentss')

    service_id = request.POST.get('service_id')
    quantity = int(request.POST.get('quantity', 1))

    service = get_object_or_404(ServicesModel, id=service_id, club=club)

    try:
        with transaction.atomic():
            total_price = service.price * quantity

            order = Order.objects.create(
                user=student_user,
                club=club,
                total_price=total_price,
                status='confirmed',
                payment_method='credit_card',
                first_name=student.student_profile.full_name or student_user.username,
                last_name=student_user.username,
                email=student_user.email,
                phone=student.student_profile.phone or '',
                address='anything',
                city='anything',
                region='anything',
                postal_code='12345',
                notes=f'اشتراك تم إنشاؤه بواسطة موظف الاستقبال' if lang == 'ar' else 'Subscription created by receptionist'
            )

            OrderItem.objects.create(
                order=order,
                service=service,
                quantity=quantity,
                price=service.price
            )

            existing_service_order = ServiceOrderModel.objects.filter(
                student=student_user,
                service=service
            ).order_by('-end_datetime').first()

            if existing_service_order:
                if existing_service_order.end_datetime > timezone.now():
                    new_end_datetime = existing_service_order.end_datetime + timezone.timedelta(days=service.subscription_days * quantity)
                else:
                    new_end_datetime = timezone.now() + timezone.timedelta(days=service.subscription_days * quantity)

                existing_service_order.end_datetime = new_end_datetime
                existing_service_order.price += total_price
                existing_service_order.creation_date = timezone.now()
                existing_service_order.is_complited = False
                existing_service_order.save()

                subscription_action = 'تم تجديد الاشتراك' if lang == 'ar' else 'Subscription renewed'
            else:
                ServiceOrderModel.objects.create(
                    service=service,
                    student=student_user,
                    price=total_price,
                    is_complited=False,
                    end_datetime=timezone.now() + timezone.timedelta(days=service.subscription_days * quantity),
                    creation_date=timezone.now()
                )

                subscription_action = 'تم إنشاء اشتراك جديد' if lang == 'ar' else 'New subscription created'

            receptionist_name = request.user.username
            if hasattr(request.user, 'userprofile') and hasattr(request.user.userprofile, 'receptionist_profile'):
                receptionist_name = request.user.userprofile.receptionist_profile.full_name or request.user.username

            service_title =  service.title
            student_name = student.student_profile.full_name or student_user.username
            currency_symbol = 'ر.س' if lang == 'ar' else 'SAR'

            if lang == 'ar':
                notification_message = f"تم إنشاء اشتراك جديد بواسطة موظف الاستقبال 💎 {receptionist_name} للاعب {student_name}. الخدمة: {service_title}. المبلغ: {total_price} {currency_symbol}. الكمية: {quantity}. {subscription_action}."
            else:
                notification_message = f"New subscription created by receptionist 💎 {receptionist_name} for student {student_name}. Service: {service_title}. Amount: {total_price} {currency_symbol}. Quantity: {quantity}. {subscription_action}."

            send_notification(request.user, club, notification_message)

            if lang == 'ar':
                messages.success(request, f"تم إضافة الاشتراك بنجاح للاعب {student_name}. الخدمة: {service_title}")
            else:
                messages.success(request, f"Subscription added successfully for {student_name}. Service: {service_title}")

    except Exception as e:
        logger.error(f"Error adding subscription: {str(e)}")
        messages.error(request, f"حدث خطأ أثناء إضافة الاشتراك: {str(e)}" if lang == 'ar' else f"Error adding subscription: {str(e)}")

    return redirect('student_subscriptions', student_id=student_id)

from club_dashboard.models import Notification
def send_notification(user, club, message):
    """Helper function to send notifications to club director"""
    try:
        Notification.objects.create(
            club=club,
            message=message,
            is_read=False,
            created_at=timezone.now()
        )
    except Exception as e:
        logger.error(f"Error sending notification: {str(e)}")


def get_user_club(user):
    """Helper function to get user's club"""
    try:
        if hasattr(user, 'userprofile'):
            if hasattr(user.userprofile, 'receptionist_profile'):
                return user.userprofile.receptionist_profile.club
            elif hasattr(user.userprofile, 'student_profile'):
                return user.userprofile.student_profile.club
        return None
    except:
        return None