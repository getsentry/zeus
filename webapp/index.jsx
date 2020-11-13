import React from 'react';
import {Router, browserHistory} from 'react-router';
import {render} from 'react-dom';
import {Provider} from 'react-redux';
import {ThemeProvider} from 'emotion-theming';

// These imports (core-js and regenerator-runtime) are replacements for deprecated `@babel/polyfill`
import 'core-js/stable';
import 'regenerator-runtime/runtime';

import '@reach/tooltip/styles.css';

// import {setAuth} from './actions/auth';

import routes from './routes';
import store from './store';

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
