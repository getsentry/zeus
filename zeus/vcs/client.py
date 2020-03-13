import json
import requests

from flask import current_app
from sentry_sdk import Hub
from typing import List, Optional, Union
from uuid import UUID

from zeus import auth
from zeus.exceptions import ApiError, UnknownRevision


class VcsServerClient(object):
    """
    An internal API client.

    >>> client = VcsServerClient()
    >>> response = client.get('/projects/')
    >>> print response
    """

    def request(
        self,
        path: str,
        method: str,
        params: Optional[dict] = None,
        tenant: Optional[Union[bool, auth.Tenant]] = True,
        raise_errors: Optional[bool] = True,
    ):
        if tenant is True:
            tenant = auth.get_current_tenant()
        elif tenant is False:
            tenant = None

        url = "{}/{}".format(
            current_app.config["VCS_SERVER_ENDPOINT"], path.lstrip("/")
        )

        hub = Hub.current
        with hub.start_span(op="vcs-server", description=f"{method} {path}"):
            response = requests.request(
                method=method,
                url=url,
                params=(
                    {k: v for k, v in params.items() if v is not None}
                    if params
                    else None
                ),
                headers={
                    "Authorization": "Bearer zeus-t-{}".format(
                        auth.generate_token(tenant).decode("utf-8")
                    )
                },
            )
        if raise_errors and not (200 <= response.status_code < 300):
            text = response.text
            data = {}
            try:
                data = json.loads(text)
            except ValueError:
                pass

            # XXX(dcramer): this feels a bit hacky, and ideally would be handled
            # in the vcs implementation
            if data.get("error") == "invalid_pubkey" and params:
                from zeus.tasks import deactivate_repo, DeactivationReason

                deactivate_repo.delay(
                    params["repo_id"], DeactivationReason.invalid_pubkey
                )

            if data.get("error") == "invalid_ref":
                raise UnknownRevision(ref=data.get("ref"))

            raise ApiError(text=text, code=response.status_code)

        if raise_errors and not response.headers["Content-Type"].startswith(
            "application/json"
        ):
            raise ApiError(
                text="Request returned invalid content type: {}".format(
                    response.headers["Content-Type"]
                ),
                code=response.status_code,
            )

        return response.json()

    def log(
        self,
        repo_id: UUID,
        parent: str = None,
        branch: str = None,
        offset=0,
        limit=100,
        **kwargs,
    ) -> List[dict]:
        return self.request(
            method="GET",
            path="/stmt/log",
            params={
                "repo_id": str(repo_id),
                "parent": parent,
                "branch": branch,
                "offset": offset,
                "limit": limit,
            },
            **kwargs,
        )["log"]

    def export(self, repo_id: UUID, sha: str, **kwargs) -> str:
        return self.request(
            method="GET",
            path="/stmt/export",
            params={"repo_id": str(repo_id), "sha": sha},
            **kwargs,
        )["export"]

    def resolve(self, repo_id: UUID, ref: str, **kwargs) -> dict:
        return self.request(
            method="GET",
            path="/stmt/resolve",
            params={"repo_id": str(repo_id), "ref": ref},
            **kwargs,
        )["resolve"]

    def show(self, repo_id: UUID, sha: str, filename: str, **kwargs) -> str:
        return self.request(
            method="GET",
            path="/stmt/export",
            params={"repo_id": str(repo_id), "sha": sha, "filename": filename},
            **kwargs,
        )["show"]

    def branches(self, repo_id: UUID, **kwargs) -> str:
        return self.request(
            method="GET",
            path="/stmt/branches",
            params={"repo_id": str(repo_id)},
            **kwargs,
        )["branches"]


vcs_client = VcsServerClient()
