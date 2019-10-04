import unittest
import time

from iarp_utils.pidfile import PIDFile


class PidfileTests(unittest.TestCase):

    def test_pidfile_works(self):
        with PIDFile('test') as good:
            self.assertTrue(good)

            with PIDFile('test') as good2:
                self.assertFalse(good2)

                if not good2:
                    raise PIDFile.Break

                raise AssertionError('This should not be reached since PID will be locked.')

    def test_pidfile_raises_properly(self):
        with PIDFile('test') as good:
            self.assertTrue(good)

            with self.assertRaises(ValueError):
                with PIDFile('test', raise_on_still_running=True) as good2:
                    raise AssertionError('This should not be reached since PID will be locked.')

    def test_pidfile_kwargs_set(self):
        with PIDFile('test', blah=True) as good:
            self.assertTrue(good)
            self.assertTrue(getattr(good, 'blah'))
            self.assertFalse(getattr(good, 'param', False))
