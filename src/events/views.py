from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404

from .forms import EventForm, TimeslotFormSet
from .models import Event


def event_create(request):
    """Create an event and its optional timeslots.

    GET displays an empty event form and timeslot formset. POST validates
    and saves both together.

    Arguments:
        request (HttpRequest): Incoming HTTP request

    Returns:
        HttpResponse: Rendered page or redirect
    """
    event = Event()
    form_data = request.POST if request.method == "POST" else None
    form = EventForm(form_data, instance=event)
    timeslot_formset = TimeslotFormSet(
        form_data,
        instance=event,
        prefix="timeslots",
    )

    if request.method == "POST":
        form_is_valid = form.is_valid()
        formset_is_valid = timeslot_formset.is_valid()

        if form_is_valid and formset_is_valid:
            with transaction.atomic():
                event = form.save()
                timeslot_formset.instance = event
                timeslot_formset.save()
            return redirect("events:events_your_events")

    return render(
        request,
        "events/create.html",
        {"form": form, "timeslot_formset": timeslot_formset},
    )


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
    timeslots = event.timeslots.order_by("start")
    return render(
        request,
        "events/detail.html",
        {"event": event, "timeslots": timeslots},
    )


def events_your_events(request):
    """
    Zeigt alle Veranstaltungen in der modernen Übersicht.

    Arguments:
        request (HttpRequest): HTTP-Request-Objekt

    Returns:
        HttpResponse: Event-Übersichtsseite
    """
    events = Event.objects.all()
    return render(request, "events/your_events.html", {"events": events})


def event_edit(request, id):
    """Update an event and its submitted timeslots together.

    Arguments:
        request (HttpRequest): Incoming HTTP request
        id (int): Event primary key

    Returns:
        HttpResponse: Rendered edit page or redirect
    """
    event = get_object_or_404(Event, pk=id)

    form_data = request.POST if request.method == "POST" else None
    form = EventForm(form_data, instance=event)
    timeslot_formset = TimeslotFormSet(
        form_data,
        instance=event,
        prefix="timeslots",
        queryset=event.timeslots.order_by("start"),
    )

    if request.method == "POST":
        form_is_valid = form.is_valid()
        formset_is_valid = timeslot_formset.is_valid()

        if form_is_valid and formset_is_valid:
            with transaction.atomic():
                form.save()
                timeslot_formset.save()
            return redirect("events:event_detail", id=event.id)

    return render(
        request,
        "events/edit.html",
        {
            "form": form,
            "event": event,
            "timeslot_formset": timeslot_formset,
        },
    )
