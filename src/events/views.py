from django.shortcuts import render, redirect, get_object_or_404
from .models import Event
from .forms import EventForm
from .utils import get_event_form, save_event_form

from authentication.models import CustomUserContributer, CustomUserOrganizer
from authentication.decorators import AccountType
from authentication.decorators import check_if_organizer_or_contributer, check_if_user_authneticated

@check_if_user_authneticated()
@check_if_organizer_or_contributer(AccountType.ORGANIZER)
def event_create(request):
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
        form = EventForm(request.POST)
        if form.is_valid():
            organizer=CustomUserOrganizer.objects.get(pk=request.user.pk)

            form.save(organizer)
            return redirect("events:events_your_events")
    else:
        form = EventForm()

    return render(request, "events/create.html", {"form": form})

@check_if_user_authneticated()
def event_detail(request, id):
    """
    Zeigt die Detailansicht einer Veranstaltung.

    Arguments:
        request (HttpRequest): HTTP-Request-Objekt
        id (int): Primärschlüssel der Veranstaltung

    Returns:
        HttpResponse: Detailseite der Veranstaltung
    """
    event = get_object_or_404(Event, pk=id)
    return render(request, "events/detail.html", {"event": event, "timeslots": event.timeslots.all(),})

@check_if_user_authneticated()
def events_your_events(request):
    """
    Zeigt alle Veranstaltungen in der modernen Übersicht.

    Arguments:
        request (HttpRequest): HTTP-Request-Objekt

    Returns:
        HttpResponse: Event-Übersichtsseite
    """
    if CustomUserOrganizer.objects.filter(pk=request.user.pk).exists():
        event_owner=CustomUserOrganizer.objects.get(pk=request.user.pk)
        events = Event.objects.filter(event_owner=event_owner)

    elif CustomUserContributer.objects.filter(pk=request.user.pk).exists():
        events = Event.objects.filter(contributors__pk=request.user.pk)

    return render(request, "events/your_events.html", {"events": events})

@check_if_user_authneticated()
def event_edit(request, id):
    """
    Bearbeitet eine bestehende Veranstaltung.

    Arguments:
        request (HttpRequest): HTTP-Request-Objekt
        id (int): Primärschlüssel der Veranstaltung

    Returns:
        HttpResponse: Bearbeitungsseite der Veranstaltung oder Redirect
    """
    event = get_object_or_404(Event, pk=id)

    if request.method == "POST":
        form = EventForm(request.POST, instance=event)
        if form.is_valid():
            form.save()
            return redirect("events:event_detail", id=event.id)
    else:
        form = EventForm(instance=event)

    return render(request, "events/edit.html", {"form": form, "event": event})
