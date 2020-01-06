import os
import unittest

from iarp_utils.encoders import write_funny_data_file, read_funny_data_file
from tests import BASE_DIR


class EncodersTests(unittest.TestCase):

    test_lic_file = os.path.join(BASE_DIR, 'test.lic')

    def tearDown(self) -> None:
        try:
            os.unlink(self.test_lic_file)
        except:
            pass

    def test_write_read_funny_data_dict_is_correct(self):
        data = {'blah1': 'here'}
        write_funny_data_file(self.test_lic_file, data)

        new_data = read_funny_data_file(self.test_lic_file)
        self.assertIn('blah1', new_data)
        self.assertEqual('here', new_data['blah1'])
        self.assertEqual(1, len(new_data))

    def test_write_read_funny_data_str_is_correct(self):
        data = 'here'
        write_funny_data_file(self.test_lic_file, data)

        new_data = read_funny_data_file(self.test_lic_file)
        self.assertEqual('here', new_data)
        self.assertEqual(4, len(new_data))

    def test_read_funny_data_line_length_matches(self):
        data = {'blah1': 'here'}
        width = 80
        write_funny_data_file(self.test_lic_file, data, width=width)

        with open(self.test_lic_file, 'r') as fo:
            line = fo.readline().strip()

        self.assertEqual(width, len(line))
