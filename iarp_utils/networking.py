import base64
import ipaddress
import os
import random
import requests

from . import configuration
from .strings import startswith_many


def get_wan_ip_from_linksys_router(router_ip_address='192.168.1.1',
                                   allow_returning_private_ip_ranges=False,
                                   private_ip_ranges: list = None,
                                   auth_username=None, auth_password=None):
    """ Obtains the WAN IP Address from a linksys
        based router that supports JNAP.

        Authentication is typically NOT required for GetWANStatus command we are using.
        It is included as params just in case.

    Args:
        router_ip_address: IP Address of the router to query from.
        allow_returning_private_ip_ranges: If the IP address returned falls
            into the private_ip_ranges, do you still want the value returned?
        private_ip_ranges: A list of private ip ranges. Standard ip.startswith matching.
        auth_username: Username to login to the router with
        auth_password: Password required for the user supplied

        private_ip_ranges = ['169.254.', '192.168.', '10.', '172.', '127.']

    Returns:
        string containing the IP address. None if anything went wrong.
    """
    if private_ip_ranges is None:
        private_ip_ranges = ['169.254.', '192.168.', '10.', '172.', '127.']

    headers = {
        "Content-Type": "application/json; charset=UTF-8",
        "Accept": "application/json",
        "X-JNAP-Action": "http://cisco.com/jnap/router/GetWANStatus",
    }

    if auth_username and auth_password:
        # Auth is not needed for GetWANStatus, leaving for knowledge sake.
        auth_combined = f'{auth_username}:{auth_password}'
        auth_password = base64.b64encode(auth_combined.encode('utf8')).decode('utf8')
        headers["X-JNAP-Authorization"] = f"Basic {auth_password}"

    if not router_ip_address.startswith('http'):
        router_ip_address = f'http://{router_ip_address}'

    r = requests.post(f'{router_ip_address}/JNAP/', headers=headers, data='{}', verify=False)

    data = r.json()

    if not data or data.get('result') != 'OK':
        return

    data = data.get('output')

    if not data or data.get('wanStatus') != 'Connected':
        return

    conn = data.get('wanConnection')

    if not conn:
        return

    ip = conn.get('ipAddress')

    if not isinstance(ip, str):
        return

    if startswith_many(ip, private_ip_ranges) and not allow_returning_private_ip_ranges:
        return

    try:
        ipaddress.ip_address(ip)
        return ip
    except:
        pass


def get_wan_ip_from_external_sites(sites: list = None, shuffler=random.shuffle, possible_json_keys=None,
                                   json_file='wan_ip_sites.json'):
    """ Obtains your WAN IP Address from websites that publish it.

    sites can also be stored in a json file with the following format,
    supply json_file with the filepath.

    {
        'sites': ['https://www.site1.com/wan-ip',],
        'json_keys': ['ip', 'ipaddress']
    }

    Args:
        sites: list containing websites to use, must return json {'ip': '...'} or raw text IP.
        shuffler: the shuffler to use on the sites list so that no one site always gets used
        possible_json_keys: if the website returns a json value, what key gets the value.
        json_file: Filepath to json file containing sites to poll wan ip from

    Returns:
        String with the IP address if valid, returns None otherwise.
    """
    if not possible_json_keys or not isinstance(possible_json_keys, (list, tuple, set)):
        possible_json_keys = ['ip', 'ipAddress']

    if not sites and os.path.isfile(json_file):
        config = configuration.load(json_file)
        sites = config.get('sites', [])
        possible_json_keys.extend(config.get('json_keys', []))

    if not sites:
        sites = [
            'https://api.ipify.org',
            'http://ip.jsontest.com',
            'https://jsonip.com',
            'http://icanhazip.com',
            'http://ident.me'
        ]

    if callable(shuffler):
        possible_returned_values = shuffler(sites)

        if possible_returned_values:
            # If the shuffler function the user supplied returned its values, use those.
            # Otherwise the users shuffler should've done in-place shuffling.
            sites = possible_returned_values

    if not isinstance(sites, (list, tuple, set)):
        raise ValueError('sites must by of type list, tuple, or set.')

    for s in sites:
        try:
            r = requests.get(s)
            r.raise_for_status()

            try:
                # See if the raw response text is an IP, this will avoid potentially
                # hitting multiple sites and failing the json key matching below.
                ipaddress.ip_address(r.text)
                return r.text
            except (ValueError, AttributeError):
                pass

            data = r.json()

            for k in possible_json_keys:
                try:
                    val = data[k]
                    ipaddress.ip_address(val)
                    return val
                except (ValueError, KeyError, TypeError):
                    pass  # pragma: no cover

        except requests.exceptions.HTTPError:
            pass
