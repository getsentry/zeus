import factory

from zeus import models
from zeus.constants import Result, Status

from .types import GUIDFactory


class JobFactory(factory.Factory):
    id = GUIDFactory()
    build = factory.SubFactory('zeus.factories.BuildFactory')
    build_id = factory.SelfAttribute('build.id')
    repository = factory.SelfAttribute('build.repository')
    repository_id = factory.SelfAttribute('build.repository_id')
    result = Result.passed
    status = Status.finished
    date_created = factory.Faker('date_time')
    date_started = factory.Faker('past_date')
    date_finished = factory.Faker('date_time')

    class Meta:
        model = models.Job
