import React, {Component} from 'react';
import PropTypes from 'prop-types';

import Duration from './Duration';

const ONE_MINUTE_IN_MS = 60000;

export default class dataDuration extends Component {
  static propTypes = {
    data: PropTypes.shape({
      started_at: PropTypes.string,
      finished_at: PropTypes.string,
      duration: PropTypes.number
    }).isRequired
  };

  constructor(props, context) {
    super(props, context);
    this.state = {
      duration: this.getDuration(props.data)
    };
  }

  componentDidMount() {
    this.setDurationTicker();
  }

  componentWillUnmount() {
    if (this.ticker) {
      clearTimeout(this.ticker);
      this.ticker = null;
    }
  }

  setDurationTicker() {
    let {data} = this.props;

    if (!data.finished_at) {
      this.ticker = setTimeout(() => {
        this.setState({
          duration: this.getDuration()
        });
        this.setDurationTicker();
      }, ONE_MINUTE_IN_MS);
    }
  }

  getDuration(data) {
    if (!data) data = this.props.data;
    if (data.duration) return data.duration;
    if (!data.finished_at) {
      if (data.started_at) {
        return new Date().getTime() - new Date(data.started_at).getTime();
      }
      return null;
    }
    return new Date(data.finished_at).getTime() - new Date(data.started_at).getTime();
  }

  render() {
    let {duration} = this.state;
    if (duration === null) return null;
    return <Duration ms={duration} {...this.props} />;
  }
}
