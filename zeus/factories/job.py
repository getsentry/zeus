import factory

from zeus import models
from zeus.constants import Result, Status

from .types import GUIDFactory


class JobFactory(factory.Factory):
    id = GUIDFactory()
    repository = factory.SubFactory('zeus.factories.RepositoryFactory')
    build = factory.SubFactory('zeus.factories.BuildFactory')
    result = Result.passed
    status = Status.finished
    date_created = factory.Faker('date_time')
    date_started = factory.Faker('past_date')
    date_finished = factory.Faker('date_time')

    class Meta:
        model = models.Job
