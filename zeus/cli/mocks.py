import click

from random import randint
from sqlalchemy.exc import IntegrityError

from zeus import factories, models
from zeus.config import db
from zeus.db.utils import try_create
from zeus.tasks import aggregate_build_stats_for_job

from .base import cli


def mock_single_repository(builds=10, user_ids=()):
    repo = factories.RepositoryFactory(
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

    db.session.commit()

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
        db.session.add(revision)
        db.session.flush()

        source = factories.SourceFactory(revision=revision)
        db.session.add(source)
        db.session.flush()

        build = factories.BuildFactory(source=source)
        db.session.add(build)
        db.session.flush()
        click.echo('Created {!r}'.format(build))

        for job in factories.JobFactory.create_batch(size=randint(1, 10), build=build):
            db.session.add(job)
            db.session.add_all(factories.TestCaseFactory.create_batch(size=randint(0, 50), job=job))
            db.session.add_all(
                factories.FileCoverageFactory.create_batch(size=randint(0, 50), job=job)
            )
            db.session.flush()
            aggregate_build_stats_for_job(job.id)

        db.session.commit()


@cli.group('mocks')
def mocks():
    pass


@mocks.command('load-all')
def load_all():
    user_ids = [u for u, in db.session.query(models.User.id)]
    for n in range(3):
        mock_single_repository(user_ids=user_ids)
