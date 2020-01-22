import pytest

from uuid import UUID

from zeus import factories
from zeus.db.utils import create_or_update, try_create

# we use the User model to test
from zeus.models import User


def test_try_create_only_where_new_instance():
    instance = try_create(User, {"email": "foo@example.com"})
    assert instance
    assert instance.email == "foo@example.com"


def test_try_create_with_defaults_new_instance():
    instance = try_create(
        User,
        {"id": UUID("5edb7312-316e-11ea-b6cd-8c85906d3733")},
        {"email": "foo@example.com"},
    )
    assert instance
    assert instance.id == UUID("5edb7312-316e-11ea-b6cd-8c85906d3733")
    assert instance.email == "foo@example.com"


@pytest.mark.xfail
def test_try_create_only_where_existing_instance(default_user):
    instance = try_create(User, {"email": default_user.email})
    assert not instance


@pytest.mark.xfail
def test_try_create_with_defaults_existing_instance(default_user):
    instance = try_create(
        User, {"id": default_user.id}, {"email": "defnotreal@example.com"}
    )
    assert not instance


def test_create_or_update_new_instance(db_session):
    another_user = factories.UserFactory.create()

    instance, created = create_or_update(User, {"email": "defnotreal@example.com"})
    assert created
    assert instance.email == "defnotreal@example.com"
    db_session.refresh(another_user)
    assert another_user.email != "defnotreal@example.com"


@pytest.mark.xfail
def test_create_or_update_existing_instance(db_session, default_user):
    another_user = factories.UserFactory.create()
    instance, created = create_or_update(
        User, {"id": default_user.id}, {"email": "defnotreal@example.com"}
    )
    assert not created
    assert instance.email == "defnotreal@example.com"
    db_session.refresh(another_user)
    assert another_user.email != "defnotreal@example.com"
