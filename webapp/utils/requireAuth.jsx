import React from 'react';
import PropTypes from 'prop-types';
import {connect} from 'react-redux';

export default function(ComposedComponent) {
  class Authenticate extends React.Component {
    static propTypes = {
      isAuthenticated: PropTypes.bool,
      location: PropTypes.object.isRequired
    };

    static contextTypes = {router: PropTypes.object.isRequired};

    componentWillMount() {
      if (this.props.isAuthenticated === false) {
        this.context.router.push({
          pathname: '/login',
          query: {next: this.buildUrl()}
        });
      }
    }

    componentWillUpdate(nextProps) {
      if (nextProps.isAuthenticated === false) {
        this.context.router.push({
          pathname: '/login',
          query: {next: this.buildUrl()}
        });
      }
    }

    buildUrl() {
      let {location} = this.props;
      return `${location.pathname}${location.search || ''}`;
    }

    render() {
      return <ComposedComponent {...this.props} />;
    }
  }

  return connect(
    state => ({
      isAuthenticated: state.auth.isAuthenticated
    }),
    {}
  )(Authenticate);
}
