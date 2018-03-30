from zeus import auth
from zeus.constants import Permission
from zeus.models import RepositoryRef


def test_get_with_existing(db_session, default_repo):
    auth.set_current_tenant(auth.Tenant(access={default_repo.id: Permission.read}))

    ref = RepositoryRef(repository=default_repo, name="master")
    db_session.add(ref)
    db_session.flush()

    ref2 = RepositoryRef.get(repository_id=default_repo.id, name="master")
    assert ref2 == ref


def test_get_with_new(db_session, default_repo):
    auth.set_current_tenant(auth.Tenant(access={default_repo.id: Permission.read}))
    ref = RepositoryRef.get(repository_id=default_repo.id, name="master")
    ref2 = RepositoryRef.query.filter(
        RepositoryRef.repository_id == default_repo.id, RepositoryRef.name == "master"
    ).first()
    assert ref2 == ref
