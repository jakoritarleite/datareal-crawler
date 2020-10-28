from os import environ
from lib.url import escape_ajax
from lib.models.header import Header
from w3lib.url import safe_url_string
from requests import Request as _Request, Session

class Request(object):
    def __init__(self, url, method='GET', header=None, encoding='utf-8', render=True):
        self.method = str(method).upper()
        self.render = str(render).lower()
        self.encoding = encoding
        self.headers = Header(header).__get_header__()
        self.api_url = environ['API_URL']
        self.api_key = environ['API_KEY']

        self._set_url(url)
        self._set_session()

    def _set_url(self, url):
        if not isinstance(url, str):
            raise TypeError(f'Request url must be str or unicode, got {type(url).__name__}')

        safe_url = safe_url_string(url, self.encoding)
        self._url = escape_ajax(safe_url)

        if ('://' not in self._url) and (not self._url.startswith('data:')):
            raise ValueError(f'Missing scheme in request url: {self._url}')

    def _set_session(self):
        request = _Request(
            method=self.method,
            url=self.api_url if bool(self.render) else self._url,
            headers=self.headers,
            params={
                'api_key': self.api_key,
                'render': self.render,
                'url': self._url
            } if bool(self.render) else None
        )

        self._request = request.prepare()
        self._session = Session()

    def fetch(self):
        response = self._session.send(self._request)

        if response.ok:
            return response

        else:
            raise Exception(f'Got the following Error status code: {response.status_code}')