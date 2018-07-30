import React, {Component} from 'react';
import PropTypes from 'prop-types';
import idx from 'idx';
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

  componentDidMount() {
    if (this.props.isAuthenticated) {
      this.context.router.push('/');
    }
  }

  componentDidUpdate(nextProps) {
    if (nextProps.isAuthenticated) {
      this.context.router.push('/');
    }
  }

  render() {
    return (
      <Modal title="Login">
        <p>To continue you will need to first authenticate using your GitHub account.</p>
        <p style={{textAlign: 'center'}}>
          <GitHubLoginButton next={idx(this.context.router, _ => _.query.next)} />
        </p>
        <p style={{textAlign: 'center', marginBottom: 0}}>
          <small>
            Zeus asks for both public and private permissions, however we will never
            import any of your code without your explicit consent.
          </small>
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
