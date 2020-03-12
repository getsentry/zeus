from io import BytesIO
from typing import Dict

from .base import FileStorage

_cache: Dict[str, bytes] = {}


class FileStorageCache(FileStorage):
    global _cache

    def delete(self, filename: str):
        _cache.pop(filename, None)

    def save(self, filename: str, fp):
        _cache[filename] = fp.read()

    def url_for(self, filename: str, expire: int = 300) -> str:
        return "https://example.com/artifacts/{}".format(filename)

    def get_file(self, filename: str) -> BytesIO:
        return BytesIO(_cache[filename])

    @staticmethod
    def clear():
        _cache.clear()
