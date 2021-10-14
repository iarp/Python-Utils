import os
import random
import string
import unittest

from iarp_utils.encoders import _encode_string, base32_unknown_string, write_funny_data_file, read_funny_data_file
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

    def test_encode_string_n_is_limited_to_1000(self):
        self.assertRaises(ValueError, _encode_string, 'test', n=1000)
        self.assertEqual('dGVzdA==999', _encode_string('test', n=999))

    def test_encoding_stupidly_long_data(self):
        data = ''.join([random.choice(string.ascii_lowercase) for x in range(10000)])
        width = 80
        write_funny_data_file(self.test_lic_file, data, width=width)

        new_data = read_funny_data_file(self.test_lic_file)
        self.assertEqual(data, new_data)

    def test_base32_unknown_string_doesnt_throw_an_error(self):
        self.assertEqual('HEREIAMZ', base32_unknown_string('here i am'))
        self.assertEqual('HEREIAMB', base32_unknown_string('here i am b'))
        self.assertRaises(ValueError, base32_unknown_string, '')
