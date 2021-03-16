import enum
import importlib
import os
import subprocess
import sys
from pathlib import Path


try:
    import psutil
except ImportError:  # pragma: no cover
    psutil = None


IS_WINDOWS_OS = os.name == 'nt'


def is_pid_still_running(pid_file, delete=True):
    """ Determines if a given PID in a pid file is still running.

    Args:
        pid_file: The file containing the PID
        delete: Should we delete the PID file if the PID is not running?

    Returns:
        bool if pid is running
    """

    if not psutil:  # pragma: no cover
        raise ImportError('psutil is required for this functionality. "pip install psutil"')

    pid_file = Path(pid_file)

    if not pid_file.exists():
        return False

    with pid_file.open() as fo:
        try:
            pid = int(fo.read().strip())
        except (TypeError, ValueError):
            pid = None

    # If we have a PID, lets check if it's still running or not.
    if pid and psutil.pid_exists(pid):
        return True

    if delete:
        # Otherwise delete it.
        pid_file.unlink()

    return False


def get_system_bitness():
    """ Returns 32 or 64 depending on OS bitness"""
    if IS_WINDOWS_OS:
        output = subprocess.check_output(['wmic', 'os', 'get', 'OSArchitecture']).decode('utf8')
        arch = output.split()[1]
        return ''.join([x for x in arch if x.isdigit()])
    else:
        output = subprocess.check_output(['uname', '-m']).decode('utf8')
        return '64' if 'x86_64' in output else '32'


class OSTypes(enum.Enum):
    LINUX = "linux"
    MAC = "mac"
    WIN = "win"

    @staticmethod
    def active():
        pl = sys.platform
        if pl.startswith('linux'):
            return OSTypes.LINUX
        elif pl == "darwin":
            return OSTypes.MAC
        elif pl == "win32":
            return OSTypes.WIN


def import_attribute(path):
    assert isinstance(path, str)
    pkg, attr = path.rsplit(".", 1)
    ret = getattr(importlib.import_module(pkg), attr)
    return ret


def import_callable(path_or_callable):
    if not hasattr(path_or_callable, "__call__"):
        ret = import_attribute(path_or_callable)
    else:
        ret = path_or_callable
    return ret
