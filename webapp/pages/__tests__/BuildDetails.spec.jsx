import xhrmock from 'xhr-mock';
import React from 'react';

import BuildDetails from '../BuildDetails';

describe('BuildDetails', () => {
  // replace the real XHR object with the mock XHR object before each test
  beforeEach(() => xhrmock.setup());

  // put the real XHR object back and clear the mocks after each test
  afterEach(() => xhrmock.teardown());

  it('renders with fully formed build', () => {
    let repo = TestStubs.Repository();
    let build = TestStubs.Build({repository: undefined});

    xhrmock.get(`/api/repos/${repo.full_name}/builds/${build.number}`, {
      status: 200,
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify(build)
    });

    let context = TestStubs.standardContext();
    context.context.repo = repo;

    const wrapper = TestStubs.mount(
      <BuildDetails
        params={{
          provider: repo.provider,
          ownerName: repo.owner_name,
          repoName: repo.name,
          buildNumber: build.number
        }}
      />,
      context
    );
    expect(wrapper).toMatchSnapshot();
  });

  it('renders with incomplete-build', () => {
    let repo = TestStubs.Repository();
    let build = TestStubs.Build({repository: undefined, revision: null});

    xhrmock.get(`/api/repos/${repo.full_name}/builds/${build.number}`, {
      status: 200,
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify(build)
    });

    let context = TestStubs.standardContext();
    context.context.repo = repo;

    const wrapper = TestStubs.mount(
      <BuildDetails
        params={{
          provider: repo.provider,
          ownerName: repo.owner_name,
          repoName: repo.name,
          buildNumber: build.number
        }}
      />,
      context
    );
    expect(wrapper).toMatchSnapshot();
  });
});
