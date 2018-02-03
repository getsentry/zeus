import React, {Component} from 'react';
import PropTypes from 'prop-types';
import {connect} from 'react-redux';

class DebugToolbar extends Component {
  static propTypes = {
    items: PropTypes.array
  };

  render() {
    return <div>SQL:</div>;
  }
}

export default connect(
  ({debugToolbar}) => ({
    items: debugToolbar.items
  }),
  {}
)(DebugToolbar);
