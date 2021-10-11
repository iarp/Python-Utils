"""
    This one is hard to explain. The functions were written 6+ years ago at an
    attempt to encode license data into a file to be read and checked.

    It still works so I figured I would include it here.
"""
import base64
import json
import math
import random
import textwrap

from .strings import random_character_generator


__GARBAGE_SPLITTER__ = '|----|'


def read_funny_data_file(filename: str = 'client.txt', **kwargs):
    """ The file that contains encoded data to be read.

    Args:
        filename: The file to read

    Returns:
        dict containing the originally encoded data.
    """
    with open(filename, 'r') as fo:
        certs_data = ''.join(line.strip() for line in fo)
    return decode_object(certs_data, **kwargs)


def write_funny_data_file(filename: str, raw_data, width=80, **kwargs):
    """ Writes a dict to a file encoded and obfuscated. Obviously not
     secure but secure enough from people who don't know computers
     and programming well enough.

    Args:
        filename: The file to write to
        raw_data: The data to write.
        width: The license file has text wrapping applied, how many columns?
    """
    encoded_string = encode_object(raw_data=raw_data, **kwargs)
    with open(filename, 'w') as fw:
        lines = textwrap.wrap(encoded_string, width)
        fw.write('\n'.join(lines))


def encode_object(raw_data, garbage_length=4000, **kwargs):
    """ Converts objects to a string for use in write_funny_data_file

    Args:
        raw_data: The data to encode.
        garbage_length: How much garbage to write to the file?
    """
    garbage = random_character_generator(garbage_length or 4000)

    data_type = type(raw_data).__name__
    if isinstance(raw_data, dict):
        raw_data = json.dumps(raw_data)

    # To make the license file larger, I've added a ton of garbage.
    raw_data = f'py{data_type}|{raw_data}{__GARBAGE_SPLITTER__}{garbage}'

    return _encode_string(raw_data, random.randint(5, 999), **kwargs)


def _encode_string(raw_data, n=20, encoding='utf8'):
    if n > 999:
        raise ValueError('n is greater than or equal to 100, 99 or lesser is permitted at this time.')

    encoded_data = base64.b64encode(raw_data.encode(encoding)).decode(encoding)
    split_encoded = [encoded_data[i:i + n] for i in range(0, len(encoded_data), n)]

    new_encoded_string = []
    for item in split_encoded:
        new_encoded_string.append(item)
        if len(item) == n:
            new_encoded_string.append(random_character_generator(n))

    new_string = ''.join(new_encoded_string)
    padded_n = str(n).rjust(3, '0')
    return f'{new_string}{padded_n}'


def decode_object(data, **kwargs):
    decoded_data = _decode_string(data, **kwargs)

    if __GARBAGE_SPLITTER__ in decoded_data:
        decoded_data, garbage = decoded_data.rsplit(__GARBAGE_SPLITTER__, 1)

    if decoded_data.startswith('pydict|'):
        decoded_data = json.loads(decoded_data[7:])
    elif decoded_data.startswith('pystr|'):
        decoded_data = decoded_data[6:]

    return decoded_data


def _decode_string(encoded_data, encoding='utf8'):
    n = int(encoded_data[-3:])
    data = encoded_data[:-3]

    split_encoded = [data[i:i + n] for i in range(0, len(data), n)]

    new_decoded_string = []
    row = 0
    for item in split_encoded:
        if len(item) < n or row % 2 == 0:
            new_decoded_string.append(item)
        row += 1
    return base64.b64decode(''.join(new_decoded_string)).decode(encoding)


def base32_unknown_string(string, replacement='Z', max_length=32, chars='ABCDEFGHIJKLMNOPQRSTUVWXYZ234567'):
    """ Creates a base32 safe string using the given string

    Args:
        string: The string to encode
        replacement: The character to be used in replacement of not-permitted characters
        max_length: max length of code to return, must be a multiple of 8 (8, 16, 24, 32 40, 48 ...etc)
        chars: The characters that are permitted to be in the string.

    Returns:
        str that is base32 safe using the email address
     """
    if not string:
        raise ValueError('string is required')
    string = ''.join([x for x in string.upper() if x in chars])
    return string.ljust(int(math.ceil(len(string) / 8.0) * 8), replacement)[:max_length]


rfdf = read_funny_data_file
wfdf = write_funny_data_file
