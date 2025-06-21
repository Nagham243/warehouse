from django.utils import translation


def club_context(request):
    """Ensures 'club' is available in all templates for both Club Directors and Coaches."""
    if request.user.is_authenticated:
        try:
            user_profile = request.user.userprofile  # Get the user profile

            if hasattr(user_profile, 'director_profile') and user_profile.director_profile:
                club = user_profile.director_profile.club  # Club for Directors
            elif hasattr(user_profile, 'Coach_profile') and user_profile.Coach_profile:
                club = user_profile.Coach_profile.club  # Club for Coaches
            else:
                club = None  # No club associated

            return {'club': club}  # Return the club in context
        except AttributeError:
            return {}  # Return empty if no user profile
    return {}  # Return empty if not logged in

def language_context(request):
    return {
        'LANGUAGE_CODE': translation.get_language(),
    }
