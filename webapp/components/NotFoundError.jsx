import React, {Component} from 'react';

import ErrorBox from './ErrorBox';

export default class NotFoundError extends Component {
  render() {
    return (
      <ErrorBox title="Not Found" subtext="404">
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
          <li>
            Return to the <a href="/">dashboard</a>
          </li>
        </ul>
      </ErrorBox>
    );
  }
}
