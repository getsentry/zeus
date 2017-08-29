import asyncio
import click
import os

from zeus.pubsub.server import build_server

from .base import cli


@cli.command()
@click.option('--host', default='0.0.0.0')
@click.option('--port', default=8090, type=int)
def pubsub(host, port):
    os.environ['PYTHONUNBUFFERED'] = 'true'

    loop = asyncio.get_event_loop()
    loop.run_until_complete(build_server(loop, host, port))
    print('Pubsub serving on http://{}:{}'.format(host, port))

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        print("Shutting Down!")
        loop.close()
