import React from 'react';
import {Route} from 'react-router';

import App from './components/App';

import requireAuth from './utils/requireAuth';

export default <Route path="/" component={requireAuth(App)} />;
