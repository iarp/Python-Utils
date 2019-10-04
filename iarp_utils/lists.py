

def chunks(list_obj, size):
    """ Separate lists into smaller chunks, this quickly splits them.

    For example sometimes in REST calls you can only send 20 at a time:

    Examples:

        >>> items = list(range(1, 100))
        >>> items_split_up = chunks(items, 20)
        >>> for chunk in items_split_up:
        >>>     print(chunk)
        [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20]
        [21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40]

    Args:
        list_obj: list object to be split up
        size: how many items per "chunk"

    Returns:
        yielded values from list_obj split by size.
    """
    for i in range(0, len(list_obj), size):
        yield list_obj[i:i + size]
