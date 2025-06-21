from django.utils import translation

def language_context(request):
    return {
        'LANGUAGE_CODE': translation.get_language(),
    }