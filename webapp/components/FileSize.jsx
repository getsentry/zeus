import React, {Component} from 'react';
import PropTypes from 'prop-types';

export default class FileSize extends Component {
  static propTypes = {
    value: PropTypes.number.isRequired
  };

  getSize() {
    let {value} = this.props;
    if (value === 0) return '0 B';
    if (!value) return null;

    let i = Math.floor(Math.log(value) / Math.log(1024));
    return (
      (value / Math.pow(1024, i)).toFixed(2) * 1 + ' ' + ['B', 'kB', 'MB', 'GB', 'TB'][i]
    );
  }

  render() {
    return (
      <span>
        {this.getSize()}
      </span>
    );
  }
}
