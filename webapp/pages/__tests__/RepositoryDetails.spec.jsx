import xhrmock from 'xhr-mock';
import React from 'react';

import {RepositoryDetails} from '../RepositoryDetails';

describe('RepositoryDetails', () => {
  // replace the real XHR object with the mock XHR object before each test
  beforeEach(() => xhrmock.setup());

  // put the real XHR object back and clear the mocks after each test
  afterEach(() => xhrmock.teardown());

  it('renders with repo in context', () => {
    let repo = TestStubs.Repository();

    let context = TestStubs.standardContext();
    context.context.repoList = [repo];

    const wrapper = TestStubs.mount(
      <RepositoryDetails
        params={{
          provider: repo.provider,
          ownerName: repo.owner_name,
          repoName: repo.name
        }}
      />,
      context
    );
    expect(wrapper.state('repo')).toEqual(repo);
    expect(wrapper).toMatchSnapshot();
  });

  it('renders with fetching repo', async () => {
    let repo = TestStubs.Repository();

    xhrmock.get(`/api/repos/${repo.full_name}`, {
      status: 200,
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify(repo)
    });

    let context = TestStubs.standardContext();
    context.context.repoList = [];

    const wrapper = TestStubs.mount(
      <RepositoryDetails
        params={{
          provider: repo.provider,
          ownerName: repo.owner_name,
          repoName: repo.name
        }}
      />,
      context
    );
    await tick();
    expect(wrapper.state('repo').full_name).toEqual(repo.full_name);
    expect(wrapper).toMatchSnapshot();
  });

  // TODO(dcramer): Cant figure out how to test for error boundaries
  // it('handles invalid repo', done => {
  //   let context = TestStubs.standardContext();
  //   context.context.repoList = [];

  //   xhrmock.get('/api/repos/gh/foo/bar', {
  //     status: 404
  //   });

  //   let wrapper = mount(
  //     <RepositoryDetails
  //       params={{
  //         provider: 'gh',
  //         ownerName: 'foo',
  //         repoName: 'bar'
  //       }}
  //     />,
  //     context
  //   );

  //   setTimeout(() => {
  //     expect(() => {
  //       expect(wrapper.state('errors').repo).toEqual('foo');
  //       expect(wrapper.state('repo')).toEqual(null);
  //       expect(wrapper).toMatchSnapshot();
  //       done();
  //     }).toThrow();
  //   });
  // });
});
