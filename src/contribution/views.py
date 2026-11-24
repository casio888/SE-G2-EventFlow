from django.contrib import messages
from django.shortcuts import redirect, render, get_object_or_404
from authentication.decorators import (
    AccountType,
    check_if_organizer_or_contributer,
    check_if_user_authneticated,
)
from authentication.models import CustomUserContributer, CustomUserOrganizer
from .forms import ContributionForm
from .models import Contribution
from .utils import get_contributions_for_event
from events.models import Event
from base.utils import redirect_to_referrer


def event_list(request):
    """Shows a List of all Events and Buttons to start submitting a contribution
    Temporary, will be replaced bby Submit buttons on start and event detail pages and search

    Args:
        request <request>: URL Request

    Returns:
        <HTML>: Rendered website
    """
    events = Event.objects.all()
    context = {"events": events}
    return render(request, "contribution/contribution.html", context)


@check_if_user_authneticated()
@check_if_organizer_or_contributer(AccountType.CONTRIBUTOR)
def event_application(request, event_id):
    """Opens a Form to submit a new contribution to an event.
    TODO Should refuse to open and redirect back, once user roles are implemented, and an application for an event already exists

    Args:
        request <request>: URL Request
        event_id <int>: Valid ID of an Event

    Returns:
        <HTML>: Rendered Website
    """
    contributor = get_object_or_404(CustomUserContributer, pk=request.user.pk)
    event = get_object_or_404(Event, pk=event_id)

    if Contribution.objects.filter(
        fk_event__pk=event.pk, fk_contributor__pk=contributor.pk
    ).exists():
        messages.error(request, "Du hast dich bereits für dieses Event beworben.")
        return redirect_to_referrer(request, "event_list")

    if request.method == "POST":
        form = ContributionForm(event=event, data=request.POST)
        if form.is_valid():
            try:
                form.save(contributor)
            except ValueError:
                form.add_error(None, "Einreicher muss existieren")
                pass  # TODO Show error Message
            # TODO show success message
            # TODO redirect to contribution overview page instead of index
            return redirect("base:index")
    else:
        form = ContributionForm(event=event)

    context = {"event": event, "form": form}
    return render(request, "contribution/application.html", context)


@check_if_user_authneticated()
@check_if_organizer_or_contributer(AccountType.ORGANIZER)
def event_contributions(request, event_id=None):
    """Display applications for an event owned by the current organizer.

    Authentication and organizer decorators restrict access to organizer accounts.
    Without an event ID, the first owned event ordered by date and title is selected.
    A supplied ID is resolved only within the organizer's events, preventing access
    to applications submitted to events owned by another organizer.

    Arguments:
        request (HttpRequest): Incoming HTTP request.
        event_id (int | None): Optional primary key of an owned event.

    Returns:
        HttpResponse: Rendered application overview for the selected event, or an
            empty overview when the organizer owns no events.
    """
    organizer = get_object_or_404(CustomUserOrganizer, pk=request.user.pk)
    events = Event.objects.filter(event_owner=organizer).order_by("start_date", "title")

    if event_id is None:
        event = events.first()
    else:
        event = get_object_or_404(events, pk=event_id)

    contributions = Contribution.objects.none()
    if event is not None:
        contributions = get_contributions_for_event(event.pk).select_related(
            "fk_contributor"
        )

    return render(
        request,
        "contribution/contribution_list.html",
        {
            "events": events,
            "event": event,
            "contributions": contributions,
        },
    )
