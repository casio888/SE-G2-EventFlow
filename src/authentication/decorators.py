from functools import wraps
from django.shortcuts import redirect

from base.views import index,login

def check_required_Group(groupname):

    def decoraters(view_function):

        @wraps(view_function)
        def wrapper(request, *args, **kwargs):

            if not request.user.groups.filter(name=groupname).exists():
                return redirect("base:index")

            return view_function(request, *args, **kwargs)
        
        return wrapper
    
    return decoraters

def check_if_user_authneticated():

    def decoraters(view_function):

        @wraps(view_function)
        def wrapper(request, *args, **kwargs):

            if not request.user.is_authenticated:
                return redirect("base:login")

            return view_function(request, *args, **kwargs)
        
        return wrapper
        
    return decoraters