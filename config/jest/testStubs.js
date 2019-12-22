import sinon from 'sinon';
import thunk from 'redux-thunk';
import PropTypes from 'prop-types';
import configureStore from 'redux-mock-store';
import {createMount, createShallow} from 'enzyme-context';
import {routerContext} from 'enzyme-context-react-router-3';
import {reduxContext} from 'enzyme-context-redux';

const mockStore = configureStore([thunk]);

const createRouter = () => ({
  push: sinon.spy(),
  replace: sinon.spy(),
  go: sinon.spy(),
  goBack: sinon.spy(),
  goForward: sinon.spy(),
  setRouteLeaveHook: sinon.spy(),
  isActive: sinon.spy(),
  createHref: sinon.spy()
});

const createStore = state =>
  // TODO(dcramer): It'd be nice if this could be auto generated
  mockStore({
    auth: {isAuthenticated: null, user: null},
    builds: {
      items: [],
      loaded: false,
      links: {}
    },
    repos: {
      items: [],
      loaded: false
    },
    ...state
  });

const plugins = {
  store: reduxContext({
    createStore
  }),
  history: routerContext()
};

window.TestStubs = {
  mount: createMount(plugins),
  shallow: createShallow(plugins),
  // react-router's 'router' context
  router: createRouter,

  location: () => ({
    query: {},
    pathame: '/mock-pathname/'
  }),

  routerContext: (location, router) => ({
    context: {
      location: location || TestStubs.location(),
      router: router || createRouter()
    },
    childContextTypes: {
      router: PropTypes.object,
      location: PropTypes.object
    }
  }),
  store: createStore,

  storeContext: store => ({
    context: {
      store: store || createStore()
    },
    childContextTypes: {
      store: PropTypes.object
    }
  }),

  standardContext: (params = {}) => {
    let result = TestStubs.routerContext();
    let storeResult = TestStubs.storeContext(params.store);
    result.context = {...result.context, ...storeResult.context};
    result.childContextTypes = {
      ...result.childContextTypes,
      ...storeResult.childContextTypes
    };
    return result;
  },

  Author: params => ({
    email: 'dcramer@gmail.com',
    id: '659dc21c-81db-11e7-988a-0a580a28047a',
    name: 'David Cramer',
    ...params
  }),

  Artifact: params => ({
    created_at: '2019-11-25T23:04:20.322797+00:00',
    download_url:
      '/api/repos/gh/getsentry/zeus/builds/1757/jobs/1/artifacts/e9ce7284-0fd7-11ea-b03f-ce6c6e2f7236/download',
    file: {
      name:
        '56a3/b3d40fd711ea881cee2686f8b362/e9ce72840fd711eab03fce6c6e2f7236_cobertura-coverage.xml',
      size: 221343
    },
    finished_at: '2019-11-25T23:04:21.810095+00:00',
    id: 'e9ce7284-0fd7-11ea-b03f-ce6c6e2f7236',
    job: TestStubs.Job(),
    ...params
  }),

  Build: params => {
    let author = (params || {}).author || TestStubs.Author();
    return {
      created_at: '2018-01-06T16:07:16.830829+00:00',
      external_id: '325812408',
      finished_at: '2018-01-06T16:11:04.393590+00:00',
      id: 'aa7097a2-f2fb-11e7-a565-0a580a28057d',
      label: 'fix: Remove break-word behavior on coverage',
      number: 650,
      provider: 'api.travis-ci.org',
      result: 'passed',
      started_at: '2018-01-06T16:07:16.957093+00:00',
      author: author,
      ref: 'master',
      revision: {
        author: author,
        committed_at: '2018-01-06T16:06:52+00:00',
        created_at: '2018-01-06T16:06:52+00:00',
        message: 'fix: Remove break-word behavior on coverage\n',
        sha: 'eff634a68a01d081c0bdc51752dfa0709781f0e4'
      },
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
    };
  },

  Job: params => {
    return {
      created_at: '2018-01-06T16:07:16.830829+00:00',
      external_id: '325812408',
      finished_at: '2018-01-06T16:11:04.393590+00:00',
      id: 'ea7097a2-f2fb-11e7-a565-0a580a28057e',
      hook_id: 'za7097a2-f2fb-11e7-a565-0a580a28057z',
      allow_failure: false,
      label: 'python: 3.7',
      number: 1,
      provider: 'api.travis-ci.org',
      result: 'passed',
      started_at: '2018-01-06T16:07:16.957093+00:00',
      updated_at: '2018-01-06T16:11:04.393590+00:00',
      failures: [],
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
      url: 'https://travis-ci.org/getsentry/zeus/jobs/325812408',
      ...params
    };
  },

  Email: params => ({
    id: '659dc21c-81db-11e7-988a-0a580a28047a',
    email: 'dcramer@gmail.com',
    verified: true,
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
    permissions: {
      admin: true,
      read: true,
      write: true
    },
    ...params
  }),

  Revision: params => ({
    author: TestStubs.Author(),
    committed_at: '2018-06-08T16:45:55+00:00',
    created_at: '2018-06-08T16:45:55+00:00',
    latest_build: TestStubs.Build({repository: undefined}),
    message: 'fix: Maintain repository in published data\n',
    sha: '26fef62489212d56d0a5037e3e6d876b887e972b',
    ...params
  }),

  User: params => ({
    id: '659dc21c-81db-11e7-988a-0a580a28047a',
    email: 'dcramer@gmail.com',
    created_at: '2018-01-06T16:07:16.814650+00:00',
    ...params
  })
};
