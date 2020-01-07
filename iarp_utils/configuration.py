import binascii
import os
import json
import sys
import datetime
import base64
import copy
import warnings
from .datetimes import fromisoformat


class _EncodeManager:
    _type = 'encoded'
    _prefix = 'b64'

    def __init__(self, value, encoding='utf8'):
        self._encoding = encoding
        self._value = value

        if isinstance(value, str) and value.startswith(self._prefix):
            decoded_value = base64.b64decode(value[3:]).decode(encoding)
            if decoded_value.startswith('dict:'):
                decoded_value = _load_json_data(decoded_value[5:])
            self._value = decoded_value

    def __str__(self):  # pragma: no cover
        return f'<{self.__class__.__name__}: {self._value}>'

    def __repr__(self):  # pragma: no cover
        return f'<{self.__class__.__name__}: {self._value}>'

    @property
    def encoded_value(self):
        value = self._value
        if not value:
            return ""
        if isinstance(value, dict):
            value = f'dict:{_dump_json_data(value)}'
        encoded_value = base64.b64encode(value.encode(self._encoding)).decode(self._encoding)
        return f'{self._prefix}{encoded_value}'

    @property
    def value(self):
        return self._value

    def __eq__(self, other):
        if isinstance(other, _EncodeManager):
            return self._value == other._value
        return self._value == other


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

        if isinstance(o, _EncodeManager):

            if not o.value:
                return ""

            return {
                '_type': o._type,
                'value': o.encoded_value
            }

        if isinstance(o, set):
            return {
                '_type': 'set',
                'value': list(o)
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

        obj_type = obj.get('_type')

        if obj_type == 'datetime':
            return fromisoformat(obj['value'])

        if obj_type == 'date':
            return fromisoformat(obj['value']).date()

        if obj_type in ['password', _EncodeManager._type]:
            try:
                return _EncodeManager(obj['value']).value
            except (UnicodeDecodeError, binascii.Error):
                warnings.warn('Encoded value failed to decode properly.', UnicodeWarning)
                return ''

        if obj_type == 'set':
            return set(obj['value'])

        return obj


def _recursive_encode_config_dict_passwords(d, first=True, keys_to_encode=None, keep_encoding=True):
    """ Recursively traverse the dict supplied looking for values to encode.

    Args:
        d: The dict to search.
        first: Whether or not this is the first iteration
        keys_to_encode: Keys to encode values on
        keep_encoding: Whether or not to encode values if
            the parent container is encoded or not.

    Returns:
        A modified dict with passwords wrapped in _EncodeManager
    """
    if first:
        # On first iteration of reading the dict, make a full
        # copy of it so we can alter data without affecting
        # the originally supplied dict which may still be used.
        d = copy.deepcopy(d)

    if not keys_to_encode:
        keys_to_encode = []

        if first:
            # Only attempt to load the keys data from config if its the
            # first iteration and keys_to_encode was not supplied this time.
            keys_to_encode = d.get('__config_params', {}).get('keys_to_encode', keys_to_encode)

    # Double check we're still working with a list
    if not isinstance(keys_to_encode, list):
        raise ValueError(f'keys_to_encode must by of type list or None, found {type(keys_to_encode).__name__}')

    # Re-add the keys to config on first iteration so it gets saved
    if keys_to_encode and first:
        d['__config_params'] = {'keys_to_encode': keys_to_encode}

    for k, v in d.items():

        if k == '__config_params':
            continue

        # Evaluate whether or not the value will be encoded,
        # need to pass this outcome into the recursive call
        # to stop encoding already encoded data.
        value_will_be_encoded = ('password' in k.lower() or k in keys_to_encode)

        if isinstance(v, dict):
            v = _recursive_encode_config_dict_passwords(
                d=v,
                first=False,
                keys_to_encode=keys_to_encode,
                keep_encoding=not value_will_be_encoded
            )

        if isinstance(k, str) and keep_encoding and value_will_be_encoded:
            v = _EncodeManager(v)
        d[k] = v
    return d


def _encode_config(config, encode_passwords=True, **kwargs):
    if encode_passwords:
        encoded_config = _recursive_encode_config_dict_passwords(config, **kwargs)
    else:
        encoded_config = config
    return encoded_config


def _dump_json_data(config, cls=_CustomJSONEncoder, indent=4):
    return json.dumps(config, cls=cls, indent=indent)


def _load_json_data(data, cls=_CustomJSONDecoder):
    return json.loads(data, cls=cls)


def load(file_location='config.json', use_relative_path=False, resave_on_load=True):
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
        file_location: Where to save the json file?
        use_relative_path: Use a path relative to the runtime file.
            Depending on the situation (py2exe, cx_freeze...etc) if you supplied
            a file_location='config.json' the file would attempt to load
            from the zip file of the compiled exe. If you supply use_relative_path=True,
            it will change the root path to be based on where the exe is executing from.
        resave_on_load: bool whether or not to resave after loading.
            Default is enabled, this allows encoded items that may've been
            manually updated to be re-encoded on next runtime.
    Returns:
        dict containing values from the json file.
    """

    if use_relative_path and not os.path.isfile(file_location):
        file_path = os.path.dirname(os.path.abspath(sys.argv[0]))
        file_location = os.path.join(file_path, file_location)

    try:
        with open(file_location, 'r', encoding='utf8') as fo:
            config = _load_json_data(fo.read())

        if resave_on_load:
            # Resave file on read to ensure items that should be encoded, are encoded.
            save(config=config, file_location=file_location)
    except FileNotFoundError:
        config = dict()

    return config


def save(config: dict, file_location='config.json', use_relative_path=False, encode_passwords=True, keys_to_encode=None):
    """ Saves the configuration ini file.

    Examples:

        >>> config = {'SQL': {'hostname': '192.168.1.2', ...}}
        >>> save(config, 'config.json')

        If using something like py2exe, cx_Freeze or the like, supply use_relative_path=True
        >>> save(config, 'config.jsoni', use_relative_path=True)

    Args:
        config: dict of information to save
        file_location: Where to save the json file?
        use_relative_path: Use a path relative to the runtime file.
            Depending on the situation (py2exe, cx_freeze...etc) if you supplied
            a file_location='config.json' the file would attempt to load
            from the zip file of the compiled exe. If you supply use_relative_path=True,
            it will change the root path to be based on where the exe is executing from.
        encode_passwords: bool whether or not to encode passwords in base64
        keys_to_encode: list of keys found in config that should be encoded along with passwords.
            By default any key that contains the word "password" is encoded using the base64 library.
            This is nothing more than to stop a quick opportunist from opening the file and
            seeing it immediately.

            If you supply a list of keys that should also be encoded,
            that list is stored in the json data under the key __config_params
            as such it would be best to not use __config_params as a first
            level key in your dict.

            However if you supply keys_to_encode and in the future you decide to
            add another item to keys_to_encode, you must supply all of the original
             keys_to_encode items along with the new ones. Otherwise all of the
             original encoded keys will be decoded on the next save.
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
