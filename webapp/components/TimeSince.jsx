import React, {Component} from 'react';
import moment from 'moment';
import PropTypes from 'prop-types';

const ONE_MINUTE_IN_MS = 60000;

export default class TimeSince extends Component {
  static propTypes = {
    className: PropTypes.string,
    date: PropTypes.any.isRequired,
    suffix: PropTypes.string,
    clock24Hours: PropTypes.bool
  };

  static defaultProps = {
    suffix: 'ago',
    clock24Hours: false
  };

  static getDerivedStateFromProps(props, state) {
    if (state.date !== props.date) {
      return {
        relative: this.getRelativeDate(props.date, props.suffix),
        date: props.date
      };
    }
    return null;
  }

  constructor(props, context) {
    super(props, context);
    this.state = {
      date: props.date,
      relative: this.getRelativeDate(props.date, props.suffix)
    };
  }

  componentDidMount() {
    this.setRelativeDateTicker();
  }

  componentWillUnmount() {
    if (this.ticker) {
      clearTimeout(this.ticker);
      this.ticker = null;
    }
  }

  setRelativeDateTicker() {
    this.ticker = setTimeout(() => {
      this.setState({
        relative: this.getRelativeDate(this.props.date, this.props.suffix)
      });
      this.setRelativeDateTicker();
    }, ONE_MINUTE_IN_MS);
  }

  getRelativeDate(date, suffix) {
    let mDate = moment(new Date(date));
    if (!suffix) {
      return mDate.fromNow(true);
    } else if (suffix === 'ago') {
      return mDate.fromNow();
    } else if (suffix == 'old') {
      return `${mDate.fromNow(true)} old`;
    } else {
      throw new Error('Unsupported time format suffix');
    }
  }

  render() {
    let date = new Date(this.props.date);
    let format = this.props.clock24Hours ? 'MMMM D YYYY HH:mm:ss z' : 'LLL z';

    return (
      <time
        dateTime={date.toISOString()}
        title={moment(date).format(format)}
        className={this.props.className}>
        {this.state.relative}
      </time>
    );
  }
}
