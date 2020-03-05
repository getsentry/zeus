import factory
import factory.faker

from datetime import timedelta
from faker import Factory

faker = Factory.create()

from zeus import models
from zeus.config import db
from zeus.utils import timezone

from .base import ModelFactory


class RevisionFactory(ModelFactory):
    sha = factory.Faker("sha1")
    repository = factory.SubFactory("zeus.factories.RepositoryFactory")
    repository_id = factory.SelfAttribute("repository.id")
    message = factory.LazyAttribute(
        lambda o: "{}\n\n{}".format(faker.sentence(), faker.sentence())
    )
    date_created = factory.LazyAttribute(
        lambda o: timezone.now() - timedelta(minutes=30)
    )

    @factory.post_generation
    def authors(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for author in extracted:
                self.authors.append(author)

        db.session.flush()

    class Meta:
        model = models.Revision
