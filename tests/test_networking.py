import unittest
import os
import responses
import json
import requests.exceptions
from mock import patch, Mock, mock_open

from iarp_utils import networking


class NetworkingTests(unittest.TestCase):

    @patch('iarp_utils.networking.requests.post')
    def test_get_wan_ip_from_linksys_router_remote_works(self, mock_post):
        mock_post.return_value = Mock(ok=True)
        mock_post.return_value.json.return_value = {
            'result': 'OK',
            'output': {
                'wanStatus': 'Connected',
                'wanConnection': {
                    'ipAddress': '1.1.1.1',
                },
            }
        }

        val = networking.get_wan_ip_from_linksys_router('192.168.1.1')
        self.assertIsNotNone(val)
        self.assertEqual('1.1.1.1', val)

    @patch('iarp_utils.networking.requests.post')
    def test_get_wan_ip_from_linksys_router_remote_result_not_ok(self, mock_post):
        mock_post.return_value = Mock(ok=True)
        mock_post.return_value.json.return_value = {
            'result': 'Fail',
        }

        val = networking.get_wan_ip_from_linksys_router('192.168.1.1')
        self.assertIsNone(val)

    @patch('iarp_utils.networking.requests.post')
    def test_get_wan_ip_from_linksys_router_remote_state_connecting(self, mock_post):
        mock_post.return_value = Mock(ok=True)
        mock_post.return_value.json.return_value = {
            'result': 'OK',
            'output': {
                'wanStatus': 'Connecting',
                'wanConnection': {
                    'ipAddress': '1.1.1.1',
                },
            }
        }

        val = networking.get_wan_ip_from_linksys_router('192.168.1.1')
        self.assertIsNone(val)

    @patch('iarp_utils.networking.requests.post')
    def test_get_wan_ip_from_linksys_router_remote_assigned_private_ip(self, mock_post):
        mock_post.return_value = Mock(ok=True)
        mock_post.return_value.json.return_value = {
            'result': 'OK',
            'output': {
                'wanStatus': 'Connected',
                'wanConnection': {
                    'ipAddress': '10.0.0.1',
                },
            }
        }

        val = networking.get_wan_ip_from_linksys_router()
        self.assertIsNone(val)

    @patch('iarp_utils.networking.requests.post')
    def test_get_wan_ip_from_linksys_router_remote_assigned_private_ip_allowed(self, mock_post):
        mock_post.return_value = Mock(ok=True)
        mock_post.return_value.json.return_value = {
            'result': 'OK',
            'output': {
                'wanStatus': 'Connected',
                'wanConnection': {
                    'ipAddress': '10.0.0.1',
                },
            }
        }

        val = networking.get_wan_ip_from_linksys_router(allow_returning_private_ip_ranges=True)
        self.assertEqual('10.0.0.1', val)

    @patch('iarp_utils.networking.requests.post')
    def test_get_wan_ip_from_linksys_router_remote_invalid_ip(self, mock_post):
        mock_post.return_value = Mock(ok=True)
        mock_post.return_value.json.return_value = {
            'result': 'OK',
            'output': {
                'wanStatus': 'Connected',
                'wanConnection': {
                    'ipAddress': '653.1.1.1',
                },
            }
        }

        val = networking.get_wan_ip_from_linksys_router()
        self.assertIsNone(val)

    @patch('iarp_utils.networking.requests.post')
    def test_get_wan_ip_from_linksys_router_wan_connection_empty(self, mock_post):
        mock_post.return_value = Mock(ok=True)
        mock_post.return_value.json.return_value = {
            'result': 'OK',
            'output': {
                'wanStatus': 'Connected',
                'wanConnection': {},
            }
        }

        val = networking.get_wan_ip_from_linksys_router()
        self.assertIsNone(val)

    @patch('iarp_utils.networking.requests.post')
    def test_get_wan_ip_from_linksys_router_ip_is_not_string(self, mock_post):
        mock_post.return_value = Mock(ok=True)
        mock_post.return_value.json.return_value = {
            'result': 'OK',
            'output': {
                'wanStatus': 'Connected',
                'wanConnection': {
                    'ipAddress': {'sub': 'value'},
                },
            }
        }

        val = networking.get_wan_ip_from_linksys_router('192.168.1.1')
        self.assertIsNone(val)

    @patch('iarp_utils.networking.requests.get')
    def test_get_wan_ip_from_external_sites(self, mock_get):
        mock_get.return_value = Mock(ok=True)
        mock_get.return_value.json.return_value = {
            'ip': '1.1.1.1',
        }

        val = networking.get_wan_ip_from_external_sites()
        self.assertEqual('1.1.1.1', val)

    @patch('iarp_utils.networking.requests.get')
    def test_get_wan_ip_from_external_sites_request_fails(self, mock_get):
        mock_get.side_effect = requests.exceptions.HTTPError()

        val = networking.get_wan_ip_from_external_sites()
        self.assertIsNone(val)

    @patch('iarp_utils.networking.requests.get')
    def test_get_wan_ip_from_external_sites_missing_keys(self, mock_get):
        mock_get.return_value = Mock(ok=True)
        mock_get.return_value.json.return_value = {
            'ips': '1.1.1.1',
        }

        val = networking.get_wan_ip_from_external_sites()
        self.assertIsNone(val)

    @patch('iarp_utils.networking.requests.get')
    def test_get_wan_ip_from_external_sites_matching_custom_keys(self, mock_get):
        mock_get.return_value = Mock(ok=True)
        mock_get.return_value.json.return_value = {'WanIP': '1.1.1.1'}

        val = networking.get_wan_ip_from_external_sites(possible_json_keys=['WanIP'])
        self.assertEqual('1.1.1.1', val)

    @patch('iarp_utils.networking.requests.get')
    def test_get_wan_ip_from_external_sites_raw_text_has_ip(self, mock_get):
        mock_get.return_value.text = '1.1.1.1'

        val = networking.get_wan_ip_from_external_sites()
        self.assertEqual('1.1.1.1', val)

    @patch('iarp_utils.networking.requests.get')
    def test_get_wan_ip_from_external_sites_custom_shuffler(self, mock_get):
        mock_get.return_value.text = '1.1.1.1'

        def shuffler(objs):
            return objs

        val = networking.get_wan_ip_from_external_sites(shuffler=shuffler)
        self.assertEqual('1.1.1.1', val)

    def test_get_wan_ip_from_external_sites_custom_shuffler_returns_invalid_iterable(self):

        def shuffler(objs):
            class Test:
                pass
            return Test()

        with self.assertRaises(ValueError):
            networking.get_wan_ip_from_external_sites(shuffler=shuffler)

    @responses.activate
    @patch('os.path.isfile')
    def test_get_wan_ip_from_external_sites_with_sites_in_json_file(self, mock_isopen):
        mock_isopen.return_value = True
        url = 'https://www.example.com/'
        responses.add(responses.GET, url, '1.1.1.1')

        data = json.dumps({'sites': [url, ]})
        with patch('builtins.open', mock_open(read_data=data)) as m:
            val = networking.get_wan_ip_from_external_sites()
            self.assertEqual('1.1.1.1', val)

        self.assertEqual(url, responses.calls[0].request.url)
