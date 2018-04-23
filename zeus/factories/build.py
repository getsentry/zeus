import factory

from datetime import timedelta
from faker import Factory
from random import randint

from zeus import models
from zeus.constants import Result, Status
from zeus.utils import timezone

from .base import ModelFactory
from .types import GUIDFactory

faker = Factory.create()


# TODO(dcramer): this should reflect attributes of its Jobs (and
# then needs updated when children are added)


class BuildFactory(ModelFactory):
    id = GUIDFactory()
    label = factory.faker.Faker("sentence")
    source = factory.SubFactory("zeus.factories.SourceFactory")
    source_id = factory.SelfAttribute("source.id")
    repository = factory.SelfAttribute("source.repository")
    repository_id = factory.SelfAttribute("repository.id")
    result = factory.Iterator([Result.failed, Result.passed])
    status = factory.Iterator([Status.queued, Status.in_progress, Status.finished])
    date_created = factory.LazyAttribute(
        lambda o: timezone.now() - timedelta(minutes=30)
    )
    date_started = factory.LazyAttribute(
        lambda o: (
            faker.date_time_between(
                o.date_created, o.date_created + timedelta(minutes=1)
            ) if o.status in [
                Status.finished, Status.in_progress
            ] else None
        )
    )
    date_finished = factory.LazyAttribute(
        lambda o: faker.date_time_between(
            o.date_started, o.date_started + timedelta(minutes=10)
        ) if o.status
        == Status.finished else None
    )

    class Meta:
        model = models.Build

    class Params:
        queued = factory.Trait(
            result=Result.unknown,
            status=Status.queued,
            date_started=None,
            date_finished=None,
        )
        in_progress = factory.Trait(
            result=Result.unknown, status=Status.in_progress, date_finished=None
        )
        finished = factory.Trait(status=Status.finished)
        failed = factory.Trait(result=Result.failed, status=Status.finished)
        passed = factory.Trait(result=Result.passed, status=Status.finished)
        aborted = factory.Trait(result=Result.aborted, status=Status.finished)
        anonymous = factory.Trait(author=None, author_id=None)
        travis = factory.Trait(
            provider="travis-ci",
            external_id=factory.LazyAttribute(lambda o: str(randint(10000, 999999))),
            url=factory.LazyAttribute(
                lambda o: "https://travis-ci.org/{}/{}/builds/{}".format(
                    o.repository.owner_name, o.repository.name, o.external_id
                )
            ),
        )
