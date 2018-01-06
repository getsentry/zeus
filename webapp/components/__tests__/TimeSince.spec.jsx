import React from 'react';
import {render} from 'enzyme';

import TimeSince from '../TimeSince';

describe('TimeSince', () => {
  it('renders default', () => {
    const tree = render(<TimeSince date="2017-10-15T01:41:20Z" />);
    expect(tree).toMatchSnapshot();
  });

  it('renders 24 hour clock', () => {
    const tree = render(<TimeSince date="2017-10-15T01:41:20Z" clock24Hours />);
    expect(tree).toMatchSnapshot();
  });
});
