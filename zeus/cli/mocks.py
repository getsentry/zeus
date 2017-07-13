import click

from random import randint
from sqlalchemy.exc import IntegrityError

from zeus import factories, models
from zeus.config import db
from zeus.db.utils import try_create
from zeus.tasks import aggregate_build_stats_for_job

from .base import cli


def mock_single_repository(builds=10, user_ids=()):
    repo = factories.RepositoryFactory.build(
        status=models.RepositoryStatus.active,
    )
    try:
        with db.session.begin_nested():
            db.session.add(repo)
    except IntegrityError:
        repo = models.Repository.query.unrestricted_unsafe().filter(
            models.Repository.name == repo.name
        ).first()
        if not repo:
            repo = models.Repository.query.unrestricted_unsafe().filter(
                models.Repository.url == repo.url
            ).first()
    else:
        click.echo('Created {!r}'.format(repo))

    for user_id in user_ids:
        try_create(models.RepositoryAccess, {
            'repository_id': repo.id,
            'user_id': user_id,
        })

    db.session.commit()

    for n in range(builds):
        revision = factories.RevisionFactory(
            repository=repo,
        )
        source = factories.SourceFactory(revision=revision)
        build = factories.BuildFactory(source=source)
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
            aggregate_build_stats_for_job(job_id=job.id, _app_context=False)

        db.session.commit()


@cli.group('mocks')
def mocks():
    pass


@mocks.command('load-all')
def load_all():
    user_ids = [u for u, in db.session.query(models.User.id)]
    for n in range(3):
        mock_single_repository(user_ids=user_ids)
