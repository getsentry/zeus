from flask import request
from sqlalchemy.exc import IntegrityError

from zeus import auth
from zeus.config import db, redis
from zeus.constants import Permission
from zeus.exceptions import IdentityNeedsUpgrade
from zeus.models import (
    ItemOption,
    Repository,
    RepositoryAccess,
    RepositoryBackend,
    RepositoryProvider,
    RepositoryStatus,
)
from zeus.tasks import import_repo
from zeus.utils import ssh
from zeus.vcs.providers.github import GitHubRepositoryProvider

from .base import Resource
from ..schemas import RepositorySchema

repo_schema = RepositorySchema(strict=True)


class GitHubRepositoriesResource(Resource):
    def get(self):
        """
        Return a list of GitHub repositories avaiable to the current user.
        """
        no_cache = request.args.get("noCache") in ("1", "true")
        include_private = request.args.get("private") in ("1", "true")
        owner_name = request.args.get("orgName")
        user = auth.get_current_user()
        provider = GitHubRepositoryProvider(cache=not no_cache)
        try:
            repo_list = provider.get_repos_for_owner(
                user=user, owner_name=owner_name, include_private_repos=include_private
            )
        except IdentityNeedsUpgrade as exc:
            return self.respond(
                {
                    "provider": "github",
                    "error": "identity_needs_upgrade",
                    "url": exc.get_upgrade_url(),
                },
                401,
            )

        active_repo_ids = frozenset(
            r[0]
            for r in db.session.query(Repository.external_id)
            .join(RepositoryAccess, RepositoryAccess.repository_id == Repository.id)
            .filter(
                Repository.provider == RepositoryProvider.github,
                RepositoryAccess.user_id == user.id,
            )
        )

        return [
            {
                "name": r["config"]["full_name"],
                "permissions": {
                    "read": Permission.read in r["permission"],
                    "write": Permission.write in r["permission"],
                    "admin": Permission.admin in r["permission"],
                },
                "active": str(r["id"]) in active_repo_ids,
            }
            for r in repo_list
        ]

    def delete(self):
        """
        Deactivate a GitHub repository.
        """
        repo_name = (request.get_json() or {}).get("name")
        if not repo_name:
            return self.error("missing repo_name parameter")

        raise NotImplementedError

    def post(self):
        """
        Activate a GitHub repository.
        """
        repo_name = (request.get_json() or {}).get("name")
        if not repo_name:
            return self.error("missing repo_name parameter")

        owner_name, repo_name = repo_name.split("/", 1)

        user = auth.get_current_user()
        provider = GitHubRepositoryProvider(cache=False)
        try:
            repo_data = provider.get_repo(
                user=user, owner_name=owner_name, repo_name=repo_name
            )
        except IdentityNeedsUpgrade as exc:
            return self.respond(
                {
                    "provider": "github",
                    "error": "identity_needs_upgrade",
                    "url": exc.get_upgrade_url(),
                },
                401,
            )

        if Permission.admin not in repo_data["permission"]:
            return self.respond(
                {"message": "Insufficient permissions to activate repository"}, 403
            )

        lock_key = "repo:{provider}/{owner_name}/{repo_name}".format(
            provider="github", owner_name=owner_name, repo_name=repo_name
        )
        with redis.lock(lock_key):
            try:
                with db.session.begin_nested():
                    # bind various github specific attributes
                    repo = Repository(
                        backend=RepositoryBackend.git,
                        provider=RepositoryProvider.github,
                        status=RepositoryStatus.active,
                        external_id=str(repo_data["id"]),
                        owner_name=owner_name,
                        name=repo_name,
                        url=repo_data["url"],
                        data=repo_data["config"],
                    )
                    db.session.add(repo)
                    db.session.flush()
            except IntegrityError:
                repo = (
                    Repository.query.unrestricted_unsafe()
                    .filter(
                        Repository.provider == RepositoryProvider.github,
                        Repository.external_id == str(repo_data["id"]),
                    )
                    .first()
                )
                # it's possible to get here if the "full name" already exists
                assert repo
                needs_configured = repo.status == RepositoryStatus.inactive
                if needs_configured:
                    repo.status = RepositoryStatus.active
                    db.session.add(repo)
            else:
                needs_configured = True
            if needs_configured:
                # generate a new private key for use on github
                key = ssh.generate_key()
                db.session.add(
                    ItemOption(
                        item_id=repo.id, name="auth.private-key", value=key.private_key
                    )
                )

                # register key with github
                provider.add_key(
                    user=user, repo_name=repo_name, owner_name=owner_name, key=key
                )

                # we need to commit before firing off the task
                db.session.commit()

                import_repo.delay(repo_id=repo.id)

        try:
            with db.session.begin_nested():
                db.session.add(
                    RepositoryAccess(
                        repository_id=repo.id,
                        user_id=user.id,
                        permission=repo_data["permission"],
                    )
                )
                db.session.flush()
        except IntegrityError:
            pass

        db.session.commit()

        return self.respond_with_schema(repo_schema, repo, 201)
