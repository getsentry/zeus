from sqlalchemy.orm import joinedload, subqueryload_all

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
        query = Build.query.options(
            joinedload('source').joinedload('revision'),
            joinedload('source').joinedload('patch'),
            joinedload('author'),
            subqueryload_all('stats'),
        ).filter(
            Build.repository_id == repo.id,
        ).order_by(Build.number.desc()).limit(100)
        return self.respond_with_schema(builds_schema, query)

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

        author_data = data.pop('author')
        if author_data.get('email'):
            author = Author.query.filter(
                Author.repository_id == repo.id, Author.email == author_data['email']
            ).first()
        else:
            author = None
        if not author:
            author = Author(repository_id=repo.id, **author_data)
            db.session.add(author)
            db.session.flush()

        build = Build(repository=repo, **data)
        # TODO(dcramer): we should convert source in the schema
        build.author = author
        build.author_id = author.id
        build.source = source
        build.source_id = source.id
        if not source.patch_id:
            if not build.label:
                build.label = source.revision.message.split('\n')[0]
            if not build.author_id:
                build.author_id = source.revision.author_id
        assert build.source_id
        assert build.author_id
        db.session.add(build)
        db.session.commit()

        return self.respond_with_schema(build_schema, build)
