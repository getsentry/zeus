import React, {Component} from 'react';
import PropTypes from 'prop-types';
import {connect} from 'react-redux';

import GitHubLoginButton from './GitHubLoginButton';
import Modal from './Modal';

class Login extends Component {
  static propTypes = {
    isAuthenticated: PropTypes.bool
  };

  static contextTypes = {
    router: PropTypes.object.isRequired
  };

  componentWillMount() {
    if (this.props.isAuthenticated) {
      this.context.router.push('/');
    }
  }

  componentWillUpdate(nextProps) {
    if (nextProps.isAuthenticated) {
      this.context.router.push('/');
    }
  }

  render() {
    return (
      <Modal title="Login">
        <p>To continue you will need to first authenticate using your GitHub account.</p>
        <p style={{textAlign: 'center', marginBottom: 0}}>
          <GitHubLoginButton />
        </p>
      </Modal>
    );
  }
}

export default connect(
  state => ({
    isAuthenticated: state.auth.isAuthenticated
  }),
  {}
)(Login);
