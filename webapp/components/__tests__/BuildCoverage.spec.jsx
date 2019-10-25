import React from 'react';
import {render} from 'enzyme';

import BuildCoverage from '../BuildCoverage';

const FIXTURE = {
  entries: [
    {
      is_leaf: false,
      lines_covered: 1,
      lines_uncovered: 0,
      diff_lines_covered: 0,
      diff_lines_uncovered: 0,
      name: 'conftest.py',
      path: 'conftest.py'
    },
    {
      is_leaf: false,
      lines_covered: 0,
      lines_uncovered: 8,
      diff_lines_covered: 0,
      diff_lines_uncovered: 8,
      name: 'setup.py',
      path: 'setup.py'
    },
    {
      is_leaf: false,
      lines_covered: 1528,
      lines_uncovered: 2,
      diff_lines_covered: 1528,
      diff_lines_uncovered: 2,
      name: 'tests/zeus',
      path: 'tests/zeus'
    },
    {
      is_leaf: false,
      lines_covered: 125,
      lines_uncovered: 1715,
      diff_lines_covered: 50,
      diff_lines_uncovered: 100,
      name: 'webapp',
      path: 'webapp'
    },
    {
      is_leaf: false,
      lines_covered: 4473,
      lines_uncovered: 1335,
      diff_lines_covered: 50,
      diff_lines_uncovered: 100,
      name: 'zeus',
      path: 'zeus'
    }
  ],
  is_leaf: false,
  trail: []
};

describe('BuildCoverage', () => {
  it('renders with build', () => {
    const tree = render(
      <BuildCoverage
        result={{
          ...FIXTURE,
          build: TestStubs.Build()
        }}
        location={{query: '', pathname: '/path-name'}}
      />,
      {context: {repo: TestStubs.Repository()}}
    );
    expect(tree).toMatchSnapshot();
  });

  it('renders without build', () => {
    const tree = render(
      <BuildCoverage result={FIXTURE} location={{query: '', pathname: '/path-name'}} />,
      {context: {repo: TestStubs.Repository()}}
    );
    expect(tree).toMatchSnapshot();
  });
});
