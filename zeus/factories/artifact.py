import factory

from zeus import models

from .base import ModelFactory
from .types import GUIDFactory


class ArtifactFactory(ModelFactory):
    id = GUIDFactory()
    job = factory.SubFactory('zeus.factories.JobFactory')
    job_id = factory.SelfAttribute('job.id')
    repository = factory.SelfAttribute('job.repository')
    repository_id = factory.SelfAttribute('job.repository_id')
    name = factory.Faker('file_name')

    class Meta:
        model = models.Artifact
