import React, {Component} from 'react';
import PropTypes from 'prop-types';

import Modal from './Modal';

export default class NetworkError extends Component {
  static propTypes = {
    error: PropTypes.object.isRequired,
    url: PropTypes.string
  };

  getHost(url) {
    let l = document.createElement('a');
    l.href = url;
    return l.hostname;
  }

  render() {
    let {error, url} = this.props;
    if (!url) url = error.url;
    return (
      <Modal title="Connection Error" subtext="500">
        <p>
          There was a problem communicating with <strong>{this.getHost(url)}</strong>.
        </p>
        <p>The following may provide you some recourse:</p>
        <ul>
          <li>
            Wait a few seconds and{' '}
            <a
              onClick={() => {
                window.location.href = window.location.href;
              }}
              style={{cursor: 'pointer'}}>
              reload the page
            </a>.
          </li>
          <li>
            If you think this is a bug,{' '}
            <a href="http://github.com/getsentry/zeus/issues">create an issue</a> with
            more details.
          </li>
        </ul>
      </Modal>
    );
  }
}
