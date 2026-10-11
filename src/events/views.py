from django.shortcuts import render, redirect, get_object_or_404
from .models import Veranstaltung
from .forms import VeranstaltungForm
from .utils import get_veranstaltung_form, save_veranstaltung_form

def veranstaltung_create(request):
    """
    Erstellt eine neue Veranstaltung.

    Bei GET wird ein leeres Formular angezeigt.
    Bei POST wird das Formular validiert und gespeichert.

    Arguments:
        request (HttpRequest): HTTP-Request-Objekt

    Returns:
        HttpResponse: Rendered HTML-Seite oder Redirect
    """
    if request.method == "POST":
        form = VeranstaltungForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("events:events_your_events")
    else:
        form = VeranstaltungForm()

    return render(request, "events/create.html", {"form": form})


def veranstaltung_detail(request, id):
    """
    Zeigt die Detailansicht einer Veranstaltung.

    Arguments:
        request (HttpRequest): HTTP-Request-Objekt
        id (int): Primärschlüssel der Veranstaltung

    Returns:
        HttpResponse: Detailseite der Veranstaltung
    """
    event = get_object_or_404(Veranstaltung, pk=id)
    return render(request, "events/detail.html", {"event": event, "timeslots": event.timeslots.all(),})

def events_your_events(request):
    """
    Zeigt alle Veranstaltungen in der modernen Übersicht.

    Arguments:
        request (HttpRequest): HTTP-Request-Objekt

    Returns:
        HttpResponse: Event-Übersichtsseite
    """
    events = Veranstaltung.objects.all()
    return render(request, "events/your_events.html", {"events": events})

def veranstaltung_edit(request, id):
    """
    Bearbeitet eine bestehende Veranstaltung.

    Arguments:
        request (HttpRequest): HTTP-Request-Objekt
        id (int): Primärschlüssel der Veranstaltung

    Returns:
        HttpResponse: Bearbeitungsseite der Veranstaltung oder Redirect
    """
    event = get_object_or_404(Veranstaltung, pk=id)

    if request.method == "POST":
        form = VeranstaltungForm(request.POST, instance=event)
        if form.is_valid():
            form.save()
            return redirect("events:veranstaltung_detail", id=event.id)
    else:
        form = VeranstaltungForm(instance=event)

    return render(request, "events/edit.html", {"form": form, "event": event})
