import factory

from zeus import models

from .types import GUIDFactory


class ArtifactFactory(factory.Factory):
    id = GUIDFactory()
    job = factory.SubFactory('zeus.factories.JobFactory')
    repository = factory.SelfAttribute('job.repository')
    name = factory.Faker('file_name')
    date_created = factory.Faker('date_time')

    class Meta:
        model = models.Artifact
