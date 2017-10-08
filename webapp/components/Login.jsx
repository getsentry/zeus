import React, {Component} from 'react';

import GitHubLoginButton from './GitHubLoginButton';
import Modal from './Modal';

export default class Login extends Component {
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
