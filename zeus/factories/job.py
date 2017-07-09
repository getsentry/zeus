import factory

from datetime import timedelta
from faker import Factory
faker = Factory.create()

from zeus import models
from zeus.constants import Result, Status

from .types import GUIDFactory


class JobFactory(factory.Factory):
    id = GUIDFactory()
    build = factory.SubFactory('zeus.factories.BuildFactory')
    build_id = factory.SelfAttribute('build.id')
    repository = factory.SelfAttribute('build.repository')
    repository_id = factory.SelfAttribute('build.repository_id')
    result = factory.Iterator([Result.failed, Result.passed])
    status = factory.Iterator([Status.queued, Status.in_progress, Status.finished])
    date_created = factory.LazyAttribute(lambda o: faker.date_time_between('-30m', '-5m'))
    date_started = factory.LazyAttribute(
        lambda o: (
            faker.date_time_between(o.date_created, o.date_created + timedelta(minutes=10)) if o.status in [Status.finished, Status.in_progress] else None
        )
    )
    date_finished = factory.LazyAttribute(
        lambda o: faker.date_time_between(o.date_started, o.date_started + timedelta(minutes=30)) if o.status == Status.finished else None
    )

    class Meta:
        model = models.Job

    class Params:
        queued = factory.Trait(result=Result.unknown, status=Status.queued)
        in_progress = factory.Trait(result=Result.unknown, status=Status.in_progress)
        failed = factory.Trait(result=Result.failed, status=Status.finished)
        passed = factory.Trait(result=Result.passed, status=Status.finished)
        aborted = factory.Trait(result=Result.aborted, status=Status.finished)
