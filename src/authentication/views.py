from django.shortcuts import render, redirect
from django.db import IntegrityError

from .forms import RegistrationForm


def registration_view(request):
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                return redirect("base:login")
            except IntegrityError:
                form.add_error('email', "Diese E-Mail-Adresse ist bereits registriert.")
    else:
        form = RegistrationForm()

    return render(request, "authentication/registration.html", {"form": form})

