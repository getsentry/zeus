from flask import request
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload, subqueryload_all

from zeus import auth
from zeus.config import db
from zeus.models import Author, Build, Email, Hook, Repository, Source
from zeus.pubsub.utils import publish

from .base_repository import BaseRepositoryResource
from ..schemas import BuildSchema, BuildCreateSchema

build_schema = BuildSchema()
builds_schema = BuildSchema(many=True, exclude=["repository"])


class RepositoryBuildsResource(BaseRepositoryResource):
    def select_resource_for_update(self):
        return False

    def get(self, repo: Repository):
        """
        Return a list of builds for the given repository.
        """
        user = auth.get_current_user()

        query = (
            Build.query.options(
                joinedload("author"),
                joinedload("revision"),
                subqueryload_all("stats"),
            )
            .filter(Build.repository_id == repo.id)
            .order_by(Build.number.desc())
        )
        show = request.args.get("show")
        if show == "mine":
            query = query.filter(
                Build.author_id.in_(
                    db.session.query(Author.id).filter(
                        Author.email.in_(
                            db.session.query(Email.email).filter(
                                Email.user_id == user.id, Email.verified == True  # NOQA
                            )
                        )
                    )
                )
            )

        return self.paginate_with_schema(builds_schema, query)

    def post(self, repo: Repository):
        """
        Create a new build.
        """
        schema = BuildCreateSchema(context={"repository": repo})
        data = self.schema_from_request(schema, partial=True)

        build = Build(repository=repo, **data)
        if build.data is None:
            build.data = {}
        build.data["required_hook_ids"] = Hook.get_required_hook_ids(repo.id)
        if not build.label:
            build.label = source.revision.message.split("\n")[0]

        if not build.label:
            return self.error("missing build label")

        db.session.add(build)

        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return self.respond(status=422)

        build_schema.validate(build)
        data = build_schema.dump(build)
        publish("builds", "build.create", data)
        return self.respond(data, 200)
