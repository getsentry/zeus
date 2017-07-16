import React from 'react';
import {IndexRoute, Route, IndexRedirect} from 'react-router';

import App from './pages/App';
import AddRepository from './pages/AddRepository';
import AddProject from './pages/AddProject';
import BuildCoverage from './pages/BuildCoverage';
import BuildDetails from './pages/BuildDetails';
import BuildDiff from './pages/BuildDiff';
import BuildOverview from './pages/BuildOverview';
import BuildTestList from './pages/BuildTestList';
import Login from './pages/Login';
import NotFound from './pages/NotFound';
import OrganizationDetails from './pages/OrganizationDetails';
import ProjectDetails from './pages/ProjectDetails';
import ProjectBuildList from './pages/ProjectBuildList';
import ProjectTestList from './pages/ProjectTestList';
import RepositoryList from './pages/RepositoryList';
import UserBuildList from './pages/UserBuildList';

import requireAuth from './utils/requireAuth';

export default (
  <Route path="/" component={App}>
    <IndexRedirect to="/builds" />
    <Route path="/builds" component={requireAuth(UserBuildList)} />
    <Route path="/add-project" component={requireAuth(AddProject)} />
    <Route path="/:orgName" component={requireAuth(OrganizationDetails)}>
      <Route path="/orgs/:orgName/repos" component={RepositoryList} />
      <Route path="/orgs/:orgName/repos/new" component={AddRepository} />
      <Route path=":projectName" component={ProjectDetails}>
        <IndexRoute component={ProjectBuildList} />
        <Route path="tests" component={ProjectTestList} />
        <Route path="builds/:buildNumber" component={BuildDetails}>
          <IndexRoute component={BuildOverview} />
          <Route path="coverage" component={BuildCoverage} />
          <Route path="diff" component={BuildDiff} />
          <Route path="tests" component={BuildTestList} />
        </Route>
      </Route>
    </Route>
    <Route path="/login" component={Login} />
    <Route path="*" component={NotFound} />
  </Route>
);
