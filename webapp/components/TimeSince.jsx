import React, {Component} from 'react';
import moment from 'moment';
import PropTypes from 'prop-types';

export default class TimeSince extends Component {
  static propTypes = {
    date: PropTypes.any.isRequired,
    suffix: PropTypes.string,
    clock24Hours: PropTypes.bool
  };

  static defaultProps = {
    suffix: 'ago',
    clock24Hours: false
  };

  constructor(props, context) {
    super(props, context);
    this.state = {
      relative: this.getRelativeDate()
    };
  }

  componentDidMount() {
    this.setRelativeDateTicker();
  }

  componentWillReceiveProps(nextProps) {
    if (nextProps.date !== this.props.date) {
      this.setState({
        relative: this.getRelativeDate()
      });
    }
  }

  componentWillUnmount() {
    if (this.ticker) {
      clearTimeout(this.ticker);
      this.ticker = null;
    }
  }

  setRelativeDateTicker() {
    let {date} = this.props;
    let ticker;
    let timeSinceInSeconds = (new Date().getTime() - new Date(date).getTime()) / 1000;
    if (timeSinceInSeconds < 300) {
      // update every second
      ticker = 1000;
    } else {
      // update once a minute
      ticker = 60000;
    }
    this.ticker = setTimeout(() => {
      this.setState({
        relative: this.getRelativeDate()
      });
      this.setRelativeDateTicker();
    }, ticker);
  }

  getRelativeDate() {
    let {date} = this.props;
    let mDate = moment(new Date(date));
    if (!this.props.suffix) {
      return mDate.fromNow(true);
    } else if (this.props.suffix === 'ago') {
      return mDate.fromNow();
    } else if (this.props.suffix == 'old') {
      return `${date.fromNow(true)} old`;
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
