import asyncio
import asyncpg

from aiohttp.web import Application
from flask import current_app
from lru import LRU

from zeus.utils.sentry import span

from .api import register_api_routes
from .utils import save_revision

_revision_cache = LRU(1000)


@span("worker")
async def worker(db_pool, queue: asyncio.Queue):
    """
    Async worker to perform tasks like persisting revisions to the database.
    """

    while True:
        event, payload = await queue.get()
        if event == "revision":
            key = (payload["repo_id"], payload["revision"].sha)
            if key in _revision_cache:
                continue
            async with db_pool.acquire() as conn:
                await save_revision(conn, payload["repo_id"], payload["revision"])
            _revision_cache[key] = 1
        current_app.logger.debug("worker.event event=%s qsize=%s", event, queue.qsize())


async def build_app(loop=None) -> Application:
    app = Application(loop=loop, logger=current_app.logger, debug=current_app.debug)

    register_api_routes(app)

    app["db_pool"] = await asyncpg.create_pool(
        host=current_app.config["DB_HOST"],
        port=current_app.config["DB_PORT"],
        user=current_app.config["DB_USER"],
        password=current_app.config["DB_PASSWORD"],
        database=current_app.config["DB_NAME"],
        # we want to rely on pgbouncer
        statement_cache_size=0,
    )
    app["queue"] = asyncio.Queue(loop=loop)

    return app


async def build_server(loop, host: str, port: int):
    app = await build_app(loop=loop)

    asyncio.ensure_future(worker(app["db_pool"], app["queue"]))

    return await loop.create_server(app.make_handler(), host, port)
