import React from 'react';
import {render} from 'enzyme';

import CoverageSummary from '../CoverageSummary';

const FIXTURE = [
  {
    data: 'NNNNNNNNNNNNNNNNNNCCNNNCCCCCUCCCNNCNNNUNNNNNNNNNNC',
    diff_lines_covered: 2.0,
    diff_lines_uncovered: 0.0,
    filename: 'webapp/components/Collapsable.jsx',
    lines_covered: 12.0,
    lines_uncovered: 2.0
  }
];

describe('CoverageSummary', () => {
  it('renders', () => {
    const tree = render(
      <CoverageSummary
        build={TestStubs.Build()}
        repo={TestStubs.Repository()}
        coverage={FIXTURE}
        location={{query: '', pathname: '/path-name'}}
      />
    );
    expect(tree).toMatchSnapshot();
  });
});
