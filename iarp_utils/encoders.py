"""
    This one is hard to explain. The functions were written 6+ years ago at an
    attempt to encode license data into a file to be read and checked.

    It still works so I figured I would include it here.
"""
import textwrap
import json
import base64
import random

from .strings import random_character_generator


def read_funny_data_file(filename: str):
    """ The file that contains encoded data to be read.

    Args:
        filename: The file to read

    Returns:
        dict containing the originally encoded data.
    """
    with open(filename, 'r') as fo:
        certs_data = ''.join(line.strip() for line in fo)
    decoded_data = _decode_funny_data(certs_data)

    if isinstance(decoded_data, dict) and 'garbage' in decoded_data:
        del(decoded_data['garbage'])

    return decoded_data


def write_funny_data_file(filename: str, raw_data: dict, width=80):
    """ Writes a dict to a file encoded and obfuscated. Obvisouly not
     secure but secure enough from people who don't know computers
     and programming well enough.

    Args:
        filename: The file to write to
        raw_data: The data to write.
        width: The license file has text wrapping applied, how many columns?
    """

    # To make the license file larger, I've added a ton of garbage.
    if 'garbage' not in raw_data:
        raw_data['garbage'] = random_character_generator(2000)

    encoded_string = _encode_funny_data(raw_data, random.randint(5, 90))
    with open(filename, 'w') as fw:
        lines = textwrap.wrap(encoded_string, width)
        fw.write('\n'.join(lines))


def _encode_funny_data(data, n=20):
    if n > 99:
        raise ValueError('n is greater than or equal to 100, 99 or lesser is permitted at this time.')

    encoded_data = base64.b64encode(json.dumps(data).encode('utf8')).decode('utf8')
    split_encoded = [encoded_data[i:i + n] for i in range(0, len(encoded_data), n)]

    new_encoded_string = []
    for item in split_encoded:
        new_encoded_string.append(item)
        if len(item) == n:
            new_encoded_string.append(random_character_generator(n))

    return '{}{}'.format(''.join(new_encoded_string), str(n).rjust(2, '0'))


def _decode_funny_data(encoded_data, json_item=True):
    n = int(encoded_data[-2:])
    data = encoded_data[:-2]

    split_encoded = [data[i:i + n] for i in range(0, len(data), n)]

    new_decoded_string = []
    row = 0
    for item in split_encoded:
        if len(item) < n or row % 2 == 0:
            new_decoded_string.append(item)
        row += 1
    data = base64.b64decode(''.join(new_decoded_string)).decode('utf8')
    if json_item:
        return json.loads(data)
    return data
