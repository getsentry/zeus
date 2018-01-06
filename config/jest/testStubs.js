import sinon from 'sinon';

window.TestStubs = {
  // react-router's 'router' context
  router: () => ({
    push: sinon.spy(),
    replace: sinon.spy(),
    go: sinon.spy(),
    goBack: sinon.spy(),
    goForward: sinon.spy(),
    setRouteLeaveHook: sinon.spy(),
    isActive: sinon.spy(),
    createHref: sinon.spy()
  }),

  location: () => ({
    query: {},
    pathame: '/mock-pathname/'
  }),

  Build: params => ({
    created_at: '2018-01-06T16:07:16.830829+00:00',
    external_id: '325812408',
    finished_at: '2018-01-06T16:11:04.393590+00:00',
    id: 'aa7097a2-f2fb-11e7-a565-0a580a28057d',
    label: 'fix: Remove break-word behavior on coverage',
    number: 650,
    provider: 'travis-ci',
    result: 'passed',
    source: {
      author: {
        email: 'dcramer@gmail.com',
        id: '659dc21c-81db-11e7-988a-0a580a28047a',
        name: 'David Cramer'
      },
      created_at: '2018-01-06T16:07:16.814650+00:00',
      id: 'aa6e1f90-f2fb-11e7-a565-0a580a28057d',
      revision: {
        author: {
          email: 'dcramer@gmail.com',
          id: '659dc21c-81db-11e7-988a-0a580a28047a',
          name: 'David Cramer'
        },
        committed_at: '2018-01-06T16:06:52+00:00',
        created_at: '2018-01-06T16:06:52+00:00',
        message: 'fix: Remove break-word behavior on coverage\n',
        sha: 'eff634a68a01d081c0bdc51752dfa0709781f0e4'
      }
    },
    started_at: '2018-01-06T16:07:16.957093+00:00',
    stats: {
      coverage: {
        diff_lines_covered: 0,
        diff_lines_uncovered: 0,
        lines_covered: 6127,
        lines_uncovered: 3060
      },
      style_violations: {
        count: 0
      },
      tests: {
        count: 153,
        count_unique: 153,
        duration: 14673.0,
        failures: 0,
        failures_unique: 0
      },
      webpack: {
        total_asset_size: 0
      }
    },
    status: 'finished',
    url: 'https://travis-ci.org/getsentry/zeus/builds/325812408',
    ...params
  }),

  Repository: params => ({
    backend: 'git',
    created_at: '2017-08-15T17:01:33.206772+00:00',
    full_name: 'gh/getsentry/zeus',
    id: '63e820d4-81db-11e7-a6df-0a580a28004e',
    latest_build: null,
    name: 'zeus',
    owner_name: 'getsentry',
    provider: 'gh',
    url: 'git@github.com:getsentry/zeus.git',
    ...params
  })
};
