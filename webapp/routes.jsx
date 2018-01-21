import React from 'react';
import {IndexRoute, Route, IndexRedirect} from 'react-router';
import Loadable from 'react-loadable';

import App from './pages/App';
import BuildArtifacts from './pages/BuildArtifacts';
import BuildCoverage from './pages/BuildCoverage';
import BuildDetails from './pages/BuildDetails';
import BuildDiff from './pages/BuildDiff';
import BuildOverview from './pages/BuildOverview';
import BuildStyleViolationList from './pages/BuildStyleViolationList';
import BuildTestList from './pages/BuildTestList';
import Dashboard from './pages/Dashboard';
import DashboardOrWelcome from './pages/DashboardOrWelcome';
import OwnerDetails from './pages/OwnerDetails';
import RepositoryDetails from './pages/RepositoryDetails';
import RepositoryBuildList from './pages/RepositoryBuildList';
import RepositoryFileCoverage from './pages/RepositoryFileCoverage';
import RepositoryHooks from './pages/RepositoryHooks';
import RepositoryHookCreate from './pages/RepositoryHookCreate';
import RepositoryHookDetails from './pages/RepositoryHookDetails';
import RepositoryRevisionList from './pages/RepositoryRevisionList';
import RepositorySettingsLayout from './pages/RepositorySettingsLayout';
import RepositorySettings from './pages/RepositorySettings';
import RepositoryStats from './pages/RepositoryStats';
import RepositoryTests from './pages/RepositoryTests';
import RepositoryTestList from './pages/RepositoryTestList';
import RepositoryTestTree from './pages/RepositoryTestTree';
import RevisionArtifacts from './pages/RevisionArtifacts';
import RevisionCoverage from './pages/RevisionCoverage';
import RevisionDetails from './pages/RevisionDetails';
import RevisionDiff from './pages/RevisionDiff';
import RevisionOverview from './pages/RevisionOverview';
import RevisionTestList from './pages/RevisionTestList';
import UserBuildList from './pages/UserBuildList';
import Welcome from './pages/Welcome';

import Login from './components/Login';
import NotFoundError from './components/NotFoundError';
import PageLoading from './components/PageLoading';

import requireAuth from './utils/requireAuth';

const AsyncSettings = Loadable({
  loader: () => import('./pages/Settings'),
  loading: PageLoading
});

const AsyncAccountSettings = Loadable({
  loader: () => import('./pages/AccountSettings'),
  loading: PageLoading
});

const AsyncGitHubRepositoryList = Loadable({
  loader: () => import('./pages/GitHubRepositoryList'),
  loading: PageLoading
});

const AsyncTokenSettings = Loadable({
  loader: () => import('./pages/TokenSettings'),
  loading: PageLoading
});

export default (
  <Route path="/" component={App}>
    <IndexRoute component={DashboardOrWelcome} />
    <Route path="/welcome" component={Welcome} />
    <Route path="/dashboard" component={requireAuth(Dashboard)} />
    <Route path="/settings" component={requireAuth(AsyncSettings)}>
      <IndexRedirect to="/settings/account" />
      <Route path="account" component={AsyncAccountSettings} />
      <Route path="github/repos" component={AsyncGitHubRepositoryList} />
      <Route path="token" component={AsyncTokenSettings} />
    </Route>
    <Route path="/builds" component={requireAuth(UserBuildList)} />
    <Route path="/login" component={Login} />
    <Route path="/:provider/:ownerName" component={requireAuth(OwnerDetails)} />
    <Route
      path="/:provider/:ownerName/:repoName"
      component={requireAuth(RepositoryDetails)}>
      <IndexRoute component={requireAuth(RepositoryRevisionList)} />
      <Route path="builds" component={RepositoryBuildList} />
      <Route path="coverage" component={RepositoryFileCoverage} />
      <Route path="stats" component={RepositoryStats} />
      <Route path="settings" component={RepositorySettingsLayout}>
        <IndexRoute component={RepositorySettings} />
        <Route path="hooks" component={RepositoryHooks} />
        <Route path="hooks/create" component={RepositoryHookCreate} />
        <Route path="hooks/:hookId" component={RepositoryHookDetails} />
      </Route>
      <Route path="tests" component={RepositoryTests}>
        <IndexRoute component={RepositoryTestTree} />
        <Route path="all" component={RepositoryTestList} />
      </Route>
      <Route path="builds/:buildNumber" component={BuildDetails}>
        <IndexRoute component={BuildOverview} />
        <Route path="coverage" component={BuildCoverage} />
        <Route path="diff" component={BuildDiff} />
        <Route path="style-violations" component={BuildStyleViolationList} />
        <Route path="tests" component={BuildTestList} />
        <Route path="artifacts" component={BuildArtifacts} />
      </Route>
      <Route path="revisions/:sha" component={RevisionDetails}>
        <IndexRoute component={RevisionOverview} />
        <Route path="coverage" component={RevisionCoverage} />
        <Route path="diff" component={RevisionDiff} />
        <Route path="tests" component={RevisionTestList} />
        <Route path="artifacts" component={RevisionArtifacts} />
      </Route>
    </Route>
    <Route path="*" component={NotFoundError} />
  </Route>
);
