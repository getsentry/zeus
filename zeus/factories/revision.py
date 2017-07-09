import factory
import factory.faker

from zeus import models


class RevisionFactory(factory.Factory):
    sha = factory.Faker('sha1')
    repository = factory.SubFactory('zeus.factories.RepositoryFactory')
    repository_id = factory.SelfAttribute('repository.id')
    message = factory.faker.Faker('sentence')
    date_created = factory.Faker('date_time')
    date_committed = factory.Faker('date_time')

    class Meta:
        model = models.Revision
