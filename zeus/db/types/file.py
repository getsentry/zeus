__all__ = ["File", "FileData"]

import json

from flask import current_app
from sqlalchemy.ext.mutable import Mutable
from sqlalchemy.types import TypeDecorator, Unicode

from zeus.utils.imports import import_string
from zeus.utils.sentry import span


class FileData(Mutable):
    def __init__(self, data=None, default_storage=None, default_path=None):
        if data is None:
            data = {}

        self.filename = data.get("filename")
        self.exists = bool(data and self.filename)
        self.storage = data.get(
            "storage", default_storage or current_app.config["FILE_STORAGE"]
        )
        self.path = data.get("path", default_path)
        self.size = data.get("size", None)

    def __repr__(self):
        if not self.exists:
            return "<%s: not present>" % (type(self).__name__,)

        return "<%s: filename=%s>" % (type(self).__name__, self.filename)

    def __bool__(self):
        return self.exists

    def get_storage(self):
        storage = import_string(self.storage["backend"])
        options = self.storage.get("options", {})
        if self.path is not None:
            options["path"] = self.path
        return storage(**options)

    def url_for(self, expire=300):
        if self.filename is None:
            return

        return self.get_storage().url_for(self.filename, expire=expire)

    @span("file.save")
    def save(self, fp, filename=None, allow_ref=True):
        # this is effectively a copy
        if isinstance(fp, FileData):
            self.size = fp.size
            if filename:
                self.filename = filename
                self.get_storage().save(self.filename, fp.get_file())
            elif fp.filename and allow_ref:
                # we avoid re-saving anything at this point
                self.filename = fp.filename
                self.path = fp.path
                self.storage = fp.storage
            elif self.filename:
                self.get_storage().save(self.filename, fp.get_file())
            else:
                raise ValueError("Missing filename")
            self.exists = True
        else:
            if filename:
                self.filename = filename
                self.exists = True
            elif self.filename is None:
                raise ValueError("Missing filename")

            # Flask's FileStorage object might give us an accurate content_length,
            # otherwise we need to seek the underlying file to obtain its size.
            # For in-memory files this will fail, so we just assume None as default
            if hasattr(fp, "content_length") and fp.content_length:
                self.size = fp.content_length
            else:
                try:
                    pos = fp.tell()
                    fp.seek(0, 2)
                    self.size = fp.tell()
                    fp.seek(pos)
                except (AttributeError, IOError):
                    self.size = None
            self.get_storage().save(self.filename, fp)
        self.changed()

    @span("file.delete")
    def delete(self):
        self.get_storage().delete(self.filename)
        self.exists = False
        self.filename = None
        self.size = None
        self.changed()

    def get_file(self):
        if self.filename is None:
            raise ValueError("Missing filename")

        return self.get_storage().get_file(self.filename)

    @classmethod
    def coerce(cls, key, value):
        return value


class File(TypeDecorator):
    impl = Unicode

    python_type = FileData

    def __init__(self, path="", storage=None, *args, **kwargs):

        super(File, self).__init__(*args, **kwargs)

        self.path = path
        self.storage = {"storage": storage}

    def process_bind_param(self, value, dialect):
        if value:
            if isinstance(value, FileData):
                if not value.exists:
                    value = {}
                else:
                    value = {
                        "filename": value.filename,
                        "storage": value.storage,
                        "path": value.path,
                        "size": value.size,
                    }
            return str(json.dumps(value))

        return u"{}"

    def process_result_value(self, value, dialect):
        if value:
            return FileData(json.loads(value), self.storage, self.path)

        return FileData({}, self.storage, self.path)


FileData.associate_with(File)
