import React from 'react';
import PropTypes from 'prop-types';
import {connect} from 'react-redux';

export default function(ComposedComponent) {
  class Authenticate extends React.Component {
    static propTypes = {
      isAuthenticated: PropTypes.bool
    };

    static contextTypes = {
      router: PropTypes.object.isRequired
    };

    componentWillMount() {
      if (this.props.isAuthenticated === false) {
        this.context.router.push('/login');
      }
    }

    componentWillUpdate(nextProps) {
      // logged out
      if (this.props.isAuthenticated && !nextProps.isAuthenticated) {
        this.context.router.push('/login');
      }
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
