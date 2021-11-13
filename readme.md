# IARP Python Utilities

A collection of utilities I use a lot throughout many projects.

I only work with Python 3.6 and 3.7 currently, as such these may not work in
previous versions. Most notably due to f-strings.

## Installation

    pip install -e git+https://github.com/iarp/Python-Utils.git#egg=iarp_utils

## Documentation

Every file and function is commented about what it does, how and when to use
it along with examples. Have a question? Open an issue.


## Browser Settings

If django is installed and configured, place these settings into your projects settings.py
Otherwise add them to `os.environ.setdefault('option name here', '')`

* `BROWSER_DEFAULT_DRIVER` (="iarp_utils.browser.drivers.ChromeDriver")
  * Default browser driver to use as noted below:
    * ChromeDriver
    * FirefoxDriver

* `BROWSER_DRIVER_DIR` (="bin/")
  * Specifies the default location to find webdrivers

* `BROWSER_HEADLESS` (=False)
  * Should the browser run in headless mode by default?
  * WARNING: Chrome and Firefox require this setting to be literal True or False, not 1, 0, None. True or False only. 

* `BROWSER_DEFAULT_DOWNLOAD_DIRECTORY` (=tempfile.mkdtemp())
  * Directory to use as the download target

* `BROWSER_WEBDRIVER_IN_PATH` (=False)
  * Will the driver be found in PATH?

* `BROWSER_CHECK_DRIVER_VERSION` (=True)
  * Should the system check for driver updates if available?
  * Currently, it can auto update chromedriver and geckodriver

* `BROWSER_CHECK_DRIVER_VERSION_INTERVAL` (=24)
  * How often to check for driver updates
  * Time is in hours.

* `BROWSER_USER_AGENT`
  * User agent string to apply to the browser
