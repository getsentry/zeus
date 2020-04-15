from flask import request
from sqlalchemy.orm import joinedload, subqueryload_all

from zeus import auth
from zeus.config import db
from zeus.constants import Result, Status
from zeus.models import Author, Build, Email, FailureReason, Repository, User

from .base import Resource
from ..schemas import BuildSchema

builds_schema = BuildSchema(many=True)


class BuildIndexResource(Resource):
    def select_resource_for_update(self):
        return False

    def get(self):
        """
        Return a list of builds.
        """
        # tenants automatically restrict this query but we dont want
        # to include public repos
        tenant = auth.get_current_tenant()
        if not tenant.repository_ids:
            return self.respond([])

        query = (
            Build.query.options(
                joinedload("repository"),
                joinedload("revision"),
                subqueryload_all("revision.authors"),
                subqueryload_all("stats"),
                subqueryload_all("authors"),
            )
            .filter(Build.repository_id.in_(tenant.repository_ids))
            .order_by(Build.date_created.desc())
        )
        user = request.args.get("user")
        if user:
            if user == "me":
                user = auth.get_current_user()
            else:
                user = User.query.get(user)
            if not user:
                return self.respond([])

            query = query.filter(
                Build.authors.any(
                    Author.email.in_(
                        db.session.query(Email.email).filter(
                            Email.user_id == user.id, Email.verified == True  # NOQA
                        )
                    )
                )
            )
        result = request.args.get("result")
        if result:
            query = query.filter(Build.result == Result[result])

        status = request.args.get("status")
        if status:
            query = query.filter(Build.status == Status[status])

        failure_reason = request.args.get("failure_reason")
        if failure_reason:
            query = query.filter(
                FailureReason.build_id == Build.id,
                FailureReason.reason == FailureReason.Reason[failure_reason],
            )

        repository = request.args.get("repository")
        if repository:
            repo = Repository.from_full_name(repository)
            if not repo:
                return self.respond([])
            query = query.filter(Build.repository_id == repo.id)
        return self.paginate_with_schema(builds_schema, query)
