from flask import request
from sqlalchemy.exc import IntegrityError

from zeus import auth
from zeus.config import db
from zeus.models import (
    Identity, ItemOption, Organization, Repository, RepositoryAccess, RepositoryBackend,
    RepositoryProvider, RepositoryStatus
)
from zeus.tasks import import_repo
from zeus.utils import ssh
from zeus.utils.github import GitHubClient

from .base_organization import BaseOrganizationResource
from ..schemas import GitHubRepositorySchema, RepositorySchema

repo_schema = RepositorySchema(strict=True)
github_repo_schema = GitHubRepositorySchema(strict=True)
repos_schema = RepositorySchema(many=True, strict=True)


class OrganizationRepositoriesResource(BaseOrganizationResource):
    def get(self, org: Organization):
        """
        Return a list of repositories for a given organization.
        """
        query = Repository.query.filter(
            Repository.organization_id == org.id,
        )
        return self.respond_with_schema(repos_schema, query)

    def post(self, org: Organization):
        """
        Create a new repository.
        """
        provider = (request.get_json() or {}).get('provider', 'native')

        if provider == 'github':
            schema = github_repo_schema
        elif provider == 'native':
            schema = repo_schema
        else:
            raise NotImplementedError

        result = self.schema_from_request(schema, partial=True)
        if result.errors:
            return self.respond(result.errors, 403)
        data = result.data

        if provider == 'github':
            # get their credentials
            identity = Identity.query.filter(
                Identity.provider == 'github', Identity.user_id == auth.get_current_user().id
            ).first()
            if 'repo' not in identity.config['scopes']:
                return self.respond(
                    {
                        'needUpgrade': True,
                        'upgradeUrl': '/auth/github/upgrade'
                    }, 401
                )
            assert identity

            # fetch repository details using their credentials
            github = GitHubClient(token=identity.config['access_token'])
            repo_data = github.get('/repos/{}'.format(data['github_name']))

            repo, created = Repository.query.filter(
                Repository.provider == RepositoryProvider.github,
                Repository.external_id == str(repo_data['id']),
            ).first(), False
            if repo is None:
                # bind various github specific attributes
                repo, created = Repository(
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
        elif provider == 'native':
            repo, created = Repository(
                organization=org,
                status=RepositoryStatus.active,
                **data,
            ), True
            db.session.add(repo)

        db.session.flush()

        try:
            with db.session.begin_nested():
                db.session.add(
                    RepositoryAccess(
                        organization=org,
                        repository=repo,
                        user=auth.get_current_user(),
                    )
                )
                db.session.flush()
        except IntegrityError:
            raise
            pass

        db.session.commit()

        if created:
            import_repo.delay(repo_id=repo.id)

        return self.respond_with_schema(repo_schema, repo)
