def assert_revision(revision, author=None, message=None):
    """Asserts values of the given fields in the provided revision.

    :param revision: The revision to validate
    :param author: that must be present in the ``revision``
    :param message: message substring that must be present in ``revision``
    """
    if author:
        assert author == revision.author
    if message:
        assert message in revision.message
