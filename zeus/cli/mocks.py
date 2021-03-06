import click

from random import choice, randint, randrange
from sqlalchemy.exc import IntegrityError
from typing import Iterable, List, Optional
from uuid import UUID

from zeus import auth, factories, models
from zeus.api.schemas import BuildSchema
from zeus.config import db
from zeus.constants import Result, Status
from zeus.db.utils import try_create
from zeus.pubsub.utils import publish
from zeus.tasks import aggregate_build_stats_for_job
from zeus.utils.asyncio import coroutine, create_db_pool
from zeus.vcs.backends.base import RevisionResult, Vcs
from zeus.vcs.utils import get_vcs, save_revision

from .base import cli

build_schema = BuildSchema()

repo_names = ("sentry", "zeus")


async def find_files_in_repo(vcs: Vcs) -> List[str]:
    await vcs.ensure()
    result = [
        b
        for b in (await vcs.run(["ls-tree", "-r", "--name-only", "master"])).split("\n")
        if b.endswith((".py", ".js", "jsx"))
    ]
    assert result
    return result


async def mock_single_repository(user_ids: Iterable[UUID] = ()):
    repo = factories.RepositoryFactory.build(
        status=models.RepositoryStatus.active,
        github=True,
        owner_name="getsentry",
        name=choice(repo_names),
    )
    try:
        with db.session.begin_nested():
            db.session.add(repo)
    except IntegrityError:
        repo = (
            models.Repository.query.unrestricted_unsafe()
            .filter(
                models.Repository.provider == repo.provider,
                models.Repository.owner_name == repo.owner_name,
                models.Repository.name == repo.name,
            )
            .first()
        )
        click.echo("Using {!r}".format(repo))
    else:
        click.echo("Created {!r}".format(repo))

    for user_id in user_ids:
        try_create(
            models.RepositoryAccess, {"repository_id": repo.id, "user_id": user_id}
        )

    db.session.commit()
    return repo


async def mock_author(repo: models.Repository, user_id: UUID) -> models.Author:
    author = (
        models.Author.query.unrestricted_unsafe()
        .filter(
            models.Author.email.in_(
                db.session.query(models.Email.email).filter(
                    models.Email.user_id == user_id
                )
            )
        )
        .first()
    )
    if author:
        return author

    user = models.User.query.get(user_id)
    return factories.AuthorFactory(repository=repo, email=user.email)


async def load_revisions(
    vcs: Vcs, repo: models.Repository, num_passes=100, db_pool=None
) -> Optional[RevisionResult]:
    if db_pool is None:
        db_pool = await create_db_pool()

    await vcs.ensure()
    num = 0
    has_more = True
    parent = None
    first_revision = None
    while has_more and num < num_passes:
        has_more = False
        for commit in await vcs.log(parent=parent):
            async with db_pool.acquire() as conn:
                await save_revision(conn, repo.id, commit)

            if first_revision is None:
                first_revision = commit
            if parent == commit.sha:
                break

            parent = commit.sha
            has_more = True
        num += 1
    return first_revision


async def mock_revision(
    repo: models.Repository,
    parent_revision: models.Revision = None,
    author: models.Author = None,
) -> models.Revision:
    revision = factories.RevisionFactory.create(
        repository=repo,
        parents=[parent_revision.sha] if parent_revision else None,
        **{"authors": [author]} if author else {}
    )
    return revision


