from unittest import TestCase
import requests
import responses

from iarp_utils.requests_utils import BearerAuth


class RequestsUtilsTestCase(TestCase):

    @responses.activate
    def test_authorization_in_header(self):
        expected_token = 'test token'
        expected_headers = {'Authorization': f'Bearer {expected_token}'}
        responses.add(responses.GET, 'https://www.google.ca', status=200, headers=expected_headers)
        r = requests.get('https://www.google.ca', auth=BearerAuth(expected_token))
        self.assertIn('Authorization', r.request.headers)
        self.assertEqual(f'Bearer {expected_token}', r.request.headers.get('Authorization'))

