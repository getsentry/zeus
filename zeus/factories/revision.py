import factory
import factory.faker

from datetime import timedelta
from faker import Factory

faker = Factory.create()

from zeus import models
from zeus.utils import timezone

from .base import ModelFactory


class RevisionFactory(ModelFactory):
    sha = factory.Faker("sha1")
    repository = factory.SubFactory("zeus.factories.RepositoryFactory")
    repository_id = factory.SelfAttribute("repository.id")
    author = factory.SubFactory(
        "zeus.factories.AuthorFactory", repository=factory.SelfAttribute("..repository")
    )
    author_id = factory.SelfAttribute("author.id")
    message = factory.LazyAttribute(
        lambda o: "{}\n\n{}".format(faker.sentence(), faker.sentence())
    )
    date_created = factory.LazyAttribute(
        lambda o: timezone.now() - timedelta(minutes=30)
    )

    class Meta:
        model = models.Revision
