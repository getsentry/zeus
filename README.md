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
createdb -E utf-8 zeus
zeus db upgrade
zeus devserver
```

## Layout

```
zeus
├── setup.py  // server dependencies
├── zeus  // server code
├── templates  // server-rendered templates
├── public  // general static assets
├── package.json  // web client dependencies
└── webapp // web client
```