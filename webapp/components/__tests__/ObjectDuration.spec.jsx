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
          started_at: '2017-10-17T04:41:26',
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
          started_at: '2017-10-17T04:41:20',
          finished_at: '2017-10-17T04:43:31'
        }}
      />
    );
    expect(tree).toMatchSnapshot();
  });
});
