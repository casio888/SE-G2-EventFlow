from django.shortcuts import render, redirect, get_object_or_404
from .models import Veranstaltung
from .forms import VeranstaltungForm

def veranstaltung_erstellen(request):
    if request.method == "POST":
        form = VeranstaltungForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("veranstaltungen:veranstaltungen_your_events")
    else:
        form = VeranstaltungForm()

    return render(request, "veranstaltungen/erstellen.html", {"form": form})


def veranstaltung_detail(request, id):
    event = get_object_or_404(Veranstaltung, pk=id)
    return render(request, "veranstaltungen/detail.html", {"event": event})

def veranstaltungen_your_events(request):
    events = Veranstaltung.objects.all()
    return render(request, "veranstaltungen/your_events.html", {"events": events})
