import React, {Component} from 'react';
import PropTypes from 'prop-types';

import Modal from './Modal';

export default class InternalError extends Component {
  static propTypes = {
    error: PropTypes.object.isRequired
  };

  render() {
    let {error} = this.props;
    return (
      <Modal title="Unhandled Error" subtext="500">
        <p>We hit an unexpected error while loading the page.</p>
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
        <div style={{fontSize: 0.8}}>
          <p>
            {"For the curious, here's what Zeus reported:"}
          </p>
          <pre>
            {error.toString()}
          </pre>
        </div>
      </Modal>
    );
  }
}
