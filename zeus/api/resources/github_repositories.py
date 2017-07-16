from flask import request
from sqlalchemy.exc import IntegrityError

from zeus import auth
from zeus.config import db
from zeus.exceptions import IdentityNeedsUpgrade
from zeus.models import (
    Identity, ItemOption, Repository, RepositoryAccess, RepositoryBackend, RepositoryProvider,
    RepositoryStatus
)
from zeus.tasks import import_repo
from zeus.utils import ssh
from zeus.utils.github import GitHubClient

from .base import Resource
from ..schemas import GitHubRepositorySchema, RepositorySchema

repo_schema = RepositorySchema(strict=True)
github_repo_schema = GitHubRepositorySchema(strict=True)
repos_schema = RepositorySchema(many=True, strict=True)


class GitHubRepositoriesResource(Resource):
    def get_github_client(self, user):
        assert user
        identity = Identity.query.filter(
            Identity.provider == 'github', Identity.user_id == user.id
        ).first()
        if 'repo' not in identity.config['scopes']:
            raise IdentityNeedsUpgrade(
                scope='repo',
                identity=identity,
            )
        return GitHubClient(token=identity.config['access_token']), identity

    def get(self):
        """
        Return a list of GitHub repositories avaiable to the current user.
        """
        user = auth.get_current_user()
        try:
            github, identity = self.get_github_client(user)
        except IdentityNeedsUpgrade as exc:
            return self.respond(
                {
                    'error': 'identity_needs_upgrade',
                    'url': exc.get_upgrade_url(),
                }, 401
            )

        # the results of =these API calls are going to need cached
        owner_name = request.args.get('owner_name')
        if not owner_name:
            response = github.get('/user/repos')
        else:
            response = github.get('/orgs/{}/repos'.format(owner_name))

        active_repo_ids = frozenset(
            db.session.query(Repository.external_id).filter(
                Repository.provider == RepositoryProvider.github,
            )
        )

        return [
            {
                'name': r['full_name'],
                'active': str(r['id']) in active_repo_ids,
            } for r in response
        ]

    def delete(self):
        """
        Deactivate a GitHub repository.
        """
        repo_name = (request.get_json() or {}).get('name')
        if not repo_name:
            return self.error('missing repo_name parameter')

        raise NotImplementedError

    def post(self):
        """
        Activate a GitHub repository.
        """
        repo_name = (request.get_json() or {}).get('name')
        if not repo_name:
            return self.error('missing repo_name parameter')

        user = auth.get_current_user()
        try:
            github, _ = self.get_github_client(user)
        except IdentityNeedsUpgrade as exc:
            return self.respond(
                {
                    'error': 'identity_needs_upgrade',
                    'url': exc.get_upgrade_url(),
                }, 401
            )

        # fetch repository details using their credentials
        repo_data = github.get('/repos/{}'.format(repo_name))
        owner_name, repo_name = repo_data['full_name'].split('/', 1)

        repo = Repository.query.filter(
            Repository.provider == RepositoryProvider.github,
            Repository.external_id == str(repo_data['id']),
        ).first()
        if repo is None:
            # bind various github specific attributes
            repo = Repository(
                backend=RepositoryBackend.git,
                provider=RepositoryProvider.github,
                status=RepositoryStatus.active,
                external_id=str(repo_data['id']),
                owner_name=owner_name,
                name=repo_name,
                url=repo_data['clone_url'],
                data={'github': {
                    'full_name': repo_data['full_name']
                }},
            )
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

            import_repo.delay(repo_id=repo.id)

        try:
            with db.session.begin_nested():
                db.session.add(RepositoryAccess(
                    repository_id=repo.id,
                    user_id=user.id,
                ))
                db.session.flush()
        except IntegrityError:
            pass

        db.session.commit()
        return self.respond_with_schema(repo_schema, repo, 201)
