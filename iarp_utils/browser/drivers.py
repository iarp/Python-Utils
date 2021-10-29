import datetime
import json
import logging
import os
import shutil
import tarfile
import tempfile
import warnings
import zipfile

from ..datetimes import fromisoformat
from ..exceptions import ImproperlyConfigured
from ..files import (
    download_file,
    extract_tar_single_file,
    extract_zip_single_file,
    get_mime_types_as_str,
)
from ..system import IS_WINDOWS_OS, get_system_bitness
from . import utils


try:
    from selenium import webdriver
    from selenium.webdriver.remote.webdriver import (
        WebDriver as RemoteWebDriver,
    )
except ImportError:
    webdriver = None

try:
    import requests
except ImportError:
    requests = None

try:
    from django.conf import settings

    # If this is being used in a django installation, look for the path in settings
    # otherwise base the path on BASE_DIR.
    DEFAULT_DRIVER_ROOT = getattr(settings, 'BROWSER_DRIVER_DIR', None)
    if not DEFAULT_DRIVER_ROOT:
        DEFAULT_DRIVER_ROOT = os.path.join(settings.BASE_DIR, 'bin')

    DEFAULT_HEADLESS = getattr(settings, 'BROWSER_HEADLESS', None)
    DEFAULT_DOWNLOAD_DIRECTORY = getattr(settings, 'BROWSER_DEFAULT_DOWNLOAD_DIRECTORY', None)

    WEBDRIVER_IN_PATH = getattr(settings, 'BROWSER_WEBDRIVER_IN_PATH', False)
    CHECK_DRIVER_VERSION = getattr(settings, 'BROWSER_CHECK_DRIVER_VERSION', True)
    CHECK_DRIVER_VERSION_INTERVAL = getattr(settings, 'BROWSER_CHECK_DRIVER_VERSION_INTERVAL', 24)
    USER_AGENT = getattr(settings, 'BROWSER_USER_AGENT', None)
except: # noqa
    settings = None
    DEFAULT_DRIVER_ROOT = os.environ.get('BROWSER_DRIVER_DIR', 'bin/')
    WEBDRIVER_IN_PATH = os.environ.get('BROWSER_WEBDRIVER_IN_PATH', False)
    CHECK_DRIVER_VERSION = os.environ.get('BROWSER_CHECK_DRIVER_VERSION', True)
    CHECK_DRIVER_VERSION_INTERVAL = os.environ.get('BROWSER_CHECK_DRIVER_VERSION_INTERVAL', 24)
    USER_AGENT = os.environ.get('BROWSER_USER_AGENT', None)
    DEFAULT_HEADLESS = os.environ.get('BROWSER_HEADLESS', None)
    DEFAULT_DOWNLOAD_DIRECTORY = os.environ.get('BROWSER_DEFAULT_DOWNLOAD_DIRECTORY', None)


log = logging.getLogger('iarp_utils.browser.drivers')


def download_and_extract_zip_file(url, local_zip_file, extracting_file, **kwargs):

    download_file(url=url, path_to_file=local_zip_file)

    if zipfile.is_zipfile(local_zip_file):

        extract_zip_single_file(
            zip_file=local_zip_file,
            file_to_extract=extracting_file,
            folder_to_extract_to=DEFAULT_DRIVER_ROOT,
            log=log,
            **kwargs
        )

    elif tarfile.is_tarfile(local_zip_file):
        extract_tar_single_file(
            tar_file=local_zip_file,
            file_to_extract=extracting_file,
            folder_to_extract_to=DEFAULT_DRIVER_ROOT,
            log=log,
            **kwargs
        )

    else:
        raise ValueError(f'File {local_zip_file} is not compatible with zipfile or tarfile libraries.')


