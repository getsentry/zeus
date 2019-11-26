import xhrmock from 'xhr-mock';
import React from 'react';

import BuildArtifacts from '../BuildArtifacts';

describe('BuildArtifacts', () => {
  // replace the real XHR object with the mock XHR object before each test
  beforeEach(() => xhrmock.setup());

  // put the real XHR object back and clear the mocks after each test
  afterEach(() => xhrmock.teardown());

  it('renders with artifacts', () => {
    let repo = TestStubs.Repository();
    let build = TestStubs.Build({repository: undefined});

    xhrmock.get(`/api/repos/${repo.full_name}/builds/${build.number}/artifacts`, {
      status: 200,
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify([TestStubs.Artifact()])
    });

    let context = TestStubs.standardContext();
    context.context.repo = repo;
    context.context.build = build;

    const wrapper = TestStubs.mount(
      <BuildArtifacts
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

  it('renders without artifacts', () => {
    let repo = TestStubs.Repository();
    let build = TestStubs.Build({repository: undefined});

    xhrmock.get(`/api/repos/${repo.full_name}/builds/${build.number}/artifacts`, {
      status: 200,
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify([])
    });

    let context = TestStubs.standardContext();
    context.context.repo = repo;
    context.context.build = build;

    const wrapper = TestStubs.mount(
      <BuildArtifacts
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
