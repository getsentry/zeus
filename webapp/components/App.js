import React, {Component} from 'react';
import PropTypes from 'prop-types';
import {connect} from 'react-redux';
import {authSession, logout} from '../actions/auth';

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
        <p>
          You are logged in as{' '}
          {this.props.user
            ? <span>
                <strong>{this.props.user.email}</strong> (<a onClick={this.props.logout}>Logout</a>)
              </span>
            : <em>anonymous</em>}
        </p>
        {this.props.isAuthenticated === null ? <div>Loading!</div> : this.props.children}
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

export default connect(mapStateToProps, {authSession, logout})(App);
