import datetime
import json
import logging
import os
import shutil
import tempfile

from ..datetimes import fromisoformat
from ..exceptions import ImproperlyConfigured
from ..files import download_file, extract_zip_single_file
from .utils import get_mime_types

try:
    from selenium import webdriver
    from selenium.webdriver.remote.webdriver import WebDriver as RemoteWebDriver
    from selenium.webdriver.firefox.options import Options as FirefoxOptions
except ImportError:
    webdriver = None

try:
    import requests
except ImportError:
    requests = None

# DEFAULT_DRIVER_ROOT is the folder where chromedriver.exe
#  or geckodriver.exe should be stored.
try:
    from django.conf import settings

    # If this is being used in a django installation, look for the path in settings
    # otherwise base the path on BASE_DIR.
    DEFAULT_DRIVER_ROOT = getattr(settings, 'BROWSER_DRIVER_DIR', None)
    if not DEFAULT_DRIVER_ROOT:
        DEFAULT_DRIVER_ROOT = os.path.join(settings.BASE_DIR, 'bin')

    WEBDRIVER_IN_PATH = getattr(settings, 'BROWSER_WEBDRIVER_IN_PATH', False)
    CHECK_DRIVER_VERSION = getattr(settings, 'BROWSER_CHECK_DRIVER_VERSION', True)
    CHECK_DRIVER_VERSION_INTERVAL = getattr(settings, 'BROWSER_CHECK_DRIVER_VERSION_INTERVAL', 24)
except:
    settings = None
    DEFAULT_DRIVER_ROOT = 'bin/'
    WEBDRIVER_IN_PATH = False
    CHECK_DRIVER_VERSION = True
    CHECK_DRIVER_VERSION_INTERVAL = 24


log = logging.getLogger('iarp_utils.browser')


def download_and_extract_zip_file(url, local_zip_file, extracting_file, **kwargs):

    download_file(url=url, path_to_file=local_zip_file)

    extract_zip_single_file(
        zip_file=local_zip_file,
        file_to_extract=extracting_file,
        folder_to_extract_to=DEFAULT_DRIVER_ROOT,
        log=log,
        **kwargs
    )


class DriverBase:

    def __init__(self, **kwargs):

        if webdriver is None:
            raise ImproperlyConfigured('selenium is required for iarp_utils.browser to operate. pip install selenium')
        if requests is None:
            raise ImproperlyConfigured('requests is required for iarp_utils.browser to operate. pip install requests')

        self.headless = kwargs.get('headless')
        self._download_directory = kwargs.get('download_directory')
        self.user_agent = kwargs.get('user_agent')
        self.latest_version = None
        self._browser = None

        # Whether or not we should check driver version before running the browser.
        self._check_driver_version = kwargs.get('check_driver_version', CHECK_DRIVER_VERSION)

        # How often (in hours) to check if the driver version needs updating
        self._check_driver_version_interval = kwargs.get('check_driver_version_interval', CHECK_DRIVER_VERSION_INTERVAL)

    @property
    def webdriver(self):
        raise NotImplementedError('webdriver property must be supplied')

    @property
    def driver(self):
        raise NotImplementedError('driver property must be supplied')

    @property
    def browser(self) -> RemoteWebDriver:
        return self._browser

    def get_options(self, **kwargs):

        if WEBDRIVER_IN_PATH:
            return kwargs

        try:
            binary = self._driver_binary_location(self.driver)
        except FileNotFoundError:
            # If the binary file could not be found, run a version check
            # which will download the latest by default.
            self.check_driver_version()
            binary = self._driver_binary_location(self.driver)

        kwargs.update({'executable_path': binary})
        return kwargs

    def start(self):
        # If start was already called, attempt to kill the existing session.
        self.quit()

        self._browser = self.webdriver(**self.get_options())

        if self._check_driver_version_allowed():
            self.check_driver_version()

        return self.browser

    def _check_driver_version_allowed(self):

        if not self._check_driver_version or WEBDRIVER_IN_PATH:
            return False

        dt_file = os.path.join(DEFAULT_DRIVER_ROOT, 'check_driver_version.json')
        driver_name = type(self).__name__

        try:
            with open(dt_file, 'r') as fo:
                data = json.load(fo)
        except (FileNotFoundError, json.decoder.JSONDecodeError):
            data = {driver_name: []}

        # By default, allow the version check to happen
        allowed = True

        if isinstance(data, dict) and data.get(driver_name):

            # Attempt to convert the first string in the list from isoformat
            # into datetime object for time comparison. In the event it fails
            # to convert, clear the data list and let it resave the file.
            try:
                last_checked = fromisoformat(data[driver_name][0])
                hours_ago = datetime.datetime.now() - datetime.timedelta(hours=self._check_driver_version_interval)
                allowed = hours_ago >= last_checked
            except (TypeError, ValueError, KeyError):
                data = {driver_name: []}

            # If check is not allowed to happen, return now as to prevent
            # another timestamp from being saved.
            if not allowed:
                return False

            # For future sake, only keep the last 50 checks.
            if len(data[driver_name]) > 50:
                data[driver_name] = data[driver_name][:50]

        if not data or not isinstance(data, dict):
            data = {}
        if driver_name not in data:
            data[driver_name] = {}

        data[driver_name].insert(0, datetime.datetime.now().isoformat())

        with open(dt_file, 'w') as fo:
            json.dump(data, fo, indent=4)

        return allowed

    def check_driver_version(self):
        raise NotImplementedError(f'{type(self).__name__} must implement check_driver_version method')

    def get_capabilities(self):
        return getattr(self._browser, 'capabilities', None)

    @staticmethod
    def _driver_binary_location(filename):
        """ Attempts to find the browsers required driver in one of several common places.

        Args:
            filename: The driver file to be found.

        Returns:
            A path to the file that was found.

        Raises:
            FileNotFoundError: If the driver was not found.
        """

        if os.path.isfile(os.path.join(DEFAULT_DRIVER_ROOT, filename)):
            return os.path.join(DEFAULT_DRIVER_ROOT, filename)

        for root in ['bin/', '', 'setup/', 'setup/bin/']:

            try:
                root_driver = os.path.join(settings.BASE_DIR, root, filename)
            except AttributeError:
                root_driver = os.path.join(root, filename)

            if os.path.isfile(root_driver):
                return root_driver

        raise FileNotFoundError('browser driver not found')

    def quit(self, **kwargs):
        self.delete_download_directory(**kwargs)
        try:
            self._browser.quit()
        except:
            pass

    @property
    def download_directory(self):
        """ Returns the path to the download directory. If no download_directory
        was supplied on DriveBase.__init__ then create one.

        Returns:
            string to directory path.
        """
        if not self._download_directory:
            self._download_directory = tempfile.mkdtemp()
        return self._download_directory

    def delete_download_directory(self, **kwargs):

        if not self._download_directory:
            return

        kwargs['ignore_errors'] = kwargs.get('ignore_errors', True)
        shutil.rmtree(self._download_directory, **kwargs)


