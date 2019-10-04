import datetime
import os
import unittest

from iarp_utils.configuration import load, save
from tests import BASE_DIR


class ConfigurationTests(unittest.TestCase):

    garbage_json_file = os.path.join(BASE_DIR, 'garbage_config.json')

    def tearDown(self) -> None:
        try:
            os.unlink(self.garbage_json_file)
        except (OSError, PermissionError, FileNotFoundError):
            pass

    def test_load(self):
        config = load(os.path.join(BASE_DIR, 'test_config.json'))
        self.assertIn('for testing', config)
        self.assertIn('value', config['for testing'])
        self.assertEqual(config['for testing']['value'], 1)

    def test_save(self):

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

        save(config, self.garbage_json_file)

        config2 = load(self.garbage_json_file)
        self.assertIn('type_checks', config2)
        tc = config2['type_checks']

        self.assertEqual(d, tc['d'])
        self.assertEqual(dt, tc['dt'])
        self.assertEqual(1, tc['int'])
        self.assertTrue(tc['bool_true'])
        self.assertFalse(tc['bool_false'])
        self.assertEqual('%', tc['escape percentages'])
        self.assertEqual('12345', tc['b64encode password'])
        self.assertIn('_type', tc)
        self.assertEqual('test', tc['_type'])
