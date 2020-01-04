import datetime
import warnings
import unittest

from iarp_utils.configuration import (
    _encode_config, _load_json_data, _encode_value,
    _decode_value, _dump_json_data, _CustomJSONDecoder,
    _EncodeManager
)


class ConfigurationTests(unittest.TestCase):

    def test_encode_value(self):
        self.assertEqual('b64MTIzNDU=', _encode_value("12345"))
        self.assertEqual('', _encode_value(''))

    def test_decode_value(self):
        self.assertEqual("12345", _decode_value("b64MTIzNDU="))
        self.assertEqual('here', _decode_value('here'))

    def test_encode_config_with_encode_passwords_false(self):
        config = {'sub': {'password': '12345'}}
        encoded_config = _encode_config(config, encode_passwords=False)
        self.assertEqual(config['sub']['password'], encoded_config['sub']['password'])

    def test_encode_config_with_encode_passwords_false_as_string(self):
        config = {'sub': {'password': '12345'}}
        encoded_config = _encode_config(config, encode_passwords=False)
        string_config = _dump_json_data(encoded_config)
        self.assertIn(config['sub']['password'], string_config)

    def test_encode_config_with_encode_passwords_true(self):
        config = {'sub': {'password': '12345'}}
        encoded_config = _encode_config(config, encode_passwords=True)
        self.assertNotEqual(config['sub']['password'], encoded_config['sub']['password'])

    def test_encode_config_with_encode_passwords_true_as_string(self):
        config = {'sub': {'password': '12345'}}
        encoded_config = _encode_config(config, encode_passwords=True)
        string_config = _dump_json_data(encoded_config)
        self.assertNotIn(config['sub']['password'], string_config)

    def test_encode_config_with_encode_passwords_true_and_keys_to_encode(self):
        config = {'sub': {'sid': '12345'}}
        encoded_config = _encode_config(config, encode_passwords=True, keys_to_encode=['sid'])
        self.assertNotEqual(config['sub']['sid'], encoded_config['sub']['sid'])

    def test_encode_config_with_encode_passwords_true_and_keys_to_encode_as_string(self):
        config = {'sub': {'sid': '12345'}}
        encoded_config = _encode_config(config, encode_passwords=True, keys_to_encode=['sid'])
        string_config = _dump_json_data(encoded_config)
        self.assertNotIn(config['sub']['sid'], string_config)

    def test_type_checks_after_encode_and_decode_config_dict(self):

        d = datetime.datetime.now().date()
        dt = datetime.datetime.now()

        config = {
            'type_checks': {
                'd': d,
                'dt': dt,
                'int': 1,
                'bool_true': True,
                'bool_false': False,
                'escape percentages': '%',
                'b64encode password': '12345',
                '_type': 'test'
            }
        }

        encoded_config = _encode_config(config)
        dumped_config = _dump_json_data(encoded_config)

        self.assertIn(_encode_value("12345"), dumped_config)

        config2 = _load_json_data(dumped_config)
        self.assertIn('type_checks', config2)
        type_checks = config2['type_checks']

        self.assertEqual(d, type_checks['d'])
        self.assertEqual(dt, type_checks['dt'])
        self.assertEqual(1, type_checks['int'])
        self.assertTrue(type_checks['bool_true'])
        self.assertFalse(type_checks['bool_false'])
        self.assertEqual('%', type_checks['escape percentages'])
        self.assertEqual('12345', type_checks['b64encode password'])
        self.assertEqual('test', type_checks['_type'])

    def test_encode_config_with_keys_to_encode(self):

        config = {
            'Test': {
                'InDepth': '12345'
            }
        }

        encoded_config = _encode_config(config=config, keys_to_encode=['InDepth'])
        dumped_config = _dump_json_data(encoded_config)

        self.assertIn('__config_params', dumped_config)
        self.assertIn(_encode_value("12345"), dumped_config)

        dejsoned_config = _load_json_data(dumped_config)

        self.assertIn('__config_params', dejsoned_config)
        self.assertIn('keys_to_encode', dejsoned_config['__config_params'])
        self.assertIn('InDepth', dejsoned_config['__config_params']['keys_to_encode'])

        self.assertEqual('12345', dejsoned_config['Test']['InDepth'])

    def test_customjsondecoder_password_failure(self):
        with warnings.catch_warnings(record=True) as w:
            _CustomJSONDecoder.object_hook({
                '_type': _EncodeManager._type,
                'value': 'b64blahs'
            })
            msg = w[-1]
            self.assertTrue(issubclass(msg.category, UnicodeWarning))
            self.assertEqual("Encoded value failed to decode properly.", str(msg.message))

    def test_encode_config_raises_on_invalid_keys_to_encode(self):
        config = {'test': ''}
        with self.assertRaises(ValueError):
            _encode_config(config, keys_to_encode='bad value')
