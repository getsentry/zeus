import json

from flask import current_app, request

from zeus.constants import Result, Status
from zeus.models import Build, Repository, Source

from ..client import api_client
from .base_repository import BaseRepositoryResource
from ..schemas import BuildSchema

build_schema = BuildSchema(strict=True, exclude=["repository"])


class RepositoryFileCoverageTreeResource(BaseRepositoryResource):
    def get(self, repo: Repository):
        """
        Return a tree of testcases for the given repository.
        """
        latest_build = (
            Build.query.join(Source, Source.id == Build.source_id)
            .filter(
                Source.patch_id == None,  # NOQA
                Build.repository_id == repo.id,
                Build.result == Result.passed,
                Build.status == Status.finished,
            )
            .order_by(Build.date_created.desc())
            .first()
        )

        if not latest_build:
            current_app.logger.info("no successful builds found for repository")
            return self.respond({"entries": [], "trail": []})

        path = "/repos/{}/builds/{}/file-coverage-tree".format(
            repo.get_full_name(), latest_build.number
        )

        response = api_client.get(path, request=request)
        data = json.loads(response.data)
        data["build"] = build_schema.dump(latest_build).data
        return self.respond(data)
