import logging
import re
import subprocess

from ..system import OSTypes


log = logging.getLogger('iarp_utils.browser.utils')


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

    commands = cmd_mapping[browser_type][OSTypes.active()]
    return _get_version_from_commands('Google Chrome', commands, r'\d+\.\d+\.\d+')


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

    commands = cmd_mapping.get(OSTypes.active())
    return _get_version_from_commands('Firefox', commands, r'(\d+.\d+)')


def _run_commands(commands):

    if isinstance(commands, str):
        commands = [commands]

    for cmd in commands:
        try:
            return subprocess.Popen(cmd, stdout=subprocess.PIPE).stdout.read().decode('utf-8').strip()
        except:  # noqa
            pass


def _process_commands_output(output, pattern):
    return re.search(pattern, output)


def _get_version_from_commands(name, commands, pattern):
    if not commands:
        raise ValueError(f'No command found for {name} version with os {OSTypes.active()}')

    log.debug(f'{name} version, running commands {commands}')

    output = _run_commands(commands)

    if not output:
        raise ValueError(f'Could not get version for {name} with this command: {commands}')

    log.debug(f'{name} version, commands returned "{output}"')

    version = _process_commands_output(output, pattern)

    if version:
        version = version.group(0)
    else:
        raise ValueError(f'Could not process version for {name} commands output: {commands}')

    log.debug(f'{name} version, version processed as {version}')

    return version