class DriverBase:

    def __init__(self, **kwargs):

        if webdriver is None:
            raise ImproperlyConfigured('selenium is required for iarp_utils.browser to operate. pip install selenium')

        self.headless = kwargs.get('headless', DEFAULT_HEADLESS)
        self._download_directory = kwargs.get('download_directory', DEFAULT_DOWNLOAD_DIRECTORY)
        self.user_agent = kwargs.get('user_agent', USER_AGENT)
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
        """ Returns a dict ready for driver initialization, base locates the driver.

        Args:
            **kwargs: other keyword params to pass

        Returns:
            dict
        """

        if WEBDRIVER_IN_PATH:
            return kwargs

        try:
            binary = self.binary_location()
        except FileNotFoundError:
            # If the binary file could not be found, run a version check
            # which will download the latest by default.
            self.check_driver_version()
            binary = self.binary_location()

        kwargs.update({'executable_path': binary})
        return kwargs

    def start(self):
        """ Starts the driver and browser with all options. """
        # If start was already called, attempt to kill the existing session.
        self.quit()

        if self._check_driver_version_allowed():
            self.check_driver_version()

        options = self.get_options()
        self._browser = self.webdriver(**options)

        return self.browser

    def _check_driver_version_allowed(self):

        if not self._check_driver_version:
            log.debug('webdriver check: not checking due to check_driver_version=False')
            return False

        if WEBDRIVER_IN_PATH:
            log.debug('webdriver check: not checking due to WEBDRIVER_IN_PATH=True')
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

                # If check is not allowed to happen, return now as to prevent
                # another timestamp from being saved.
                if not allowed:
                    tmp = datetime.datetime.now() - last_checked
                    hours = tmp.days * 24 + tmp.seconds // 3600
                    minutes = (tmp.seconds % 3600) // 60
                    log.debug(f'webdriver check: not allowed due to {self._check_driver_version_interval}hr check '
                              f'interval: {hours}hr {minutes}min since last check')
                    return False

            except (TypeError, ValueError, KeyError):
                data = {driver_name: []}

            # For future sake, only keep the last 50 checks.
            if len(data[driver_name]) > 50:
                data[driver_name] = data[driver_name][:50]

        if not data or not isinstance(data, dict):
            data = {}
        if driver_name not in data:
            data[driver_name] = []

        data[driver_name].insert(0, datetime.datetime.now().isoformat())

        # 2021-01-12: make sure directory exists...
        os.makedirs(os.path.dirname(dt_file), exist_ok=True)

        with open(dt_file, 'w') as fo:
            json.dump(data, fo, indent=4)

        return allowed

    def check_driver_version(self):
        """ Called just before driver initialization and intended
        to be used to determine if a driver is installed and up to date.

        Must be overridden by child class"""
        pass

    def get_capabilities(self):
        return getattr(self._browser, 'capabilities', None)

    def binary_location(self):
        """ Attempts to find the browsers required driver in one of several common places.

        Returns:
            A path to the file that was found.

        Raises:
            FileNotFoundError: If the driver was not found.
        """

        filename = self.driver

        root_driver = os.path.join(DEFAULT_DRIVER_ROOT, filename)
        if os.path.isfile(root_driver):
            log.debug(f'{self.__class__.__name__} binary located at default {root_driver}')
            return root_driver

        for root in ['bin/', '', 'setup/', 'setup/bin/']:

            try:
                root_driver = os.path.join(settings.BASE_DIR, root, filename)
            except AttributeError:
                root_driver = os.path.join(root, filename)

            if os.path.isfile(root_driver):
                log.debug(f'{self.__class__.__name__} binary located at {root_driver}')
                return root_driver

        log.debug(f'{self.__class__.__name__} binary not found anywhere')
        raise FileNotFoundError('browser driver not found')

    def quit(self, **kwargs):
        """ Cleanup and close the driver"""
        self.delete_download_directory(**kwargs)
        try:
            self._browser.quit()
        except: # noqa
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

    def delete_download_directory(self, ignore_errors=True, **kwargs):
        if self._download_directory:
            shutil.rmtree(self._download_directory, ignore_errors=ignore_errors, **kwargs)

    def get_driver_version(self):
        binary = self.binary_location()
        version = utils.binary_file_version(binary)
        log.debug(f'{self.__class__.__name__} binary version: found {version}')
        return version


