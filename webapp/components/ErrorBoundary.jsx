import React, {Component} from 'react';
import idx from 'idx';
// This is being pulled form the CDN currently
// import Raven from 'raven-js';

import IdentityNeedsUpgradeError from './IdentityNeedsUpgradeError';
import InternalError from './InternalError';
import Login from './Login';
import NetworkError from './NetworkError';
import NotFoundError from './NotFoundError';
import * as errors from '../errors';

export default class ErrorBoundary extends Component {
  constructor(props) {
    super(props);
    this.state = {error: null};
  }

  unstable_handleError(...params) {
    // This method is a fallback for react <= 16.0.0-alpha.13
    this.componentDidError(...params);
  }

  componentDidCatch(error, errorInfo) {
    this.setState({error});
    if (window.Raven) {
      window.Raven.captureException(error, {extra: errorInfo});
      window.Raven.lastEventId() && window.Raven.showReportDialog();
    }
  }

  render() {
    let {error} = this.state;
    if (error) {
      switch (error.constructor) {
        case errors.ResourceNotFound:
          return <NotFoundError />;
        case errors.ApiError:
          if (
            error.code === 401 &&
            idx(error, _ => _.data.error) === 'identity_needs_upgrade'
          ) {
            return (
              <IdentityNeedsUpgradeError
                location={this.props.location || window.location}
                url={error.data.url}
              />
            );
          } else if (error.code === 401) {
            // TOOD(dcramer): we need to bind next, and likely just redirect to the login view
            return <Login />;
          }
          return <InternalError error={error} />;
        case errors.NetworkError:
          return <NetworkError error={error} />;
        default:
          return <InternalError error={error} />;
      }
    } else {
      return this.props.children;
    }
  }
}
