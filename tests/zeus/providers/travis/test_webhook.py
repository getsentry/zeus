from base64 import b64encode

from zeus import factories
from zeus.constants import Result, Status
from zeus.models import Build, Job

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
            "scopes": ["read:org", "user:email", "repo_deployment", "repo:status", "write:repo_hook"]
        },
        "notifications": {
            "webhook": {
                "public_key": "%(public_key)s"
            }
        }
    }
}
"""

EXAMPLE = b"""{
  "id": 288639281,
  "number": "2843",
  "config": {
    "sudo": false,
    "dist": "trusty",
    "language": "python",
    "python": [
      "3.5.2"
    ],
    "branches": {
      "only": [
        "master"
      ]
    },
    "cache": {
      "pip": true,
      "directories": [
        "vendor/bundle",
        "node_modules"
      ]
    },
    "deploy": {
      "provider": "heroku",
      "api_key": {
        "secure": "hylw2GIHMvZKOKX3uPSaLEzVrUGEA9mzGEA0s4zK37W9HJCTnvAcmgRCwOkRuC4L7R4Zshdh/CGORNnBBgh1xx5JGYwkdnqtjHuUQmWEXCusrIURu/iEBNSsZZEPK7zBuwqMHj2yRm64JfbTDJsku3xdoA5Z8XJG5AMJGKLFgUQ="
      },
      "app": "docs-travis-ci-com",
      "skip_cleanup": true,
      "true": {
        "branch": [
          "master"
        ]
      }
    },
    "notifications": {
      "slack": {
        "rooms": {
          "secure": "LPNgf0Ra6Vu6I7XuK7tcnyFWJg+becx1RfAR35feWK81sru8TyuldQIt7uAKMA8tqFTP8j1Af7iz7UDokbCCfDNCX1GxdAWgXs+UKpwhO89nsidHAsCkW2lWSEM0E3xtOJDyNFoauiHxBKGKUsApJTnf39H+EW9tWrqN5W2sZg8="
        },
        "on_success": "never"
      },
      "webhooks": "https://docs.travis-ci.com/update_webhook_payload_doc"
    },
    "install": [
      "rvm use 2.3.1 --install",
      "bundle install --deployment"
    ],
    "script": [
      "bundle exec rake test"
    ],
    ".result": "configured",
    "global_env": [
      "PATH=$HOME/.local/user/bin:$PATH"
    ],
    "group": "stable"
  },
  "type": "cron",
  "state": "passed",
  "status": 0,
  "result": 0,
  "status_message": "Passed",
  "result_message": "Passed",
  "started_at": "2017-10-16T16:08:56Z",
  "finished_at": "2017-10-16T16:12:35Z",
  "duration": 219,
  "build_url": "https://travis-ci.org/travis-ci/docs-travis-ci-com/builds/288639281",
  "commit_id": 84531696,
  "commit": "d79e3a6ff0cada29d731ed93de203f76a81d02c0",
  "base_commit": "d79e3a6ff0cada29d731ed93de203f76a81d02c0",
  "head_commit": null,
  "branch": "master",
  "message": "Merge pull request #1389 from christopher-dG/patch-1\\n\\nJulia: Refer to PkgDev's generate instead of Pkg's",
  "compare_url": "https://github.com/travis-ci/docs-travis-ci-com/compare/eb58bd2fac2e339d0339689d9eb7290246805a1d...d79e3a6ff0cada29d731ed93de203f76a81d02c0",
  "committed_at": "2017-10-16T14:56:34Z",
  "author_name": "Plaindocs",
  "author_email": "lykoszine@gmail.com",
  "committer_name": "GitHub",
  "committer_email": "noreply@github.com",
  "pull_request": false,
  "pull_request_number": null,
  "pull_request_title": null,
  "tag": null,
  "repository": {
    "id": 1771959,
    "name": "docs-travis-ci-com",
    "owner_name": "travis-ci",
    "url": "http://docs.travis-ci.com"
  },
  "matrix": [
    {
      "id": 288639284,
      "repository_id": 1771959,
      "parent_id": 288639281,
      "number": "2843.1",
      "state": "passed",
      "config": {
        "sudo": false,
        "dist": "trusty",
        "language": "python",
        "python": "3.5.2",
        "branches": {
          "only": [
            "master"
          ]
        },
        "cache": {
          "pip": true,
          "directories": [
            "vendor/bundle",
            "node_modules"
          ]
        },
        "notifications": {
          "slack": {
            "rooms": {
              "secure": "LPNgf0Ra6Vu6I7XuK7tcnyFWJg+becx1RfAR35feWK81sru8TyuldQIt7uAKMA8tqFTP8j1Af7iz7UDokbCCfDNCX1GxdAWgXs+UKpwhO89nsidHAsCkW2lWSEM0E3xtOJDyNFoauiHxBKGKUsApJTnf39H+EW9tWrqN5W2sZg8="
            },
            "on_success": "never"
          },
          "webhooks": "https://docs.travis-ci.com/update_webhook_payload_doc"
        },
        "install": [
          "rvm use 2.3.1 --install",
          "bundle install --deployment"
        ],
        "script": [
          "bundle exec rake test"
        ],
        ".result": "configured",
        "global_env": [
          "PATH=$HOME/.local/user/bin:$PATH"
        ],
        "group": "stable",
        "os": "linux",
        "addons": {
          "deploy": {
            "provider": "heroku",
            "api_key": {
              "secure": "hylw2GIHMvZKOKX3uPSaLEzVrUGEA9mzGEA0s4zK37W9HJCTnvAcmgRCwOkRuC4L7R4Zshdh/CGORNnBBgh1xx5JGYwkdnqtjHuUQmWEXCusrIURu/iEBNSsZZEPK7zBuwqMHj2yRm64JfbTDJsku3xdoA5Z8XJG5AMJGKLFgUQ="
            },
            "app": "docs-travis-ci-com",
            "skip_cleanup": true,
            "true": {
              "branch": [
                "master"
              ]
            }
          }
        }
      },
      "status": 0,
      "result": 0,
      "commit": "d79e3a6ff0cada29d731ed93de203f76a81d02c0",
      "branch": "master",
      "message": "Merge pull request #1389 from christopher-dG/patch-1\\n\\nJulia: Refer to PkgDev's generate instead of Pkg's",
      "compare_url": "https://github.com/travis-ci/docs-travis-ci-com/compare/eb58bd2fac2e339d0339689d9eb7290246805a1d...d79e3a6ff0cada29d731ed93de203f76a81d02c0",
      "started_at": null,
      "finished_at": null,
      "committed_at": "2017-10-16T14:56:34Z",
      "author_name": "Plaindocs",
      "author_email": "lykoszine@gmail.com",
      "committer_name": "GitHub",
      "committer_email": "noreply@github.com",
      "allow_failure": true
    }
  ]
}"""

UNSET = object()


def make_signature(payload, private_key) -> bytes:
    from cryptography.hazmat.primitives import hashes
    from cryptography.hazmat.primitives.asymmetric import padding

    return private_key.sign(
        payload,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA1()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA1()
    )


def get_config_response(public_key_bytes):
    return CONFIG_RESPONSE % {b'public_key': public_key_bytes.replace(b'\n', b'\\n')}


def post_request(client, hook, payload, public_key, signature):
    path = '/hooks/{}/public/provider/travis/webhook/'.format(
        hook.id,
    )

    return client.post(path, data={
        'payload': payload,
    }, headers={
        'Signature': b64encode(signature),
    })


def test_missing_payload(client, default_repo, default_hook):
    path = '/hooks/{}/public/provider/travis/webhook/'.format(
        default_hook.id,
    )

    resp = client.post(path)
    assert resp.status_code == 400, repr(resp.data)


def test_missing_signature(client, default_repo, default_hook):
    path = '/hooks/{}/public/provider/travis/webhook/'.format(
        default_hook.id,
    )

    resp = client.post(path)
    assert resp.status_code == 400, repr(resp.data)


def test_queued_build(client, default_repo, default_hook, default_revision,
                      private_key, public_key_bytes, mocker, responses):
    responses.add(responses.GET, 'https://api.travis-ci.org/config',
                  get_config_response(public_key_bytes))

    source = factories.SourceFactory.create(revision=default_revision)

    mock_identify_revision = mocker.patch(
        'zeus.api.resources.repository_builds.identify_revision')

    mock_identify_revision.return_value = default_revision

    resp = post_request(client, default_hook, EXAMPLE,
                        public_key_bytes, make_signature(EXAMPLE, private_key))
    assert resp.status_code == 200, repr(resp.data)

    build = Build.query.unrestricted_unsafe().filter(
        Build.provider == 'travis',
        Build.external_id == '288639281',
    ).first()
    assert build
    assert build.repository_id == default_repo.id
    assert build.source_id == source.id
    assert build.label == default_revision.subject
    assert build.url == 'https://travis-ci.org/travis-ci/docs-travis-ci-com/builds/288639281'

    job = Job.query.unrestricted_unsafe().filter(
        Job.provider == 'travis',
        Job.external_id == '288639284',
    ).first()
    assert job
    assert job.build_id == build.id
    assert job.repository_id == default_repo.id
    assert job.status == Status.finished
    assert job.result == Result.passed
    assert job.allow_failure
    assert job.url == 'https://travis-ci.org/travis-ci/docs-travis-ci-com/jobs/288639284'
