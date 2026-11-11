from enum import Enum
from functools import wraps
from django.shortcuts import redirect

from .models import CustomUserOrganizer, CustomUserContributer

class AccountType(Enum):
    ORGANIZER = "organizer"
    CONTRIBUTOR = "contributor"

def check_if_organizer_or_contributer(Account_Type):
    """
    Restrict access to users with a specific account type.

    Returns a decorator that checks whether the requesting user has
    an associated organizer or contributor account. Users without
    the required account type are redirected to the index page.

    Arguments:
        Account_Type (AccountType): Required account type
            (ORGANIZER or CONTRIBUTOR).

    Returns:
        function: Decorator that checks the user's account type.
    """

    def decoraters(view_function):

        @wraps(view_function)
        def wrapper(request, *args, **kwargs):

            if Account_Type == AccountType.ORGANIZER:
                if not CustomUserOrganizer.objects.filter(pk = request.user.pk).exists():
                    print("User was not of AccountType Organizer")
                    return redirect("base:index")
            
                return view_function(request, *args, **kwargs)
            
            elif Account_Type == AccountType.CONTRIBUTOR:
                print(f"Uid: {request.user.pk}")
                if not CustomUserContributer.objects.filter(pk = request.user.pk).exists():
                    print("User was not of AccountType Contributor")
                    return redirect("base:index")
            
                return view_function(request, *args, **kwargs)
            
        return wrapper
    
    return decoraters


def check_if_user_authneticated():
    """
    Restrict access to authenticated users.

    Returns a decorator that checks whether the requesting user
    is authenticated. Unauthenticated users are redirected to
    the login page.

    Returns:
        function: Decorator that checks the user's authentication status.
    """

    def decoraters(view_function):

        @wraps(view_function)
        def wrapper(request, *args, **kwargs):

            if not request.user.is_authenticated:
                return redirect("base:login")

            return view_function(request, *args, **kwargs)
        
        return wrapper
        
    return decoraters