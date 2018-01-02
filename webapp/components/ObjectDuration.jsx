import React, {Component} from 'react';
import PropTypes from 'prop-types';
import percentile from 'percentile';

import Duration from './Duration';

const ONE_SECOND_IN_MS = 1000;

export class AggregateDuration extends Component {
  static propTypes = {
    data: PropTypes.arrayOf(
      PropTypes.shape({
        started_at: PropTypes.string,
        finished_at: PropTypes.string,
        duration: PropTypes.number
      })
    ).isRequired
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
    if (data.find(d => !d.finished_at)) {
      this.ticker = setTimeout(() => {
        this.setState({
          duration: this.getDuration(data)
        });
        this.setDurationTicker();
      }, ONE_SECOND_IN_MS);
    }
  }

  getDuration(data) {
    if (!data) return null;
    return percentile(
      95,
      data
        .map(item => {
          if (!item) return null;
          if (item.duration) return item.duration;
          if (!item.finished_at) {
            if (item.started_at) {
              return new Date().getTime() - new Date(item.started_at).getTime();
            }
            return null;
          }
          return (
            new Date(item.finished_at).getTime() - new Date(item.started_at).getTime()
          );
        })
        .filter(i => i !== null)
    );
  }

  render() {
    let {duration} = this.state;
    if (duration === null) return null;
    return <Duration ms={duration} {...this.props} />;
  }
}

export default class ObjectDuration extends Component {
  static propTypes = {
    data: PropTypes.shape({
      started_at: PropTypes.string,
      finished_at: PropTypes.string,
      duration: PropTypes.number
    }).isRequired
  };

  render() {
    return <AggregateDuration data={[this.props.data]} />;
  }
}
