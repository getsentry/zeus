from flask import Response

from zeus.models import Build, Job, Repository

from .base import Resource


class BaseJobResource(Resource):
    def dispatch_request(
        self, owner_name: str, repo_name: str, build_number: int, job_number: int, *args, **kwargs
    ) -> Response:
        job = Job.query.join(Build, Build.id == Job.build_id).join(
            Repository, Repository.id == Build.repository_id
        ).filter(
            Repository.owner_name == owner_name,
            Repository.name == repo_name,
            Build.number == build_number,
            Job.number == job_number,
        ).first()
        if not job:
            return self.not_found()

        return Resource.dispatch_request(self, job, *args, **kwargs)
