class ArtifactHandler(object):
    supported_types = frozenset([])

    def __init__(self, job):
        self.job = job
