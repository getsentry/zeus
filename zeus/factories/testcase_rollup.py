import factory
import factory.fuzzy

from faker import Factory

faker = Factory.create()

from zeus import models

from .base import ModelFactory
from .types import GUIDFactory


class TestCaseRollupFactory(ModelFactory):
    id = GUIDFactory()
    name = factory.LazyAttribute(
        lambda o: "tests.%s.%s.%s" % (faker.word(), faker.word(), faker.word())
    )
    repository = factory.SubFactory("zeus.factories.RepositoryFactory")
    repository_id = factory.SelfAttribute("repository.id")
    total_runs = factory.LazyAttribute(lambda o: o.runs_passed + o.runs_failed)
    total_duration = factory.Faker("random_int", min=1, max=100000)
    runs_passed = factory.Faker("random_int", min=1, max=100)
    runs_failed = factory.Faker("random_int", min=1, max=100)

    class Meta:
        model = models.TestCaseRollup
