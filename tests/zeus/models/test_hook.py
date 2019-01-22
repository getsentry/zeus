from zeus import factories
from zeus.models import Hook


def test_get_required_hook_ids(default_repo):
    hook = factories.HookFactory.create(repository=default_repo, is_required=True)
    factories.HookFactory.create(repository=default_repo, is_required=False)

    assert Hook.get_required_hook_ids(default_repo.id) == [str(hook.id)]
