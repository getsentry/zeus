from io import BytesIO

from .base import FileStorage

_cache = {}


class FileStorageCache(FileStorage):
    global _cache

    def delete(self, filename):
        _cache.pop(filename, None)

    def save(self, filename, fp):
        _cache[filename] = fp.read()

    def url_for(self, filename, expire=300):
        return 'https://example.com/artifacts/{}'.format(filename)

    def get_file(self, filename):
        return BytesIO(_cache[filename])

    @staticmethod
    def clear():
        _cache.clear()
