import DocumentTitle from 'react-document-title';
import React, {Component} from 'react';
import PropTypes from 'prop-types';
import {isEqual} from 'lodash';

import {Client} from '../api';

export default class AsyncComponent extends Component {
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
        component.setState({
          error: err
        });
        return null;
      }
    };
  };

  constructor(props, context) {
    super(props, context);

    this.fetchData = AsyncComponent.errorHandler(this, this.fetchData.bind(this));
    this.render = AsyncComponent.errorHandler(this, this.render.bind(this));

    this.state = this.getDefaultState();
  }

  componentWillMount() {
    this.api = new Client();
    this.fetchData();
  }

  componentWillReceiveProps(nextProps, nextContext) {
    if (!isEqual(this.props.params, nextProps.params)) {
      this.remountComponent();
    }
  }

  componentWillUnmount() {
    this.api.clear();
  }

  // XXX: cant call this getInitialState as React whines
  getDefaultState() {
    let endpoints = this.getEndpoints();
    let state = {
      // has all data finished requesting?
      loading: true,
      // is there an error loading ANY data?
      error: false,
      errors: {}
    };
    endpoints.forEach(([stateKey, endpoint]) => {
      state[stateKey] = null;
    });
    return state;
  }

  remountComponent() {
    this.setState(this.getDefaultState(), this.fetchData);
  }

  fetchData() {
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
      this.api.request(endpoint, params).then(
        data => {
          this.setState(prevState => {
            return {
              [stateKey]: data,
              remainingRequests: prevState.remainingRequests - 1,
              loading: prevState.remainingRequests > 1
            };
          });
        },
        error => {
          this.setState(prevState => {
            return {
              [stateKey]: null,
              errors: {
                ...prevState.errors,
                [stateKey]: error
              },
              remainingRequests: prevState.remainingRequests - 1,
              loading: prevState.remainingRequests > 1,
              error: true
            };
          });
        }
      );
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
    let endpoint = this.getEndpoint();
    if (!endpoint) return [];
    return [['data', endpoint, this.getEndpointParams()]];
  }

  getTitle() {
    return 'Zeus';
  }

  renderLoading() {
    return <p>Loading...</p>;
  }

  renderError(error) {
    // TODO
    return <p style={{color: 'red'}}>Something went wrong!</p>;
    // return <RouteError error={error} component={this} onRetry={this.remountComponent} />;
  }

  render() {
    return (
      <DocumentTitle title={this.getTitle()}>
        {this.state.loading
          ? this.renderLoading()
          : this.state.error
            ? this.renderError(new Error('Unable to load all required endpoints'))
            : this.renderBody()}
      </DocumentTitle>
    );
  }
}
