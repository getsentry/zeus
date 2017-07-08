from .base import Resource


class CatchallResource(Resource):
    def get(self, path=None):
        return self.not_found()

    post = get
    put = get
    delete = get
    patch = get
