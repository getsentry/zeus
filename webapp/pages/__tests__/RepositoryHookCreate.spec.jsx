import React from 'react';
import {render} from 'enzyme';
import sinon from 'sinon';

import {RepositoryHookCreate} from '../RepositoryHookCreate';

describe('RepositoryHookCreate', () => {
  it('renders', () => {
    const tree = render(
      <RepositoryHookCreate addIndicator={sinon.spy()} removeIndicator={sinon.spy()} />,
      {
        context: {repo: TestStubs.Repository(), router: TestStubs.router()}
      }
    );
    expect(tree).toMatchSnapshot();
  });
});
