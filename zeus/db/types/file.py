__all__ = ['File', 'FileData']

import json

from flask import current_app
from sqlalchemy.ext.mutable import Mutable
from sqlalchemy.types import TypeDecorator, Unicode

from zeus.utils.imports import import_string


class FileData(Mutable):
    def __init__(self, data=None, storage=None):
        if data is None:
            data = {}

        self.filename = data.get('filename')
        self.storage = (
            data.get('storage', storage) or current_app.config['FILE_STORAGE']
        )

    def __repr__(self):
        return '<%s: filename=%s>' % (type(self).__name__, self.filename)

    def __nonzero__(self):
        return bool(self.filename)

    def get_storage(self):
        storage = import_string(self.storage['backend'])
        return storage(**self.storage.get('options', {}))

    def url_for(self):
        if self.filename is None:
            return
        return self.get_storage().url_for(self.filename)

    def save(self, fp, filename=None):
        if filename:
            self.filename = filename
        elif self.filename is None:
            raise ValueError('Missing filename')

        self.get_storage().save(self.filename, fp)
        self.changed()

    def get_file(self):
        if self.filename is None:
            raise ValueError('Missing filename')
        return self.get_storage().get_file(self.filename)

    @classmethod
    def coerce(cls, key, value):
        return value


class File(TypeDecorator):
    impl = Unicode

    python_type = FileData

    def __init__(self, storage=None, *args, **kwargs):

        super(File, self).__init__(*args, **kwargs)

        self.storage = {
            'storage': storage,
        }

    def process_bind_param(self, value, dialect):
        if value:
            if isinstance(value, FileData):
                value = {
                    'filename': value.filename,
                    'storage': value.storage,
                }
            return str(json.dumps(value))

        return u'{}'

    def process_result_value(self, value, dialect):
        if value:
            return FileData(json.loads(value), self.storage)

        return FileData({}, self.storage)


FileData.associate_with(File)
