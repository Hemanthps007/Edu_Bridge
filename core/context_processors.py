from django.conf import settings
from . import firebase_client

def global_context(request):
    return {
        'site_name': settings.SITE_NAME,
        'demo_mode': firebase_client.is_demo_mode(),
        'current_user': request.session.get('user'),
    }
