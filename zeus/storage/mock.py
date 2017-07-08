from io import BytesIO

from .base import FileStorage

_cache = {}


class FileStorageCache(FileStorage):
    global _cache

    def save(self, filename, fp):
        _cache[filename] = fp.read()

    def url_for(self, filename, expire=300):
        raise NotImplementedError

    def get_file(self, filename):
        return BytesIO(_cache[filename])

    @staticmethod
    def clear():
        _cache.clear()
