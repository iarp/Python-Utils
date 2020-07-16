import time


def wait(seconds=1):  # pragma: no cover
    """ A wrapping for time.sleep depending on if we change how we wait in the future.

    Args:
        seconds: How many seconds to wait
    """
    time.sleep(seconds)
