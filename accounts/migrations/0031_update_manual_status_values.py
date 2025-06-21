from django.db import migrations
from django.db.models import F

def update_manual_status_values(apps, schema_editor):
    StudentProfile = apps.get_model('accounts', 'StudentProfile')

    # Update any Arabic values to their English key equivalents
    StudentProfile.objects.filter(manual_status='تجريبي').update(manual_status='trial')
    StudentProfile.objects.filter(manual_status='نشط').update(manual_status='active')
    StudentProfile.objects.filter(manual_status='سينتهي قريبًا').update(manual_status='expiring_soon')
    StudentProfile.objects.filter(manual_status='منتهي').update(manual_status='expired')

    # Handle nulls by setting them to 'trial'
    StudentProfile.objects.filter(manual_status__isnull=True).update(manual_status='trial')

class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0030_studentprofile_manual_status'),
    ]

    operations = [
        migrations.RunPython(update_manual_status_values),
    ]