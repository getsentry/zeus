# https://github.com/pallets/click/issues/85#issuecomment-503464628
import asyncio
import asyncpg

from flask import current_app
from functools import wraps


def coroutine(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        return asyncio.run(f(*args, **kwargs))

    return wrapper


async def create_db_pool(current_app=current_app):
    return await asyncpg.create_pool(
        host=current_app.config["DB_HOST"],
        port=current_app.config["DB_PORT"],
        user=current_app.config["DB_USER"],
        password=current_app.config["DB_PASSWORD"],
        database=current_app.config["DB_NAME"],
        # we want to rely on pgbouncer
        statement_cache_size=0,
    )
