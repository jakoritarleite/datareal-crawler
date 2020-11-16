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
        request: ClassVar

        if self.render.lower() == 'true':
            request = _Request(
                method=self.method,
                url=self.api_url,
                headers=self.headers,
                params={
                    'api_key': self.api_key,
                    'render': str(self.render).lower(),
                    'url': self._url
                }
            )

        else:
            request = _Request(
                method=self.method,
                url=self._url,
                headers=self.headers
            )

        self._request = request.prepare()
        self._session = Session()

    def fetch(self):
        response = self._session.send(self._request)

        if response.ok:
            return response

        else:
            # This code block above is a handler for when the server returns us a 403 status code
            # It's just a quick fix to make the PoC fully functional and start running that shit

            if int(response.status_code) == 403:
                print('Blocked by server, trying to use Proxy')
                self.render = 'true'
                self._set_session()

                response = self._session.send(self._request)

                if response.ok:
                    return response

                print('Looking up on server response')
                print(response)

            else:
                raise Exception(f'Got the following Error status code: {response.status_code}')
