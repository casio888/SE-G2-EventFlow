from django.shortcuts import render, redirect, get_object_or_404
from .models import Veranstaltung
from .forms import VeranstaltungForm
from .utils import get_veranstaltung_form, save_veranstaltung_form

def veranstaltung_erstellen(request):
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
            return redirect("veranstaltungen:veranstaltungen_your_events")
    else:
        form = VeranstaltungForm()

    return render(request, "veranstaltungen/erstellen.html", {"form": form})


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
    return render(request, "veranstaltungen/detail.html", {"event": event})

def veranstaltungen_your_events(request):
    """
    Zeigt alle Veranstaltungen in der modernen Übersicht.

    Arguments:
        request (HttpRequest): HTTP-Request-Objekt

    Returns:
        HttpResponse: Event-Übersichtsseite
    """
    events = Veranstaltung.objects.all()
    return render(request, "veranstaltungen/your_events.html", {"events": events})

def veranstaltung_bearbeiten(request, id):
  
    event = get_object_or_404(Veranstaltung, pk=id)
    form = get_veranstaltung_form(request, event)

    if request.method == "POST":
        save_veranstaltung_form(form)

    return render(request, "veranstaltungen/bearbeiten.html", {
            "form" : form,
            "event": event
        })
