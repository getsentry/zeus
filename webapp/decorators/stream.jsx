import React, {Component} from 'react';

export const subscribe = config => {
  return DecoratedComponent => {
    return class StreamSubscription extends Component {
      static contextTypes = {...DecoratedComponent.contextTypes};

      componentWillMount() {
        this.subscriptions = config(this.props, this.context);
      }

      componentWillUnmount() {
        this.subscriptions.forEach(sub => {
          // disconnect
        });
      }
      render() {
        return <DecoratedComponent {...this.props} />;
      }
    };
  };
};
