import xhrmock from 'xhr-mock';
import React from 'react';

import BuildCoverage from '../BuildCoverage';

describe('BuildCoverage', () => {
  // replace the real XHR object with the mock XHR object before each test
  beforeEach(() => xhrmock.setup());

  // put the real XHR object back and clear the mocks after each test
  afterEach(() => xhrmock.teardown());

  it('renders root tree', () => {
    let repo = TestStubs.Repository();
    let build = TestStubs.Build({repository: undefined});

    xhrmock.get(
      `/api/repos/${repo.full_name}/builds/${build.number}/file-coverage-tree`,
      {
        status: 200,
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
          entries: [
            {
              diff_lines_covered: 0,
              diff_lines_uncovered: 0,
              is_leaf: false,
              lines_covered: 0,
              lines_uncovered: 17,
              name: 'AccountSettings.jsx',
              path: 'webapp/pages/AccountSettings.jsx'
            }
          ],
          is_leaf: false,
          trail: []
        })
      }
    );

    let context = TestStubs.standardContext();
    context.context.repo = repo;
    context.context.build = build;

    const wrapper = TestStubs.mount(
      <BuildCoverage
        location={{query: {}}}
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

  it('renders leaf without file source', () => {
    let repo = TestStubs.Repository();
    let build = TestStubs.Build({repository: undefined});

    xhrmock.get(
      `/api/repos/${repo.full_name}/builds/${build.number}/file-coverage-tree?parent=webapp%2Fpages%2FBuildArtifacts.jsx`,
      {
        status: 200,
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
          coverage: {
            data: 'NNNNNNNNUNNNNNNUUUNNNU',
            diff_lines_covered: 0.0,
            diff_lines_uncovered: 0.0,
            filename: 'webapp/pages/BuildArtifacts.jsx',
            lines_covered: 0.0,
            lines_uncovered: 5.0
          },
          entries: [
            {
              diff_lines_covered: 0,
              diff_lines_uncovered: 0,
              is_leaf: true,
              lines_covered: 0,
              lines_uncovered: 5,
              name: 'webapp/pages/BuildArtifacts.jsx',
              path: 'webapp/pages/BuildArtifacts.jsx'
            }
          ],
          file_source: null,
          is_leaf: true,
          trail: [
            {
              name: 'webapp',
              path: 'webapp'
            },
            {
              name: 'pages',
              path: 'webapp/pages'
            },
            {
              name: 'BuildArtifacts.jsx',
              path: 'webapp/pages/BuildArtifacts.jsx'
            }
          ]
        })
      }
    );

    let context = TestStubs.standardContext();
    context.context.repo = repo;
    context.context.build = build;

    const wrapper = TestStubs.mount(
      <BuildCoverage
        location={{query: {parent: 'webapp/pages/BuildArtifacts.jsx'}}}
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