class ChromeDriver(DriverBase):
    driver = 'chromedriver.exe'

    @property
    def webdriver(self):
        return webdriver.Chrome

    def get_options(self):
        chrome_options = webdriver.ChromeOptions()
        if self.headless:
            chrome_options.add_argument('--headless')

        if self.download_directory:
            chrome_options.add_experimental_option('prefs', {
                'download.default_directory': self.download_directory
            })

        # chrome_options.add_argument('--user-agent={}'.format(self.user_agent))

        return super().get_options(
            chrome_options=chrome_options
        )

    def get_browser_version(self):
        capabilities = self.get_capabilities()
        try:
            return capabilities['browserVersion'].split('.')[0]
        except (AttributeError, IndexError, KeyError, TypeError):
            return

    def get_driver_version(self):
        capabilities = self.get_capabilities()
        try:
            return capabilities['chrome']['chromedriverVersion'].split('.')[0]
        except (AttributeError, IndexError, KeyError, TypeError):
            return

    def check_driver_version(self):
        """ Check to ensure the local chromedriver being used is valid for the chrome installation. """

        if WEBDRIVER_IN_PATH:
            return

        root_url = 'https://chromedriver.storage.googleapis.com/'

        browser_version = self.get_browser_version()
        driver_version = self.get_driver_version()

        # If we obtained the browsers version and the driver version matches,
        # we don't need to check anything more.
        if browser_version and browser_version == driver_version:
            return

        url = f'{root_url}LATEST_RELEASE'
        if browser_version:
            url = f'{root_url}LATEST_RELEASE_{browser_version}'

        self.latest_version = requests.get(url).text.strip()

        self.quit()

        zip_file_name = 'chromedriver_win32.zip'
        try:
            local_zip_file = os.path.join(settings.CACHE_DIR, zip_file_name)
        except AttributeError:
            local_zip_file = zip_file_name

        download_and_extract_zip_file(
            url=f'{root_url}{self.latest_version}/{zip_file_name}',
            local_zip_file=local_zip_file,
            extracting_file='chromedriver.exe'
        )


class FirefoxDriver(DriverBase):
    driver = 'geckodriver.exe'

    @property
    def webdriver(self):
        return webdriver.Firefox

    def get_options(self):
        profile = webdriver.FirefoxProfile()
        profile.set_preference('browser.download.folderList', 2)
        profile.set_preference('pdfjs.disabled', True)

        if self.download_directory:
            profile.set_preference('browser.download.dir', self.download_directory)

        profile.set_preference("browser.helperApps.neverAsk.saveToDisk", get_mime_types())
        profile.set_preference('browser.helperApps.alwaysAsk.force', False)
        # profile.set_preference("general.useragent.override", self.user_agent)

        options = FirefoxOptions()
        options.headless = self.headless

        return super().get_options(
            options=options,
            firefox_profile=profile,
        )

    def check_driver_version(self):
        """ Check to ensure the local geckodriver being used is valid for the firefox installation. """

        if WEBDRIVER_IN_PATH:
            return

        capabilities = self.get_capabilities()

        if not self.latest_version:
            self.latest_version = requests.get('https://api.github.com/repos/mozilla/geckodriver/releases').json()[0]

        try:
            driver_version = capabilities['moz:geckodriverVersion']

            if self.latest_version['tag_name'][1:] == driver_version:
                return
        except (AttributeError, IndexError, KeyError, TypeError):
            pass

        for dl in self.latest_version.get('assets', []):
            if dl.get('content_type') == 'application/zip' and 'win64' in dl.get('browser_download_url', ''):
                break
        else:
            return

        self.quit()

        zip_file_name = dl['name']
        try:
            local_zip_file = os.path.join(settings.CACHE_DIR, zip_file_name)
        except AttributeError:
            local_zip_file = zip_file_name

        download_and_extract_zip_file(
            url=dl['browser_download_url'],
            local_zip_file=local_zip_file,
            extracting_file='geckodriver.exe'
        )
