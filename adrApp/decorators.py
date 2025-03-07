from django.shortcuts import redirect
from .models import Anetaret

def check_status(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if 'user_id' in request.session:
            user = Anetaret.objects.get(id=request.session['user_id'])
            
            # If the user is in 'I heshtur' status
            if user.status_i_kartës == 'I heshtur':
                # Prevent actions on pages that require submission or interaction (except login page)
                if request.method in ['POST', 'PUT', 'DELETE']:  # Check if it's a modifying request
                    if request.path not in ['/login/']:  # Allow login attempts
                        return redirect('home')  # Redirect to home or any other page
                
        return view_func(request, *args, **kwargs)
    return _wrapped_view

