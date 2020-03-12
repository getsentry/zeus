<p align="center">
    <img src="https://user-images.githubusercontent.com/1433023/32629198-3c6f225e-c54d-11e7-96db-99fd22709a1b.png" width="271">
</p>

# Zeus

**This project is under development.**

Zeus is a frontend and analytics provider for CI solutions. It is inspired by the work done at Dropbox on [Changes](https://github.com/dropbox/changes/).

## User Guide

Currently Zeus publicly supports GitHub.com as well as easy integration with Travis CI.

To add a new project:

1. Add a repository (via settings).
2. Go to the repository's settings and generate a new Hook.
3. Bind ZEUS_HOOK_BASE as a secret environment variable in Travis.
4. Update your .travis.yml to include the Zeus webhook.
5. (Optional) Update your .travis.yml to include artifact upload.
6. (Optional, not yet recommended) Update your .travis.yml to disable Travis' native email notifications.

Once you've added a project Zeus will automatically update with details from any builds you've run.

Some quick caveats:

- The project is still pretty early on, and may break/change without warning.
- travis-ci.com and GitHub Enterprise are not yet supported.
- Notifications will only be triggered for users which have authenticated against Zeus.

If you want to use Zeus with a build system that's not currently supported, see the details on "Hooks" in the documentation.

### Supported Artifact Types

While you can upload any kind of Artifact to zeus (e.g. `.html` output), the platform has knowledge of certain types
and will grant additional functionality if they're present.

The recommended way to support artifacts is to configure a post-build step (on both failure and success) to do something similar to the following:

```bash
npm install -g @zeus-ci/cli
$(npm bin -g)/zeus upload -t "application/x-junit+xml" jest.junit.xml
$(npm bin -g)/zeus upload -t "application/x-cobertura+xml" coverage.xml
```

#### Code Coverage

- application/x-clover+xml
- application/x-cobertura+xml

#### xUnit

- application/x-bitten+xml
- application/x-junit+xml
- application/x-xunit+xml

#### Style Checks

- application/x-checkstyle+xml
- text/x-pep8
- text/x-pycodestyle
- test/x-pylint

#### Webpack Stats

Webpack stats can be generated with:

```bash
webpack --profile --json > webpack-stats.json
```

They should be submitted with the `application/x-webpack-stats+json` type.

## Contributing

### Requirements

- Python 3.8
- Node (and [Volta](https://volta.sh/))
- Postgres 9.4+

Note: If you're using pyenv for Python and macOS Mojave and having issues installing 3.7.1, take a look here:

https://github.com/pyenv/pyenv/issues/1219

### Setup

```shell
# install poetry
curl -sSL https://raw.githubusercontent.com/sdispater/poetry/0.12.10/get-poetry.py | python

# load dependencies
make

# initialize config
poetry run zeus init
```

Note, before running any future Python commands (including `zeus`), you'll
need to activate the environment:

```shell
poetry shell
```

You can also setup [direnv](https://direnv.net/) to automatically activate the environment.

Once dependencies are resolved, bootstrap the database (see `Makefile` for details):

```shell
make db
```

Finally, launch the webserver:

```shell
zeus devserver

# or alternatively, with workers:
zeus devserver --workers
```

### Getting some data

```shell
$ zeus repos add https://github.com/getsentry/zeus.git
```

Once you've authenticated, give yourself access to the repository:

```shell
$ zeus repos access add https://github.com/getsentry/zeus.git [you@example.com]
```

Additionally, you can generate some mock data:

```shell
$ zeus mocks load-all
```

### Layout

```
zeus
├── setup.py                // server dependencies
├── zeus                    // server code
|   ├── artifacts           // artifact handlers
|   ├── api
|   |   ├── resources       // api endpoints/resources
|   |   └── schemas         // api serializer/schemas
|   ├── cli                 // command line utilities
|   ├── models              // database schema
|   ├── storage             // file storage implementations
|   ├── tasks               // async task definitions
|   ├── vcs                 // version control system implementations
|   └── web                 // server-rendered web views
├── templates               // server-rendered templates
├── public                  // general static assets
├── package.json            // web client dependencies
└── webapp                  // web client
    ├── actions             // redux actions
    ├── components          // react components
    ├── reducers            // redux reducers
    ├── routes.js           // routes (react-router)
    └── pages.js            // react components (pages)
```

### Data Model

- Most models contain a GUID (UUID) primary key.
- Some generalized models (such as `ItemStat`) are keyed by GUID, and do not contain backrefs or constraints.
- Access is controlled at the repository level, and is generally enforced if you use the `{ModelClass}.query` utilities.
- Refs are unresolved (pointers to shas). They are often resolved asynchronously. Models containing a sha will also often contain a parallel ref field.

```
zeus
├── ApiToken
|   └── ApiTokenRepositoryAccess
├── Hook
├── Repository
|   ├── RepositoryAccess
|   ├── ItemOption
|   ├── Build
|   |   ├── ItemStat
|   |   ├── Source
|   |   ├── FileCoverage
|   |   └── Job
|   |       ├── Artifact
|   |       ├── ItemStat
|   |       └── TestCase
|   |           ├── Artifact
|   |           └── ItemStat
|   ├── ChangeRequest
|   |   └── Revision
|   └── Source
|       ├── Author
|       ├── Patch
|       └── Revision
|           └── Author
└── User
    ├── Email
    └── Identity
```

### Hooks

A subset of APIs are exposed using simple hook credentials. These credentials are coupled to a provider (e.g. `travis-ci`) and a single repository.

To create a new hook:

```
zeus hooks add https://github.com/getsentry/zeus.git travis-ci
```

Using the subpath, you'll be able to access several endpoints:

- `{prefix}/builds/{build-external-id}`
- `{prefix}/builds/{build-external-id}/jobs/{job-external-id}`
- `{prefix}/builds/{build-external-id}/jobs/{job-external-id}/artifacts`

The prefix will be generated for you as part of the new hook, and is made up of the Hook's GUID and it's signature:

http://example.com/hooks/{hook-id}/{hook-signature}/{path}

Each endpoint takes an external ID, which is used as a unique query parameter. The constraints are coupled to the parent object. For example, to create or patch a build:

```
POST http://example.com/hooks/{hook-id}/{hook-signature}/builds/abc
```

This will look for a Build object with the following characteristics:

- `provider={Hook.provider}`
- `external_id=abc`
- `repository_id={Hook.repository_id}`

If a match is found, it will be updated with the given API parameters. If it isn't found, it will be created. All of these operations are treated like a standard UPSERT (UPDATE IF EXISTS or INSERT).

The process for publishing data generally looks like this:

1. if applicable, upsert a change request and its source association
2. upsert the build's basic parameters
3. upsert the detailed job parameters
4. publish artifacts

These actions can be also performed manually (without using the native webhooks) with `zeus-cli` (recommended) or `curl`.

### Updating data with `zeus-cli`

More information (installation instructions, documentation) about `zeus-cli` can be found on its project's page: https://github.com/getsentry/zeus-cli

`zeus-cli` is a command line tool that facilitates interaction with Zeus API for actions such as updating jobs or uploading artifacts.

The following command creates a build and a job for a given `git` revision:

```shell
zeus job update -b $MY_BUILD_ID -j $MY_JOB_ID  --ref=$MY_REF_ID
```

And here's how you upload an artifact:

```shell
zeus upload -b $MY_BUILD_ID -j $MY_JOB_ID -t 'text/xml+coverage' coverage.xml
```

### Updating data with `curl`

Here's an example of how you can publish job details without the native webhooks with `curl` from Travis:

```shell
#!/bin/bash -eu
if [[ "$TRAVIS_PULL_REQUEST" != "false" ]]; then
    BUILD_LABEL="PR #${TRAVIS_PULL_REQUEST}"
else
    BUILD_LABEL=""
fi

# ensure the build exists
curl $ZEUS_HOOK_BASE/builds/$TRAVIS_BUILD_NUMBER \
    -X POST \
    -H 'Content-Type: application/json' \
    -d "{\"label\": \"${BUILD_LABEL}\", \"ref\": \"$TRAVIS_COMMIT\", \"url\": \"https://travis-ci.org/${TRAVIS_REPO_SLUG}/builds/${TRAVIS_BUILD_ID}\"}"

# upsert current job details
curl $ZEUS_HOOK_BASE/builds/$TRAVIS_BUILD_NUMBER/jobs/$TRAVIS_JOB_NUMBER \
    -X POST \
    -H 'Content-Type: application/json' \
    -d "{\"status\": \"$1\", \"result\": \"$2\", \"url\": \"https://travis-ci.org/${TRAVIS_REPO_SLUG}/jobs/${TRAVIS_JOB_ID}\", \"allow_failure\": ${TRAVIS_ALLOW_FAILURE}}"
```

From there you can submit artifacts using `zeus-cli` and its standard mechanisms.
