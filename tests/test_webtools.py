import unittest
import os

from iarp_utils import webtools


class WebToolsTests(unittest.TestCase):

    def test_get_client_ip_remote_works(self):
        meta = {'REMOTE_ADDR': '123.123.123.123'}
        self.assertEqual('123.123.123.123', webtools.get_client_ip(meta=meta))

    def test_get_client_ip_forwarded_for_works(self):
        meta = {
            'HTTP_X_FORWARDED_FOR': 'Forwarded For Address',
            'REMOTE_ADDR': 'REMOTE_ADDR Address'
        }
        self.assertEqual('Forwarded For Address', webtools.get_client_ip(meta=meta))

    def test_get_client_ip_forwarded_for_multiples_works(self):
        meta = {
            'HTTP_X_FORWARDED_FOR': 'Forwarded For Address,Forwarded For Second Address',
            'REMOTE_ADDR': 'REMOTE_ADDR Address'
        }
        self.assertEqual('Forwarded For Address', webtools.get_client_ip(meta=meta))
