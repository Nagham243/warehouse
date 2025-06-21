from django.db import models
from django.contrib.auth.models import User
from accounts.models import ClubsModel, UserProfile

class ActivityLog(models.Model):
    ACTIVITY_TYPES = (
        ('club_added', 'Club Added'),
        ('director_added', 'Director Added'),
        ('administrator_added', 'Administrator Added'),
        ('coach_added', 'Coach Added'),
        ('student_added', 'Student Added'),
        ('accountant_added', 'Accountant Added'),
        ('receptionist_added', 'Receptionist Added'),
    )

    activity_type = models.CharField(max_length=50, choices=ACTIVITY_TYPES)
    description = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    club = models.ForeignKey(ClubsModel, on_delete=models.SET_NULL, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.get_activity_type_display()} - {self.description}"