async def mock_build(
    repo: models.Repository,
    revision: models.Revision = None,
    parent_revision: models.Revision = None,
    user_ids=(),
    file_list=(),
    with_change_request=True,
) -> models.Build:
    author: Optional[models.Author] = None
    if user_ids and randint(0, 1) == 0:
        chosen_user_id = choice(user_ids)
        author = await mock_author(repo, chosen_user_id)

    if not revision:
        revision = await mock_revision(repo, parent_revision, author)

    if with_change_request and parent_revision is None:
        parent_revision = factories.RevisionFactory.create(repository=repo)

    if with_change_request:
        factories.ChangeRequestFactory.create(
            repository=repo,
            head_revision=revision,
            head_revision_sha=revision.sha,
            parent_revision=parent_revision,
            github=True,
            **{"authors": [author]} if author else {}
        )

    parent_revision = revision

    build = factories.BuildFactory.create(revision=revision, travis=True)

    data = build_schema.dump(build)
    publish("builds", "build.create", data)
    click.echo("Created {!r}".format(build))

    # we need to find some filenames for the repo
    if file_list is None:
        file_list = await find_files_in_repo(repo)

    for n in range(randint(0, 50)):
        try:
            with db.session.begin_nested():
                factories.FileCoverageFactory.create(
                    filename=choice(file_list), build=build, in_diff=randint(0, 5) == 0
                )
        except IntegrityError:
            continue

    for n in range(1, 4):
        has_failure = randint(0, 2) == 0
        job = factories.JobFactory.create(
            build=build,
            failed=has_failure,
            passed=not has_failure,
            travis=True,
            allow_failure=n == 3,
        )

        for n in range(randint(0, 50)):
            test_failed = has_failure and randint(0, 5) == 0
            factories.TestCaseFactory.create(
                job=job, failed=test_failed, passed=not test_failed
            )
            if has_failure and randint(0, 2) == 0:
                for n in range(1, 5):
                    factories.StyleViolationFactory.create(job=job)

        for n in range(randint(0, 2)):
            bundle = factories.BundleFactory.create(job=job)
            for n in range(randint(0, 4)):
                factories.BundleAssetFactory.create(bundle=bundle, job=job)

        factories.FailureReasonFactory.create(build=build, job=job, failing_tests=True)

        artifact_count = (
            randrange(3)
            if job.status == Status.finished and job.result == Result.passed
            else 0
        )
        for n in range(0, artifact_count):
            factories.ArtifactFactory.create(job=job, repository=repo, finished=True)

        db.session.commit()

        aggregate_build_stats_for_job(job_id=job.id)

        data = build_schema.dump(build)
        publish("builds", "build.update", data)
        click.echo("Created {!r}".format(job))

    db.session.commit()
    return build


@cli.group("mocks")
def mocks():
    pass


@mocks.command("load-all")
@coroutine
async def load_all(repos=3, commits_per_repo=10):
    db_pool = await create_db_pool()

    user_ids = [u for u, in db.session.query(models.User.id)]

    for n in range(repos):
        repo = await mock_single_repository(user_ids=user_ids)

        async with db_pool.acquire() as conn:
            vcs = await get_vcs(conn, repo.id)

        auth.set_current_tenant(auth.RepositoryTenant(repository_id=repo.id))
        file_list = await find_files_in_repo(vcs)
        await load_revisions(vcs, repo)
        revision_iter = iter(
            list(
                models.Revision.query.unrestricted_unsafe()
                .filter(models.Revision.repository_id == repo.id)
                .order_by(models.Revision.date_created.desc())
                .limit(commits_per_repo)
            )
        )
        parent_revision = None
        for n in range(commits_per_repo):
            revision = next(revision_iter)
            build = await mock_build(
                repo,
                parent_revision=parent_revision,
                revision=revision,
                user_ids=user_ids,
                file_list=file_list,
            )
            parent_revision = build.revision


@mocks.command()
@coroutine
async def stream():
    user_ids = [u for u, in db.session.query(models.User.id)]
    repo = mock_single_repository(user_ids=user_ids)

    db_pool = await create_db_pool()
    async with db_pool.acquire() as conn:
        vcs = await get_vcs(conn, repo.id)

    file_list = find_files_in_repo(vcs)
    parent_revision = None
    while True:
        build = await mock_build(
            repo, parent_revision, user_ids=user_ids, file_list=file_list
        )
        parent_revision = build.revision
