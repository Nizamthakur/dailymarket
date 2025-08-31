from django.shortcuts import redirect
from django.contrib import messages

def vendor_required(view_func):
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.user_role == '3':
            if request.user.is_vendor_approved:
                return view_func(request, *args, **kwargs)
            else:
                messages.error(request, "Your vendor account is not approved yet!")
                return redirect('user_dashboard')
        else:
            messages.error(request, "You must be a vendor to access this page.")
            return redirect('user_dashboard')
    return wrapper
