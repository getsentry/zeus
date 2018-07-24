import React, {Component} from 'react';
import PropTypes from 'prop-types';

import {getSize} from '../utils/fileSize';

export default class FileSize extends Component {
  static propTypes = {
    value: PropTypes.number.isRequired
  };

  render() {
    return <span>{getSize(this.props.value)}</span>;
  }
}
