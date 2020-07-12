from pathlib import Path

try:
    import psutil
except ImportError:
    psutil = None


def is_pid_still_running(pid_file, delete=True):
    """ Determines if a given PID in a pid file is still running.

    Args:
        pid_file: The file containing the PID
        delete: Should we delete the PID file if the PID is not running?

    Returns:
        bool if pid is running
    """

    if not psutil:
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
