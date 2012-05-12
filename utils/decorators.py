
from django.conf import settings
from django.http import HttpResponseForbidden


def admin_required(view_func):
    def wrapper(request, *args, **kwargs):
        if request.method != "POST" or request.POST.get("key") != settings.API_SECRET_KEY:
            return HttpResponseForbidden()
        return view_func(request, *args, **kwargs)
    return wrapper
