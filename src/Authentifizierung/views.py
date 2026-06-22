from django.shortcuts import render, redirect
from django.db import IntegrityError

from .forms import RegistrierungsForm


def registrierung_view(request):
    if request.method == "POST":
        form = RegistrierungsForm(request.POST)
        if form.is_valid():
            try:
                form.save()
                return redirect("Basis:login")
            except IntegrityError:
                form.add_error('email', "Diese E-Mail-Adresse ist bereits registriert.")
    else:
        form = RegistrierungsForm()

    return render(request, "Authentifizierung/Registrierung.html", {"form": form})

