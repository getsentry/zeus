import React, {Component} from 'react';
import PropTypes from 'prop-types';
import {isEqual} from 'lodash';

import PageLoadingIndicator from './PageLoadingIndicator';

import {Client} from '../api';

export default class AsyncComponent extends Component {
  static propTypes = {
    loading: PropTypes.bool,
    error: PropTypes.bool
  };

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

    this.fetchData = AsyncComponent.errorHandler(this, this.fetchData.bind(this));
    this.render = AsyncComponent.errorHandler(this, this.render.bind(this));

    this.state = this.getDefaultState(props, context);
  }

  componentWillMount() {
    this.api = new Client();
    this.fetchData();
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
  }

  fetchData() {}

  // XXX: cant call this getInitialState as React whines
  getDefaultState(props, context) {
    return {};
  }

  remountComponent(props, context) {
    this.setState(this.getDefaultState(props, context), this.fetchData);
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
    return this.props.loading
      ? this.renderLoading()
      : this.props.error
        ? this.renderError(new Error('Unable to load all required endpoints'))
        : this.renderBody();
  }

  renderBody() {
    return this.props.children;
  }

  render() {
    return this.renderContent();
  }
}
