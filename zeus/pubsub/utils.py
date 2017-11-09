import json

from uuid import uuid4

from zeus.config import redis


def publish(channel, event, data):
    redis.publish(channel, json.dumps({
        'id': uuid4().hex,
        'event': event,
        'data': data,
    }))
