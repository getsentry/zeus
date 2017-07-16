from sqlalchemy.exc import IntegrityError

from zeus import auth
from zeus.config import db
from zeus.exceptions import IdentityNeedsUpgrade
from zeus.models import (
    Identity, ItemOption, Organization, OrganizationAccess, Project, Repository, RepositoryAccess,
    RepositoryBackend, RepositoryProvider, RepositoryStatus
)
from zeus.tasks import import_repo
from zeus.utils.github import GitHubClient
from zeus.utils import ssh

from .base import Resource
from ..schemas import GitHubRepositorySchema, ProjectSchema

github_repo_schema = GitHubRepositorySchema(strict=True)
project_schema = ProjectSchema(strict=True)


class GitHubProjectsResource(Resource):
    def get_client(self, user):
        identity = Identity.query.filter(
            Identity.provider == 'github', Identity.user_id == user.id
        ).first()
        if 'repo' not in identity.config['scopes']:
            raise IdentityNeedsUpgrade(
                scope='repo',
                identity=identity,
            )
        return GitHubClient(token=identity.config['access_token'])

    def get(self):
        """
        Return a list of GitHub repos the user has access to.
        """
        user = auth.get_current_user()
        assert user

        github = self.get_client(user)

    def post(self):
        """
        Add a Zeus project from a GitHub repo.
        """
        user = auth.get_current_user()
        assert user

        result = self.schema_from_request(github_repo_schema, partial=True)
        if result.errors:
            return self.respond(result.errors, 403)
        data = result.data

        github = self.get_client(user)
        repo_data = github.get('/repos/{}'.format(data['name']))

        org_name, project_name = data['name'].split('/', 1)

        # we now need to upsert:
        # - organization
        # - repository
        # - project
        org = Organization.query.filter(
            Organization.name == org_name,
        ).first()
        if not org:
            org = Organization(
                name=org_name,
            )
            db.session.add(org)
            db.session.flush()

        try:
            with db.session.begin_nested():
                db.session.add(OrganizationAccess(
                    organization=org,
                    user=user,
                ))
                db.session.flush()
        except IntegrityError:
            pass

        repo, created = Repository.query.filter(
            Repository.organization_id == org.id,
            Repository.provider == RepositoryProvider.github,
            Repository.external_id == str(repo_data['id']),
        ).first()
        if repo is None:
            # bind various github specific attributes
            repo = Repository(
                organization=org,
                backend=RepositoryBackend.git,
                provider=RepositoryProvider.github,
                status=RepositoryStatus.active,
                external_id=str(repo_data['id']),
                url=repo_data['clone_url'],
                data={'github': {
                    'full_name': repo_data['full_name']
                }},
            ), True
            db.session.add(repo)

            # generate a new private key for use on github
            key = ssh.generate_key()
            db.session.add(
                ItemOption(
                    item_id=repo.id,
                    name='auth.private-key',
                    value=key.private_key,
                )
            )

            # register key with github
            github.post(
                '/repos/{}/keys'.format(repo.data['github']['full_name']),
                json={
                    'title': 'zeus',
                    'key': key.public_key,
                    'read_only': True,
                }
            )

            db.session.commit()

            import_repo.delay(repo_id=repo.id)

        try:
            with db.session.begin_nested():
                db.session.add(RepositoryAccess(
                    organization=org,
                    repository=repo,
                    user=user,
                ))
                db.session.flush()
        except IntegrityError:
            pass

        db.session.commit()

        project = Project.query.filter(
            Project.organization_id == org.id,
            Project.name == repo_data['name'],
        ).first()
        if not project:
            project = Project(
                name=repo_data['name'],
                repository=repo,
                organization=org,
            )
            db.session.add(project)
            db.session.commit()

        return self.respond_with_schema(project_schema, project)
