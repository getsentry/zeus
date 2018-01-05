import React from 'react';
import {shallow} from 'enzyme';
import configureStore from 'redux-mock-store';

import App from '../App';

const mockStore = configureStore();

describe('App', () => {
  it('renders without crashing', () => {
    let store = mockStore({
      auth: {}
    });
    const tree = shallow(<App store={store} />);
    expect(tree).toMatchSnapshot();
  });
});
