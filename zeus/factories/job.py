import factory

from zeus import models
from zeus.constants import Result, Status

from .types import GUIDFactory


class JobFactory(factory.Factory):
    id = GUIDFactory()
    repository = factory.SubFactory('zeus.factories.RepositoryFactory')
    build = factory.SubFactory('zeus.factories.BuildFactory')
    date_started = factory.Faker('past_date', start_date='-5m')
    date_finished = factory.Faker('date_time')
    result = Result.passed
    status = Status.finished

    class Meta:
        model = models.Job
