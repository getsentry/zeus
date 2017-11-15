import React from 'react';
import {Router, browserHistory} from 'react-router';
import {render} from 'react-dom';
import {Provider} from 'react-redux';

import {setAuth} from './actions/auth';

import routes from './routes';
import store from './store';

import 'react-select/dist/react-select.css';

import './index.css';

// we cache the user details in localStorage, but its still fetched on
// the initial load to update/validate
let auth = localStorage.getItem('auth');
if (auth) {
  try {
    store.dispatch(setAuth(JSON.parse(auth)));
  } catch (ex) {
    console.error(ex);
    localStorage.removeItem('auth');
  }
}

import {registerLanguage} from 'react-syntax-highlighter/dist/light';
import diff from 'react-syntax-highlighter/dist/languages/diff';

registerLanguage('diff', diff);

render(
  <Provider store={store}>
    <Router history={browserHistory} routes={routes} />
  </Provider>,
  document.getElementById('root')
);
