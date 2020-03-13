import factory
import factory.fuzzy

from faker import Factory

faker = Factory.create()

from zeus import models

from .base import ModelFactory
from .types import GUIDFactory


class FailureReasonFactory(ModelFactory):
    id = GUIDFactory()
    build = factory.SelfAttribute("job.build")
    build_id = factory.SelfAttribute("build.id")
    job = factory.SubFactory("zeus.factories.JobFactory")
    job_id = factory.SelfAttribute("job.id")
    repository = factory.LazyAttribute(
        lambda o: o.job.repository if o.job else o.build.repository if o.build else None
    )
    repository_id = factory.SelfAttribute("repository.id")
    reason = factory.Iterator(list(models.FailureReason.Reason))

    class Meta:
        model = models.FailureReason

    class Params:
        failing_tests = factory.Trait(reason=models.FailureReason.Reason.failing_tests)
        missing_tests = factory.Trait(reason=models.FailureReason.Reason.missing_tests)
        no_jobs = factory.Trait(
            reason=models.FailureReason.Reason.no_jobs, job=None, job_id=None
        )
        unresolvable_ref = factory.Trait(
            reason=models.FailureReason.Reason.unresolvable_ref, job=None, job_id=None
        )
