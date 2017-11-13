import React, {Component} from 'react';
import idx from 'idx';
// This is being pulled form the CDN currently
// import Raven from 'raven-js';

import IdentityNeedsUpgradeError from './IdentityNeedsUpgradeError';
import InternalError from './InternalError';
import Login from './Login';
import NotFoundError from './NotFoundError';
import {ApiError, ResourceNotFound} from '../errors';

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
    if (error.constructor === Error && window.Raven) {
      window.Raven.captureException(error, {extra: errorInfo});
      window.Raven.lastEventId() && window.Raven.showReportDialog();
    }
  }

  render() {
    let {error} = this.state;
    if (error) {
      switch (error.constructor) {
        case ResourceNotFound:
          return <NotFoundError />;
        case ApiError:
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
            return <Login />;
          }
          return <InternalError error={error} />;
        default:
          return <InternalError error={error} />;
      }
    } else {
      return this.props.children;
    }
  }
}
