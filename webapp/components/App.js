import React, {Component} from 'react';
import PropTypes from 'prop-types';
import {connect} from 'react-redux';
import {authSession, logout} from '../actions/auth';
import styled from 'styled-components';

import './App.css';

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

  render() {
    return (
      <div className="App">
        {this.props.isAuthenticated === null ? <div>Loading!</div> : this.props.children}
        <Auth>
          {this.props.user
            ? <span>
                <strong>{this.props.user.email}</strong> <br/><a onClick={this.props.logout}>Sign out</a>
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
