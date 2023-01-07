
def round_to_nearest(x, base=5):
    """ Round to the nearest base, default is 5.

        >>> round_to_nearest(3, 5)
        5
        >>> round_to_nearest(16, 5)
        15

    Args:
        x: integer to round
        base: round to this nearest integer

    Returns:
        integer
    """
    return base * round(x / base)

