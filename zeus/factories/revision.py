import factory

from zeus import models


class RevisionFactory(factory.Factory):
    sha = factory.Faker('sha1')
    repository = factory.SubFactory('zeus.factories.RepositoryFactory')

    class Meta:
        model = models.Revision
