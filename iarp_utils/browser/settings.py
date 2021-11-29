import os

from ..system import import_attribute


try:
    from django.conf import settings as _django_settings
except: # noqa
    _django_settings = None


class Settings(object):

    def _setting(self, name, default=None):
        name = f'BROWSER_{name}'
        try:
            return getattr(_django_settings, name)
        except: # noqa
            pass
        return os.environ.get(name, default)

    @property
    def DEFAULT_DRIVER(self):
        return import_attribute(self._setting('DEFAULT_DRIVER', 'iarp_utils.browser.drivers.FirefoxDriver'))

    @property
    def EXECUTABLE_ROOT(self):
        exe = self._setting('DRIVER_DIR')
        if not exe:
            exe = self._setting('EXECUTABLE_ROOT')
        return exe or 'bin/'

    @property
    def WEBDRIVER_IN_PATH(self):
        return bool(self._setting('WEBDRIVER_IN_PATH', False))

    @property
    def CHECK_DRIVER_VERSION(self):
        return bool(self._setting('CHECK_DRIVER_VERSION', True))

    @property
    def CHECK_DRIVER_VERSION_INTERVAL(self):
        return int(self._setting('CHECK_DRIVER_VERSION_INTERVAL', 24))

    @property
    def USER_AGENT(self):
        return self._setting('USER_AGENT')

    @property
    def DOWNLOAD_DIRECTORY(self):
        return self._setting('DOWNLOAD_DIRECTORY')

    @property
    def HEADLESS(self):
        return bool(self._setting('BROWSER_HEADLESS'))


settings = Settings()