class ChromeDriver(DriverBase):
    webdriver = webdriver.Chrome
    driver = 'chromedriver.exe' if IS_WINDOWS_OS else 'chromedriver'

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        if self.headless and not self.user_agent:
            # Headless Chrome sends a user agent telling the website its headless. Lets override that.
            self.user_agent = f'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 ' \
                              f'(KHTML, like Gecko) Chrome/{utils.chrome_version()} Safari/537.36'

    def get_options(self):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.headless = self.headless

        if self.download_directory:
            chrome_options.add_experimental_option('prefs', {
                'download.default_directory': self.download_directory
            })

        if self.user_agent:
            chrome_options.add_argument(f'--user-agent={self.user_agent}')

        return super().get_options(options=chrome_options)

    def get_browser_version(self):
        capabilities = self.get_capabilities()
        try:
            version = capabilities['browserVersion'].split('.')[0]
        except (AttributeError, IndexError, KeyError, TypeError):
            version = utils.chrome_version()
        log.debug(f'{self.__class__.__name__} browser version: {version}')
        return version

    def get_driver_version(self):
        try:
            version = super().get_driver_version()
        except FileNotFoundError:
            try:
                capabilities = self.get_capabilities()
                version = capabilities['chrome']['chromedriverVersion'].split('.')[0]
            except (AttributeError, IndexError, KeyError, TypeError):
                version = None
        log.debug(f'{self.__class__.__name__} driver version: {version}')
        return version

    def check_driver_version(self):
        """ Check to ensure the local chromedriver being used is valid for the chrome installation. """

        if WEBDRIVER_IN_PATH:
            log.debug(f'{self.__class__.__name__} version checks: not checking due to WEBDRIVER_IN_PATH=True')
            return
        if not requests:
            log.debug(f'{self.__class__.__name__} version checks: not checking due to requests not being installed.')
            warnings.warn('requests not installed. Required to auto-download browser driver. "pip install requests"',
                          ImportWarning)
            return

        root_url = 'https://chromedriver.storage.googleapis.com/'

        browser_version = self.get_browser_version()
        driver_version = self.get_driver_version()

        try:
            browser_version_major = browser_version.split('.')[0]
        except (AttributeError, IndexError):
            browser_version_major = None

        try:
            driver_version_major = driver_version.split('.')[0]
        except (AttributeError, IndexError):
            driver_version_major = None

        log.debug(f'{self.__class__.__name__} version check: browser: '
                  f'{browser_version} driver: {driver_version}')

        majors_matching = browser_version_major and browser_version_major == driver_version_major

        # If we obtained the browsers version and the driver version matches,
        # we don't need to check anything more.
        if majors_matching:
            return

        url = f'{root_url}LATEST_RELEASE'
        if browser_version_major:
            url = f'{root_url}LATEST_RELEASE_{browser_version_major}'

        log.debug(f'{self.__class__.__name__} version check: requesting {url}')
        self.latest_version = requests.get(url).text.strip()
        log.debug(f'{self.__class__.__name__} version check: latest found {self.latest_version}')

        self.quit()

        if IS_WINDOWS_OS:
            zip_file_name = 'chromedriver_win32.zip'
        else:
            zip_file_name = 'chromedriver_linux64.zip'

        try:
            local_zip_file = os.path.join(settings.CACHE_DIR, zip_file_name)
        except AttributeError:
            local_zip_file = zip_file_name

        file_url = f'{root_url}{self.latest_version}/{zip_file_name}'
        log.debug(f'{self.__class__.__name__} version check: downloading {file_url}')
        log.debug(f'{self.__class__.__name__} version check: to {local_zip_file} extracting '
                  f'{self.driver} to {DEFAULT_DRIVER_ROOT}')

        download_and_extract_zip_file(
            url=file_url,
            local_zip_file=local_zip_file,
            extracting_file=self.driver
        )


