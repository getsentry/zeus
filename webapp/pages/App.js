import React, {Component} from 'react';
import PropTypes from 'prop-types';
import {connect} from 'react-redux';
import {authSession, logout} from '../actions/auth';
import styled from 'styled-components';

import AsyncPage from '../components/AsyncPage';
import Indicators from '../components/Indicators';
import PageLoadingIndicator from '../components/PageLoadingIndicator';

import './App.css';

class AuthedContext extends AsyncPage {
  static childContextTypes = {
    repoList: PropTypes.arrayOf(PropTypes.object)
  };

  getChildContext() {
    return {repoList: this.state.repoList || []};
  }

  getEndpoints() {
    return [['repoList', '/repos']];
  }

  renderBody() {
    return this.props.children;
  }
}

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
