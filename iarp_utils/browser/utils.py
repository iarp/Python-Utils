import os
import re
import subprocess
import shutil
import time

from ..system import OSTypes


class ChromeType(object):
    GOOGLE = 'google-chrome'
    CHROMIUM = 'chromium'
    MSEDGE = 'edge'


def chrome_version(browser_type=ChromeType.GOOGLE):
    """ Obtain the version of Chrome being controlled.

    Code from:
        https://github.com/SergeyPirogov/webdriver_manager/blob/master/webdriver_manager/utils.py#L118

    Args:
        browser_type: google, chromium, msedge

    Returns:
        str containing version of chrome
    """
    cmd_mapping = {
        ChromeType.GOOGLE: {
            OSTypes.LINUX: [
                ['google-chrome', '--version'], ['google-chrome-stable', '--version'],
                ['chromium', '--version'], ['chromium-browser', '--version'],
            ],
            OSTypes.MAC: r'/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --version',
            OSTypes.WIN: r'reg query "HKEY_CURRENT_USER\Software\Google\Chrome\BLBeacon" /v version'
        },
        ChromeType.CHROMIUM: {
            OSTypes.LINUX: [
                ['chromium', '--version'], ['chromium-browser', '--version'],
            ],
            OSTypes.MAC: '/Applications/Chromium.app/Contents/MacOS/Chromium --version',
            OSTypes.WIN: r'reg query "HKEY_CURRENT_USER\Software\Chromium\BLBeacon" /v version'
        },
        ChromeType.MSEDGE: {
            OSTypes.MAC: r'/Applications/Microsoft\ Edge.app/Contents/MacOS/Microsoft\ Edge --version',
            OSTypes.WIN: r'reg query "HKEY_CURRENT_USER\SOFTWARE\Microsoft\Edge\BLBeacon" /v version',
        }
    }

    cmds = cmd_mapping[browser_type][OSTypes.active()]
    return _process_version_commands('Google Chrome', cmds)


def binary_file_version(binary, version_flag='--version'):
    return subprocess.check_output([binary, version_flag]).decode('utf-8').split(' ')[1]


def firefox_version():
    """ Obtain the version of Mozilla Firefox being controlled.

    Returns:
        str containing version of firefox
    """
    cmd_mapping = {
        OSTypes.WIN: [
            r'"C:\\Program Files (x86)\\Mozilla Firefox\\firefox.exe" --version',
            r'"C:\\Program Files\\Mozilla Firefox\\firefox.exe" --version'
        ],
        OSTypes.LINUX: [
            ['firefox', '--version'],
        ]
    }

    cmds = cmd_mapping.get(OSTypes.active())
    return _process_version_commands('Firefox', cmds, r'\d+\.\d+')


def _process_version_commands(name, cmds, pattern=r'\d+\.\d+\.\d+\.\d+|\d+\.\d+\.\d+'):

    if not cmds:
        raise ValueError(f'No command found for {name} version with os {OSTypes.active()}')

    if isinstance(cmds, str):
        cmds = [cmds]

    for cmd in cmds:
        try:
            stdout = subprocess.Popen(cmd, stdout=subprocess.PIPE).stdout.read()
            break
        except: # noqa
            pass
    else:
        raise ValueError(f'Could not get version for {name} with this command: {cmds}')

    version = re.search(pattern, stdout.decode('utf-8'))
    if not version:
        raise ValueError(f'Could not process version for {name} commands output: {cmds}')
    return version.group(0)


def save_working_profile_directory(driver, profile_storage_path):
    """ Saves the currently in-use browser profile directory to a custom location.

    Args:
        driver: The driver running the
        profile_storage_path: Where to save the profiles contents.
    """

    driver.browser.execute_script("window.close()")

    time.sleep(0.5)

    # Copy the profile directory (must be done BEFORE driver.quit()!)
    current_profile_path = driver.active_driver._get_active_profile_data_directory()

    assert os.path.isdir(current_profile_path)

    try:
        shutil.rmtree(profile_storage_path)
    except FileNotFoundError:
        pass

    shutil.copytree(
        src=current_profile_path,
        dst=profile_storage_path,
        ignore_dangling_symlinks=True
    )
