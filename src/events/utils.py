from datetime import date
from events.models import Event
from django.utils import timezone

from events.models import Event


def _add_calendar_years(value: date, years: int) -> date:
    """Add calendar years to a date.

    February 29 is mapped to February 28 when the target year is not
    a leap year.

    Arguments:
        value {date} -- Date to adjust
        years {int} -- Number of calendar years to add

    Returns:
        date -- Corresponding date in the target year
    """
    try:
        return value.replace(year=value.year + years)
    except ValueError:
        return value.replace(year=value.year + years, day=28)


def get_event_form(request, event=None):
    #checks correct Event-Form while saving a new event.
    from .forms import EventForm

    if request.method == "POST":
        return EventForm(request.POST, instance=event)
    
    return EventForm(instance=event)

def save_event_form(form):
    #checks if the Event which should be saved has a correct form
    if form.is_valid():
        return form.save()
    return None


def get_six_elements():
    # get the six nearests events out of the DB. If there arent enouth it would be filled up with a demonstator
    # If wanted change here to also get Events from the same date. And can be modified for other uses
    event_list=list(Event.objects
    .filter(start_date__gt=timezone.now())
    .order_by('start_date')[:6]
)  # get max 6 elements of Events and make list
    empty_event = {
        'title': 'Demo',
        'description': 'Es fehlen Events',
        'start_date': None,
        'end_date': None,
        'location': 'Hinterkleinsiestdenicht',
        }

    while len(event_list)< 6:
        event_list.append(empty_event)

    return event_list
def get_event(event_id):
    """Sanitize event request, because event_id is user supplied.

    Args:
        event_id (int): ID of a valid event 

    Returns:
        Event: Returns the corresponding Event, or None if input was wrong or id is not found
    """
    if (type(event_id) is not int):
        return None
    try: 
        return Event.objects.get(pk=event_id)
    except:
        return None
