import React from 'react';
import {IndexRoute, Route} from 'react-router';

import App from './components/App';
import Dashboard from './components/Dashboard';
import Login from './components/Login';
import NotFound from './components/NotFound';
import RepositoryBuildList from './components/RepositoryBuildList';

import requireAuth from './utils/requireAuth';

// <Route path="/" component={requireAuth(App)} />;

export default (
  <Route path="/" component={App}>
    <IndexRoute component={requireAuth(Dashboard)} />
    <Route path="/repos/:repoID" component={requireAuth(RepositoryBuildList)} />
    <Route path="/login" component={Login} />
    <Route path="*" component={NotFound} />
  </Route>
);
