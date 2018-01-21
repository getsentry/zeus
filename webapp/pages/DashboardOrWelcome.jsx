import React, {Component} from 'react';
import PropTypes from 'prop-types';
import {connect} from 'react-redux';

import Dashboard from './Dashboard';
import Welcome from './Welcome';

class DashboardOrWelcome extends Component {
  static propTypes = {
    isAuthenticated: PropTypes.bool,
    user: PropTypes.object
  };

  render() {
    if (this.props.isAuthenticated) return <Dashboard />;
    return <Welcome />;
  }
}

export default connect(({auth}) => ({
  user: auth.user,
  isAuthenticated: auth.isAuthenticated
}))(DashboardOrWelcome);
