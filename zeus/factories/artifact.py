import factory

from zeus import models

from .base import ModelFactory
from .types import GUIDFactory


class ArtifactFactory(ModelFactory):
    id = GUIDFactory()
    job = factory.SubFactory('zeus.factories.JobFactory')
    job_id = factory.SelfAttribute('job.id')
    project = factory.SelfAttribute('job.project')
    project_id = factory.SelfAttribute('project.id')
    organization = factory.SelfAttribute('project.organization')
    organization_id = factory.SelfAttribute('organization.id')
    name = factory.Faker('file_name')

    class Meta:
        model = models.Artifact
