import React, {Component} from 'react';
// This is being pulled form the CDN currently
// import Raven from 'raven-js';

import Modal from './Modal';
import NotFoundError from './NotFoundError';
import {Error404} from '../errors';

export default class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = {error: null};
  }

  componentDidCatch(error, errorInfo) {
    this.setState({error});
    if (error.constructor !== Error404 && window.Raven) {
      window.Raven.captureException(error, {extra: errorInfo});
      window.Raven.lastEventId() && window.Raven.showReportDialog();
    }
  }

  render() {
    let {error} = this.state;
    if (error) {
      switch (error.constructor) {
        case Error404:
          return <NotFoundError />;
        default:
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
                  <a href="http://github.com/getsentry/zeus/issues">
                    create an issue
                  </a>{' '}
                  with more details.
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
    } else {
      return this.props.children;
    }
  }
}
