import requests

from functools import partialmethod
from requests.exceptions import HTTPError

from zeus.exceptions import ApiError


class GitHubClient(object):
    url = 'https://api.github.com'

    def __init__(self, url=None, token=None):
        if url is not None:
            self.url = url.rstrip('/')
        self.token = token

    def _dispatch(
        self, method: str, path: str, headers: dict=None, json: dict=None, params: dict=None
    ):
        try:
            resp = requests.request(
                method=method,
                url='{}{}'.format(self.url, path),
                headers=headers,
                json=json,
                params=params,
                allow_redirects=True,
            )
            resp.raise_for_status()
        except HTTPError as e:
            raise ApiError.from_response(e.response)

        if resp.status_code == 204:
            return {}

        return resp.json()

    def dispatch(self, path: str, method: str, json: dict=None, params: dict=None):
        headers = {}
        if self.token:
            headers['Authorization'] = 'token %s' % self.token

        return self._dispatch(method=method, path=path, headers=headers, json=json, params=params)

    delete = partialmethod(dispatch, method='DELETE')
    get = partialmethod(dispatch, method='GET')
    head = partialmethod(dispatch, method='HEAD')
    options = partialmethod(dispatch, method='OPTIONS')
    patch = partialmethod(dispatch, method='PATCH')
    post = partialmethod(dispatch, method='POST')
    put = partialmethod(dispatch, method='PUT')
