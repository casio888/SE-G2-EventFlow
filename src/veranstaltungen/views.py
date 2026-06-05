from django.shortcuts import render
from django.http import HttpResponse

def veranstaltungen_liste(request):
    dummy_events = [
        {"id": 1, "titel": "Event 1", "ort": "Dresden"},
        {"id": 2, "titel": "Event 2", "ort": "Berlin"},
    ]
    return render(request, "veranstaltungen/liste.html", {"events": dummy_events})

def veranstaltung_erstellen(request):
    return render(request, "veranstaltungen/erstellen.html")

def veranstaltung_detail(request, id):
    dummy_event = {
        "id": id,
        "titel": f"Event {id}",
        "ort": "Dresden",
        "start_datum": "2026-06-01",
        "end_datum": "2026-06-02",
        "beschreibung": "Beschreibung folgt",
        "bewerber": [],
    }
    return render(request, "veranstaltungen/detail.html", {"event": dummy_event})
