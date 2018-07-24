import aioredis
import asyncio
import io
import json

from aiohttp.web import Application, Response, StreamResponse
from collections import namedtuple
from functools import wraps
from flask import current_app
from urllib.parse import urlparse
from uuid import uuid4

from zeus import auth
from zeus.config import sentry

Event = namedtuple("Event", ["id", "event", "data"])


def is_valid_origin(request):
    allowed_origins = current_app.config.get("ALLOWED_ORIGINS")
    if allowed_origins is None:
        return request.url.host == current_app.config["DOMAIN"]

    return request.url.host in allowed_origins


# TODO(dcramer): this still isnt working. is_valid_origin had an error
# and it was never bubbled up


def log_errors(func):
    @wraps(func)
    async def wrapped(*a, **k):
        try:
            return await func(*a, **k)

        except Exception as e:
            current_app.logger.exception(str(e))
            raise

    return wrapped


# @log_errors


async def worker(channel, queue, token, repo_ids=None, build_ids=None):
    allowed_repo_ids = frozenset(token["repo_ids"])

    while await channel.wait_message():
        msg = await channel.get_json()
        data = msg.get("data")
        if data["repository"]["id"] not in allowed_repo_ids:
            continue

        if build_ids and data["id"] not in build_ids:
            continue

        if repo_ids and data["repository"]["id"] not in repo_ids:
            continue

        evt = Event(msg.get("id"), msg.get("event"), data)
        await queue.put(evt)
        current_app.logger.debug("pubsub.event.received qsize=%s", queue.qsize())


# @log_errors


async def ping(loop, resp, client_guid):
    # periodically send ping to the browser. Any message that
    # starts with ":" colon ignored by a browser and could be used
    # as ping message.
    while True:
        await asyncio.sleep(15, loop=loop)
        current_app.logger.debug("pubsub.ping guid=%s", client_guid)
        resp.write(b": ping\r\n\r\n")


# @log_errors


async def stream(request):
    client_guid = str(uuid4())

    sentry.tags_context({"client_guid": client_guid})

    if request.headers.get("accept") != "text/event-stream":
        return Response(status=406)

    if request.method != "GET":
        return Response(status=405)

    token = request.query.get("token")
    if not token:
        return Response(status=401)

    build_ids = frozenset(request.query.get("build") or [])
    repo_ids = frozenset(request.query.get("repo") or [])

    token = auth.parse_token(token)
    if not token:
        return Response(status=401)

    if "uid" in token:
        sentry.user_context({"id": token["uid"]})

    current_app.logger.debug(
        "pubsub.client.connected guid=%s tenant=%s", client_guid, token
    )

    loop = request.app.loop

    parts = urlparse(current_app.config["REDIS_URL"])

    conn = await aioredis.create_redis(
        address=(parts.hostname or "localhost", parts.port or "6379"),
        db=parts.path.split("1", 1)[:-1] or 0,
        password=parts.password,
        loop=loop,
    )
    try:
        queue = asyncio.Queue(loop=loop)

        res = await conn.subscribe("builds")
        asyncio.ensure_future(worker(res[0], queue, token, repo_ids, build_ids))

        resp = StreamResponse(status=200, reason="OK")
        resp.headers["Content-Type"] = "text/event-stream"
        resp.headers["Cache-Control"] = "no-cache"
        resp.headers["Connection"] = "keep-alive"
        if "Origin" in request.headers and is_valid_origin(request):
            resp.headers["Access-Control-Allow-Origin"] = request.headers.get("Origin")
            resp.headers["Access-Control-Expose-Headers"] = "*"
        resp.enable_chunked_encoding()

        await resp.prepare(request)

        # loop.create_task(ping(loop, resp, client_guid))

        # resp.write(b'retry: 100\r\n\r\n')

        while True:
            event = await queue.get()
            if event is None:
                break

            buffer = io.BytesIO()
            if event.id:
                buffer.write(b"id: %s\r\n" % (event.id.encode("utf-8"),))
            if event.event:
                buffer.write(b"event: %s\r\n" % (event.event.encode("utf-8")))
            if event.data:
                buffer.write(b"data: %s\r\n" % (json.dumps(event.data).encode("utf-8")))
            buffer.write(b"\r\n")
            resp.write(buffer.getvalue())
            queue.task_done()
            current_app.logger.debug("pubsub.event.sent qsize=%s", queue.qsize())
            # Yield to the scheduler so other processes do stuff.
            await resp.drain()

        await resp.write_eof()
        return resp

    finally:
        conn.close()
        await conn.wait_closed()
        current_app.logger.debug(
            "client.disconnected guid=%s", client_guid, exc_info=True
        )


async def health_check(request):
    return Response(text='{"ok": true}')


async def build_server(loop, host, port):
    app = Application(loop=loop, logger=current_app.logger, debug=current_app.debug)
    app.router.add_route("GET", "/", stream)
    app.router.add_route("GET", "/healthz", health_check)

    return await loop.create_server(app.make_handler(), host, port)
