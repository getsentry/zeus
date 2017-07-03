from .base import Resource


class IndexResource(Resource):
    def get(self):
        return {'version': 0}
