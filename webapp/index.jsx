import React from 'react';
import {Router, browserHistory} from 'react-router';
import {render} from 'react-dom';
import {Provider} from 'react-redux';

import {setAuth} from './actions/auth';

import routes from './routes';
import store from './store';

// we cache the user details in localStorage, but its still fetched on
// the initial load to update/validate
if (localStorage.auth) {
  store.dispatch(setAuth(localStorage.auth));
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
