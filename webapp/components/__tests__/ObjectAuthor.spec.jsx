import React from 'react';
import {shallow} from 'enzyme';

import ObjectAuthor from '../ObjectAuthor';

describe('ObjectAuthor', () => {
  it('renders source author', () => {
    const tree = shallow(
      <ObjectAuthor
        data={{
          source: {
            author: {
              email: 'foo@example.com',
              name: 'Foo Bar'
            }
          }
        }}
      />
    );
    expect(tree).toMatchSnapshot();
  });

  it('renders source anonymous', () => {
    const tree = shallow(
      <ObjectAuthor
        data={{
          source: {
            author: null
          }
        }}
      />
    );
    expect(tree).toMatchSnapshot();
  });

  it('renders author', () => {
    const tree = shallow(
      <ObjectAuthor
        data={{
          author: {
            email: 'foo@example.com',
            name: 'Foo Bar'
          }
        }}
      />
    );
    expect(tree).toMatchSnapshot();
  });

  it('renders anonymous', () => {
    const tree = shallow(
      <ObjectAuthor
        data={{
          author: null
        }}
      />
    );
    expect(tree).toMatchSnapshot();
  });
});
