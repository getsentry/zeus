import React from 'react';
import {shallow} from 'enzyme';

import ObjectAuthor from '../ObjectAuthor';

describe('ObjectAuthor', () => {
  it('renders author', () => {
    const tree = shallow(
      <ObjectAuthor
        data={{
          authors: [
            {
              email: 'foo@example.com',
              name: 'Foo Bar'
            }
          ]
        }}
      />
    );
    expect(tree).toMatchSnapshot();
  });

  it('renders anonymous', () => {
    const tree = shallow(
      <ObjectAuthor
        data={{
          authors: []
        }}
      />
    );
    expect(tree).toMatchSnapshot();
  });
});
