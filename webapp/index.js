import React from 'react';
import {Router, browserHistory} from 'react-router';
import {render} from 'react-dom';
import {Provider} from 'react-redux';
import thunk from 'redux-thunk';
import {createStore, applyMiddleware, compose} from 'redux';

import registerServiceWorker from './registerServiceWorker';
import reducers from './reducers';
import {setAuth} from './actions/auth';

import routes from './routes';

const store = createStore(
  reducers,
  compose(
    applyMiddleware(thunk),
    window.devToolsExtension ? window.devToolsExtension() : f => f
  )
);

// we cache the user details in localStorage, but its still fetched on
// the initial load to update/validate
if (localStorage.auth) {
  store.dispatch(setAuth(localStorage.auth));
}

render(
  <Provider store={store}>
    <Router history={browserHistory} routes={routes} />
  </Provider>,
  document.getElementById('root')
);

registerServiceWorker();
