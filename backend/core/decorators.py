from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from . import firebase_client as fb

def role_required(allowed_roles):
    """
    Decorator requiring the session user to hold one of the specified roles.
    e.g. @role_required(['admin']) or @role_required(['student', 'counselor'])
    """
    if isinstance(allowed_roles, str):
        allowed_roles = [allowed_roles]

    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            user_session = request.session.get('user')
            if not user_session:
                messages.warning(request, "Please sign in to access this page.")
                return redirect('login')

            uid = user_session.get('uid')
            profile = fb.get_user_profile(uid) or {}
            user_role = profile.get('role', 'student')

            if user_role not in allowed_roles and 'admin' not in allowed_roles:
                messages.error(request, f"Access restricted. Role '{user_role}' lacks permissions for this page.")
                return redirect('dashboard')

            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator
