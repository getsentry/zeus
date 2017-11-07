__all__ = ['File', 'FileData']

import json

from flask import current_app
from sqlalchemy.ext.mutable import Mutable
from sqlalchemy.types import TypeDecorator, Unicode

from zeus.utils.imports import import_string


class FileData(Mutable):
    def __init__(self, data=None, default_storage=None, default_path=None):
        if data is None:
            data = {}

        self.filename = data.get('filename')
        self.storage = (
            data.get(
                'storage', default_storage or current_app.config['FILE_STORAGE'])
        )
        self.path = data.get('path', default_path)

    def __repr__(self):
        return '<%s: filename=%s>' % (type(self).__name__, self.filename)

    def __nonzero__(self):
        return bool(self.filename)

    def get_storage(self):
        storage = import_string(self.storage['backend'])
        options = self.storage.get('options', {})
        if self.path is not None:
            options['path'] = self.path
        return storage(**options)

    def url_for(self, expire=300):
        if self.filename is None:
            return
        return self.get_storage().url_for(self.filename, expire=expire)

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

    def __init__(self, path='', storage=None, *args, **kwargs):

        super(File, self).__init__(*args, **kwargs)

        self.path = path
        self.storage = {
            'storage': storage,
        }

    def process_bind_param(self, value, dialect):
        if value:
            if isinstance(value, FileData):
                value = {
                    'filename': value.filename,
                    'storage': value.storage,
                    'path': value.path,
                }
            return str(json.dumps(value))

        return u'{}'

    def process_result_value(self, value, dialect):
        if value:
            return FileData(json.loads(value), self.storage, self.path)

        return FileData({}, self.storage, self.path)


FileData.associate_with(File)
