import datetime
import unittest
from unittest.mock import patch, mock_open
from pathlib import Path

from iarp_utils.browser.drivers import DriverBase


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

    @patch("builtins.open", new_callable=mock_open, read_data="")
    def test_check_version_allowed(self, mock_file):
        self.assertTrue(self.driver._check_driver_version_allowed())

    @patch("builtins.open", new_callable=mock_open, read_data="{")
    def test_check_version_allowed_bad_json_format(self, mock_file):
        self.assertTrue(self.driver._check_driver_version_allowed())

    @patch("builtins.open", new_callable=mock_open, read_data=f'{{"DriverBase": ["{datetime.datetime.now().isoformat()}"]}}')
    def test_check_version_allowed_recent_entry(self, mock_file):
        self.assertFalse(self.driver._check_driver_version_allowed())

    @patch("builtins.open", new_callable=mock_open, read_data=f'{{"DriverBase": ["{(datetime.datetime.now() - datetime.timedelta(hours=7*23)).isoformat()}"]}}')
    def test_check_version_allowed_older_entry(self, mock_file):
        self.assertFalse(self.driver._check_driver_version_allowed())

    @patch("builtins.open", new_callable=mock_open, read_data=f'{{"DriverBase": ["{(datetime.datetime.now() - datetime.timedelta(hours=7*24)).isoformat()}"]}}')
    def test_check_version_allowed_old_entry(self, mock_file):
        self.assertTrue(self.driver._check_driver_version_allowed())

    @patch("builtins.open", new_callable=mock_open, read_data=f'{{"DriverBase": ["{(datetime.datetime.now() - datetime.timedelta(hours=7*25)).isoformat()}"]}}')
    def test_check_version_allowed_very_old_entry(self, mock_file):
        self.assertTrue(self.driver._check_driver_version_allowed())
