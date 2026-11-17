from datetime import date

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
