import React, {Component} from 'react';

import Modal from './Modal';

export default class NotFoundError extends Component {
  render() {
    return (
      <Modal title="Not Found" subtext="404">
        <p>
          The resource you were trying to access was not found, or you do not have
          permission to view it.
        </p>
        <p>The following may provide you some recourse:</p>
        <ul>
          <li>
            Wait a few seconds and{' '}
            <a
              onClick={() => {
                window.location.reload();
              }}
              style={{cursor: 'pointer'}}>
              reload the page
            </a>
            .
          </li>
          <li>
            If you think this is a bug,{' '}
            <a href="http://github.com/getsentry/zeus/issues">create an issue</a> with
            more details.
          </li>
          <li>
            Return to the <a href="/">dashboard</a>
          </li>
        </ul>
      </Modal>
    );
  }
}
