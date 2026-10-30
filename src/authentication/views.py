from django.db import IntegrityError
from django.shortcuts import redirect, render
from django.http import HttpRequest, HttpResponse

from .forms import (
    UserContributerRegestrationForm,
    UserOrganizerRegestrationForm,
)


def organizer_registration_view(request: HttpRequest) -> HttpResponse:
    """
    Register a new organizer.

    Processes the organizer registration form and creates an organizer
    account if the submitted data is valid. Redirects to the login page
    after successful registration.

    Arguments:
        request (HttpRequest): The HTTP request containing the form data.

    Returns:
        HttpResponse: The rendered registration form or a redirect to the
            login page.
    """
    if request.method == "POST":
        form = UserOrganizerRegestrationForm(request.POST)

        if form.is_valid():
            try:
                form.save()
                return redirect("base:login")
            except IntegrityError:
                form.add_error(
                    None,
                    "Die Registrierung konnte nicht abgeschlossen werden. "
                    "Bitte überprüfe deine Angaben.",
                )
    else:
        form = UserOrganizerRegestrationForm()

    return render(request,"authentication/organizer_registration.html",{"form": form},)


def contributer_registration_view(request: HttpRequest) -> HttpResponse:
    """
    Register a new contributor.

    Processes the contributor registration form and creates a contributor
    account if the submitted data is valid. Redirects to the login page
    after successful registration.

    Arguments:
        request (HttpRequest): The HTTP request containing the form data.

    Returns:
        HttpResponse: The rendered registration form or a redirect to the
            login page.
    """
    if request.method == "POST":
        form = UserContributerRegestrationForm(request.POST)

        if form.is_valid():
            try:
                form.save()
                return redirect("base:login")
            except IntegrityError:
                form.add_error(
                    None,
                    "Die Registrierung konnte nicht abgeschlossen werden. "
                    "Bitte überprüfe deine Angaben.",
                )
    else:
        form = UserContributerRegestrationForm()

    return render(request,"authentication/contributer_registration.html",{"form": form},)