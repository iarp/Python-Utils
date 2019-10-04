import re


def unique_emails(*args, joiner: str = None, pattern=r"[^@]+@[^@]+\.[^@]+"):
    """ Accepts any number of arguments, match all strings that
    are email addresses and return a unique set.

    String joiner value to have the set joined: joiner.join(set)

    Examples:

        >>> unique_emails('test@example.com', 'test@example.com;test2@example.com')
        {'test@example.com', 'test2@example.com'}
        >>> unique_emails('test@example.com', 'test@example.com;test2@example.com', joiner=',')
        test2@example.com,test@example.com
        >>> unique_emails('test@example.com', ['test@example.com', 'test2@example.com'], joiner=',')
        test2@example.com,test@example.com

    Args:
        *args: strings or lists of strings containing email addresses
        joiner: string to join email addresses
        pattern: regex pattern used to match email addresses

    Returns:
        set if joiner=None or string of email addresses joined by joiner value.
    """
    ueq = set()
    for arg in args:

        if not arg:
            continue

        # Attempt to split the argument value by ; , or | turning it into a list.
        try:
            arg = re.split("[;,|]", arg)
        except TypeError:
            pass

        # The argument must be an iterable by this point
        if not isinstance(arg, (list, tuple, set)):
            continue

        for email in arg:

            if not isinstance(email, str):
                continue

            if re.match(pattern, email):
                ueq.add(email.lower().strip())

    if joiner is not None:
        return joiner.join(ueq)

    return ueq
