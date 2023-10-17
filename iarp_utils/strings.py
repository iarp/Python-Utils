import random
import re
import string
import unicodedata


def replace_all(text: str, replace_withs: dict):
    """Mass replacement of variables in a dict format.

    Examples:
        >>> my_text = 'custom string replacing id1, or id2'
        >>> replacers = {'id1': 'newvalue1', 'id2': 'newvalue2'}
        >>> replace_all(my_text, replacers)
        custom string replacing newvalue1, or newvalue2

    Advanced Examples::

        # You can also pass a dict with a sublist of bad values
        # to be converted into good values:
        >>> data = {
        >>>     'Good Value': ['Bad Value 1', 'Bad Value 2']
        >>> }
        >>> replace_all('Location: Bad Value 1', data)
        Location: Good Value
        >>> replace_all('Location: Bad Value 2', data)
        Location: Good Value

    Args:
        text: Text containing items to be replaced
        replace_withs: Dict containing key=values of items to be replaced

    Returns:
        Plain text with replaced values
    """
    for k, v in replace_withs.items():
        if isinstance(v, list):
            text = _replace_values(text, k, v)
        else:
            text = text.replace(k, v)
    return text


def _replace_values(text: str, find: str, replace_withs: list):
    for v in replace_withs:
        if isinstance(v, list):
            text = _replace_values(text, find, v)
        else:
            # orig_text = text
            text = text.replace(v, find)

            # Only process 1 replacement within the list, if the orig_text doesn't match,
            # meaning a replacement was done, just stop.
            # if orig_text != text:
            #     return text
    return text


def find_between(value: str, first: str, second: str):
    """ Grabs the characters between two points in a string

    If first is blank or not found, it starts at the start of the string.
    If second is blank or not found, it goes to the end of the string.

    Examples:
        >>> value = 'We need [some data] found in this string.'
        >>> find_between(value, '[', ']')
        some data

        >>> value = 'Missing [some data found in this string.'
        >>> find_between(value, '[', ']')
        some data found in this string.

        >>> value = 'Missing some data] found in this string.'
        >>> find_between(value, '', ']')
        Missing some data

    Args:
        value: The string to search in
        first: The first character to find
        second: The second character to find

    Returns:
        String containing whatever was between first and second.
    """
    data_start = value.find(first) + len(first)
    data_end = value[data_start:].find(second)
    if data_end >= 0:
        data_end += data_start
        return value[data_start:data_end]
    return value[data_start:]


def in_many(value: str, finders: list) -> bool:
    """ Checks if value contains any of the finders

    Args:
        value: The string to search in
        finders: A list of strings to search for within value

    Returns:
        boolean if value contains any of the finders
    """
    for f in finders:
        if f in value:
            return True
    return False


def slugify(value, replace_with='-', allow_unicode=False, lowercase=True):
    """ Convert to ASCII if 'allow_unicode' is False. Convert spaces to hyphens.
    Remove characters that aren't alphanumerics, underscores, or hyphens.
    Convert to lowercase. Also strip leading and trailing whitespace.

    Examples:

        >>> slugify('My String')
        my-string

        >>> slugify('My String')
        My-String

        >>> slugify('$4 dollars')
        4-dollars

    Args:
        value: String to slugify
        replace_with: Character to replace invalid characters with
        allow_unicode:
        lowercase: bool whether or not to lowercase the end result.

    Returns:
        Slugified string.
    """
    value = str(value)
    if allow_unicode:
        value = unicodedata.normalize('NFKC', value)
    else:
        value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
    value = re.sub(r'[^\w\s-]', '', value).strip()
    if lowercase:
        value = value.lower()
    return re.sub(r'[-\s]+', replace_with, value)


def random_character_generator(length=5):
    return "".join(
        random.SystemRandom().choice(string.ascii_uppercase + string.digits)
        for _ in range(length)
    )
