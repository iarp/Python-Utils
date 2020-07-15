import os

from . import system

try:
    from django.conf import settings
except ImportError:
    settings = None


class PIDFile(object):
    """ Creates a type of lock that prevents a script from running multiple times.

    PID Files are used to determine if another process is already running.
    Supply a unique name for the pid context and the script being run.

    If the script is running in another process and it tries to run again,
    we raise PIDFile.Break to stop processing.

    The lock only exists until the context closes.

    Examples::

        with PIDFile('test') as good:

            # If good returns as False, stop execution, another copy of this
            # script is still running.
            if not good:
                raise PIDFile.Break

            counter = 0
            for x in range(1000000):
                counter += 1

            print(counter)
    """

    class Break(Exception):
        """Allows breaking out of PIDFile early"""

    def __init__(self, pid_file_name, folder='', raise_on_still_running=False, **kwargs):

        if not folder:
            # I commonly use this in django management commands and crontab,
            # attempt to load the PID storage folder from django settings.
            for attr in ['PID_DIR', 'CACHE_DIR', 'BASE_DIR']:
                try:
                    folder = getattr(settings, attr)
                    break
                except:
                    continue

        self.folder = folder or ''
        self.pid_file_name = pid_file_name
        self.pid_file = os.path.join(self.folder, f'{self.pid_file_name}.pid')
        self.raise_on_pid_exists = raise_on_still_running
        self.file_obj = None

        if self.folder and not os.path.isdir(self.folder):
            os.mkdir(self.folder)

        for k, v in kwargs.items():
            setattr(self, k, v)

    def is_safe_to_execute(self):
        return not system.is_pid_still_running(self.pid_file)

    def start_pid_file(self):
        # Open the PId file and hold a lock on it so it cannot be deleted.
        self.file_obj = open(self.pid_file, 'wb', buffering=0)
        self.file_obj.write(str(os.getpid()).encode('utf8'))

    def __enter__(self):

        if not self.is_safe_to_execute():

            if self.raise_on_pid_exists:
                raise ValueError(f'PID File exists and is in use, {self.pid_file}')

            return False

        self.start_pid_file()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):

        # If the user raises PIDFile.Break within context, its a good break.
        if exc_type == self.Break:
            return True

        if exc_type and hasattr(self, 'browser'):
            #  Supply browser=<selenium browser object> to PIDFile(...) during context creation,
            # if an exception occurs within the context, attempt to take a screenshot
            # of the current browser screen.
            try:
                self.browser.save_screenshot(filename_prefix=f'{self.pid_file_name}_')
            except:
                pass

        if self.file_obj:
            self.file_obj.close()

        try:
            os.remove(self.pid_file)
        except PermissionError:
            pass
