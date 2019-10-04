import tempfile
import unittest
from pathlib import Path

from iarp_utils.browser.drivers import DriverBase
from iarp_utils.browser import utils


class DriverBaseTests(unittest.TestCase):

    def setUp(self) -> None:
        self.driver = DriverBase()

    def test_download_dir_is_custom(self):
        self.driver = DriverBase(download_directory='C:/temp')
        self.assertEqual('C:/temp', self.driver.download_directory)

    def test_download_dir_deletes_on_quit(self):
        dir = Path(self.driver.download_directory)
        self.assertTrue(dir.exists())
        self.driver.quit()
        self.assertFalse(dir.exists())

    def test_download_dir_is_same_on_multiple_calls(self):
        dir = self.driver.download_directory
        self.assertEqual(dir, self.driver.download_directory)


class BrowserUtilsTests(unittest.TestCase):

    def test_get_mime_types_returned_as_str(self):
        self.assertIs(str, type(utils.get_mime_types()))

    def test_mime_types_list_is_list(self):
        self.assertIs(list, type(utils.MIME_TYPES_LIST))

    def test_mime_types_list_contains_many(self):
        self.assertLessEqual(100, len(utils.MIME_TYPES_LIST))

    def test_mime_types_list_contains_some_common_types(self):
        self.assertIn('text/css', utils.MIME_TYPES_LIST)
        self.assertIn('application/zip', utils.MIME_TYPES_LIST)
        self.assertIn('application/json', utils.MIME_TYPES_LIST)

    def test_get_mime_types_return_contains_some_common_types(self):
        self.assertIn('text/css', utils.get_mime_types())
        self.assertIn('application/zip', utils.get_mime_types())
        self.assertIn('application/json', utils.get_mime_types())
