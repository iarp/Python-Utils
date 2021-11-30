import datetime
import logging
import os
import time
import warnings
from pathlib import Path

from ..exceptions import ImproperlyConfigured
from ..pidfile import PIDFile
from .drivers import ChromeDriver, DriverBase, FirefoxDriver
from .exceptions import LoginFailureException
from .settings import settings


try:
    from selenium.common.exceptions import (
        NoSuchElementException,
        SessionNotCreatedException,
    )
    from selenium.webdriver.common.action_chains import ActionChains
    from selenium.webdriver.common.by import By
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.remote.webdriver import WebDriver
    from selenium.webdriver.support import expected_conditions
    from selenium.webdriver.support.ui import Select, WebDriverWait
except ImportError:  # pragma: no cover
    WebDriver = None

    class By:
        NAME = None
        ID = None

log = logging.getLogger('iarp_utils.browser.browsers')


class Browser:
    """ Base browser methods that apply to all browsers.

    Inherit BrowserBase within your own class and override the `def initialize(self):` method, add
        whatever you need to whenever you start this browser. For example, I would start the browser, login,
        and then click a menu item. The reason is there was never a time whenever I login and not
        HAVE to click on that menu item.

    # An example of a browser:

        class GitHubBrowser(BrowserBase):

            url_login = 'https://github.com/login'

            def initialize(self):
                self.load_url(self.url_login)

                self.login(
                    username='my-username',
                    password='my-password',
                    username_element_attr=By.NAME,
                    username_element_attr_value='login',
                    password_element_attr=By.NAME,
                    password_element_attr_value='password'
                )


    The purpose behind execute_initialize:
        I needed a way to check that the login credentials provided are correct BUT I didn't want the
        entirety of the override initialize method to be executed. So I ended up creating another
        method called check_login and then use the following code:

            try:
                br = CustomBrowser(headless=True, execute_initialize=False)
                br.initialize(login_check=True)
                return True
            except:
                return False

    The code above would when login but NOT execute the rest of my initialize code, only the necessary
        stuff to ensure the login credentials work.

    """

    def __init__(self, start_browser=True, global_wait=0, execute_initialize=True,
                 selected_driver=None, **kwargs):
        """
        Args:
            start_browser: Boolean if we should start the browser immediately. If you pass False,
                            you must call .start_browser() yourself when you're ready.
            global_wait: An integer of how many seconds to wait between each call to the browser.
            execute_initialize: Boolean if we should call the inheriting classes initialize method upon start_browser()
            selected_driver: class extended from DriverBase, see iarp_utils.drivers.
            kwargs: passed onto the Driver class.
        """

        if WebDriver is None:
            raise ImproperlyConfigured(f'selenium is required for {type(self).__name__}. '
                                       f'Use pip install iarp_utils[browser]')

        self.global_wait = global_wait
        self._execute_initialize = execute_initialize
        self.browser = None  # type: WebDriver
        self.selected_driver_kwargs = kwargs
        self.active_driver = None  # type: DriverBase

        self.selected_driver = selected_driver or settings.DEFAULT_DRIVER

        if start_browser:
            self.start_browser()

    def is_browser_started(self):
        return self.browser

    def initialize(self):
        """ Method meant to be overridden by classes inheriting BrowserBase.

        Execute whatever calls are needed whenever you first open the browser. i.e. load the login page,
            login, click control panel or something along those lines.
        """
        pass

    def start_browser(self):

        self.browser = self._start_driver()

        if self._execute_initialize:
            self.initialize()

    def swap_headless_state(self):
        """ Swaps the current session to/from headless state.

        cookies are only copied for the currently loaded domain.
        """
        cookies = self.browser.get_cookies()
        current_url = self.browser.current_url

        is_currently_headless = self.selected_driver_kwargs.get('headless')
        current_user_agent = self.selected_driver_kwargs.get('user_agent')

        # If the current driver is NOT headless, copy the current user agent.
        # Many sites require it to match with cookies for security reasons.
        if not is_currently_headless:
            current_user_agent = self.browser.execute_script("return navigator.userAgent;")

        self.quit()
        self.selected_driver_kwargs['headless'] = not is_currently_headless  # flip/flop setting
        self.selected_driver_kwargs['user_agent'] = current_user_agent
        self.start_browser()
        self.load_url(current_url)
        self.browser.delete_all_cookies()
        for cookie in cookies:
            self.browser.add_cookie(cookie)
        self._wait(2)
        self.load_url(current_url)

    @property
    def download_directory(self):
        try:
            return self.active_driver.download_directory
        except AttributeError:
            pass

    def _start_driver(self):

        log.debug(f'browser selected driver: {self.selected_driver.__name__}')

        self.active_driver = self.selected_driver(**self.selected_driver_kwargs)

        try:
            return self.active_driver.start()
        except SessionNotCreatedException:
            # SessionNotCreatedException typically means mismatching browser and driver version
            log.critical('browser failed to start driver with SessionNotCreatedException')

            # Only allow 1 browser version checker to be running at a time.
            with PIDFile('browser_version_checker') as good:

                if not good:
                    log.critical('browser failed to retry as another process is already checking')
                    raise PIDFile.Break

                log.debug('browser force checking driver')
                self.active_driver.check_driver_version()

            log.debug('browser attempting to start driver again')

            # Attempt to restart the browser
            try:
                return self.active_driver.start()
            except SessionNotCreatedException:
                log.exception('browser failed to start driver again, stopping execution')
                self.quit()
                raise

    def load_url(self, url):
        self.browser.get(url)

    def get_types(self, element_name=None, element_id=None, element_class=None, element_xpath=None):
        """ Matches the correct By. values for the given element_* param

        Argument values must match 100% (no contains searching)

        Args:
            element_name: the name="" value of the element
            element_id: the id="" value of the element
            element_class: the class="" value of the element
            element_xpath: Google xpath searching

        Returns:
            tuple of By.TYPE, element_* value given

        Raises:
            ValueError: If no param given has a value
        """

        if self.global_wait:
            self._wait()

        if element_id:
            return By.ID, element_id
        if element_name:
            return By.NAME, element_name
        if element_class:
            return By.CLASS_NAME, element_class
        if element_xpath:
            return By.XPATH, element_xpath

        raise ValueError('element id, name, class, or xpath must be supplied')

    def get_element(self, *args, **kwargs):
        """ Obtain an element

        Args:

            element_name: the name="" value of the element
            element_id: the id="" value of the element
            element_class: the class="" value of the element
            element_xpath: Google xpath searching

        Returns:
            WebElement: The element object

        Raises:
            NoSuchElementException
        :rtype WebElement
        """
        find_by, find_value = self.get_types(*args, **kwargs)
        log.debug(f'browser get_element By.{find_by}, Value:{find_value}')
        return self.browser.find_element(by=find_by, value=find_value)

    def fill_input_element(self, value, *args, **kwargs):
        warnings.warn("fill_input_element is deprecated. Use fill_element instead.", DeprecationWarning)
        return self.fill_element(value, *args, **kwargs)

    def fill_element(self, value, *args, **kwargs):
        """Finds an element and fills it in using value given.

        Args::

            value: The value to fill into the element

            # And one of the following:
            element_name: the name="" value of the element
            element_id: the id="" value of the element
            element_class: the class="" value of the element
            element_xpath: Google xpath searching

        Raises:
            NoSuchElementException: If the element was not foun
        """
        elem = self.get_element(*args, **kwargs)
        elem.clear()
        elem.send_keys(Keys.HOME + str(value))
        return elem

    def double_click_element(self, *args, **kwargs):
        elem = self.get_element(*args, **kwargs)
        self.action_chains.double_click(elem).perform()
        return elem

    def select_dropdown(self, value=None, text=None, index=None, *args, **kwargs):
        """ Find and select a specific option element

         Args:

             # Only one of the following

             value: value="" of option element
             text: Displayed text of option element
             index: Index of the option element

             # And one of the following:
             element_name: the name="" value of the element
             element_id: the id="" value of the element
             element_class: the class="" value of the element
             element_xpath: Google xpath searching

        Returns:
            Select element object

        Raises:
            NoSuchElementException: if the select option doesn't exist

        """
        sel = Select(self.get_element(*args, **kwargs))

        if text:
            sel.select_by_visible_text(text)
        elif value:
            sel.select_by_value(value)
        elif index:
            sel.select_by_index(index)

        return sel

    def wait_until(self, max_wait_in_seconds=30, wait_until_invisible=False, *args, **kwargs):
        """ Continuously checks the browser for a specific element to be present which signifies the page has loaded.

        Args:

             max_wait_in_seconds: How long to wait, in seconds.
             wait_until_invisible: Whether or not to wait for invisible fields to become visible.

             And one of the following:
             element_name: the name="" value of the element
             element_id: the id="" value of the element
             element_class: the class="" value of the element
             element_xpath: Google xpath searching

        Raises:
            TimeoutException: If the timeout is reached and the element still doesn't exist.

        """
        find_by, find_value = self.get_types(*args, **kwargs)

        func = expected_conditions.visibility_of_element_located
        if wait_until_invisible:
            func = expected_conditions.invisibility_of_element_located
        return WebDriverWait(self.browser, max_wait_in_seconds).until(func((find_by, find_value)))

    def element_exists(self, *args, **kwargs):
        """ Does the element given exist?

        Args:
            element_name: the name="" value of the element
            element_id: the id="" value of the element
            element_class: the class="" value of the element
            element_xpath: Google xpath searching

        Returns:
            bool if the element_* given exists
        """
        find_by, find_value = self.get_types(*args, **kwargs)
        try:
            return self.browser.find_element(find_by, find_value)
        except NoSuchElementException:
            return False

    def quit(self):
        """ Clears/Removes the temporary folder and then closes the browser session. """
        try:
            self.active_driver.quit()
        except AttributeError:
            pass

    def login(self, username, password, username_element_attr_value, password_element_attr_value,
              username_element_attr=By.NAME, password_element_attr=By.NAME,
              check_attempts=5, check_wait_seconds=2, split_element_screens=False):
        """ Base login method used by multiple browsers, based on login screens with with
                username and password fields displayed on a single screen.

        The *_element_attr_* params indicate the elements attribute to target and the value of that attribute.
            Such as name="username" is:
                username_element_attr=By.NAME
                username_element_attr_value='username'

        Args:
            username: The username to login with
            password: The password to login with
            username_element_attr: The type attribute for the username element. (i.e. type="...")
            password_element_attr: The type attribute for the password element. (i.e. type="...")
            username_element_attr_value: The value for the attribute supplied to find the username element.
            password_element_attr_value: The value for the attribute supplied to find the password element.
            check_attempts: How many times to check for a username element to check if the login failed.
            check_wait_seconds: How many seconds to wait between checks for login failure.
            split_element_screens: Are username/password inputs on separate screens and we need to wait?

        Raises:
            NoSuchElementException: If username or password elements are not found.
            LoginFailureException: determined by the username element still existing after submission.
        """

        if password_element_attr == By.CLASS_NAME:
            password_element_attr = 'class'
        if username_element_attr == By.CLASS_NAME:
            username_element_attr = 'class'

        username_element = self.wait_until(**{
            f'element_{username_element_attr}': username_element_attr_value
        })
        username_element.send_keys(username)

        if split_element_screens:
            username_element.send_keys(Keys.ENTER)

        password_element = self.wait_until(**{
            f'element_{password_element_attr}': password_element_attr_value
        })
        password_element.send_keys(password + Keys.RETURN)

        # Re-check for the username element, if NoSuchElementException is thrown then we're then likely logged in.
        checks = 0
        while checks <= check_attempts:
            checks += 1

            try:
                if split_element_screens:
                    self.browser.find_element(password_element_attr, password_element_attr_value)
                else:
                    self.browser.find_element(username_element_attr, username_element_attr_value)
            except NoSuchElementException:
                break

            self._wait(check_wait_seconds)
        else:
            self.quit()
            raise LoginFailureException('Login failure, check username and password')

    def save_screenshot(self, filename=None, filename_prefix='', save_dir=None, sub_folder='', notes=None):

        save_dir = Path(os.path.join(save_dir or '', sub_folder))
        save_dir.mkdir(parents=True, exist_ok=True)

        if not filename:
            filename = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')

        file = save_dir / f'{filename_prefix}{filename}.png'

        self.browser.save_screenshot(str(file))

        if notes:
            with open(f'{file}.txt', 'w') as fw:
                fw.write(notes)

        return file

    @property
    def action_chains(self):
        return ActionChains(self.browser)

    def _wait(self, seconds=None):
        """ Used to add delay in certain actions

        Args:
            seconds: how many seconds to wait?
        """
        time.sleep(seconds or self.global_wait)


class BrowserBase(Browser):
    def __init__(self, *args, **kwargs):
        warnings.warn('BrowserBase is deprecated, use Browser instead.', DeprecationWarning, stacklevel=2)
        super().__init__(*args, **kwargs)


class FirefoxBrowser(Browser):
    """
        BrowserBase preconfigured to run as Firefox browser.
    """
    def __init__(self, *args, **kwargs):
        kwargs['selected_driver'] = FirefoxDriver
        super().__init__(*args, **kwargs)


class ChromeBrowser(Browser):
    """
        BrowserBase preconfigured to run as Chrome browser.
    """
    def __init__(self, *args, **kwargs):
        kwargs['selected_driver'] = ChromeDriver
        super().__init__(*args, **kwargs)
