import click

from random import randint
from sqlalchemy.exc import IntegrityError

from zeus import factories, models
from zeus.config import db
from zeus.db.utils import try_create
from zeus.tasks import aggregate_build_stats_for_job

from .base import cli


def mock_single_repository(builds=10, user_ids=()):
    org = factories.OrganizationFactory.build()
    try:
        with db.session.begin_nested():
            db.session.add(org)
    except IntegrityError:
        org = models.Organization.query.unrestricted_unsafe().filter(
            models.Organization.name == org.name
        ).first()

    click.echo('Created {!r}'.format(org))

    for user_id in user_ids:
        try_create(models.OrganizationAccess, {
            'organization_id': org.id,
            'user_id': user_id,
        })

    repo = factories.RepositoryFactory(
        organization=org,
        status=models.RepositoryStatus.active,
    )

    for user_id in user_ids:
        try_create(
            models.RepositoryAccess, {
                'organization_id': org.id,
                'repository_id': repo.id,
                'user_id': user_id,
            }
        )

    project = factories.ProjectFactory.build(
        repository=repo,
    )
    try:
        with db.session.begin_nested():
            db.session.add(project)
    except IntegrityError:
        project = models.Project.query.unrestricted_unsafe().filter(
            models.Project.organization_id == org.id, models.Project.name == project.name
        ).first()

    db.session.commit()

    parent_revision = None
    for n in range(builds):
        revision = factories.RevisionFactory.create(
            repository=repo,
            parents=[parent_revision.sha] if parent_revision else None,
        )
        source = factories.SourceFactory.create(
            revision=revision,
            patch=factories.PatchFactory(
                parent_revision=parent_revision,
            ) if parent_revision else None,
        )
        parent_revision = revision
        build = factories.BuildFactory.create(project=project, source=source)
        click.echo('Created {!r}'.format(build))

        for n in range(1, 4):
            has_failure = randint(0, 2) == 0
            job = factories.JobFactory.create(build=build, failed=has_failure)

            for n in range(randint(0, 50)):
                test_failed = has_failure and randint(0, 5) == 0
                factories.TestCaseFactory.create(
                    job=job,
                    failed=test_failed,
                    passed=not test_failed,
                )
            for n in range(randint(0, 50)):
                factories.FileCoverageFactory.create(job=job, in_diff=randint(0, 5) == 0)
            db.session.commit()
            aggregate_build_stats_for_job(job_id=job.id)

        db.session.commit()


@cli.group('mocks')
def mocks():
    pass


@mocks.command('load-all')
def load_all():
    user_ids = [u for u, in db.session.query(models.User.id)]
    for n in range(3):
        mock_single_repository(user_ids=user_ids)
