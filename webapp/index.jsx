import React from 'react';
import {Router, browserHistory} from 'react-router';
import {render} from 'react-dom';
import {Provider} from 'react-redux';
import {ThemeProvider} from 'emotion-theming';

// import {setAuth} from './actions/auth';

import routes from './routes';
import store from './store';

// TODO(dcramer): until we can resolve babel not compiling Error classes correctly
// in prod this compounds issues
// we cache the user details in localStorage, but its still fetched on
// the initial load to update/validate
// let auth = localStorage.getItem('auth');
// if (auth) {
//   try {
//     store.dispatch(setAuth(JSON.parse(auth)));
//   } catch (ex) {
//     console.error(ex);
//     localStorage.removeItem('auth');
//   }
// }

import * as Sentry from '@sentry/browser';
import {Tracing} from '@sentry/integrations';

// TODO(dcramer): bind user context
Sentry.init({
  ...(window.SENTRY_CONFIG || {}),
  integrations: [
    new Tracing({
      tracingOrigins: ['localhost', 'zeus.ci', /^\//]
    })
  ]
});

const theme = {
  space: [0, 4, 8, 16, 32, 64, 128, 256]
};

render(
  <ThemeProvider theme={theme}>
    <Provider store={store}>
      <Router history={browserHistory} routes={routes} />
    </Provider>
  </ThemeProvider>,
  document.getElementById('root')
);
