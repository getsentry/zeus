from uuid import UUID

from zeus import factories
from zeus.db.utils import create_or_update, try_create

# we use the User model to test
from zeus.models import User


def test_try_create_only_where_new_instance():
    created = try_create(User, {"email": "foo@example.com"})
    assert created
    instance = User.query.filter_by(email="foo@example.com").first()
    assert instance


def test_try_create_with_defaults_new_instance():
    created = try_create(
        User,
        {"id": UUID("5edb7312-316e-11ea-b6cd-8c85906d3733")},
        {"email": "foo@example.com"},
    )
    assert created
    instance = User.query.get("5edb7312-316e-11ea-b6cd-8c85906d3733")
    assert instance.email == "foo@example.com"


def test_try_create_only_where_existing_instance(default_user):
    created = try_create(User, {"email": default_user.email})
    assert not created


def test_try_create_with_defaults_existing_instance(default_user):
    created = try_create(
        User, {"id": default_user.id}, {"email": "defnotreal@example.com"}
    )
    assert not created
    instance = User.query.get(default_user.id)
    assert instance.email == default_user.email


def test_create_or_update_new_instance(db_session):
    another_user = factories.UserFactory.create()

    created = create_or_update(User, {"email": "defnotreal@example.com"})
    assert created
    assert User.query.filter_by(email="defnotreal@example.com").first()
    db_session.refresh(another_user)
    assert another_user.email != "defnotreal@example.com"


def test_create_or_update_existing_instance(db_session, default_user):
    another_user = factories.UserFactory.create()
    created = create_or_update(
        User, {"id": default_user.id}, {"email": "defnotreal@example.com"}
    )
    assert not created
    db_session.refresh(default_user)
    assert default_user.email == "defnotreal@example.com"
    db_session.refresh(another_user)
    assert another_user.email != "defnotreal@example.com"
