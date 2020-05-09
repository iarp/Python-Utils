from requests.auth import AuthBase


class BearerAuth(AuthBase):
    """ Easy usage of bearer auth in headers.

    Examples:
        requests.get('https://www.example.com/', auth=BearerAuth('3pVzwec1Gs1m'))
    """

    def __init__(self, token):
        self.token = token

    def __call__(self, r):
        r.headers['Authorization'] = f'Bearer {self.token}'
        return r
