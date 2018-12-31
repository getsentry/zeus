import xhrmock from 'xhr-mock';
import React from 'react';
import {mount} from 'enzyme';

import UserBuildList from '../UserBuildList';
import {RepositoryContext} from '../App';

describe('UserBuildList', () => {
  let repo, build;
  beforeEach(() => {
    repo = TestStubs.Repository();
    build = TestStubs.Build({repository: repo});

    xhrmock.setup();

    xhrmock.get(/.*/, (req, res) => {
      let {path} = req.url();

      switch (path) {
        case '/api/builds':
          return res.status(200).body(JSON.stringify([build]));
        default:
          return null;
      }
    });
  });

  afterEach(() => xhrmock.teardown());

  it('fetches builds', async () => {
    let store = TestStubs.store({
      repos: {
        items: [repo],
        loaded: true
      },
      builds: {
        items: [],
        loaded: false
      },
      auth: {
        isAuthenticated: true,
        user: TestStubs.User(),
        emails: [TestStubs.Email()]
      }
    });
    let context = TestStubs.standardContext({
      store
    });

    const wrapper = mount(
      <RepositoryContext repoList={[repo]} loading={false}>
        <UserBuildList params={{}} location={TestStubs.location()} />
      </RepositoryContext>,
      context
    );
    expect(wrapper.find('UserBuildList')).toHaveLength(1);
    let userBuildList = wrapper.find('UserBuildList').first();
    expect(userBuildList.props().loading).toBe(true);
    expect(userBuildList.props().buildList).toEqual([]);
    expect(wrapper).toMatchSnapshot();

    // TODO(dcramer): we need to propagate builds but the mock store
    // we're using doesn't seem to be getting the results

    // await tick();

    // expect(wrapper.find('UserBuildList')).toHaveLength(1);
    // userBuildList = wrapper.find('UserBuildList').first();
    // expect(store.getState().builds.items).toHaveLength(1);
    // expect(userBuildList.props().loading).toBe(false);
    // expect(userBuildList.props().buildList).toHaveLength(1);
    // expect(userBuildList.props().buildList)[0] == build;
  });

  it('renders with pre-existing builds loaded', () => {
    let store = TestStubs.store({
      repos: {
        items: [repo],
        loaded: true
      },
      auth: {
        isAuthenticated: true,
        user: TestStubs.User(),
        emails: [TestStubs.Email()]
      },
      builds: {
        items: [build],
        loaded: true,
        links: {}
      }
    });
    let context = TestStubs.standardContext({
      store
    });

    const wrapper = mount(
      <RepositoryContext repoList={[repo]} loading={false}>
        <UserBuildList params={{}} location={TestStubs.location()} />
      </RepositoryContext>,
      context
    );

    expect(wrapper.find('UserBuildList')).toHaveLength(1);
    let userBuildList = wrapper.find('UserBuildList').first();
    expect(userBuildList.props().loading).toBe(false);
    expect(userBuildList.props().buildList).toHaveLength(1);
    expect(userBuildList.props().buildList)[0] == build;
    expect(wrapper).toMatchSnapshot();
  });
});
