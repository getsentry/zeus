import factory
import factory.fuzzy

from faker import Factory

faker = Factory.create()

from zeus import models

from .base import ModelFactory
from .types import GUIDFactory


class FailureReasonFactory(ModelFactory):
    id = GUIDFactory()
    job = factory.SubFactory("zeus.factories.JobFactory")
    job_id = factory.SelfAttribute("job.id")
    repository = factory.SelfAttribute("job.repository")
    repository_id = factory.SelfAttribute("repository.id")
    reason = factory.Iterator(list(models.FailureReason.Reason))

    class Meta:
        model = models.FailureReason

    class Params:
        failing_tests = factory.Trait(reason=models.FailureReason.Reason.failing_tests)
        missing_tests = factory.Trait(reason=models.FailureReason.Reason.missing_tests)
