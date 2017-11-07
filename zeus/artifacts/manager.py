import re

from fnmatch import fnmatch
from zeus.config import db


class Manager(object):
    def __init__(self):
        self.handlers = {}

    def register(self, cls, matches):
        name = re.sub(r"Handler$", '', cls.__name__).upper()
        if name in self.handlers:
            raise KeyError('Handler with name %s already registered' % name)

        self.handlers[name] = (cls, matches)

    def infer_type(self, artifact_name):
        for id, (cls, matches) in self.handlers.items():
            for pattern in matches:
                if fnmatch(artifact_name, pattern):
                    return id

        return None

    def process(self, artifact):
        job = artifact.job
        artifact_name = artifact.name

        if not artifact.type:
            inferred_type = self.infer_type(artifact_name)
            if inferred_type != artifact.type:
                artifact.type = inferred_type
                db.session.add(artifact)

        if artifact.type not in self.handlers:
            return

        cls = self.handlers[artifact.type][0]
        handler = cls(job)
        fp = artifact.file.get_file()
        try:
            handler.process(fp)
        finally:
            fp.close()
