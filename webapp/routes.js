import React from 'react';
import {IndexRoute, Route, IndexRedirect} from 'react-router';

import App from './pages/App';
import BuildCoverage from './pages/BuildCoverage';
import BuildDetails from './pages/BuildDetails';
import BuildJobList from './pages/BuildJobList';
import BuildTestList from './pages/BuildTestList';
import Login from './pages/Login';
import NotFound from './pages/NotFound';
import RepositoryDetails from './pages/RepositoryDetails';
import RepositoryBuildList from './pages/RepositoryBuildList';
import RepositoryTestList from './pages/RepositoryTestList';
import UserBuildList from './pages/UserBuildList';

import requireAuth from './utils/requireAuth';

export default (
  <Route path="/" component={App}>
    <IndexRedirect to="/builds" />
    <Route path="/builds" component={requireAuth(UserBuildList)} />
    <Route path="/repos/:repoName" component={requireAuth(RepositoryDetails)}>
      <IndexRoute component={RepositoryBuildList} />
      <Route path="tests" component={RepositoryTestList} />
      <Route path="builds/:buildNumber" component={BuildDetails}>
        <IndexRoute component={BuildJobList} />
        <Route path="tests" component={BuildTestList} />
        <Route path="coverage" component={BuildCoverage} />
      </Route>
    </Route>
    <Route path="/login" component={Login} />
    <Route path="*" component={NotFound} />
  </Route>
);
