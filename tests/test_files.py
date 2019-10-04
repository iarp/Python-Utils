import os
import unittest

from iarp_utils.files import unique_file_exists
from tests import BASE_DIR


class FilesTests(unittest.TestCase):

    def test_unique_file_exists_not_exist(self):
        self.assertEqual(
            os.path.join('cache', 'test.pdf'),
            unique_file_exists('cache', 'test', 'pdf')
        )

    def test_unique_file_exists_does_exist(self):
        self.assertEqual(
            os.path.join(BASE_DIR, '__init___1.py'),
            unique_file_exists(BASE_DIR, '__init__', 'py')
        )

    def test_unique_file_exists_does_exist_no_counter(self):
        value = unique_file_exists(BASE_DIR, '__init__', 'py', use_counter=False)
        raw_value = value.replace(BASE_DIR, '').replace('.py', '').replace('__init__', '').lstrip(os.sep)
        self.assertEqual(6, len(raw_value), raw_value)

    def test_unique_file_exists_does_exist_no_counter_lengths(self):
        length = 5
        value = unique_file_exists(BASE_DIR, '__init__', 'py', use_counter=False, length=length)
        raw_value = value.replace(BASE_DIR, '').replace('.py', '').replace('__init__', '').lstrip(os.sep)
        self.assertEqual(length + 1, len(raw_value), raw_value)

        length = 15
        value = unique_file_exists(BASE_DIR, '__init__', 'py', use_counter=False, length=length)
        raw_value = value.replace(BASE_DIR, '').replace('.py', '').replace('__init__', '').lstrip(os.sep)
        self.assertEqual(length + 1, len(raw_value), raw_value)
