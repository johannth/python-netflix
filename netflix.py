""" Python-Netflix """
'''
For Netflix API documentation, visit: http://developer.netflix.com/docs
'''

__author__ = 'Mike Helmick <mikehelmick@me.com>'
__version__ = '0.4.0'

import json
import urllib

import requests
from requests_oauthlib import OAuth1Session

try:
    from urlparse import parse_qsl
except ImportError:
    from cgi import parse_qsl


class NetflixAPIError(Exception):
    pass


class NetflixAuthError(NetflixAPIError):
    pass


class NetflixAPI(object):
    def __init__(self, api_key, api_secret,
                 oauth_token=None, oauth_token_secret=None,
                 callback_url='', headers=None):

        self.api_key = api_key
        self.api_secret = api_secret
        self.oauth_token = oauth_token and u'%s' % oauth_token
        self.oauth_token_secret = oauth_token_secret and u'%s' % oauth_token_secret
        self.callback_url = callback_url

        self.request_token_url = 'http://api-public.netflix.com/oauth/request_token'
        self.access_token_url = 'http://api-public.netflix.com/oauth/access_token'
        self.authorize_url = 'https://api-user.netflix.com/oauth/login'

        self.api_base = 'http://api-public.netflix.com/'

        if all((self.oauth_token, self.oauth_token_secret)):
            self.client = OAuth1Session(
                self.api_key,
                client_secret=self.api_secret,
                resource_owner_key=self.oauth_token,
                resource_owner_secret=self.oauth_token_secret,
                signature_type='auth_header'
            )
        else:
            self.client = OAuth1Session(
                self.api_key,
                client_secret=self.api_secret,
                signature_type='auth_header'
            )

        default_headers = {'User-Agent': 'Python-Netflix v{}'.format(__version__)}
        if headers:
            default_headers.update(headers or {})
        self.headers = default_headers

        self.client.headers.update(self.headers)
        self.auth = None

    def get_authentication_tokens(self):
        """ Returns an authentication tokens, includes an 'auth_url' for user
        """

        url = self.request_token_url + '?oauth_callback=' + self.callback_url
        response = self.client.get(url, headers=self.headers, auth=self.auth)

        if response.status_code != 200:
            raise NetflixAuthError('There was a problem retrieving an authentication url.')

        try:
            request_tokens = dict(parse_qsl(response.content))
        except requests.exceptions.RequestException:
            raise NetflixAuthError('Unable to obtain auth tokens.')

        auth_url_params = {
            'oauth_token': request_tokens['oauth_token'],
            'oauth_callback': self.callback_url,
            'oauth_consumer_key': self.api_key,
        }

        request_tokens['auth_url'] = '%s?%s' % (self.authorize_url, urllib.urlencode(auth_url_params))
        return request_tokens

    def get_auth_tokens(self, oauth_verifier):
        """ Returns 'final' tokens to store and used to make authorized calls to Netflix.
        """

        url = self.access_token_url + '?oauth_verifier=' + oauth_verifier

        try:
            response = self.client.get(url, headers=self.headers, auth=self.auth)
        except requests.exceptions.RequestException:
            raise NetflixAuthError('An unknown error occurred.')

        if response.status_code != 200:
            raise NetflixAuthError('Getting access tokens failed: %s Response Status' % response.status_code)

        try:
            auth_tokens = dict(parse_qsl(response.content))
        except AttributeError:
            raise NetflixAuthError('Unable to obtain auth tokens.')

        return auth_tokens

    def api_request(self, endpoint, method='GET', params=None):
        method = method.lower()
        if not method in ('get', 'put', 'post', 'delete'):
            raise NetflixAPIError('Method must be of GET, PUT, POST or DELETE')

        if endpoint.startswith(self.api_base):
            url = endpoint
        else:
            url = self.api_base + endpoint

        params = params or {}
        params.update({'output': 'json'})

        # if method == 'put':
        #     params.update({'method': 'PUT'})
        #     method = 'post'

        kwargs = dict(method=method, url=url)
        if params:
            if method == 'get':
                kwargs["params"] = params
            else:
                kwargs["data"] = params

        try:
            response = self.client.request(**kwargs)
        except requests.exceptions.RequestException:
            raise NetflixAPIError('An unknown error occurred.')

        status = response.status_code
        content = response.content

        if status == 403:
            raise NetflixAuthError()

        try:
            content = json.loads(content)
        except ValueError:
            raise NetflixAPIError('Content is not valid JSON, unable to be decoded.')

        if status < 200 or status >= 300:
            raise NetflixAPIError('Code {}: {}'.format(status, content['status']['message']))

        return dict(content)

    def get(self, endpoint, params=None):
        return self.api_request(endpoint, params=params)

    def put(self, endpoint, params=None):
        return self.api_request(endpoint, method='PUT', params=params)

    def post(self, endpoint, params=None):
        return self.api_request(endpoint, method='POST', params=params)

    def delete(self, endpoint, params=None):
        return self.api_request(endpoint, method='DELETE', params=params)
