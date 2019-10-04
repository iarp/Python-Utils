import os
import json
import sys
import datetime
import base64
import copy
import collections.abc
from .datetimes import fromisoformat


class _PasswordManager:

    def __init__(self, value):
        self.value = str(value)

    def __str__(self):
        return f'<{self.__class__.__name__}: {self.value}>'

    def __repr__(self):
        return f'<{self.__class__.__name__}: {self.value}>'

    @staticmethod
    def encode(value):
        return 'b64{}'.format(base64.b64encode(value.encode('utf-8')).decode('utf-8'))

    @staticmethod
    def decode(value):
        if value.startswith('b64'):
            return base64.b64decode(value[3:]).decode('utf-8')
        return value


class _CustomJSONEncoder(json.JSONEncoder):
    """ When the default JSONEncoder does not know how to deal with a certain
    object type, it calls to default and we can do whats needed to convert
    the data into a string value.
    """

    def default(self, o):

        if isinstance(o, (datetime.date, datetime.datetime)):
            return {
                '_type': type(o).__name__,
                'value': o.isoformat()
            }

        if isinstance(o, _PasswordManager):
            return {
                '_type': 'password',
                'value': _PasswordManager.encode(o.value)
            }

        return super().default(o=o)


class _CustomJSONDecoder(json.JSONDecoder):
    """ When data loads from the json file, check if there is a _type value
    that matches what we know of and can convert back to that object.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(object_hook=self.object_hook, *args, **kwargs)

    @staticmethod
    def object_hook(obj):
        if '_type' not in obj:
            return obj

        if obj.get('_type') == 'datetime':
            return fromisoformat(obj['value'])
        if obj.get('_type') == 'date':
            return fromisoformat(obj['value']).date()
        if obj.get('_type') == 'password':
            return _PasswordManager.decode(obj['value'])

        return obj


def _recursive_encode_config_dict_passwords(d, first=True):
    """ Recursively traverse the dict supplied looking for passwords.

    Args:
        d: The dict to search.

    Returns:
        A modified dict with passwords wrapped in _PasswordManager
    """
    if first:
        d = copy.deepcopy(d)
    for k, v in d.items():
        dv = d.get(k, {})
        if not isinstance(dv, collections.abc.Mapping):
            if isinstance(k, str) and 'password' in k.lower():
                v = _PasswordManager(v)
            d[k] = v
        elif isinstance(v, collections.abc.Mapping):
            d[k] = _recursive_encode_config_dict_passwords(dv, first=False)
        else:
            d[k] = v
    return d


def load(file_location='config.json', use_relative_path=False):
    """ Loads up a config.json file into a multi-level dict.

    Any options that contain the name "password" are encoded. It's nothing more than
        to stop someone from taking a quick peak at the file and getting a password.
        This way they'll need to know how to decode first.

    You can manually update the password value by changing it directly in the json file.
    It will auto-resave on next load.

    Example config.json:
        {
            "SQL": {
                "hostname": "127.0.0.1",
                "database": "NorthWind",
                "username": "sa",
                "password": {
                    "_type": "password",
                    "value": "b64MTIzNDU="
                }
            }
        }

    Example output from load using above example config.json
        {
            'SQL': {
                'hostname': '127.0.0.1',
                'database': 'NorthWind',
                'username': 'sa',
                'password': '12345',
            }
        }

    Args:
        file_location: Where is the config.ini located? Best to pass full system path if possible.
        use_relative_path:

    Returns:
        dict containing values from the json file.
    """

    if use_relative_path and not os.path.isfile(file_location):
        file_path = os.path.dirname(os.path.abspath(sys.argv[0]))
        file_location = os.path.join(file_path, file_location)

    try:
        with open(file_location, 'r') as fo:
            config = json.load(fo, cls=_CustomJSONDecoder)
        save(config=config, file_location=file_location)
    except FileNotFoundError:
        config = dict()

    return config


def save(config: dict, file_location='config.json', use_relative_path=False, encode_passwords=True):
    """ Saves the configuration ini file.

    Args:
        config: dict of information to save
        file_location: Where to save the json file?
        use_relative_path: Use a path relative to the runtime file.
        encode_passwords: bool whether or not to encode passwords in base64
    """
    if use_relative_path:
        file_path = os.path.dirname(os.path.abspath(sys.argv[0]))
        file_location = os.path.join(file_path, file_location)

    with open(file_location, 'w') as fw:

        if encode_passwords:
            encoded_config = _recursive_encode_config_dict_passwords(config)
        else:
            encoded_config = config
        json.dump(encoded_config, fw, cls=_CustomJSONEncoder, indent=4)
