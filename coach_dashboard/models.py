from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import accounts.models


class Notification(models.Model):
    club = models.ForeignKey(
        accounts.models.CoachProfile,  # ✅ Correct reference to ClubsModel from accounts
        on_delete=models.CASCADE,
        related_name="notifications",
        verbose_name="التاجر"
    )
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,  # ✅ Prevents issues when a user is deleted
        null=True,
        blank=True,
        related_name="notification",
        verbose_name="المستخدم"
    )
    message = models.TextField(verbose_name="الرسالة")
    is_read = models.BooleanField(default=False, verbose_name="تم القراءة")
    created_at = models.DateTimeField(default=timezone.now, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="آخر تحديث")  # ✅ Added for tracking notification updates

    def __str__(self):
        return f"Notification for {self.user.username if self.user else 'Unknown'}: {self.message[:50]}..."


        
