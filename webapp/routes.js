import React from 'react';
import {IndexRoute, Route} from 'react-router';

import App from './components/App';
import BuildDetails from './components/BuildDetails';
import BuildJobList from './components/BuildJobList';
import BuildTestList from './components/BuildTestList';
import Dashboard from './components/Dashboard';
import Login from './components/Login';
import NotFound from './components/NotFound';
import RepositoryDetails from './components/RepositoryDetails';
import RepositoryBuildList from './components/RepositoryBuildList';

import requireAuth from './utils/requireAuth';

export default (
  <Route path="/" component={App}>
    <IndexRoute component={requireAuth(Dashboard)} />
    <Route path="/repos/:repoName" component={requireAuth(RepositoryDetails)}>
      <IndexRoute component={RepositoryBuildList} />
      <Route path="builds/:buildNumber" component={BuildDetails}>
        <IndexRoute component={BuildJobList} />
        <Route path="tests" component={BuildTestList} />
      </Route>
    </Route>
    <Route path="/login" component={Login} />
    <Route path="*" component={NotFound} />
  </Route>
);
