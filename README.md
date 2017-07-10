# Zeus

**This project is under development.**

Zeus is a frontend and analytics provider for CI solutions. It is inspired by the work done at Dropbox on [Changes](https://github.com/dropbox/changes/).

The initial version aims to support Travis CI via GitHub, including:

- xunit
- code coverage
- artifacts (e.g. from ``py.test --html``)

## Setup

```shell
mkvirtualenv zeus --python `which python3`
make
zeus init
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
├── Repository
|   ├── ItemOption
|   ├── Build
|   |   ├── Author
|   |   ├── ItemStat
|   |   ├── Source
|   |   └── Job
|   |       ├── Artifact
|   |       ├── FileCoverage
|   |       ├── ItemStat
|   |       └── TestCase
|   |           ├── Artifact
|   |           └── ItemStat
|   └── Source
|       ├── Patch
|       └── Revision
|           └── Author
└── User
    └── Identity
```
