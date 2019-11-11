import React from 'react';
import {shallow} from 'enzyme';
import sinon from 'sinon';

import {App} from '../App';

describe('App', () => {
  it('renders without crashing', () => {
    let authSession = sinon.spy();
    const tree = shallow(<App authSession={authSession} />);
    expect(tree).toMatchSnapshot();
    expect(authSession.called).toBe(true);
  });
});
