import React, {Component} from 'react';
import PropTypes from 'prop-types';
import {connect} from 'react-redux';
import {authSession} from '../actions/auth';

class App extends Component {
  static propTypes = {
    isAuthenticated: PropTypes.bool,
    user: PropTypes.object,
    authSession: PropTypes.func.isRequired
  };

  componentWillMount() {
    this.props.authSession();
  }

  render() {
    return (
      <div className="App">
        <p>
          You are logged in as{' '}
          {this.props.user ? this.props.user.email : <em>anonymous</em>}
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

export default connect(mapStateToProps, {authSession})(App);
