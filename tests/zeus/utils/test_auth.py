from zeus import auth


def test_login_user(client, default_user):
    with client.session_transaction() as session:
        auth.login_user(default_user.id, session=session)
        assert session['uid'] == default_user.id
        assert session['expire']
