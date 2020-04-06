import asyncio

from aiohttp.web import Application
from flask import current_app
from lru import LRU

from zeus.utils.asyncio import create_db_pool
from zeus.utils.sentry import span

from .api import register_api_routes
from .utils import save_revision

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
        except Exception:
            current_app.logger.error(
                "worker.event-error event=%s", event, exc_info=True
            )
        current_app.logger.debug("worker.event event=%s qsize=%s", event, queue.qsize())


async def build_app(loop=None) -> Application:
    app = Application(loop=loop, logger=current_app.logger, debug=current_app.debug)

    register_api_routes(app)

    app["db_pool"] = await create_db_pool()
    app["queue"] = asyncio.Queue(loop=loop)

    return app


async def build_server(loop, host: str, port: int):
    app = await build_app(loop=loop)

    asyncio.ensure_future(worker(app["db_pool"], app["queue"]))

    return await loop.create_server(app.make_handler(), host, port)
