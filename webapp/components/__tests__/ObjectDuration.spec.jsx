import React from 'react';
import {render} from 'enzyme';

import ObjectDuration from '../ObjectDuration';

describe('ObjectDuration', () => {
  it('renders unfinished', () => {
    const tree = render(
      <ObjectDuration
        data={{
          started_at: null,
          finished_at: null
        }}
      />
    );
    expect(tree).toMatchSnapshot();
  });

  it('renders in-progress', () => {
    const tree = render(
      <ObjectDuration
        data={{
          started_at: '2017-10-17T04:41:14Z',
          finished_at: null
        }}
      />
    );
    expect(tree).toMatchSnapshot();
  });

  it('renders finished', () => {
    const tree = render(
      <ObjectDuration
        data={{
          started_at: '2017-10-17T04:41:20Z',
          finished_at: '2017-10-17T04:43:31Z'
        }}
      />
    );
    expect(tree).toMatchSnapshot();
  });
});
