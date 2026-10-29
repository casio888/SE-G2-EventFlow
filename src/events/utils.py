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
