import React, {Component} from 'react';
import PropTypes from 'prop-types';
import {isEqual} from 'lodash';

import PageLoadingIndicator from './PageLoadingIndicator';

import {Client} from '../api';

export default class AsyncComponent extends Component {
  static propTypes = {
    children: PropTypes.node,
    loading: PropTypes.bool,
    error: PropTypes.bool,
    location: PropTypes.object,
    params: PropTypes.object
  };

  static defaultProps = {
    loading: true,
    error: false
  };

  static contextTypes = {
    router: PropTypes.object.isRequired
  };

  constructor(props, context) {
    super(props, context);

    this.reloadData = this.reloadData.bind(this);
    this.render = this.render.bind(this);

    this.state = {
      __location: {
        ...(props.location || context.router.location)
      },
      ...this.getDefaultState(props, context)
    };
  }

  componentWillMount() {
    this.api = new Client();
    this.reloadData();
  }

  componentWillReceiveProps(nextProps, nextContext) {
    let isRouterInContext = !!nextContext.router;
    let isLocationInProps = nextProps.location !== undefined;

    let prevLocation = isLocationInProps ? this.props.location : this.state.__location;
    let currentLocation = isLocationInProps
      ? nextProps.location
      : isRouterInContext
        ? nextContext.router.location
        : null;

    if (!(currentLocation && prevLocation)) {
      return;
    }

    if (
      currentLocation.pathname !== prevLocation.pathname ||
      !isEqual(this.props.params, nextProps.params) ||
      currentLocation.search !== prevLocation.search ||
      currentLocation.state !== prevLocation.state
    ) {
      this.remountComponent(nextProps, nextContext);
    }
  }

  componentWillUnmount() {
    this.api && this.api.clear();
  }

  reloadData(refresh = false) {
    this.loadData(refresh);
  }

  /**
   * Method to asynchronously load data.
   *
   * Must return a Promise.
   */
  loadData() {
    return new Promise(resolve => {
      return resolve();
    });
  }

  // XXX: cant call this getInitialState as React whines
  getDefaultState() {
    return {};
  }

  remountComponent(props, context) {
    /// XXX(dcramer): why is this happening?
    if (props === undefined) return;
    this.setState(
      {
        __location: {
          ...(props.location || context.router.location)
        },
        ...this.getDefaultState(props, context)
      },
      this.reloadData
    );
  }

  renderLoading() {
    return <PageLoadingIndicator />;
  }

  renderError(error) {
    throw error;
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
