import factory

from datetime import timedelta
from faker import Factory
from random import randint

from zeus import models
from zeus.utils import timezone

from .base import ModelFactory
from .types import GUIDFactory

faker = Factory.create()


class ChangeRequestFactory(ModelFactory):
    id = GUIDFactory()
    message = factory.faker.Faker('sentence')
    author = factory.SubFactory(
        'zeus.factories.AuthorFactory', repository=factory.SelfAttribute('..repository')
    )
    author_id = factory.SelfAttribute('author.id')
    parent_revision = factory.SubFactory('zeus.factories.RevisionFactory')
    parent_revision_sha = factory.SelfAttribute('parent_revision.sha')
    repository = factory.SelfAttribute('parent_revision.repository')
    repository_id = factory.SelfAttribute('parent_revision.repository_id')
    date_created = factory.LazyAttribute(
        lambda o: timezone.now() - timedelta(minutes=30))

    class Meta:
        model = models.ChangeRequest

    class Params:
        github = factory.Trait(
            provider='github',
            external_id=factory.LazyAttribute(
                lambda o: str(randint(10000, 999999))),
            head_revision_sha=factory.SelfAttribute('head_revision.sha'),
            head_revision=factory.SubFactory('zeus.factories.RevisionFactory'),
            url=factory.LazyAttribute(lambda o: 'https://github.com/{}/{}/issues/{}'.format(
                o.repository.owner_name,
                o.repository.name,
                o.external_id,
            )),
        )
