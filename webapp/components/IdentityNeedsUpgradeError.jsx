import React, {Component} from 'react';
import PropTypes from 'prop-types';

import GitHubLoginButton from '../components/GitHubLoginButton';
import Modal from './Modal';

export default class IdentityNeedsUpgradeError extends Component {
  static propTypes = {
    url: PropTypes.string.isRequired
  };

  render() {
    return (
      <Modal title="Additional Permissions Required">
        <p>
          You will need to grant additional permissions to Zeus to complete your request.
        </p>
        <p style={{textAlign: 'center', marginBottom: 0}}>
          <GitHubLoginButton url={this.props.url} text="Authorize in GitHub" />
        </p>
      </Modal>
    );
  }
}
