# Create this file in: accounts/management/commands/fix_coach_profiles.py

from django.core.management.base import BaseCommand
from django.db import connection
from accounts.models import UserProfile, CoachProfile

class Command(BaseCommand):
    help = 'Fix coach profile data inconsistencies'

    def handle(self, *args, **options):
        self.stdout.write('Checking for data inconsistencies...')

        # Check for invalid foreign key values
        with connection.cursor() as cursor:
            # Check UserProfile table for invalid Coach_profile_id values
            cursor.execute("""
                SELECT id, Coach_profile_id 
                FROM accounts_userprofile 
                WHERE Coach_profile_id IS NOT NULL
            """)

            user_profiles = cursor.fetchall()

            for up_id, coach_profile_id in user_profiles:
                # Check if this is a datetime object or invalid ID
                try:
                    # Try to get the actual CoachProfile
                    coach_profile = CoachProfile.objects.filter(id=coach_profile_id).first()
                    if not coach_profile:
                        self.stdout.write(
                            self.style.WARNING(
                                f'UserProfile {up_id} has invalid Coach_profile_id: {coach_profile_id}'
                            )
                        )
                        # Option 1: Set to NULL
                        UserProfile.objects.filter(id=up_id).update(Coach_profile=None)

                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(
                            f'Error with UserProfile {up_id}: {str(e)}'
                        )
                    )
                    # Fix by setting to NULL
                    UserProfile.objects.filter(id=up_id).update(Coach_profile=None)

        self.stdout.write(self.style.SUCCESS('Data cleanup completed!'))