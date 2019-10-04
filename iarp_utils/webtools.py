from collections import OrderedDict
import datetime


def dropdown_timerange(inc_in_minutes=15):
    """ Creates a list of time objects starting from start_datetime increment by inc_in_minutes

    Examples:

        >>> dropdown_timerange(inc_in_minutes=15)
        OrderedDict([
            (datetime.time(0, 0), datetime.datetime(2019, 10, 2, 0, 0)),
            (datetime.time(0, 15), datetime.datetime(2019, 10, 2, 0, 15)),
            (datetime.time(0, 30), datetime.datetime(2019, 10, 2, 0, 30)),
            (datetime.time(0, 45), datetime.datetime(2019, 10, 2, 0, 45)),
            ...
        ])

        >>> dropdown_timerange(inc_in_minutes=5)
        OrderedDict([
            (datetime.time(0, 0), datetime.datetime(2019, 10, 2, 0, 0)),
            (datetime.time(0, 5), datetime.datetime(2019, 10, 2, 0, 5)),
            (datetime.time(0, 10), datetime.datetime(2019, 10, 2, 0, 10)),
            (datetime.time(0, 15), datetime.datetime(2019, 10, 2, 0, 15)),
            ...
        ])

    Args:
        inc_in_minutes: How many minutes between each increment?

    Returns:
        OrderedDict of datetime.time => datetime.datetime objects.
    """
    start_datetime = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    inc = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

    date_range = OrderedDict()
    while start_datetime.date() == inc.date():

        # Prevent double entries, namely 00:00:00 hours happens twice while calculating dates in this manner
        if inc.time() not in date_range:
            date_range[inc.time()] = inc

        inc = inc + datetime.timedelta(minutes=inc_in_minutes)
    return date_range
