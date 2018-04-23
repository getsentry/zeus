from zeus.config import db
from zeus.models import ItemOption


def test_user_details(client, default_login):
    resp = client.get("/api/users/me")
    assert resp.status_code == 200
    data = resp.json()
    assert data["email"] == default_login.email
    assert data["options"]["mail"]["notify_author"] == "1"


def test_update_mail_notify_author(client, default_login, default_user):
    resp = client.put(
        "/api/users/me", json={"options": {"mail": {"notify_author": "0"}}}
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["options"]["mail"]["notify_author"] == "0"

    assert db.session.query(
        ItemOption.query.filter(
            ItemOption.name == "mail.notify_author",
            ItemOption.item_id == default_user.id,
            ItemOption.value == "0",
        ).exists()
    ).scalar()
