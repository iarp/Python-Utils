import os
import unittest

from iarp_utils.cxFreeze import resource_path


class cxFreezeTests(unittest.TestCase):

    def test_resource_path(self):
        path = resource_path('config.ini')
        self.assertTrue(path.endswith('config.ini'))