class FirefoxDriver(DriverBase):
    driver = 'geckodriver.exe' if IS_WINDOWS_OS else 'geckodriver'
    webdriver = webdriver.Firefox

    def get_options(self):
        profile = webdriver.FirefoxProfile()

        if self.download_directory:
            profile.set_preference('browser.download.folderList', 2)
            profile.set_preference('pdfjs.disabled', True)
            profile.set_preference('browser.download.dir', self.download_directory)
            profile.set_preference("browser.helperApps.neverAsk.saveToDisk", get_mime_types_as_str(joiner=','))
            profile.set_preference('browser.helperApps.alwaysAsk.force', False)

        if self.user_agent:
            profile.set_preference("general.useragent.override", self.user_agent)

        options = webdriver.FirefoxOptions()
        options.headless = self.headless

        return super().get_options(options=options, firefox_profile=profile)

    def get_driver_version(self):
        try:
            version = super().get_driver_version()
        except FileNotFoundError:
            try:
                capabilities = self.get_capabilities()
                version = capabilities['moz:geckodriverVersion'].split('.')[0]
                log.debug(f'FirefoxDriver driver version: found {version}')
            except (AttributeError, IndexError, KeyError, TypeError):
                version = None
        return version

    def check_driver_version(self):
        """ Check to ensure the local geckodriver being used is valid for the firefox installation. """

        if WEBDRIVER_IN_PATH:
            log.debug('FirefoxDriver version checks: not checking due to WEBDRIVER_IN_PATH=True')
            return
        if not requests:
            log.debug('FirefoxDriver version checks: not checking due to requests not being installed.')
            warnings.warn('requests not installed. Required to auto-download browser driver. "pip install requests"',
                          ImportWarning)
            return

        if not self.latest_version:
            url = 'https://api.github.com/repos/mozilla/geckodriver/releases'
            log.debug(f'FirefoxDriver version check: requesting {url}')
            self.latest_version = requests.get(url).json()[0]
            log.debug(f"FirefoxDriver version check: latest version {self.latest_version['tag_name']}")

        driver_version = self.get_driver_version()

        try:
            if self.latest_version['tag_name'].replace('v', '') == driver_version:
                log.debug(f'FirefoxDriver version check: latest version '
                          f'already matches located driver {driver_version}')
                return
        except (AttributeError, IndexError, KeyError, TypeError):
            pass

        BITNESS = get_system_bitness()
        val_checker = f'win{BITNESS}' if IS_WINDOWS_OS else f'linux{BITNESS}'
        wanted_file_types = [
            'application/zip',      # Windows
            'application/x-gzip'    # Linux
        ]
        for dl in self.latest_version.get('assets', []):
            if dl.get('content_type') in wanted_file_types and val_checker in dl.get('browser_download_url', ''):
                log.debug(f'FirefoxDriver version check: found latest version from url for {val_checker}')
                break
        else:
            log.debug(f'FirefoxDriver version check: failed to find latest version from url for {val_checker}')
            return

        self.quit()

        zip_file_name = dl['name']
        try:
            local_zip_file = os.path.join(settings.CACHE_DIR, zip_file_name)
        except AttributeError:
            local_zip_file = zip_file_name

        file_url = dl['browser_download_url']
        log.debug(f'FirefoxDriver version check: downloading {file_url}')
        log.debug(f'FirefoxDriver version check: to {local_zip_file} extracting '
                  f'{self.driver} to {DEFAULT_DRIVER_ROOT}')

        download_and_extract_zip_file(
            url=file_url,
            local_zip_file=local_zip_file,
            extracting_file=self.driver
        )
