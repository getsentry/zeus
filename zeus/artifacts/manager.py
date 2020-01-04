from flask import current_app
from fnmatch import fnmatch
from zeus.utils.sentry import Span


class Manager(object):
    def __init__(self):
        self.handlers = []

    def register(self, cls, matches):
        self.handlers.append((cls, matches))

    def process(self, artifact):
        job = artifact.job
        artifact_name = artifact.name

        matches = []
        if not artifact.type:
            for cls, patterns in self.handlers:
                for pattern in patterns:
                    if fnmatch(artifact_name, pattern):
                        matches.append(cls)
        else:
            for cls, _ in self.handlers:
                if artifact.type in cls.supported_types:
                    matches.append(cls)

        for cls in matches:
            with Span("artifacts.process", description=cls.__name__):
                handler = cls(job)
                fp = artifact.file.get_file()
                try:
                    current_app.logger.info(
                        "artifact.process",
                        extra={"handler_cls": cls.__name__, "artifact_id": artifact.id},
                    )
                    handler.process(fp)
                finally:
                    fp.close()
