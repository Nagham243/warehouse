from django.db import models
from accounts.models import StudentProfile
from students.models import ServicesModel
from django.contrib.auth.models import User

class SalonBooking(models.Model):
    appointment = models.OneToOneField(
        'club_dashboard.SalonAppointment',
        on_delete=models.CASCADE,
        related_name='booking'
    )
    employee = models.CharField(max_length=255)
    primary_coach = models.ForeignKey(
        'accounts.CoachProfile',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='primary_bookings',
        help_text="Primary coach for this booking"
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='bookings_created'
    )
    created_by_type = models.CharField(max_length=50)
    created_by_name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        try:
            service_names = ", ".join([bs.service.title for bs in self.services.all()])
            # Use appointment day and employee/created_by_name instead of non-existent student field
            appointment_info = f"{self.appointment.day}" if self.appointment else "No appointment"
            creator_info = self.created_by_name or self.employee or "Unknown"
            return f"{creator_info} - {service_names} - {appointment_info}"
        except Exception:
            # Fallback in case of any other issues
            return f"SalonBooking #{self.id}"

    class Meta:
        ordering = ['-created_at']

class BookingService(models.Model):
    """Model to handle multiple services per booking"""
    booking = models.ForeignKey(
        SalonBooking,
        on_delete=models.CASCADE,
        related_name='services'
    )
    service = models.ForeignKey(
        ServicesModel,
        on_delete=models.CASCADE,
        related_name='booking_services'
    )
    coach_name = models.CharField(max_length=255, blank=True, null=True)
    coach = models.ForeignKey(
        'accounts.CoachProfile',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='service_bookings'
    )

    def __str__(self):
        coach_info = f" with {self.coach.full_name}" if self.coach else ""
        return f"{self.service.title}{coach_info}"

    class Meta:
        unique_together = ('booking', 'service')