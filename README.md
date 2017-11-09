# Zeus

**This project is under development.**

Zeus is a frontend and analytics provider for CI solutions. It is inspired by the work done at Dropbox on [Changes](https://github.com/dropbox/changes/).

The initial version aims to support Travis CI via GitHub, including:

- xunit
- code coverage
- artifacts (e.g. from ``py.test --html``)

## Requirements

- Python 3 (3.6+)
- Node
- Postgres 9.4+

## Setup

```shell
# create a new python environment
python3 -m venv venv

# load the environment as the active
source venv/bin/activate

# load dependencies
make

# initialize config
zeus init
```

Note, before running any future Python commands (including ``zeus``), you'll
need to activate the environment:

```shell
source venv/bin/activate
```

Bootstrap the database (see ``Makefile`` for details):

```shell
make reset-db
```

Finally, launch the webserver:

```shell
zeus devserver

# or alternatively, with workers:
zeus devserver --workers
```

## Getting some data

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

## Layout

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

## Data Model

- Most models contain a GUID (UUID) primary key.
- Some generalized models (such as ``ItemStat``) are keyed by GUID, and do not contain backrefs or constraints.
- Access is controlled at the repository level, and is generally enforced if you use the ``{ModelClass}.query`` utilities.

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
|   └── Source
|       ├── Author
|       ├── Patch
|       └── Revision
|           └── Author
└── User
    ├── Email
    └── Identity
```


## Hooks

A subset of APIs are exposed using simple hook credentials. These credentials are coupled to a provider (e.g. `travis-ci`) and a single repository.

To create a new hook:

```
zeus hooks add https://github.com/getsentry/zeus.git travis-ci
```

Using the subpath, you'll be able to access several endpoints:

- `{prefix}/builds/{build-external-id}`
- `{prefix}/builds/{build-external-id}/jobs/{job-external-id}`
- `{prefix}/builds/{build-external-id}/jobs/{job-external-id}/artifacts`

The prefix will be generated for you as part of the a new hook, and is made up of the Hook's GUID and it's signature:

http://example.com/hooks/{hook-id}/{hook-signature}/{path}

Each endpoint takes an external ID, which is used as a unique query parameter. The constraints are coupled to the parent object. For example, to create or patch a build:

```
POST http://example.com/hooks/{hook-id}/{hook-signature}/builds/abc
```

This will look for a Build object with the following characteristics:

- `provider={Hook.provider}`
- `external_id=abc`
- `repository_id={Hook.repository_id}`

If a match is found, it will be updated with the given API parameters. If it isn't found, it will be created.
