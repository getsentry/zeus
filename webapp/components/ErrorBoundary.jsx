import React, {Component} from 'react';
import PropTypes from 'prop-types';
import idx from 'idx';
import {isEqual} from 'lodash';
// This is being pulled form the CDN currently
// import Raven from 'raven-js';

import IdentityNeedsUpgradeError from './IdentityNeedsUpgradeError';
import InternalError from './InternalError';
import NetworkError from './NetworkError';
import NotFoundError from './NotFoundError';
import * as errors from '../errors';

export default class ErrorBoundary extends Component {
  static contextTypes = {
    router: PropTypes.object
  };

  static propTypes = {
    children: PropTypes.node,
    location: PropTypes.object
  };

  constructor(...params) {
    super(...params);
    this.state = {error: null, location: null};
  }

  UNSAFE_componentWillReceiveProps(nextProps, nextContext) {
    let {router} = nextContext;
    if (!isEqual(this.state.location, router.location)) {
      this.setState({error: null, location: null});
    }
    super.componentWillReceiveProps &&
      super.componentWillReceiveProps(nextProps, nextContext);
  }

  componentDidCatch(error, errorInfo) {
    this.setState({
      error,
      location: {...(idx(this.context.router, _ => _.location) || {})}
    });
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
            // XXX(dcramer): we can't seem to render <Login> here as error boundary doesn't recover
            window.location.href = `/login/?next=${encodeURIComponent(
              window.location.pathname
            )}`;
            return null;
          } else if (error.code === 502) {
            return <NetworkError error={error} url={error.data.url} />;
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
