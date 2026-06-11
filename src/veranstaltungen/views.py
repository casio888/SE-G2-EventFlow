from django.shortcuts import render, get_object_or_404
from veranstaltungen.models import Veranstaltung
from .utils import get_veranstaltung_form, save_veranstaltung_form

def veranstaltungen_liste(request):
    events = Veranstaltung.objects.all()
    return render(request, "veranstaltungen/liste.html", {"events": events})

def veranstaltung_erstellen(request):
    return render(request, "veranstaltungen/erstellen.html")

def veranstaltung_detail(request, id):
    event = get_object_or_404(Veranstaltung, pk=id)
    return render(request, "veranstaltungen/detail.html", {"event": event})

def veranstaltung_bearbeiten(request, id):
    event = get_object_or_404(Veranstaltung, pk=id)
    form = get_veranstaltung_form(request, event)
    
    if request.method == "POST":
        save_veranstaltung_form(form)

    return render(request, "veranstaltungen/bearbeiten.html", {
            "form" : form,
            "event": event
        })
