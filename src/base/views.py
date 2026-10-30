from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render


def index(request: HttpRequest) -> HttpResponse:
    """
    displays the public index page.

    Arguments:
        request (HttpRequest): The HTTP request.

    Returns:
        HttpResponse: The rendered index page.
    """

    return render(request, "index.html",)


def login_view(request: HttpRequest) -> HttpResponse:
    """
    Authenticate a user and log them in.

    Retrieves the user by email, authenticates the submitted password,
    and logs the user in if the credentials are valid.

    Arguments:
        request (HttpRequest): The HTTP request containing the login data.

    Returns:
        HttpResponse: A redirect to the index page after successful login,
            or the rendered login page with an error message.
    """
    if request.method == "POST":
        user_obj = User.objects.filter(email=request.POST.get("email")).first()
        password = request.POST.get("password")

        if user_obj:
            user = authenticate(request, username=user_obj.username, password=password)

            if user:
                login(request, user)

                return redirect("base:index")

        return render(request, "login.html", {"error": "E-Mail oder Passwort ungültig."})

    return render(request, "login.html")


def logout_view(request: HttpRequest) -> HttpResponse:
    """
    Log out the current user.

    Ends the user's authenticated session and redirects to the index page.

    Arguments:
        request (HttpRequest): The HTTP request.

    Returns:
        HttpResponse: A redirect to the index page.
    """
    logout(request)
    return redirect("base:index")