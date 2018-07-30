import xhrmock from 'xhr-mock';
import React from 'react';
import {mount} from 'enzyme';

import Dashboard from '../Dashboard';
import {RepositoryContext} from '../App';

describe('Dashboard', () => {
  // replace the real XHR object with the mock XHR object before each test
  beforeEach(() => xhrmock.setup());

  // put the real XHR object back and clear the mocks after each test
  afterEach(() => xhrmock.teardown());

  it('renders with repos loaded', () => {
    let repo = TestStubs.Repository();
    let store = TestStubs.store({
      repos: {
        items: [repo],
        loaded: true
      }
    });
    let context = TestStubs.standardContext({
      store
    });

    const wrapper = mount(
      <RepositoryContext repoList={[repo]} loading={false}>
        <Dashboard />
      </RepositoryContext>,
      context
    );
    expect(wrapper).toMatchSnapshot();
  });

  it('renders with repos and builds loaded', () => {
    let repo = TestStubs.Repository();
    let build = TestStubs.Build();
    let store = TestStubs.store({
      repos: {
        items: [repo],
        loaded: true
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
        <Dashboard />
      </RepositoryContext>,
      context
    );
    expect(wrapper).toMatchSnapshot();
  });
});
