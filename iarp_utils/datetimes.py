
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


def iterate_steps_between_datetimes(start, end, steps):
    """
        >>> import datetime
        >>> start_raw = '2022-01-04 00:00'
        >>> end_raw = '2022-01-05 00:00'

        >>> start = datetime.datetime.strptime(start_raw, '%Y-%m-%d %H:%M')
        >>> end = datetime.datetime.strptime(end_raw, '%Y-%m-%d %H:%M')
        >>> delta = datetime.timedelta(minutes=5)

        >>> for dt in iterate_steps_between_datetimes(start, end, delta):
        ...    print(dt)
        2022-01-04 00:00
        2022-01-04 00:05
        2022-01-04 00:10
        2022-01-04 00:15
        ...
        2022-01-05 00:00

    Args:
        start: datetime to start at
        end: datetime to end at, this datetime is included in the results
        steps: timedelta with steps

    Yields:
        datetimes for each step

    """

    while start <= end:
        yield start

        start += steps
