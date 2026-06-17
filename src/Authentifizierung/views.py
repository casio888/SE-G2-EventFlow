from django.shortcuts import render, redirect

from .forms import RegistrierungsForm


def registrierung_view(request):
    if request.method == "POST":
        form = RegistrierungsForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("Basis:login")
    else:
        form = RegistrierungsForm()

    return render(request, "Authentifizierung/Registrierung.html", {"form": form})

