import React from 'react';
import {IndexRoute, Route, IndexRedirect} from 'react-router';

import App from './pages/App';
import AddRepository from './pages/AddRepository';
import BuildCoverage from './pages/BuildCoverage';
import BuildDetails from './pages/BuildDetails';
import BuildDiff from './pages/BuildDiff';
import BuildOverview from './pages/BuildOverview';
import BuildTestList from './pages/BuildTestList';
import Login from './pages/Login';
import NotFound from './pages/NotFound';
import ProjectDetails from './pages/ProjectDetails';
import ProjectBuildList from './pages/ProjectBuildList';
import ProjectTestList from './pages/ProjectTestList';
import UserBuildList from './pages/UserBuildList';

import requireAuth from './utils/requireAuth';

export default (
  <Route path="/" component={App}>
    <IndexRedirect to="/builds" />
    <Route path="/add-repository" component={requireAuth(AddRepository)} />
    <Route path="/builds" component={requireAuth(UserBuildList)} />
    <Route path="/:orgName/:projectName" component={requireAuth(ProjectDetails)}>
      <IndexRoute component={ProjectBuildList} />
      <Route path="tests" component={ProjectTestList} />
      <Route path="builds/:buildNumber" component={BuildDetails}>
        <IndexRoute component={BuildOverview} />
        <Route path="coverage" component={BuildCoverage} />
        <Route path="diff" component={BuildDiff} />
        <Route path="tests" component={BuildTestList} />
      </Route>
    </Route>
    <Route path="/login" component={Login} />
    <Route path="*" component={NotFound} />
  </Route>
);
