import DocumentTitle from 'react-document-title';
import React from 'react';
import PropTypes from 'prop-types';

import AsyncComponent from './AsyncComponent';

// TODO(dcramer): make this simply call AsyncComponent instead of extend
export default class AsyncPage extends AsyncComponent {
  static propTypes = {
    params: PropTypes.object,
    location: PropTypes.object
  };

  // XXX: cant call this getInitialState as React whines
  getDefaultState(props, context) {
    let endpoints = this.getEndpoints(props, context);
    let state = {
      // has all data finished requesting?
      loading: endpoints.length > 0,
      // is there an error loading ANY data?
      error: false,
      errors: {}
    };
    endpoints.forEach(([stateKey]) => {
      state[stateKey] = null;
    });
    return state;
  }

  reloadData() {
    let endpoints = this.getEndpoints(this.props, this.context);
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
      this.loadDataForEndpoint(stateKey, endpoint, params);
    });
  }

  loadDataForEndpoint(stateKey, endpoint, params) {
    this.api
      .request(endpoint, params)
      .then(data => {
        this.setState(prevState => {
          return {
            [stateKey]: data,
            remainingRequests: Math.max(prevState.remainingRequests - 1, 0),
            loading: prevState.remainingRequests > 1
          };
        });
      })
      .catch(error => {
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
      });
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

  renderError(error) {
    throw this.state.errors[Object.keys(this.state.errors).find(() => true)] || error;
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
    if (!title) return <div>{this.renderContent()}</div>;
    return <DocumentTitle title={title}>{this.renderContent()}</DocumentTitle>;
  }
}
