def assert_revision(revision, author=None, message=None, subject=None, branches=None):
    """Asserts values of the given fields in the provided revision.

    :param revision: The revision to validate
    :param author: that must be present in the ``revision``
    :param message: message substring that must be present in ``revision``
    :param subject: exact subject that must be present in the ``revision``
    :param branches: all the branches that must be in the ``revision``
    """
    if author:
        assert author == revision.author
    if message:
        assert message in revision.message
    if subject:
        assert subject in revision.subject
    if branches:
        assert sorted(branches) == sorted(revision.branches)
