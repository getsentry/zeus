import React from 'react';
import {IndexRoute, Route} from 'react-router';

import App from './components/App';
import BuildDetails from './components/BuildDetails';
import BuildJobList from './components/BuildJobList';
import Dashboard from './components/Dashboard';
import Login from './components/Login';
import NotFound from './components/NotFound';
import RepositoryDetails from './components/RepositoryDetails';
import RepositoryBuildList from './components/RepositoryBuildList';

import requireAuth from './utils/requireAuth';

// <Route path="/" component={requireAuth(App)} />;

export default (
  <Route path="/" component={App}>
    <IndexRoute component={requireAuth(Dashboard)} />
    <Route path="/repos/:repoID" component={requireAuth(RepositoryDetails)}>
      <IndexRoute component={RepositoryBuildList} />
      <Route path="builds/:buildID" component={requireAuth(BuildDetails)}>
        <IndexRoute path="jobs" component={BuildJobList} />
      </Route>
    </Route>
    <Route path="/login" component={Login} />
    <Route path="*" component={NotFound} />
  </Route>
);
