import factory

from datetime import timedelta
from faker import Factory
from random import randint

from zeus import models
from zeus.utils import timezone

from .base import ModelFactory
from .types import GUIDFactory
from .repository import RepositoryFactory

faker = Factory.create()


class ChangeRequestFactory(ModelFactory):
    id = GUIDFactory()
    message = factory.faker.Faker("sentence")
    repository = factory.LazyAttribute(
        lambda o: o.parent_revision.repository
        if getattr(o, "parent_revision", None)
        else RepositoryFactory()
    )
    repository_id = factory.SelfAttribute("repository.id")
    author = factory.SubFactory(
        "zeus.factories.AuthorFactory", repository=factory.SelfAttribute("..repository")
    )
    author_id = factory.SelfAttribute("author.id")
    parent_ref = factory.LazyAttribute(
        lambda o: o.parent_revision.sha
        if getattr(o, "parent_revision", None)
        else faker.sha1()
    )
    parent_revision_sha = factory.LazyAttribute(
        lambda o: o.parent_revision.sha if getattr(o, "parent_revision", None) else None
    )
    head_ref = factory.LazyAttribute(
        lambda o: o.head_revision.sha if getattr(o, "head_revision", None) else None
    )
    head_revision_sha = factory.LazyAttribute(
        lambda o: o.head_revision.sha if getattr(o, "head_revision", None) else None
    )
    date_created = factory.LazyAttribute(
        lambda o: timezone.now() - timedelta(minutes=30)
    )

    class Meta:
        model = models.ChangeRequest

    class Params:
        github = factory.Trait(
            provider="github",
            external_id=factory.LazyAttribute(lambda o: str(randint(10000, 999999))),
            head_revision=factory.SubFactory("zeus.factories.RevisionFactory"),
            head_revision_sha=factory.SelfAttribute("head_revision.sha"),
            url=factory.LazyAttribute(
                lambda o: "https://github.com/{}/{}/issues/{}".format(
                    o.repository.owner_name, o.repository.name, o.external_id
                )
            ),
        )
