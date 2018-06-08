import requests

from cached_property import cached_property
from functools import partialmethod
from requests.exceptions import HTTPError

from zeus.exceptions import ApiError


class BaseResponse(object):
    @cached_property
    def rel(self):
        link_header = self.headers.get("Link")
        if not link_header:
            return {}

        return {
            item["rel"]: item["url"]
            for item in requests.utils.parse_header_links(link_header)
        }

    @classmethod
    def from_response(self, resp):
        data = resp.json()
        if isinstance(data, dict):
            return MappingResponse(data, resp.headers)

        elif isinstance(data, (list, tuple)):
            return SequenceResponse(data, resp.headers)


class MappingResponse(dict, BaseResponse):
    def __init__(self, data, headers):
        dict.__init__(self, data)
        self.headers = headers


class SequenceResponse(list, BaseResponse):
    def __init__(self, data, headers):
        list.__init__(self, data)
        self.headers = headers


class GitHubClient(object):
    url = "https://api.github.com"

    def __init__(self, url=None, token=None):
        if url is not None:
            self.url = url.rstrip("/")
        self.token = token

    def _dispatch(
        self,
        method: str,
        path: str,
        headers: dict = None,
        json: dict = None,
        params: dict = None,
    ):
        if path.startswith(("http:", "https:")):
            url = path
        else:
            url = "{}{}".format(self.url, path)

        try:
            resp = requests.request(
                method=method,
                url=url,
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

        return BaseResponse.from_response(resp)

    def dispatch(self, path: str, method: str, json: dict = None, params: dict = None):
        headers = {}
        if self.token:
            headers["Authorization"] = "token {}".format(self.token)

        return self._dispatch(
            method=method, path=path, headers=headers, json=json, params=params
        )

    delete = partialmethod(dispatch, method="DELETE")
    get = partialmethod(dispatch, method="GET")
    head = partialmethod(dispatch, method="HEAD")
    options = partialmethod(dispatch, method="OPTIONS")
    patch = partialmethod(dispatch, method="PATCH")
    post = partialmethod(dispatch, method="POST")
    put = partialmethod(dispatch, method="PUT")
