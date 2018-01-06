import React from 'react';
import {render} from 'enzyme';

import Collapsable from '../Collapsable';

describe('Collapsable', () => {
  it('renders collapsed', () => {
    const tree = render(
      <Collapsable maxVisible={2} collapsable={true}>
        <div>1</div>
        <div>2</div>
        <div>3</div>
        <div>4</div>
      </Collapsable>
    );
    expect(tree).toMatchSnapshot();
  });
});
