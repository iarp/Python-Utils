import datetime
import unittest
from unittest.mock import patch, mock_open
from pathlib import Path

from iarp_utils.browser import utils
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

    @patch("builtins.open", new_callable=mock_open, read_data=f'{{"DriverBase": ["{(datetime.datetime.now() - datetime.timedelta(hours=23)).isoformat()}"]}}')
    def test_check_version_allowed_older_entry(self, mock_file):
        self.assertFalse(self.driver._check_driver_version_allowed())

    @patch("builtins.open", new_callable=mock_open, read_data=f'{{"DriverBase": ["{(datetime.datetime.now() - datetime.timedelta(hours=24)).isoformat()}"]}}')
    def test_check_version_allowed_old_entry(self, mock_file):
        self.assertTrue(self.driver._check_driver_version_allowed())

    @patch("builtins.open", new_callable=mock_open, read_data=f'{{"DriverBase": ["{(datetime.datetime.now() - datetime.timedelta(hours=25)).isoformat()}"]}}')
    def test_check_version_allowed_very_old_entry(self, mock_file):
        self.assertTrue(self.driver._check_driver_version_allowed())

    def test_webdriver_base_raises_notimplementederror(self):
        with self.assertRaises(NotImplementedError):
            tmp = self.driver.webdriver

    def test_driver_base_raises_notimplementederror(self):
        with self.assertRaises(NotImplementedError):
            tmp = self.driver.driver

    def test_driver_webbrowser_is_none_by_default(self):
        self.assertIsNone(self.driver.browser)


class BrowserUtilsTests(unittest.TestCase):

    def test_firefox_process_version_commands_output(self):
        expected = '94.0'
        agent = f'Mozilla Firefox {expected}\n'
        version = utils._process_commands_output(agent, r'(\d+.\d+)')
        self.assertIsNotNone(version)
        self.assertEqual(expected, version.group(0))

    def test_chrome_process_version_commands_output(self):
        expected = '97.0.4692'
        agent = "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, " \
                f"like Gecko) Chrome/{expected} Safari/537.36"
        version = utils._process_commands_output(agent, r'\d+\.\d+\.\d+')
        self.assertIsNotNone(version)
        self.assertEqual(expected, version.group(0))
