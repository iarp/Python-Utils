import unittest
import os

from iarp_utils.system import is_pid_still_running, get_system_bitness, OSTypes, import_callable, import_attribute


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

    def test_system_bitness_is_32_or_64(self):
        self.assertIn(get_system_bitness(), ['32', '64'])

    def test_os_name_is_expected(self):
        self.assertIn(OSTypes.active(), OSTypes)

    def test_import_callable(self):
        func = import_callable('iarp_utils.system.is_pid_still_running')
        self.assertIs(func, is_pid_still_running)

    def test_import_attribute(self):
        func = import_attribute('iarp_utils.system.is_pid_still_running')
        self.assertIs(func, is_pid_still_running)

    def test_import_attribute_errors(self):
        self.assertRaises(AttributeError, import_attribute, 'iarp_utils.system.is_pid_still_runnings')
