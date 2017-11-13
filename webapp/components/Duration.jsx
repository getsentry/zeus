import React, {Component} from 'react';
import PropTypes from 'prop-types';

export default class Duration extends Component {
  static propTypes = {
    ms: PropTypes.number.isRequired,
    short: PropTypes.bool
  };

  static defaultProps = {
    short: true
  };

  getDuration() {
    let {ms, short} = this.props;
    let value = Math.abs(ms);
    let result = '';

    if (value >= 604800000) {
      // one week
      result = Math.round(value / 604800000);
      if (short) return `${result}w`;
      return result !== 1 ? result + ' weeks' : result + ' week';
    } else if (value >= 172800000) {
      // two days
      result = Math.round(value / 86400000);
      if (short) return `${result}d`;
      return result !== 1 ? result + ' days' : result + ' day';
    } else if (value >= 7200000) {
      result = Math.round(value / 3600000);
      if (short) return `${result}h`;
      return result !== 1 ? result + ' hours' : result + ' hour';
    } else if (value >= 120000) {
      result = Math.round(value / 60000);
      if (short) return `${result}m`;
      return result !== 1 ? result + ' minutes' : result + ' minute';
    } else if (value >= 1000) {
      result = Math.round(value / 1000);
      if (short) return `${result}s`;
      return result !== 1 ? result + ' seconds' : result + ' second';
    } else {
      result = Math.round(value) / 1000;
      if (short) return `${result}s`;
      return `${result} seconds`;
    }
  }

  render() {
    return (
      <span>
        {this.getDuration()}
      </span>
    );
  }
}
