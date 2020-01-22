import factory

from zeus import models
from zeus.utils import timezone

from .base import ModelFactory
from .types import GUIDFactory


class HookFactory(ModelFactory):
    id = GUIDFactory()
    repository = factory.SubFactory("zeus.factories.RepositoryFactory")
    repository_id = factory.SelfAttribute("repository.id")
    provider = "travis"
    config = factory.LazyAttribute(lambda x: {"domain": "api.travis-ci.com"})
    date_created = factory.LazyAttribute(lambda o: timezone.now())

    class Meta:
        model = models.Hook

    class Params:
        travis_com = factory.Trait(
            provider="travis", config={"domain": "api.travis-ci.com"}
        )
        travis_org = factory.Trait(
            provider="travis", config={"domain": "api.travis-ci.org"}
        )
