import factory

from zeus import models

from .types import GUIDFactory


class ArtifactFactory(factory.Factory):
    id = GUIDFactory()
    repository = factory.SubFactory('zeus.factories.RepositoryFactory')
    job = factory.SubFactory('zeus.factories.JobFactory')
    name = factory.Faker('file_name')
    date_created = factory.Faker('date_time')

    class Meta:
        model = models.Artifact
