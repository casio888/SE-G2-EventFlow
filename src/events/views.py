from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404

from authentication.decorators import (
    AccountType,
    check_if_organizer_or_contributer,
    check_if_user_authneticated,
)
from authentication.models import CustomUserContributer, CustomUserOrganizer

from .forms import EventForm, TimeslotFormSet
from .models import Event


@check_if_user_authneticated()
@check_if_organizer_or_contributer(AccountType.ORGANIZER)
def event_create(request):
    """Create an event and its optional timeslots.

    GET displays an empty event form and timeslot formset. POST validates
    and saves both together.

    Arguments:
        request (HttpRequest): Incoming HTTP request

    Returns:
        HttpResponse: Rendered page or redirect
    """
    organizer = get_object_or_404(CustomUserOrganizer, pk=request.user.pk)
    event = Event(event_owner=organizer)
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
                event = form.save(organizer=organizer)
                timeslot_formset.instance = event
                timeslot_formset.save()
            return redirect("events:events_your_events")

    return render(
        request,
        "events/create.html",
        {"form": form, "timeslot_formset": timeslot_formset},
    )


@check_if_user_authneticated()
def event_detail(request, id):
    """Display an event and its timeslots.

    Arguments:
        request (HttpRequest): Incoming HTTP request
        id (int): Event primary key

    Returns:
        HttpResponse: Rendered event detail page
    """
    event = get_object_or_404(Event, pk=id)
    timeslots = event.timeslots.order_by("start")
    return render(
        request,
        "events/detail.html",
        {"event": event, "timeslots": timeslots},
    )


@check_if_user_authneticated()
@check_if_organizer_or_contributer(AccountType.ORGANIZER)
def events_your_events(request):
    """Display events associated with the authenticated account.

    Arguments:
        request (HttpRequest): Incoming HTTP request

    Returns:
        HttpResponse: Rendered event overview
    """
    if CustomUserOrganizer.objects.filter(pk=request.user.pk).exists():
        event_owner = CustomUserOrganizer.objects.get(pk=request.user.pk)
        events = Event.objects.filter(event_owner=event_owner)
    elif CustomUserContributer.objects.filter(pk=request.user.pk).exists():
        events = Event.objects.filter(contributors__pk=request.user.pk)

    return render(request, "events/your_events.html", {"events": events})


@check_if_user_authneticated()
@check_if_organizer_or_contributer(AccountType.ORGANIZER)
def event_edit(request, id):
    """Update an event and its submitted timeslots together.

    Arguments:
        request (HttpRequest): Incoming HTTP request
        id (int): Event primary key

    Returns:
        HttpResponse: Rendered edit page or redirect
    """
    organizer = get_object_or_404(CustomUserOrganizer, pk=request.user.pk)
    event = get_object_or_404(Event, pk=id, event_owner=organizer)

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
                form.save(organizer=organizer)
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
