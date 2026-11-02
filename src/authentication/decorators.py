from functools import wraps
from django.shortcuts import redirect


def check_required_Group(groupname):
    """Restrict access to users belonging to a specific group.

    Returns a decorator that checks whether the requesting user belongs
    to the group specified by groupname. Users who are not members of
    the group are redirected to the index page.

    Arguments:
        groupname {str}: Name of the required Django group.

    Returns:
        function: Decorator that checks the user's group membership.
    """

    def decoraters(view_function):

        @wraps(view_function)
        def wrapper(request, *args, **kwargs):

            if not request.user.groups.filter(name=groupname).exists():
                return redirect("base:index")

            return view_function(request, *args, **kwargs)
        
        return wrapper
    
    return decoraters


def check_if_user_authneticated():
    """Restrict access to authenticated users.

    Returns a decorator that checks whether the requesting user is
    authenticated. Unauthenticated users are redirected to the login page.

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