import factory

from zeus import models

from .base import ModelFactory
from .types import GUIDFactory


class IdentityFactory(ModelFactory):
    id = GUIDFactory()
    user = factory.SubFactory("zeus.factories.UserFactory")
    user_id = factory.SelfAttribute("user.id")
    external_id = factory.Faker("email")

    class Meta:
        model = models.Identity

    class Params:
        github = factory.Trait(
            provider="github",
            scopes=["user:email", "read:org", "repo"],
            config={
                "access_token": "access-token",
                "refresh_token": "refresh-token",
                "login": "test",
            },
        )
        github_barebones = factory.Trait(
            provider="github",
            scopes=["user:email", "read:org"],
            config={
                "access_token": "access-token",
                "refresh_token": "refresh-token",
                "login": "test",
            },
        )
