import React, {Component} from 'react';
import PropTypes from 'prop-types';
import {connect} from 'react-redux';
import {authSession, logout} from '../actions/auth';
import {loadRepos} from '../actions/repos';
import styled from 'styled-components';

import Indicators from '../components/Indicators';
import PageLoadingIndicator from '../components/PageLoadingIndicator';

import './App.css';

class RepositoryContext extends Component {
  static propTypes = {
    repoList: PropTypes.arrayOf(PropTypes.object),
    loaded: PropTypes.bool
  };

  static childContextTypes = {
    ...RepositoryContext.propTypes
  };

  getChildContext() {
    return {repoList: this.props.repoList};
  }

  componentWillMount() {
    this.props.loadRepos();
  }

  render() {
    if (!this.props.loaded) return null;
    return this.props.children;
  }
}

const AuthedContext = connect(
  function(state) {
    return {
      repoList: state.repos.items,
      loaded: state.repos.loaded
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
        {this.props.isAuthenticated === null
          ? <PageLoadingIndicator />
          : <AuthedContext>
              {this.props.children}
            </AuthedContext>}
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
