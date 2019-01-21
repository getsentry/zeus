import React, {Component} from 'react';
import PropTypes from 'prop-types';
import {connect} from 'react-redux';
import {authSession} from '../actions/auth';
import {loadRepos} from '../actions/repos';

import AsyncComponent from '../components/AsyncComponent';
import ErrorBoundary from '../components/ErrorBoundary';
import Indicators from '../components/Indicators';
import PageLoadingIndicator from '../components/PageLoadingIndicator';

export class RepositoryContext extends AsyncComponent {
  static propTypes = {
    repoList: PropTypes.arrayOf(PropTypes.object),
    ...AsyncComponent.propTypes
  };

  static childContextTypes = {
    ...RepositoryContext.propTypes
  };

  getChildContext() {
    return {
      repoList: this.props.repoList
    };
  }

  loadData() {
    return new Promise(resolve => {
      this.props.loadRepos();
      return resolve();
    });
  }
}

const AuthedContext = connect(
  function(state) {
    return {
      repoList: state.repos.items,
      loading: !state.repos.loaded
    };
  },
  {loadRepos}
)(RepositoryContext);

class App extends Component {
  static propTypes = {
    isAuthenticated: PropTypes.bool,
    children: PropTypes.node,
    user: PropTypes.object,
    authSession: PropTypes.func.isRequired
  };

  componentDidMount() {
    this.props.authSession();
  }

  getTitle() {
    return 'Zeus';
  }

  render() {
    return (
      <React.Fragment>
        <Indicators />
        <ErrorBoundary>
          {!this.props.isAuthenticated === null ? (
            <PageLoadingIndicator />
          ) : (
            <AuthedContext>{this.props.children}</AuthedContext>
          )}
        </ErrorBoundary>
      </React.Fragment>
    );
  }
}

export default connect(
  ({auth}) => ({
    user: auth.user,
    isAuthenticated: auth.isAuthenticated
  }),
  {authSession}
)(App);
