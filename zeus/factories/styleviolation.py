import factory
import factory.fuzzy

from faker import Factory

faker = Factory.create()

from zeus import models
from zeus.constants import Severity

from .base import ModelFactory
from .types import GUIDFactory


class StyleViolationFactory(ModelFactory):
    id = GUIDFactory()
    filename = factory.LazyAttribute(
        lambda o: "tests/%s/%s/%s.js" % (faker.word(), faker.word(), faker.word())
    )
    job = factory.SubFactory("zeus.factories.JobFactory")
    job_id = factory.SelfAttribute("job.id")
    repository = factory.SelfAttribute("job.repository")
    repository_id = factory.SelfAttribute("repository.id")
    severity = factory.Iterator(
        [Severity.error, Severity.warning, Severity.info, Severity.ignore]
    )
    message = factory.faker.Faker("sentence")
    lineno = factory.faker.Faker("pyint")
    colno = factory.faker.Faker("pyint")
    source = factory.LazyAttribute(lambda o: "eslint.{}".format(faker.word()))

    class Meta:
        model = models.StyleViolation
