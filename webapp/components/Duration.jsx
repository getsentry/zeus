import React, {Component} from 'react';
import PropTypes from 'prop-types';

import {getDuration} from '../utils/duration';

export default class Duration extends Component {
  static propTypes = {
    ms: PropTypes.number.isRequired,
    short: PropTypes.bool
  };

  static defaultProps = {
    short: true
  };

  render() {
    let {ms, short} = this.props;
    return <span>{getDuration(ms, short)}</span>;
  }
}
