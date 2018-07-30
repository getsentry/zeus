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

  static propTypes = {
    params: PropTypes.object,
    location: PropTypes.object
  };

  constructor(props, context) {
    super(props, context);

    this.refreshData = this.refreshData.bind(this);
    this.render = this.render.bind(this);

    this.state = this.getDefaultState(props, context);
  }

  UNSAFE_componentWillMount() {
    this.api = new Client();
    this.refreshData();
    super.componentWillMount && super.componentWillMount();
  }

  UNSAFE_componentWillReceiveProps(nextProps, nextContext) {
    if (
      !isEqual(this.props.params, nextProps.params) ||
      !isEqual((this.props.location || {}).query, (nextProps.location || {}).query)
    ) {
      this.remountComponent(nextProps, nextContext);
    }
    super.componentWillReceiveProps &&
      super.componentWillReceiveProps(nextProps, nextContext);
  }

  componentWillUnmount() {
    this.api && this.api.clear();
    super.componentWillUnmount && super.componentWillUnmount();
  }

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

  remountComponent(props, context) {
    this.setState(this.getDefaultState(props, context), this.refreshData);
  }

  refreshData() {
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
      this.fetchDataForEndpoint(stateKey, endpoint, params);
    });
  }

  fetchDataForEndpoint(stateKey, endpoint, params) {
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

  renderLoading() {
    return <PageLoadingIndicator />;
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
