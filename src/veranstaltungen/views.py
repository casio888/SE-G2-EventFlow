from django.shortcuts import render, get_object_or_404
from veranstaltungen.models import Veranstaltung

def veranstaltungen_liste(request):
    events = Veranstaltung.objects.all()
    return render(request, "veranstaltungen/liste.html", {"events": events})

def veranstaltung_erstellen(request):
    return render(request, "veranstaltungen/erstellen.html")

def veranstaltung_detail(request, id):
    event = get_object_or_404(Veranstaltung, pk=id)
    return render(request, "veranstaltungen/detail.html", {"event": event})
