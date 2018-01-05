import React from 'react';
import {shallow} from 'enzyme';

import FileSize from '../FileSize';

describe('FileSize', () => {
  it('renders bytes', () => {
    const tree = shallow(<FileSize value={413} />);
    expect(tree).toMatchSnapshot();
  });
});
