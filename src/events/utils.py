from datetime import date


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
    from .forms import EventForm

    if request.method == "POST":
        return EventForm(request.POST, instance=event)
    
    return EventForm(instance=event)

def save_event_form(form):
    if form.is_valid():
        return form.save()

    return None
