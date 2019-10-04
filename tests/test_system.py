import unittest
import os

from iarp_utils.system import is_pid_still_running


class SystemsTests(unittest.TestCase):

    def test_is_pid_still_running(self):
        pid_file = 'test.pid'

        self.assertFalse(is_pid_still_running(pid_file))

        with open(pid_file, 'w') as fw:
            fw.write(str(os.getpid()))

        self.assertTrue(is_pid_still_running(pid_file, delete=True))

        with open(pid_file, 'w') as fw:
            fw.write('9999999')

        self.assertFalse(is_pid_still_running(pid_file, delete=True))

        with open(pid_file, 'w') as fw:
            fw.write('bad value')

        self.assertFalse(is_pid_still_running(pid_file))

        if os.path.exists(pid_file):
            os.remove(pid_file)
