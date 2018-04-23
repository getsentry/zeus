import factory
import factory.faker

from faker import Factory

faker = Factory.create()

from zeus import models

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

    class Meta:
        model = models.Revision
