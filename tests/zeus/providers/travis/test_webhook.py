import json

from base64 import b64encode


CONFIG_RESPONSE = b"""
{
    "config": {
        "host": "travis-ci.org",
        "shorten_host": "trvs.io",
        "assets": {
            "host": "travis-ci.org"
        },
        "pusher": {
            "key": "5df8ac576dcccf4fd076"
        },
        "github": {
            "api_url": "https://api.github.com",
            "scopes": [
                "read:org", "user:email",
                "repo_deployment", "repo:status",
                "write:repo_hook"
            ]
        },
        "notifications": {
            "webhook": {
                "public_key": "%(public_key)s"
            }
        }
    }
}
"""

UNSET = object()


def make_signature(payload, private_key) -> bytes:
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.asymmetric import padding

    return private_key.sign(payload, padding.PKCS1v15(), hashes.SHA1())


def get_config_response(public_key_bytes):
    return CONFIG_RESPONSE % {b"public_key": public_key_bytes.replace(b"\n", b"\\n")}


def post_request(client, hook, payload, public_key, signature):
    path = "/hooks/{}/public/provider/travis/webhook".format(hook.id)

    return client.post(
        path, data={"payload": payload}, headers={"Signature": b64encode(signature)}
    )


def test_missing_payload(client, default_repo, default_hook):
    path = "/hooks/{}/public/provider/travis/webhook".format(default_hook.id)

    resp = client.post(path)
    assert resp.status_code == 400, repr(resp.data)


def test_missing_signature(client, default_repo, default_hook):
    path = "/hooks/{}/public/provider/travis/webhook".format(default_hook.id)

    resp = client.post(path)
    assert resp.status_code == 400, repr(resp.data)


def test_queued_build(
    client,
    default_repo,
    default_hook,
    default_revision,
    private_key,
    public_key_bytes,
    mocker,
    responses,
    sample_travis_build_commit,
):
    responses.add(
        responses.GET,
        "https://api.travis-ci.org/config",
        get_config_response(public_key_bytes),
    )

    payload = json.dumps(sample_travis_build_commit).encode("utf-8")

    resp = post_request(
        client,
        default_hook,
        payload,
        public_key_bytes,
        make_signature(payload, private_key),
    )
    assert resp.status_code == 202, repr(resp.data)
