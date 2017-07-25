from flask import request
from sqlalchemy.orm import contains_eager, joinedload, subqueryload_all

from zeus import auth
from zeus.config import db
from zeus.models import Author, Build, Repository, Source

from .base_repository import BaseRepositoryResource
from ..schemas import BuildSchema, BuildCreateSchema

build_create_schema = BuildCreateSchema(strict=True)
build_schema = BuildSchema(strict=True)
builds_schema = BuildSchema(many=True, strict=True)


class RepositoryBuildsResource(BaseRepositoryResource):
    def get(self, repo: Repository):
        """
        Return a list of builds for the given repository.
        """
        user = auth.get_current_user()

        query = Build.query.options(
            contains_eager('source'),
            joinedload('source').joinedload('author'),
            joinedload('source').joinedload('revision'),
            joinedload('source').joinedload('patch'),
            subqueryload_all('stats'),
        ).join(
            Source,
            Build.source_id == Source.id,
        ).filter(
            Build.repository_id == repo.id,
        ).order_by(Build.number.desc())
        show = request.args.get('show')
        if show == 'mine' or (not show and user):
            query = query.filter(
                Source.author_id.
                in_(db.session.query(Author.id).filter(Author.email == user.email)),
            )

        return self.paginate_with_schema(builds_schema, query)

    def post(self, repo: Repository):
        """
        Create a new build.
        """
        result = self.schema_from_request(build_create_schema, partial=True)
        if result.errors:
            return self.respond(result.errors, 403)
        data = result.data

        revision_sha = data.pop('revision_sha')
        source = Source.query.filter(
            Source.revision_sha == revision_sha,
            Source.repository_id == repo.id,
        ).first()
        if not source:
            return self.error('invalid source')

        # TODO(dcramer): only if we create a source via a patch will we need the author
        # author_data = data.pop('author')
        # if author_data.get('email'):
        #     author = Author.query.filter(
        #         Author.repository_id == repo.id, Author.email == author_data['email']
        #     ).first()
        # else:
        #     author = None
        # if not author:
        #     author = Author(repository_id=repo.id, **author_data)
        #     db.session.add(author)
        #     db.session.flush()

        build = Build(repository=repo, **data)
        # TODO(dcramer): we should convert source in the schema
        build.source = source
        build.source_id = source.id
        if not source.patch_id:
            if not build.label:
                build.label = source.revision.message.split('\n')[0]
        assert build.source_id
        db.session.add(build)
        db.session.commit()

        return self.respond_with_schema(build_schema, build)
