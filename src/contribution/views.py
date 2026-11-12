from django.shortcuts import redirect, render, get_object_or_404
from authentication.decorators import (
    AccountType,
    check_if_organizer_or_contributer,
    check_if_user_authneticated,
)
from authentication.models import CustomUserContributer, CustomUserOrganizer
from .forms import ContributionForm
from .models import Contribution
from events.models import Event
from events.utils import get_event

def event_list(request):
    """Shows a List of all Events and Buttons to start submitting a contribution
    Temporary, will be replaced bby Submit buttons on start and event detail pages and search

    Args:
        request <request>: URL Request

    Returns:
        <HTML>: Rendered website
    """
    events=Event.objects.all()
    context={'events': events}
    return render(request,'contribution/contribution.html',context)

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

    if request.method == "POST":
        form = ContributionForm(event_id=event_id, data=request.POST)
        if form.is_valid():
            try:
                form.save(contributor)
            except ValueError:
                form.add_error(None,"Einreicher muss existieren")
                pass # TODO Show error Message
            # TODO show success message
            # TODO redirect to contribution overview page instead of index
            return redirect("base:index")
    else:
        form = ContributionForm(event_id=event_id)
        # TODO if contribution exists, redirect to calling page and show message of error

    event = get_event(event_id)
    context = {'event': event, 'form': form}
    return render(request,'contribution/application.html',context)