import json
import requests

from flask import current_app
from sentry_sdk import Hub
from typing import List
from uuid import UUID

from zeus import auth
from zeus.exceptions import ApiError


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
        params: dict = None,
        tenant=True,
        raise_errors=True,
    ):
        if tenant is True:
            tenant = auth.get_current_tenant()

        url = "{}/{}".format(
            current_app.config["VCS_SERVER_ENDPOINT"], path.lstrip("/")
        )

        hub = Hub.current
        with hub.start_span(op="vcs-server", description=f"{method} {path}"):
            response = requests.request(
                method=method,
                url=url,
                params={k: v for k, v in params.items() if v is not None}
                if params
                else None,
                headers={
                    "Authorization": "token {}".format(
                        auth.generate_token(tenant).decode("utf-8")
                    )
                },
            )
        if raise_errors and not (200 <= response.status_code < 300):
            text = response.text
            try:
                data = json.loads(text)
            except ValueError:
                data = {}

            # XXX(dcramer): this feels a bit hacky, and ideally would be handled
            # in the vcs implementation
            if data.get("error") == "invalid_pubkey":
                from zeus.tasks import deactivate_repo, DeactivationReason

                deactivate_repo.delay(
                    params["repo_id"], DeactivationReason.invalid_pubkey
                )

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
        self, repo_id: UUID, parent: str = None, branch: str = None, offset=0, limit=100
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
        )["log"]

    def export(self, repo_id: UUID, sha: str) -> str:
        return self.request(
            method="GET",
            path="/stmt/export",
            params={"repo_id": str(repo_id), "sha": sha},
        )["export"]

    def show(self, repo_id: UUID, sha: str, filename: str) -> str:
        return self.request(
            method="GET",
            path="/stmt/export",
            params={"repo_id": str(repo_id), "sha": sha, "filename": filename},
        )["show"]

    def branches(self, repo_id: UUID) -> str:
        return self.request(
            method="GET", path="/stmt/branches", params={"repo_id": str(repo_id)}
        )["branches"]


vcs_client = VcsServerClient()
