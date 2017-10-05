import React, {Component} from 'react';
import PropTypes from 'prop-types';
import {connect} from 'react-redux';
import {authSession, logout} from '../actions/auth';
import {loadRepos} from '../actions/repos';
import styled from 'styled-components';

import AsyncComponent from '../components/AsyncComponent';
import ErrorBoundary from '../components/ErrorBoundary';
import Indicators from '../components/Indicators';
import PageLoadingIndicator from '../components/PageLoadingIndicator';

import './App.css';

class RepositoryContext extends AsyncComponent {
  static propTypes = {
    repoList: PropTypes.arrayOf(PropTypes.object)
  };

  static childContextTypes = {
    ...RepositoryContext.propTypes
  };

  getChildContext() {
    return {repoList: this.props.repoList};
  }

  shouldFetchUpdates() {
    return false;
  }

  fetchData() {
    return new Promise((resolve, reject) => {
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
    user: PropTypes.object,
    authSession: PropTypes.func.isRequired,
    logout: PropTypes.func.isRequired
  };

  componentWillMount() {
    this.props.authSession();
  }

  getTitle() {
    return 'Zeus';
  }

  render() {
    return (
      <div className="App">
        <Indicators />
        <ErrorBoundary>
          {!this.props.isAuthenticated === null
            ? <PageLoadingIndicator />
            : <AuthedContext>
                {this.props.children}
              </AuthedContext>}
        </ErrorBoundary>
        <Auth>
          {this.props.user
            ? <span>
                <strong>{this.props.user.email}</strong> <br />
                <a onClick={this.props.logout} style={{cursor: 'pointer'}}>
                  Sign out
                </a>
              </span>
            : <em>anonymous</em>}
        </Auth>
      </div>
    );
  }
}

function mapStateToProps(state) {
  return {
    user: state.auth.user,
    isAuthenticated: state.auth.isAuthenticated
  };
}

const Auth = styled.div`
  position: fixed;
  color: #fff;
  font-size: 11px;
  left: 20px;
  bottom: 15px;
  width: 220px;
  line-height: 1.5;
`;

export default connect(mapStateToProps, {authSession, logout})(App);
