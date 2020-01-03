import os
import json
import sys
import datetime
import base64
import copy
import collections.abc
from .datetimes import fromisoformat


def _encode_value(value):
    return 'b64{}'.format(base64.b64encode(value.encode('utf-8')).decode('utf-8'))


def _decode_value(value):
    if value.startswith('b64'):
        return base64.b64decode(value[3:]).decode('utf-8')
    return value


class _PasswordManager:
    _type = 'encoded'

    def __init__(self, value):
        self.value = str(value)

    def __str__(self):
        return f'<{self.__class__.__name__}: {self.value}>'

    def __repr__(self):
        return f'<{self.__class__.__name__}: {self.value}>'


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
                '_type': o._type,
                'value': _encode_value(o.value)
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
        if obj.get('_type') in ['password', _PasswordManager._type]:
            return _decode_value(obj['value'])

        return obj


def _recursive_encode_config_dict_passwords(d, first=True, keys_to_encode=None):
    """ Recursively traverse the dict supplied looking for passwords.

    Args:
        d: The dict to search.

    Returns:
        A modified dict with passwords wrapped in _PasswordManager
    """
    if first:
        d = copy.deepcopy(d)

    if not keys_to_encode:
        keys_to_encode = []

    # Only attempt to load the keys data from config if its the first iteration
    if not keys_to_encode and first:
        keys_to_encode = d.get('__config_params', {}).get('keys_to_encode', [])

    # Double check we're still working with a list
    if not isinstance(keys_to_encode, list):
        raise ValueError(f'keys_to_encode must by of type list or None, found {type(keys_to_encode)}')

    # Re-add the keys to config on first iteration so it gets saved
    if keys_to_encode and first:
        d['__config_params'] = {'keys_to_encode': keys_to_encode}

    for k, v in d.items():

        if k == '__config_params':
            continue

        dv = d.get(k, {})
        if not isinstance(dv, collections.abc.Mapping):
            if isinstance(k, str) and ('password' in k.lower() or k in keys_to_encode):
                v = _PasswordManager(v)
            d[k] = v
        elif isinstance(v, collections.abc.Mapping):
            d[k] = _recursive_encode_config_dict_passwords(dv, first=False, keys_to_encode=keys_to_encode)
        else:
            d[k] = v
    return d


def _encode_config(config, encode_passwords=True, keys_to_encode=None):
    if encode_passwords:
        encoded_config = _recursive_encode_config_dict_passwords(config, keys_to_encode=keys_to_encode)
    else:
        encoded_config = config
    return encoded_config


def _dump_json_data(config, cls=_CustomJSONEncoder, indent=4):
    return json.dumps(config, cls=cls, indent=indent)


def _load_json_data(data, cls=_CustomJSONDecoder):
    return json.loads(data, cls=cls)


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
        with open(file_location, 'r', encoding='utf8') as fo:
            config = _load_json_data(fo.read())

        # Resave file on read to ensure items that should be encoded, are encoded.
        save(config=config, file_location=file_location)
    except FileNotFoundError:
        config = dict()

    return config


def save(config: dict, file_location='config.json', use_relative_path=False, encode_passwords=True, keys_to_encode=None):
    """ Saves the configuration ini file.

    Args:
        config: dict of information to save
        file_location: Where to save the json file?
        use_relative_path: Use a path relative to the runtime file.
        encode_passwords: bool whether or not to encode passwords in base64
        keys_to_encode: list of keys found in config that should be encoded along with passwords.
    """
    if use_relative_path:
        file_path = os.path.dirname(os.path.abspath(sys.argv[0]))
        file_location = os.path.join(file_path, file_location)

    encoded_config = _encode_config(
        config=config,
        encode_passwords=encode_passwords,
        keys_to_encode=keys_to_encode
    )

    dumped_data = _dump_json_data(encoded_config)

    with open(file_location, 'w', encoding='utf8') as fw:
        fw.write(dumped_data)
