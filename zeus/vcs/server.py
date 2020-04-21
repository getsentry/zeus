import asyncio

from aiohttp.web import Application
from flask import current_app
from lru import LRU

from zeus.constants import VCS_CLEANUP_INTERVAL
from zeus.utils.asyncio import create_db_pool
from zeus.utils.sentry import span

from .api import register_api_routes
from .utils import cleanup, save_revision

_revision_cache = LRU(100000)


@span("worker")
async def worker(db_pool, queue: asyncio.Queue):
    """
    Async worker to perform tasks like persisting revisions to the database.
    """

    while True:
        event, payload = await queue.get()
        try:
            if event == "revision":
                key = (payload["repo_id"], payload["revision"].sha)
                if key in _revision_cache:
                    continue
                async with db_pool.acquire() as conn:
                    await save_revision(conn, payload["repo_id"], payload["revision"])
                _revision_cache[key] = 1
            if event == "cleanup":
                repo_id = payload["repo_id"]
                async with db_pool.acquire() as conn:
                    await cleanup(conn, repo_id)
        except Exception:
            current_app.logger.error(
                "worker.event-error event=%s", event, exc_info=True
            )
        current_app.logger.debug("worker.event event=%s qsize=%s", event, queue.qsize())


@span("cleanup_scheduler")
async def cleanup_scheduler(db_pool, queue: asyncio.Queue):
    """
    Automatically schedules cleanup tasks for repositories.
    """
    while True:
        async with db_pool.acquire() as conn:
            repo_list = list(
                await conn.fetch(
                    """
                    SELECT DISTINCT repository.id
                    FROM repository
                    LEFT JOIN itemoption
                    ON itemoption.item_id = repository.id
                    AND itemoption.name = 'cleanup.last-run'
                    WHERE repository.status != 0
                    AND (itemoption.value IS NULL
                        OR (itemoption.value::float + {}) < extract(epoch from now()))
                """.format(
                        VCS_CLEANUP_INTERVAL
                    )
                )
            )
        for (repo_id,) in repo_list:
            current_app.logger.info("cleanup-scheduler.cleanup repo_id=%s", repo_id)
            async with db_pool.acquire() as conn:
                await cleanup(conn, repo_id)
        await asyncio.sleep(60)


async def build_app(loop=None) -> Application:
    app = Application(loop=loop, logger=current_app.logger, debug=current_app.debug)

    register_api_routes(app)

    app["db_pool"] = await create_db_pool()
    app["queue"] = asyncio.Queue(loop=loop)

    return app


async def build_server(loop, host: str, port: int):
    app = await build_app(loop=loop)

    asyncio.ensure_future(worker(app["db_pool"], app["queue"]))
    asyncio.ensure_future(cleanup_scheduler(app["db_pool"], app["queue"]))

    return await loop.create_server(app.make_handler(), host, port)
