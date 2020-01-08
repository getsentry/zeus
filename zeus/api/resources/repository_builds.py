from flask import request
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload, subqueryload_all

from zeus import auth
from zeus.config import db
from zeus.models import Author, Build, Email, Repository, User
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
        query = (
            Build.query.options(
                joinedload("author"),
                joinedload("revision"),
                joinedload("revision").joinedload("author"),
                subqueryload_all("stats"),
            )
            .filter(Build.repository_id == repo.id)
            .order_by(Build.number.desc())
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
                or_(
                    Build.author_id.in_(
                        db.session.query(Author.id).filter(
                            Author.email.in_(
                                db.session.query(Email.email).filter(
                                    Email.user_id == user.id,
                                    Email.verified == True,  # NOQA
                                )
                            )
                        )
                    ),
                    Build.authors.any(
                        Author.email.in_(
                            db.session.query(Email.email).filter(
                                Email.user_id == user.id, Email.verified == True  # NOQA
                            )
                        )
                    ),
                )
            )

        return self.paginate_with_schema(builds_schema, query)

    def post(self, repo: Repository):
        """
        Create a new build.
        """
        schema = BuildCreateSchema(context={"repository": repo})
        build = self.schema_from_request(schema)
        db.session.add(build)

        try:
            db.session.commit()
        except IntegrityError as exc:
            if "duplicate" in str(exc):
                db.session.rollback()
                return self.respond(status=422)
            raise

        if not build.revision_sha:
            from zeus.tasks import resolve_ref_for_build

            resolve_ref_for_build.delay(build_id=build.id)

        build_schema.validate(build)
        data = build_schema.dump(build)
        publish("builds", "build.create", data)

        return self.respond(data, 200)
