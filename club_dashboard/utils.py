from club_dashboard.models import Notification

def send_notification(user, club, message):
    """Creates a notification for the club dashboard."""
    Notification.objects.create(
        club=club,
        user=user,
        message=message
    )
