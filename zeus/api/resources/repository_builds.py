from flask import current_app, request
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import contains_eager, joinedload, subqueryload_all

from zeus import auth
from zeus.config import db
from zeus.models import Author, Build, Email, Repository, Revision, Source
from zeus.pubsub.utils import publish
from zeus.vcs.base import UnknownRevision

from .base_repository import BaseRepositoryResource
from ..schemas import BuildSchema, BuildCreateSchema

build_create_schema = BuildCreateSchema(strict=True)
build_schema = BuildSchema(strict=True)
builds_schema = BuildSchema(many=True, strict=True)


def identify_revision(repository, treeish):
    """
    Attempt to transform a a commit-like reference into a valid revision.
    """
    # try to find it from the database first
    if len(treeish) == 40:
        revision = Revision.query.filter(
            Revision.repository_id == repository.id,
            Revision.sha == treeish,
        ).first()
        if revision:
            return revision

    vcs = repository.get_vcs()
    if not vcs:
        return

    vcs.ensure(update_if_exists=False)

    try:
        commit = next(vcs.log(parent=treeish, limit=1))
    except UnknownRevision:
        vcs.update()
        commit = next(vcs.log(parent=treeish, limit=1))

    revision, _ = commit.save(repository)

    return revision


class RepositoryBuildsResource(BaseRepositoryResource):
    def select_resurce_for_update(self):
        return False

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
        if show == 'mine':
            query = query.filter(
                Source.author_id.in_(
                    db.session.query(Author.id).filter(Author.email.in_(
                        db.session.query(Email.email).filter(
                            Email.user_id == user.id
                        )
                    ))
                )
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

        ref = data.pop('ref', None)
        if ref is None:
            return self.error('missing ref')

        try:
            revision = identify_revision(repo, ref)
        except UnknownRevision:
            current_app.logger.warn('invalid ref received', exc_info=True)
            return self.error('unable to find a revision matching ref')

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

        # TODO(dcramer): need to handle patch case yet
        source = Source.query.options(
            joinedload('author'),
        ).filter(
            Source.revision_sha == revision.sha,
            Source.repository_id == repo.id,
        ).first()

        build = Build(repository=repo, **data)
        # TODO(dcramer): we should convert source in the schema
        build.source = source
        # build.source_id = source.id
        build.author = source.author
        if not source.patch_id:
            if not build.label:
                build.label = source.revision.message.split('\n')[0]

        if not build.label:
            return self.error('missing build label')

        db.session.add(build)

        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return self.respond(status=422)

        result = build_schema.dump(build)
        assert not result.errors, 'this should never happen'
        publish('builds', 'build.create', result.data)
        return self.respond(result.data, 200)
