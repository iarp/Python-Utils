import datetime


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


def get_current_week_of(weekday_number, date=None):
    """ Returns the last date of the weekday_number supplied.

    i.e. I always need Thursdays but if today isn't Thursday,
        give me the one that just passed.

    >>> import calendar
    >>> get_current_week_of(calendar.THURSDAY)
    # assuming today is 2023-06-18 the above call will return 2023-06-15

    Args:
        weekday_number: The weekday index (Monday = 0)
            that we're basing our week on.
        date: The date to base it on.

    Returns:
        date object

    """
    today = date
    if not date:
        today = datetime.datetime.today()

    offset = (today.weekday() - weekday_number) % 7

    return today - datetime.timedelta(days=offset)
