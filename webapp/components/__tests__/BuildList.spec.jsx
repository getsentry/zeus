import React from 'react';
import {render} from 'enzyme';

import BuildList from '../BuildList';

describe('BuildList', () => {
  it('renders', () => {
    let repository = TestStubs.Repository();
    const tree = render(
      <BuildList
        buildList={[
          TestStubs.Build({repository}),
          TestStubs.Build({repository, revision: null})
        ]}
        location={{query: '', pathname: '/path-name'}}
      />
    );
    expect(tree).toMatchSnapshot();
  });
});
