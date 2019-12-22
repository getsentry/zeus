from typing import FrozenSet


class ArtifactHandler(object):
    supported_types: FrozenSet[str] = frozenset()

    def __init__(self, job):
        self.job = job
