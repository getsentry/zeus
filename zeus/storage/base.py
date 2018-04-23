class FileStorage(object):

    def __init__(self, path=""):
        self.path = path

    def delete(self, filename):
        raise NotImplementedError

    def save(self, filename, fp):
        raise NotImplementedError

    def url_for(self, filename, expire=300):
        raise NotImplementedError

    def get_file(self, filename):
        raise NotImplementedError
