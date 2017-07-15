from sqlalchemy.orm import joinedload, subqueryload_all

from zeus.config import db
from zeus.models import Build, Project, Source

from .base_project import BaseProjectResource
from ..schemas import BuildSchema, BuildCreateSchema

build_create_schema = BuildCreateSchema(strict=True)
build_schema = BuildSchema(strict=True)
builds_schema = BuildSchema(many=True, strict=True)


class ProjectBuildsResource(BaseProjectResource):
    def get(self, project: Project):
        """
        Return a list of builds for the given project.
        """
        query = Build.query.options(
            joinedload('source').joinedload('author'),
            joinedload('source').joinedload('revision'),
            joinedload('source').joinedload('patch'),
            subqueryload_all('stats'),
        ).filter(
            Build.project_id == project.id,
        ).order_by(Build.number.desc()).limit(100)
        return self.respond_with_schema(builds_schema, query)

    def post(self, project: Project):
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
            Source.repository_id == project.repository_id,
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

        build = Build(**data)
        build.organization_id = project.organization_id
        build.project_id = project.id
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
