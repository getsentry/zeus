import React from 'react';
import {render} from 'enzyme';

import BuildList from '../BuildList';

describe('BuildList', () => {
  it('renders', () => {
    const tree = render(
      <BuildList
        buildList={[TestStubs.Build({repository: TestStubs.Repository()})]}
        location={{query: '', pathname: '/path-name'}}
      />
    );
    expect(tree).toMatchSnapshot();
  });
});
