import React from 'react';
import PropTypes from 'prop-types';
import {connect} from 'react-redux';

export default function(ComposedComponent) {
  class Authenticate extends React.Component {
    static propTypes = {
      isAuthenticated: PropTypes.bool.isRequired
    };

    static contextTypes = {
      router: PropTypes.object.isRequired
    };
    componentWillMount() {
      if (!this.props.isAuthenticated) {
        this.context.router.push('/login');
      }
    }

    componentWillUpdate(nextProps) {
      if (!nextProps.isAuthenticated) {
        this.context.router.push('/');
      }
    }

    render() {
      return <ComposedComponent {...this.props} />;
    }
  }

  function mapStateToProps(state) {
    return {
      isAuthenticated: state.auth.isAuthenticated
    };
  }

  return connect(mapStateToProps, {})(Authenticate);
}
