import re
import subprocess
import sys
import os

from ..system import OSTypes, os_name


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
    pattern = r'\d+\.\d+\.\d+'

    cmd_mapping = {
        ChromeType.GOOGLE: {
            OSTypes.LINUX: 'google-chrome --version || google-chrome-stable --version',
            OSTypes.MAC: r'/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --version',
            OSTypes.WIN: r'reg query "HKEY_CURRENT_USER\Software\Google\Chrome\BLBeacon" /v version'
        },
        ChromeType.CHROMIUM: {
            OSTypes.LINUX: 'chromium --version || chromium-browser --version',
            OSTypes.MAC: r'/Applications/Chromium.app/Contents/MacOS/Chromium --version',
            OSTypes.WIN: r'reg query "HKEY_CURRENT_USER\Software\Chromium\BLBeacon" /v version'
        },
        ChromeType.MSEDGE: {
            OSTypes.MAC: r'/Applications/Microsoft\ Edge.app/Contents/MacOS/Microsoft\ Edge --version',
            OSTypes.WIN: r'reg query "HKEY_CURRENT_USER\SOFTWARE\Microsoft\Edge\BLBeacon" /v version',
        }
    }

    cmd = cmd_mapping[browser_type][os_name()]
    stdout = subprocess.check_output(cmd).decode('utf-8')
    version = re.search(pattern, stdout)
    if not version:
        raise ValueError(f'Could not get version for Chrome with this command: {cmd}')
    current_version = version.group(0)
    return current_version


def binary_file_version(binary, version_flag='--version'):
    return subprocess.check_output([binary, version_flag]).decode('utf-8').split(' ')[1]


def firefox_version(browser_type=ChromeType.GOOGLE):
    """ Obtain the version of Mozilla Firefox being controlled.

    Args:
        browser_type: google, chromium, msedge

    Returns:
        str containing version of chrome
    """
    pattern = r'\d+\.\d+\.\d+'

    cmd_mapping = {
        ChromeType.GOOGLE: {
            OSTypes.WIN: [
                r'"C:\\Program Files (x86)\\Mozilla Firefox\\firefox.exe" --version',
                r'"C:\\Program Files\\Mozilla Firefox\\firefox.exe" --version'
            ]
        },
    }

    cmd = cmd_mapping.get(browser_type, {}).get(os_name())

    if not cmd:
        raise ValueError(f'No command found for {browser_type} with os {os_name()}')

    stdout = None
    if isinstance(cmd, list):
        for cmd in cmd.copy():
            try:
                stdout = subprocess.check_output(cmd)
            except:
                pass
    else:
        stdout = subprocess.check_output(cmd)

    if not stdout:
        raise ValueError(f'Could not get version for Mozilla Firefox with this command: {cmd}')

    version = re.search(pattern, stdout.decode('utf-8'))
    if not version:
        raise ValueError(f'Could not process version for Mozilla Firefox commands output: {cmd}')
    current_version = version.group(0)
    return current_version
