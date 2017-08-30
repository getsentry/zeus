import aioredis
import asyncio
from functools import wraps
import io
import json

from aiohttp.web import Application, Response, StreamResponse
from collections import namedtuple
from flask import current_app
from urllib.parse import urlparse
from uuid import uuid4

from zeus import auth

Event = namedtuple('Event', ['id', 'event', 'data'])


def log_errors(func):
    @wraps(func)
    async def wrapped(*a, **k):
        try:
            return await func(*a, **k)
        except Exception as e:
            import traceback
            traceback.print_exc()
            raise
    return wrapped


@log_errors
async def worker(channel, queue, token, repo_ids=None, build_ids=None):
    allowed_repo_ids = frozenset(token['repo_ids'])

    while (await channel.wait_message()):
        msg = await channel.get_json()
        data = msg.get('data')
        if data['repository']['id'] not in allowed_repo_ids:
            continue
        if build_ids and data['id'] not in build_ids:
            continue
        if repo_ids and data['repository']['id'] not in repo_ids:
            continue
        evt = Event(
            msg.get('id'),
            msg.get('event'),
            data,
        )
        await queue.put(evt)


@log_errors
async def stream(request):
    client_guid = str(uuid4())

    if request.headers.get('accept') != 'text/event-stream':
        return Response(status=406)

    token = request.query.get('token')
    if not token:
        return Response(status=401)

    build_ids = frozenset(request.query.get('build') or [])
    repo_ids = frozenset(request.query.get('repo') or [])

    token = auth.parse_token(token)
    print('client.connected guid={} tenant={}'.format(client_guid, token))

    loop = request.app.loop

    parts = urlparse(current_app.config['REDIS_URL'])

    conn = await aioredis.create_redis(
        address=(parts.hostname or 'localhost', parts.port or '6379'),
        db=parts.path.split('1', 1)[:-1] or 0,
        password=parts.password,
        loop=loop,
    )
    try:
        queue = asyncio.Queue(loop=loop)

        res = await conn.subscribe('builds')
        asyncio.ensure_future(
            worker(res[0], queue, token, repo_ids, build_ids))

        resp = StreamResponse()
        resp.headers['Content-Type'] = 'text/event-stream; charset=UTF-8'
        resp.headers['Cache-Control'] = 'no-cache'
        resp.headers['Connection'] = 'keep-alive'
        domain_parts = urlparse(request.url)
        if domain_parts.hostname == current_app.config.get(
                'DOMAIN', current_app.config.get('SERVER_NAME', '')):
            resp.headers['Access-Control-Allow-Origin'] = request.headers.get(
                'Origin')
            resp.headers['Access-Control-Expose-Headers'] = '*'
        resp.enable_chunked_encoding()
        # The StreamResponse is a FSM. Enter it with a call to prepare.
        await resp.prepare(request)

        while True:
            event = await queue.get()
            if event is None:
                break
            buffer = io.BytesIO()
            if event.id:
                buffer.write(b"id: %s\r\n" % (event.id.encode('utf-8'),))
            if event.event:
                buffer.write(b"event: %s\r\n" %
                             (event.event.encode('utf-8')))
            if event.data:
                buffer.write(b"data: %s\r\n" %
                             (json.dumps(event.data).encode('utf-8')))
            buffer.write(b'\r\n')
            resp.write(buffer.getvalue())
            queue.task_done()
            # Yield to the scheduler so other processes do stuff.
            await resp.drain()

        await resp.write_eof()
        return resp
    finally:
        await conn.wait_closed()
        print('client.disconnected guid={}'.format(client_guid))


async def debug(request):
    d = """
        <html>
        <head>
            <script type="text/javascript">
            var eventList = document.getElementById('events');
            var evtSource = new EventSource('/');
            evtSource.addEventListener('message', function(e) {
                console.log('we here');
                var newElement = document.createElement("li");
                newElement.innerHTML = "message: " + e.data;
                eventList.appendChild(newElement);
            });
            </script>
        </head>
        <body>
            <h1>Response from server:</h1>
            <ul id="events"></ul>
        </body>
    </html>
    """
    return Response(text=d, content_type='text/html')


async def build_server(loop, host, port):
    app = Application(loop=loop)
    app.router.add_route('GET', '/', stream)
    app.router.add_route('GET', '/debug', debug)

    return await loop.create_server(app.make_handler(), host, port)
