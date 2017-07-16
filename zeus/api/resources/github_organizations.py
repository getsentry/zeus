from zeus import auth
from zeus.models import Identity
from zeus.utils.github import GitHubClient

from .base import Resource


class GitHubOrganizationsResource(Resource):
    def get_github_client(self, user):
        assert user
        identity = Identity.query.filter(
            Identity.provider == 'github', Identity.user_id == user.id
        ).first()
        return GitHubClient(token=identity.config['access_token']), identity

    def get(self):
        """
        Return a list of GitHub organizations avaiable to the current user.
        """
        user = auth.get_current_user()
        github, identity = self.get_github_client(user)
        response = github.get('/user/orgs')

        return [{
            'name': r['login'],
        } for r in response]
