import React, {Component} from 'react';
import PropTypes from 'prop-types';
import {connect} from 'react-redux';

import {
  subscribe as subscribeAction,
  unsubscribe as unsubscribeAction
} from '../actions/stream';

export const subscribe = config => {
  return DecoratedComponent => {
    class StreamSubscription extends Component {
      static contextTypes = {...DecoratedComponent.contextTypes};

      static propTypes = {
        subscribe: PropTypes.func.isRequired,
        unsubscribe: PropTypes.func.isRequired
      };

      componentDidMount() {
        this.subscriptions = config(this.props, this.context);
        this.props.subscribe(this.subscriptions);
      }

      componentWillUnmount() {
        this.props.unsubscribe(this.subscriptions);
      }
      render() {
        return <DecoratedComponent {...this.props} />;
      }
    }

    return connect(
      null,
      {subscribe: subscribeAction, unsubscribe: unsubscribeAction}
    )(StreamSubscription);
  };
};
