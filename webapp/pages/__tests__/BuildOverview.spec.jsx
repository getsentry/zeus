import xhrmock from 'xhr-mock';
import React from 'react';

import BuildOverview from '../BuildOverview';

describe('BuildOverview', () => {
  // replace the real XHR object with the mock XHR object before each test
  beforeEach(() => xhrmock.setup());

  // put the real XHR object back and clear the mocks after each test
  afterEach(() => xhrmock.teardown());

  it('renders with fully formed build', () => {
    let repo = TestStubs.Repository();
    let build = TestStubs.Build({repository: undefined});
    let job = TestStubs.Job();

    xhrmock.get(`/api/repos/${repo.full_name}/builds/${build.number}/artifacts`, {
      status: 200,
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify([])
    });
    xhrmock.get(`/api/repos/${repo.full_name}/builds/${build.number}/jobs`, {
      status: 200,
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify([job])
    });
    xhrmock.get(
      `/api/repos/${repo.full_name}/builds/${build.number}/style-violations?allowed_failures=false`,
      {
        status: 200,
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify([])
      }
    );
    xhrmock.get(
      `/api/repos/${repo.full_name}/builds/${build.number}/tests?result=failed&allowed_failures=false`,
      {
        status: 200,
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify([])
      }
    );
    xhrmock.get(`/api/repos/${repo.full_name}/builds/${build.number}/bundle-stats`, {
      status: 200,
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify([])
    });
    xhrmock.get(
      `/api/repos/${repo.full_name}/builds/${build.number}/file-coverage?diff_only=true`,
      {
        status: 200,
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify([])
      }
    );

    let context = TestStubs.standardContext();
    context.context.build = build;
    context.context.repo = repo;

    const wrapper = TestStubs.mount(
      <BuildOverview
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

    xhrmock.get(`/api/repos/${repo.full_name}/builds/${build.number}/artifacts`, {
      status: 200,
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify([])
    });
    xhrmock.get(`/api/repos/${repo.full_name}/builds/${build.number}/jobs`, {
      status: 200,
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify([])
    });
    xhrmock.get(
      `/api/repos/${repo.full_name}/builds/${build.number}/style-violations?allowed_failures=false`,
      {
        status: 200,
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify([])
      }
    );
    xhrmock.get(
      `/api/repos/${repo.full_name}/builds/${build.number}/tests?result=failed&allowed_failures=false`,
      {
        status: 200,
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify([])
      }
    );
    xhrmock.get(`/api/repos/${repo.full_name}/builds/${build.number}/bundle-stats`, {
      status: 200,
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify([])
    });
    xhrmock.get(
      `/api/repos/${repo.full_name}/builds/${build.number}/file-coverage?diff_only=true`,
      {
        status: 200,
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify([])
      }
    );

    let context = TestStubs.standardContext();
    context.context.build = build;
    context.context.repo = repo;

    const wrapper = TestStubs.mount(
      <BuildOverview
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
