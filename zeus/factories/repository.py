import factory
import factory.fuzzy

from zeus import models

from .base import ModelFactory
from .types import GUIDFactory


class RepositoryFactory(ModelFactory):
    id = GUIDFactory()
    owner_name = factory.Faker("word")
    name = factory.Faker("word")
    url = factory.LazyAttribute(
        lambda o: "git@github.com:%s/%s.git" % (o.owner_name, o.name)
    )
    backend = models.RepositoryBackend.git
    status = models.RepositoryStatus.active
    provider = models.RepositoryProvider.github
    external_id = factory.LazyAttribute(lambda o: "{}/{}".format(o.owner_name, o.name))
    public = False

    class Meta:
        model = models.Repository

    class Params:
        github = factory.Trait(
            provider=models.RepositoryProvider.github,
            external_id=factory.LazyAttribute(
                lambda o: "{}/{}".format(o.owner_name, o.name)
            ),
            data=factory.LazyAttribute(
                lambda o: {"full_name": "{}/{}".format(o.owner_name, o.name)}
            ),
        )
