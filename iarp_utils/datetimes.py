
DAYNAMES = 'sun', 'mon', 'tue', 'wed', 'thu', 'fri', 'sat'
WEEKDAYS = dict(zip(DAYNAMES, range(7)))


def weekday(name):
    """Return the position of a weekday: 0 - 7, where 0 is Sunday.

    Example:
        >>> weekday('sunday'), weekday('sun'), weekday('mon')
        (0, 0, 1)
    """
    abbreviation = name[0:3].lower()
    try:
        return WEEKDAYS[abbreviation]
    except KeyError:
        # Show original day name in exception, instead of abbr.
        raise KeyError(name)
