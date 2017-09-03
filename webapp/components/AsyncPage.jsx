import DocumentTitle from 'react-document-title';
import React, {Component} from 'react';
import PropTypes from 'prop-types';
import {isEqual} from 'lodash';

import PageLoadingIndicator from './PageLoadingIndicator';

import {Client} from '../api';

export default class AsyncPage extends Component {
  static contextTypes = {
    router: PropTypes.object.isRequired
  };

  static errorHandler = (component, fn) => {
    return function(...args) {
      try {
        return fn(...args);
      } catch (err) {
        /*eslint no-console:0*/
        setTimeout(() => {
          throw err;
        });
        // component.setState({
        //   error: err
        // });
        return null;
      }
    };
  };

  constructor(props, context) {
    super(props, context);

    this.refreshData = AsyncPage.errorHandler(this, this.refreshData.bind(this));
    this.render = AsyncPage.errorHandler(this, this.render.bind(this));

    this.state = this.getDefaultState(props, context);

    this.timers = {};
  }

  componentWillMount() {
    this.api = new Client();
    this.refreshData();
  }

  componentWillReceiveProps(nextProps, nextContext) {
    if (
      !isEqual(this.props.params, nextProps.params) ||
      !isEqual((this.props.location || {}).query, (nextProps.location || {}).query)
    ) {
      this.remountComponent(nextProps, nextContext);
    }
  }

  componentWillUnmount() {
    this.api && this.api.clear();
    Object.keys(this.timers).forEach(key => {
      window.clearTimeout(this.timers[key]);
    });
  }

  // XXX: cant call this getInitialState as React whines
  getDefaultState(props, context) {
    let endpoints = this.getEndpoints();
    let state = {
      // has all data finished requesting?
      loading: endpoints.length > 0,
      // is there an error loading ANY data?
      error: false,
      errors: {}
    };
    endpoints.forEach(([stateKey, endpoint]) => {
      state[stateKey] = null;
    });
    return state;
  }

  remountComponent(props, context) {
    this.setState(this.getDefaultState(props, context), this.refreshData);
  }

  refreshData() {
    let endpoints = this.getEndpoints();
    if (!endpoints.length) {
      this.setState({
        loading: false,
        error: false
      });
      return;
    }
    this.api.clear();
    this.setState({
      loading: true,
      error: false,
      remainingRequests: endpoints.length
    });
    endpoints.forEach(([stateKey, endpoint, params]) => {
      this.fetchDataForEndpoint(stateKey, endpoint, params);
    });
  }

  fetchDataForEndpoint(stateKey, endpoint, params) {
    this.api.request(endpoint, params).then(
      data => {
        this.setState(prevState => {
          return {
            [stateKey]: data,
            remainingRequests: Math.max(prevState.remainingRequests - 1, 0),
            loading: prevState.remainingRequests > 1
          };
        });
        // "Real Time"
        // XXX(dcramer): Sophos (an antivirus tool that Sentry mandates) causes issues
        // with things like websockets and other streaming requests. On top of that,
        // streaming in data is a huge pain in the ass, so here's our "real time" bit.
        if (this.timers[stateKey]) window.clearTimeout(this.timers[stateKey]);
        if (this.shouldFetchUpdates(stateKey, endpoint, params)) {
          this.timers[stateKey] = window.setTimeout(
            () => this.fetchDataForEndpoint(stateKey, endpoint, params),
            5000
          );
        }
      },
      error => {
        this.setState(prevState => {
          return {
            [stateKey]: null,
            errors: {
              ...prevState.errors,
              [stateKey]: error
            },
            remainingRequests: Math.max(prevState.remainingRequests - 1, 0),
            loading: prevState.remainingRequests > 1,
            error: true
          };
        });
      }
    );
  }

  /**
   * Return a list of endpoint queries to make.
   *
   * return [
   *   ['stateKeyName', '/endpoint/', {optional: 'query params'}]
   * ]
   */
  getEndpoints() {
    return [];
  }

  getTitle() {
    return null;
  }

  /**
   * Return a boolean indicating whether this endpoint should attempt to
   * automatically fetch updates (using polling).
   */
  shouldFetchUpdates(stateKey, endpoint, params) {
    return true;
  }

  renderLoading() {
    return <PageLoadingIndicator />;
  }

  renderError(error) {
    // TODO
    return <p style={{color: 'red'}}>Something went wrong!</p>;
    // return <RouteError error={error} component={this} onRetry={this.remountComponent} />;
  }

  renderContent() {
    return this.state.loading
      ? this.renderLoading()
      : this.state.error
        ? this.renderError(new Error('Unable to load all required endpoints'))
        : this.renderBody();
  }

  render() {
    let title = this.getTitle();
    if (!title)
      return (
        <div>
          {this.renderContent()}
        </div>
      );
    return (
      <DocumentTitle title={title}>
        {this.renderContent()}
      </DocumentTitle>
    );
  }
}
