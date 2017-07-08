import factory

from zeus import models
from zeus.constants import Result, Status

from .types import GUIDFactory


class BuildFactory(factory.Factory):
    id = GUIDFactory()
    source = factory.SubFactory('zeus.factories.SourceFactory')
    repository = factory.SelfAttribute('source.repository')
    result = Result.passed
    status = Status.finished
    date_created = factory.Faker('date_time')
    date_started = factory.Faker('past_date')
    date_finished = factory.Faker('date_time')

    class Meta:
        model = models.Build
