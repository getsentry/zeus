from fnmatch import fnmatch


class Manager(object):
    def __init__(self):
        self.handlers = []

    def register(self, cls, matches):
        self.handlers.append((cls, matches))

    def process(self, artifact):
        job = artifact.job
        artifact_name = artifact.name
        for cls, matches in self.handlers:
            for pattern in matches:
                if fnmatch(artifact_name, pattern):
                    break
            else:
                continue

            handler = cls(job)
            fp = artifact.file.get_file()
            try:
                handler.process(fp)
            finally:
                fp.close()
