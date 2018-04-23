from zeus import auth
from zeus.vcs.providers.github import GitHubRepositoryProvider

from .base import Resource


class GitHubOrganizationsResource(Resource):

    def get(self):
        """
        Return a list of GitHub organizations avaiable to the current user.
        """
        user = auth.get_current_user()
        provider = GitHubRepositoryProvider()
        return provider.get_owners(user)
