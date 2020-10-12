import mock
import hashlib
import os
import unittest

from iarp_utils.files import unique_file_exists, get_mime_types_as_str, MIME_TYPES_LIST, generate_file_hash
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

    def test_get_mime_types_returned_as_str(self):
        self.assertIs(str, type(get_mime_types_as_str()))

    def test_mime_types_list_is_list(self):
        self.assertIs(list, type(MIME_TYPES_LIST))

    def test_mime_types_list_contains_many(self):
        self.assertLessEqual(100, len(MIME_TYPES_LIST))

    def test_mime_types_list_contains_some_common_types(self):
        self.assertIn('text/css', MIME_TYPES_LIST)
        self.assertIn('application/zip', MIME_TYPES_LIST)
        self.assertIn('application/json', MIME_TYPES_LIST)

    def test_get_mime_types_return_contains_some_common_types(self):
        self.assertIn('text/css', get_mime_types_as_str())
        self.assertIn('application/zip', get_mime_types_as_str())
        self.assertIn('application/json', get_mime_types_as_str())

    def test_mime_types_has_excel_types(self):
        # Is this french or spelling mistake on websites behalf?
        self.assertIn('application/vnd.openxmlformates-officedocument.spreadsheetml.sheet', MIME_TYPES_LIST)
        self.assertIn('application/vnd.spreadsheet-openxml', MIME_TYPES_LIST)
        self.assertIn('application/xls', MIME_TYPES_LIST)
        self.assertIn('application/xlsx', MIME_TYPES_LIST)

    def test_generate_file_hash(self):
        with mock.patch('%s.open' % __name__, mock.mock_open(read_data=b'aaa'), create=True) as m:
            with open('gen_hash_test_file.txt') as fo:
                result = generate_file_hash(fo)
            self.assertEqual('47bce5c74f589f4867dbd57e9ca9f808', result)

    def test_generate_file_hash_with_sha1(self):
        with mock.patch('%s.open' % __name__, mock.mock_open(read_data=b'aaa'), create=True) as m:
            with open('gen_hash_test_file.txt') as fo:
                result = generate_file_hash(fo, func=hashlib.sha1)
            self.assertEqual('7e240de74fb1ed08fa08d38063f6a6a91462a815', result)
